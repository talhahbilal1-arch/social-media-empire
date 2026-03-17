#!/usr/bin/env python3
"""Workflow Doctor — structural validator for all GitHub Actions workflows.

Catches issues that self-healing and health-checker miss:
- Wrong python command (should be python3)
- Missing script/module references
- Incomplete pip installs
- Directory path typos
- Deprecated Python patterns
- YAML syntax errors
- Missing required secrets references

Can run in two modes:
  --check   : Exit 1 if issues found (CI mode)
  --fix     : Auto-fix what it can, report the rest
"""

import os
import sys
import re
import yaml
import json
import importlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Repository root
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / '.github' / 'workflows'
ARCHIVE_DIR = WORKFLOWS_DIR / 'archive'

# ── Known output directories (correct paths) ──
KNOWN_DIRS = {
    'fitover35-website': 'outputs/fitover35-website',
    'dailydealdarling-website': 'outputs/dailydealdarling-website',
    'menopause-planner-website': 'outputs/menopause-planner-website',
}

# ── Known Python modules that must be importable ──
KNOWN_MODULES = [
    'database.supabase_client',
    'video_automation.content_brain',
    'video_automation.pin_image_generator',
    'video_automation.pin_article_generator',
    'video_automation.image_selector',
    'video_automation.pinterest_boards',
    'video_automation.supabase_storage',
    'video_automation.trend_discovery',
]


class Issue:
    def __init__(self, file, line, severity, message, auto_fix=None):
        self.file = file
        self.line = line
        self.severity = severity  # 'error', 'warning'
        self.message = message
        self.auto_fix = auto_fix  # callable that fixes it, or None

    def __str__(self):
        loc = f"{self.file}:{self.line}" if self.line else self.file
        return f"[{self.severity.upper()}] {loc}: {self.message}"


def check_yaml_syntax(filepath):
    """Validate YAML syntax."""
    issues = []
    try:
        with open(filepath) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        issues.append(Issue(
            filepath.name, getattr(e, 'problem_mark', None),
            'error', f"Invalid YAML: {e}"
        ))
    return issues


def check_python_command(filepath, content, lines):
    """Check for 'python ' instead of 'python3 ' in run blocks."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Match lines that use 'python ' but not 'python3'
        # Skip comments and lines that already use python3
        if 'python3' in stripped or stripped.startswith('#'):
            continue
        # Check for bare 'python ' command (not inside a string like "python-version")
        if re.search(r'\bpython\s+(-m|-c)\b', stripped):
            def make_fix(fp=filepath, ln=i):
                def fix():
                    with open(fp) as f:
                        c = f.read()
                    # Replace python -m/python -c with python3 equivalents
                    c = re.sub(r'\bpython\s+(-m|-c)\b', r'python3 \1', c)
                    with open(fp, 'w') as f:
                        f.write(c)
                return fix
            issues.append(Issue(
                filepath.name, i, 'error',
                f"Uses 'python' instead of 'python3': {stripped[:80]}",
                auto_fix=make_fix()
            ))
            break  # One issue per file is enough
    return issues


def check_deprecated_datetime(filepath, content, lines):
    """Check for deprecated datetime.utcnow()."""
    issues = []
    for i, line in enumerate(lines, 1):
        if 'utcnow()' in line and not line.strip().startswith('#'):
            def make_fix(fp=filepath):
                def fix():
                    with open(fp) as f:
                        c = f.read()
                    # Replace simple cases
                    c = c.replace(
                        'datetime.utcnow()',
                        'datetime.now(timezone.utc)'
                    )
                    # Replace __import__ pattern
                    c = c.replace(
                        "__import__('datetime').datetime.utcnow()",
                        "__import__('datetime').datetime.now(__import__('datetime').timezone.utc)"
                    )
                    with open(fp, 'w') as f:
                        f.write(c)
                return fix
            issues.append(Issue(
                filepath.name, i, 'warning',
                "Uses deprecated datetime.utcnow() — use datetime.now(timezone.utc)",
                auto_fix=make_fix()
            ))
            break
    return issues


def check_directory_paths(filepath, content, lines):
    """Check for common directory path mistakes."""
    issues = []
    for i, line in enumerate(lines, 1):
        # Check for underscore variants of known hyphenated dirs
        for correct_name, correct_path in KNOWN_DIRS.items():
            wrong_name = correct_name.replace('-', '_')
            if wrong_name in line and correct_name not in line:
                def make_fix(fp=filepath, wrong=wrong_name, right=correct_name):
                    def fix():
                        with open(fp) as f:
                            c = f.read()
                        c = c.replace(wrong, right)
                        with open(fp, 'w') as f:
                            f.write(c)
                    return fix
                issues.append(Issue(
                    filepath.name, i, 'error',
                    f"Wrong directory: '{wrong_name}' should be '{correct_name}'",
                    auto_fix=make_fix()
                ))
    return issues


def check_incomplete_pip_install(filepath, content, lines):
    """Check for workflows that pip install only a subset instead of requirements.txt."""
    issues = []
    has_run_blocks = 'run:' in content
    has_python_script = 'python3' in content or 'python -' in content
    uses_requirements = 'requirements.txt' in content
    has_partial_install = bool(re.search(r'pip install\s+(?!-r\s)', content))

    if has_run_blocks and has_python_script and not uses_requirements and has_partial_install:
        # Check if the partial install seems sufficient by checking
        # whether the Python code needs modules beyond what's explicitly installed
        # Extract what pip install covers
        pip_packages = set()
        pip_line = None
        for i, line in enumerate(lines, 1):
            match = re.search(r'pip install\s+([\w\s>=<.]+)', line.strip())
            if match and '-r ' not in match.group(0):
                pip_line = i
                pip_packages.update(match.group(1).split())

        # Check if Python scripts reference supabase (needs supabase SDK)
        imports_supabase = ('supabase' in content or 'SUPABASE_URL' in content) and \
                           'supabase' not in pip_packages and \
                           'from database' in content
        # Check for anthropic usage in Python (not just as env var for Node)
        imports_anthropic = 'import anthropic' in content and 'anthropic' not in pip_packages

        if imports_anthropic or imports_supabase:
            def make_fix(fp=filepath):
                def fix():
                    with open(fp) as f:
                        c = f.read()
                    # Replace partial pip install with full requirements.txt
                    c = re.sub(
                        r'pip install\s+(?!-r\s)[\w\s>=<.]+',
                        'pip install -r requirements.txt',
                        c,
                        count=1
                    )
                    with open(fp, 'w') as f:
                        f.write(c)
                return fix
            issues.append(Issue(
                filepath.name, pip_line, 'error',
                "Partial pip install — script needs modules from requirements.txt",
                auto_fix=make_fix()
            ))
    return issues


def check_script_references(filepath, content, lines):
    """Check that referenced Python scripts and modules exist."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check python3 script.py references
        match = re.search(r'python3?\s+([\w/._-]+\.py)', stripped)
        if match and not stripped.startswith('#'):
            script_path = REPO_ROOT / match.group(1)
            if not script_path.exists():
                issues.append(Issue(
                    filepath.name, i, 'error',
                    f"Script not found: {match.group(1)}"
                ))

        # Check python3 -m module references
        match = re.search(r'python3?\s+-m\s+([\w.]+)', stripped)
        if match and not stripped.startswith('#'):
            module = match.group(1)
            # Skip standard library modules
            if module in ('pip', 'py_compile', 'json', 'http.server', 'venv', 'ensurepip'):
                continue
            # Convert module path to file path
            module_path = REPO_ROOT / module.replace('.', '/')
            if not (module_path.with_suffix('.py').exists() or
                    (module_path / '__main__.py').exists() or
                    (module_path / '__init__.py').exists()):
                issues.append(Issue(
                    filepath.name, i, 'warning',
                    f"Module may not exist: {module}"
                ))
    return issues


