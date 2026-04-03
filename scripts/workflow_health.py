#!/usr/bin/env python3
"""
Workflow Health Report Generator

Reads .github/workflows/ directory, categorizes active vs archived workflows,
extracts cron schedules, and generates a markdown health report.

Output: monitoring/workflow-health.md
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve repo root (works from any working directory)
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
ARCHIVE_DIR = WORKFLOWS_DIR / "archive"
OUTPUT_DIR = REPO_ROOT / "monitoring"
OUTPUT_FILE = OUTPUT_DIR / "workflow-health.md"

# Cron field descriptions (day-of-week)
DOW_MAP = {
    "0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed",
    "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun",
}


def parse_workflow(filepath: Path) -> dict:
    """Parse a workflow YAML file for name, cron schedules, and trigger types."""
    text = filepath.read_text(encoding="utf-8", errors="replace")

    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    name = name_match.group(1).strip().strip("'\"") if name_match else filepath.stem

    # Extract cron schedules (both active and commented-out)
    active_crons = re.findall(r"^\s+-\s*cron:\s*['\"](.+?)['\"]", text, re.MULTILINE)
    commented_crons = re.findall(r"#\s*-\s*cron:\s*['\"](.+?)['\"]", text, re.MULTILINE)

    # Determine trigger types
    triggers = []
    if active_crons:
        triggers.append("schedule")
    if "workflow_dispatch" in text:
        triggers.append("manual")
    if re.search(r"on:\s*\n\s+push:", text) or "on:\n  push:" in text:
        triggers.append("push")
    if "workflow_call" in text:
        triggers.append("callable")

    # Check if schedule is disabled (commented out)
    schedule_disabled = len(commented_crons) > 0 and len(active_crons) == 0

    return {
        "file": filepath.name,
        "name": name,
        "crons": active_crons,
        "commented_crons": commented_crons,
        "triggers": triggers,
        "schedule_disabled": schedule_disabled,
    }


def describe_cron(cron: str) -> str:
    """Convert a cron expression to a human-readable description."""
    parts = cron.split()
    if len(parts) != 5:
        return cron

    minute, hour, dom, month, dow = parts

    # Handle */N patterns first (e.g., */2 = every 2 hours)
    if "/" in hour:
        _, interval = hour.split("/")
        return f"Every {interval}h at :{minute}"

    # Build time string
    time_str = f"{int(hour):02d}:{int(minute):02d} UTC"

    # Day of week
    if dow == "*":
        if dom == "*":
            day_str = "Daily"
        else:
            day_str = f"Day {dom}"
    else:
        # Handle ranges like 1-5, lists like 1,3,5
        days = []
        for part in dow.split(","):
            if "-" in part:
                start, end = part.split("-")
                for d in range(int(start), int(end) + 1):
                    days.append(DOW_MAP.get(str(d), str(d)))
            else:
                days.append(DOW_MAP.get(part, part))
        day_str = "/".join(days)

    return f"{day_str} {time_str}"


def generate_report(active_workflows: list, archived_workflows: list) -> str:
    """Generate the markdown health report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Workflow Health Report",
        f"",
        f"Generated: {now}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Active workflows | {len(active_workflows)} |",
        f"| Archived workflows | {len(archived_workflows)} |",
        f"| Total | {len(active_workflows) + len(archived_workflows)} |",
        f"",
    ]

    # Categorize active workflows
    scheduled = [w for w in active_workflows if w["crons"]]
    event_driven = [w for w in active_workflows if not w["crons"] and not w["schedule_disabled"]]
    disabled_schedule = [w for w in active_workflows if w["schedule_disabled"]]

    lines.append(f"| Scheduled (cron) | {len(scheduled)} |")
    lines.append(f"| Event-driven (push/manual) | {len(event_driven)} |")
    if disabled_schedule:
        lines.append(f"| Schedule disabled | {len(disabled_schedule)} |")
    lines.append("")

    # Scheduled workflows with cron details
    lines.append("## Scheduled Workflows")
    lines.append("")
    lines.append("| Workflow | File | Schedule |")
    lines.append("|----------|------|----------|")

    for w in sorted(scheduled, key=lambda x: x["name"]):
        schedules = ", ".join(describe_cron(c) for c in w["crons"])
        lines.append(f"| {w['name']} | `{w['file']}` | {schedules} |")

    lines.append("")

    # Event-driven workflows
    if event_driven:
        lines.append("## Event-Driven Workflows")
        lines.append("")
        lines.append("| Workflow | File | Triggers |")
        lines.append("|----------|------|----------|")
        for w in sorted(event_driven, key=lambda x: x["name"]):
            triggers = ", ".join(w["triggers"])
            lines.append(f"| {w['name']} | `{w['file']}` | {triggers} |")
        lines.append("")

    # Cron schedule summary (daily timeline)
    lines.append("## Daily Schedule (UTC)")
    lines.append("")
    lines.append("```")

    # Collect all cron times and sort
    time_slots = []
    for w in scheduled:
        for cron in w["crons"]:
            parts = cron.split()
            if len(parts) == 5:
                minute, hour = parts[0], parts[1]
                if "/" not in hour and "*" not in hour:
                    time_slots.append((int(hour), int(minute), w["name"], cron))

    time_slots.sort(key=lambda x: (x[0], x[1]))

    for hour, minute, name, cron in time_slots:
        parts = cron.split()
        dow = parts[4] if len(parts) == 5 else "*"
        day_note = ""
        if dow != "*":
            day_parts = []
            for part in dow.split(","):
                if "-" in part:
                    start, end = part.split("-")
                    for d in range(int(start), int(end) + 1):
                        day_parts.append(DOW_MAP.get(str(d), str(d)))
                else:
                    day_parts.append(DOW_MAP.get(part, part))
            day_note = f" ({'/'.join(day_parts)} only)"
        lines.append(f"  {hour:02d}:{minute:02d}  {name}{day_note}")

    # Also add interval-based
    for w in scheduled:
        for cron in w["crons"]:
            parts = cron.split()
            if len(parts) == 5 and "/" in parts[1]:
                _, interval = parts[1].split("/")
                lines.append(f"  Every {interval}h  {w['name']}")

    lines.append("```")
    lines.append("")

    # Archived workflows
    lines.append("## Archived Workflows")
    lines.append("")
    for w in sorted(archived_workflows, key=lambda x: x["name"]):
        lines.append(f"- `{w['file']}` — {w['name']}")
    lines.append("")

    return "\n".join(lines)


def main():
    if not WORKFLOWS_DIR.exists():
        print(f"ERROR: {WORKFLOWS_DIR} not found")
        sys.exit(1)

    # Parse active workflows (exclude archive dir)
    active_workflows = []
    for f in sorted(WORKFLOWS_DIR.glob("*.yml")):
        active_workflows.append(parse_workflow(f))

    # Parse archived workflows
    archived_workflows = []
    if ARCHIVE_DIR.exists():
        for f in sorted(ARCHIVE_DIR.glob("*.yml")):
            archived_workflows.append(parse_workflow(f))

    # Generate report
    report = generate_report(active_workflows, archived_workflows)

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print(f"Health report written to {OUTPUT_FILE}")
    print(f"  Active:   {len(active_workflows)}")
    print(f"  Archived: {len(archived_workflows)}")
    print(f"  Total:    {len(active_workflows) + len(archived_workflows)}")


if __name__ == "__main__":
    main()
