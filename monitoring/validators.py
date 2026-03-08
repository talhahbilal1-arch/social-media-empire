"""
Preventive validators for Social Media Empire.

Catches configuration drift, schema mismatches, dependency gaps, and brand
inconsistencies BEFORE they cause production failures.

Usage:
    python -m monitoring.validators              # Run all validators
    python -m monitoring.validators --check brands
    python -m monitoring.validators --check deps
    python -m monitoring.validators --check schema
    python -m monitoring.validators --check webhooks
    python -m monitoring.validators --fix         # Auto-fix what's possible
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# Brand Registry — THE single source of truth
# ─────────────────────────────────────────────

BRAND_REGISTRY = {
    "daily_deal_darling": {
        "active": True,
        "aliases": [],  # No aliases — this is the canonical name
        "content_bank_file": "deal_topics.json",
        "display_name": "Daily Deal Darling",
    },
    "fitness": {
        "active": True,
        "aliases": ["fitover35"],  # Historical alias — flag if found in code
        "content_bank_file": "fitness_topics.json",
        "display_name": "Fitness Over 35",
    },
    "menopause_planner": {
        "active": True,
        "aliases": [],
        "content_bank_file": "menopause_topics.json",
        "display_name": "Menopause Planner",
    },
    "nurse_planner": {
        "active": False,
        "aliases": [],
        "content_bank_file": None,
        "display_name": "Nurse Planner",
    },
    "adhd_planner": {
        "active": False,
        "aliases": [],
        "content_bank_file": None,
        "display_name": "ADHD Planner",
    },
}

ACTIVE_BRANDS = [b for b, cfg in BRAND_REGISTRY.items() if cfg["active"]]

# All known aliases that should NOT appear in code (use canonical name instead)
STALE_ALIASES = {}
for brand, cfg in BRAND_REGISTRY.items():
    for alias in cfg["aliases"]:
        STALE_ALIASES[alias] = brand


class ValidationResult:
    def __init__(self, name: str):
        self.name = name
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.fixed: list[str] = []

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def fix(self, msg: str):
        self.fixed.append(msg)

    def summary(self) -> str:
        status = "PASS" if self.ok else "FAIL"
        parts = [f"[{status}] {self.name}"]
        for e in self.errors:
            parts.append(f"  ERROR: {e}")
        for w in self.warnings:
            parts.append(f"  WARN:  {w}")
        for f in self.fixed:
            parts.append(f"  FIXED: {f}")
        return "\n".join(parts)


# ─────────────────────────────────────────────
# Validator 1: Brand Consistency
# ─────────────────────────────────────────────

def validate_brands(auto_fix: bool = False) -> ValidationResult:
    """Check that brand names are consistent across all config sources."""
    result = ValidationResult("Brand Consistency")

    # 1. Check utils/config.py brands list matches registry
    config_path = ROOT / "utils" / "config.py"
    if config_path.exists():
        content = config_path.read_text()
        for brand in ACTIVE_BRANDS:
            if f'"{brand}"' not in content:
                result.error(f"Active brand '{brand}' missing from utils/config.py")

    # 2. Check cross_platform_poster.py has all active brands
    poster_path = ROOT / "video_automation" / "cross_platform_poster.py"
    if poster_path.exists():
        content = poster_path.read_text()
        for brand in ACTIVE_BRANDS:
            if f'"{brand}"' not in content:
                result.error(f"Active brand '{brand}' missing from cross_platform_poster.py")

    # 3. Check content bank files exist for active brands
    content_bank = ROOT / "video_automation" / "content_bank"
    for brand in ACTIVE_BRANDS:
        expected_file = BRAND_REGISTRY[brand]["content_bank_file"]
        if expected_file and not (content_bank / expected_file).exists():
            result.error(f"Missing content bank: {expected_file} for brand '{brand}'")

    # 4. Scan for stale aliases in Python files and JSON files
    # Skip this file (validators.py) since it defines the aliases
    this_file = Path(__file__).resolve()
    scan_dirs = [
        ROOT / "video_automation",
        ROOT / "utils",
        ROOT / "monitoring",
        ROOT / "database",
    ]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*"):
            if fpath.resolve() == this_file:
                continue
            if fpath.suffix not in (".py", ".json", ".yml", ".yaml"):
                continue
            if "__pycache__" in str(fpath):
                continue
            try:
                text = fpath.read_text()
            except Exception:
                continue
            for alias, canonical in STALE_ALIASES.items():
                # Look for the alias used as a brand key — not inside URLs,
                # directory paths, or domain names.
                for line_num, line in enumerate(text.splitlines(), 1):
                    # Skip comments
                    stripped = line.lstrip()
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue
                    for pat in [f'"{alias}"', f"'{alias}'"]:
                        if pat in line:
                            # Ignore if it's inside a URL, path, or directory mapping
                            # Check the line AND a few surrounding lines for context
                            lower = line.lower()
                            lines = text.splitlines()
                            context_start = max(0, line_num - 5)
                            nearby = " ".join(lines[context_start:line_num]).lower()
                            combined = lower + " " + nearby
                            if any(ctx in combined for ctx in [
                                "http", "://", ".com", "dir",
                                "content_dir", "brand_content",
                                "path", "site", "domain", "url",
                            ]):
                                continue
                            rel = fpath.relative_to(ROOT)
                            result.error(
                                f"Stale brand alias '{alias}' found in "
                                f"{rel}:{line_num} (should be '{canonical}')"
                            )

    # 5. Scan workflow files
    workflows_dir = ROOT / ".github" / "workflows"
    if workflows_dir.exists():
        for fpath in workflows_dir.glob("*.yml"):
            text = fpath.read_text()
            for alias, canonical in STALE_ALIASES.items():
                if alias in text:
                    result.warn(
                        f"Stale alias '{alias}' in workflow {fpath.name} "
                        f"(should be '{canonical}')"
                    )

    return result


# ─────────────────────────────────────────────
# Validator 2: Dependency Check
# ─────────────────────────────────────────────

def validate_dependencies() -> ValidationResult:
    """Check that all imports in Python files are covered by requirements.txt."""
    result = ValidationResult("Dependency Coverage")

    req_path = ROOT / "requirements.txt"
    if not req_path.exists():
        result.error("requirements.txt not found")
        return result

    # Parse installed package names from requirements.txt
    installed = set()
    for line in req_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Extract package name (before any version specifier)
        pkg = re.split(r"[>=<!\[]", line)[0].strip().lower()
        # Normalize: dashes → underscores (pip convention)
        installed.add(pkg.replace("-", "_"))

    # Standard library modules to ignore (includes __future__)
    stdlib = {
        "__future__", "os", "sys", "json", "re", "ast", "io", "math", "time",
        "datetime", "pathlib", "logging", "typing", "collections",
        "functools", "itertools", "hashlib", "secrets", "random",
        "string", "textwrap", "urllib", "copy", "abc", "dataclasses",
        "enum", "subprocess", "shutil", "tempfile", "threading",
        "concurrent", "asyncio", "base64", "uuid", "traceback",
        "argparse", "configparser", "csv", "email", "html", "http",
        "socket", "ssl", "unittest", "warnings", "glob", "fnmatch",
        "contextlib", "operator", "struct", "codecs", "locale",
        "platform", "importlib", "inspect", "signal", "queue",
        "multiprocessing", "xml", "zipfile", "gzip", "tarfile",
        "smtplib", "mimetypes", "getpass", "numbers", "statistics",
        "fractions", "decimal", "pprint", "textwrap", "token",
        "tokenize", "dis", "pickle", "shelve", "dbm", "sqlite3",
        "zlib", "bz2", "lzma", "webbrowser", "cgi", "ftplib",
        "imaplib", "poplib", "nntplib", "xmlrpc", "difflib",
    }

    # Map common import names to their pip package names
    import_to_pkg = {
        "google": "google_generativeai",
        "google.generativeai": "google_generativeai",
        "PIL": "pillow",
        "bs4": "beautifulsoup4",
        "yaml": "pyyaml",
        "cv2": "opencv_python",
        "dotenv": "python_dotenv",
        "dateutil": "python_dateutil",
        "pydantic_settings": "pydantic_settings",
        "moviepy": "moviepy",
        "edge_tts": "edge_tts",
        "resend": "resend",
        "supabase": "supabase",
        "anthropic": "anthropic",
        "httpx": "httpx",
        "aiohttp": "aiohttp",
        "feedparser": "feedparser",
        "pytrends": "pytrends",
        "backoff": "backoff",
        "requests": "requests",
        "tuspy": "tuspy",
    }

    # Scan all Python files for imports
    scan_dirs = [
        ROOT / "video_automation",
        ROOT / "utils",
        ROOT / "monitoring",
        ROOT / "database",
        ROOT / "email_marketing",
        ROOT / "agents",
        ROOT / "core",
    ]

    third_party_imports = set()
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                tree = ast.parse(fpath.read_text())
            except SyntaxError:
                result.warn(f"Syntax error in {fpath.relative_to(ROOT)}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if top not in stdlib and not _is_local_module(top):
                            third_party_imports.add(top)
                elif isinstance(node, ast.ImportFrom):
                    # Skip relative imports (from .foo import bar)
                    if node.level and node.level > 0:
                        continue
                    if node.module:
                        top = node.module.split(".")[0]
                        if top not in stdlib and not _is_local_module(top):
                            third_party_imports.add(top)

    # Check each third-party import has a matching requirement
    for imp in sorted(third_party_imports):
        pkg_name = import_to_pkg.get(imp, imp).lower().replace("-", "_")
        if pkg_name not in installed:
            result.error(f"Import '{imp}' not covered by requirements.txt (expected package: {pkg_name})")

    return result


def _is_local_module(name: str) -> bool:
    """Check if a module name is a local project module."""
    local_modules = {
        "video_automation", "utils", "monitoring", "database",
        "email_marketing", "agents", "core",
    }
    if name in local_modules:
        return True
    # Check if it's a directory or file at root level
    if (ROOT / name).is_dir() or (ROOT / f"{name}.py").exists():
        return True
    # Check if it's a submodule file inside any of the local packages
    for pkg in local_modules:
        pkg_dir = ROOT / pkg
        if pkg_dir.is_dir():
            if (pkg_dir / f"{name}.py").exists() or (pkg_dir / name).is_dir():
                return True
    return False


# ─────────────────────────────────────────────
# Validator 3: Schema ↔ Code Consistency
# ─────────────────────────────────────────────

def validate_schema() -> ValidationResult:
    """Check that tables/columns referenced in Python code exist in schemas.sql."""
    result = ValidationResult("Schema Consistency")

    schema_path = ROOT / "database" / "schemas.sql"
    if not schema_path.exists():
        result.error("database/schemas.sql not found")
        return result

    sql = schema_path.read_text().lower()

    # Extract table names from CREATE TABLE statements
    tables_in_sql = set(re.findall(r"create\s+table\s+if\s+not\s+exists\s+(\w+)", sql))
    if not tables_in_sql:
        tables_in_sql = set(re.findall(r"create\s+table\s+(\w+)", sql))

    # Extract columns per table
    columns_per_table: dict[str, set[str]] = {}
    for table in tables_in_sql:
        # Find the CREATE TABLE block and extract column names
        pattern = rf"create\s+table\s+(?:if\s+not\s+exists\s+)?{table}\s*\((.*?)\);"
        match = re.search(pattern, sql, re.DOTALL)
        if match:
            block = match.group(1)
            cols = set()
            for line in block.split("\n"):
                line = line.strip().rstrip(",")
                if not line or line.startswith("--"):
                    continue
                # Skip constraints
                if any(line.startswith(kw) for kw in [
                    "primary", "unique", "foreign", "check", "constraint",
                    "create", "grant", "alter", "enable",
                ]):
                    continue
                # First word is column name
                parts = line.split()
                if parts and not parts[0].startswith("("):
                    col = parts[0].strip('"')
                    if col and col.isidentifier():
                        cols.add(col)
            columns_per_table[table] = cols

    # Scan Python files for Supabase table references
    scan_dirs = [
        ROOT / "database",
        ROOT / "core",
        ROOT / "monitoring",
        ROOT / "video_automation",
        ROOT / "agents",
    ]

    table_refs: dict[str, list[str]] = {}  # table -> [files that reference it]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                text = fpath.read_text()
            except Exception:
                continue

            # Find table name references in Supabase calls
            for match in re.finditer(r'\.table\(["\'](\w+)["\']\)', text):
                tbl = match.group(1).lower()
                rel = str(fpath.relative_to(ROOT))
                table_refs.setdefault(tbl, []).append(rel)

    # Check each referenced table exists in schema
    for tbl, files in sorted(table_refs.items()):
        if tbl not in tables_in_sql:
            file_list = ", ".join(set(files))
            result.error(f"Table '{tbl}' referenced in [{file_list}] but missing from schemas.sql")

    return result


# ─────────────────────────────────────────────
# Validator 4: Workflow Consistency
# ─────────────────────────────────────────────

def validate_workflows() -> ValidationResult:
    """Check for duplicate/conflicting workflow definitions."""
    result = ValidationResult("Workflow Consistency")

    workflows_dir = ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        result.warn("No .github/workflows directory")
        return result

    # Check for duplicate cron schedules doing similar things
    crons: dict[str, list[str]] = {}
    for fpath in workflows_dir.glob("*.yml"):
        try:
            text = fpath.read_text()
        except Exception:
            continue

        for match in re.finditer(r"cron:\s*'([^']+)'", text):
            cron = match.group(1)
            crons.setdefault(cron, []).append(fpath.name)

    for cron, files in crons.items():
        if len(files) > 1:
            result.warn(f"Duplicate cron schedule '{cron}' in: {', '.join(files)}")

    # Check that archived workflows aren't accidentally active
    archive_dir = workflows_dir / "archive"
    if archive_dir.exists():
        for fpath in archive_dir.glob("*.yml"):
            text = fpath.read_text()
            if "schedule:" in text and "#" not in text.split("schedule:")[0].split("\n")[-1]:
                result.warn(f"Archived workflow {fpath.name} may still have active schedule triggers")

    return result


# ─────────────────────────────────────────────
# Validator 5: Syntax Check
# ─────────────────────────────────────────────

def validate_syntax() -> ValidationResult:
    """Check all Python files for syntax errors."""
    result = ValidationResult("Python Syntax")

    scan_dirs = [
        ROOT / "video_automation",
        ROOT / "utils",
        ROOT / "monitoring",
        ROOT / "database",
        ROOT / "email_marketing",
        ROOT / "agents",
        ROOT / "core",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for fpath in scan_dir.rglob("*.py"):
            if "__pycache__" in str(fpath):
                continue
            try:
                ast.parse(fpath.read_text())
            except SyntaxError as e:
                rel = fpath.relative_to(ROOT)
                result.error(f"Syntax error in {rel}:{e.lineno} — {e.msg}")

    return result


# ─────────────────────────────────────────────
# Run all validators
# ─────────────────────────────────────────────

def run_all(auto_fix: bool = False, checks: Optional[list[str]] = None) -> list[ValidationResult]:
    """Run all validators and return results."""
    all_validators = {
        "brands": lambda: validate_brands(auto_fix=auto_fix),
        "deps": validate_dependencies,
        "schema": validate_schema,
        "workflows": validate_workflows,
        "syntax": validate_syntax,
    }

    if checks:
        validators = {k: v for k, v in all_validators.items() if k in checks}
    else:
        validators = all_validators

    results = []
    for name, fn in validators.items():
        try:
            results.append(fn())
        except Exception as e:
            r = ValidationResult(name)
            r.error(f"Validator crashed: {e}")
            results.append(r)

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run project validators")
    parser.add_argument("--check", help="Run specific check (brands, deps, schema, workflows, syntax)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    checks = [args.check] if args.check else None
    results = run_all(auto_fix=args.fix, checks=checks)

    if args.json:
        output = []
        for r in results:
            output.append({
                "name": r.name,
                "ok": r.ok,
                "errors": r.errors,
                "warnings": r.warnings,
                "fixed": r.fixed,
            })
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("Social Media Empire — Validation Report")
        print("=" * 60)
        for r in results:
            print(f"\n{r.summary()}")

        errors = sum(len(r.errors) for r in results)
        warnings = sum(len(r.warnings) for r in results)
        passed = sum(1 for r in results if r.ok)

        print(f"\n{'=' * 60}")
        print(f"Results: {passed}/{len(results)} passed, {errors} errors, {warnings} warnings")

        if errors > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