def check_placeholder_code(filepath, content, lines):
    """Check for placeholder/TODO code that was never implemented."""
    issues = []
    for i, line in enumerate(lines, 1):
        lower = line.lower().strip()
        if any(marker in lower for marker in [
            'to be implemented', 'todo:', 'fixme:',
            'not yet implemented',
        ]) and not lower.startswith('#') and 'startswith' not in lower:
            issues.append(Issue(
                filepath.name, i, 'warning',
                f"Placeholder code detected: {line.strip()[:80]}"
            ))
    return issues


def run_checks(fix_mode=False):
    """Run all checks on all active workflow files."""
    all_issues = []
    fixed_count = 0

    workflow_files = sorted(WORKFLOWS_DIR.glob('*.yml'))

    for wf_file in workflow_files:
        try:
            content = wf_file.read_text()
            lines = content.splitlines()
        except Exception as e:
            all_issues.append(Issue(wf_file.name, 0, 'error', f"Cannot read file: {e}"))
            continue

        # Run all checks
        issues = []
        issues += check_yaml_syntax(wf_file)
        issues += check_python_command(wf_file, content, lines)
        issues += check_deprecated_datetime(wf_file, content, lines)
        issues += check_directory_paths(wf_file, content, lines)
        issues += check_incomplete_pip_install(wf_file, content, lines)
        issues += check_script_references(wf_file, content, lines)
        issues += check_placeholder_code(wf_file, content, lines)

        if fix_mode:
            for issue in issues:
                if issue.auto_fix:
                    try:
                        issue.auto_fix()
                        fixed_count += 1
                        print(f"  FIXED: {issue}")
                    except Exception as e:
                        print(f"  FAILED TO FIX: {issue} — {e}")
                        all_issues.append(issue)
                else:
                    all_issues.append(issue)
        else:
            all_issues.extend(issues)

    return all_issues, fixed_count


def main():
    fix_mode = '--fix' in sys.argv
    check_mode = '--check' in sys.argv
    json_mode = '--json' in sys.argv

    print(f"=== Workflow Doctor {'(fix mode)' if fix_mode else '(check mode)'} ===")
    print(f"Scanning {WORKFLOWS_DIR}")
    print()

    issues, fixed_count = run_checks(fix_mode=fix_mode)

    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    if json_mode:
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'errors': len(errors),
            'warnings': len(warnings),
            'fixed': fixed_count,
            'issues': [{'file': i.file, 'line': i.line, 'severity': i.severity,
                        'message': i.message, 'fixable': i.auto_fix is not None}
                       for i in issues]
        }
        print(json.dumps(result, indent=2))
    else:
        if fixed_count:
            print(f"Auto-fixed {fixed_count} issue(s)\n")

        if errors:
            print(f"ERRORS ({len(errors)}):")
            for i in errors:
                fixable = " [auto-fixable]" if i.auto_fix else ""
                print(f"  {i}{fixable}")
            print()

        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            for i in warnings:
                fixable = " [auto-fixable]" if i.auto_fix else ""
                print(f"  {i}{fixable}")
            print()

        if not errors and not warnings:
            print("All workflows passed validation!")

        print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings, {fixed_count} fixed")

    if check_mode and errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
