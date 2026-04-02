#!/usr/bin/env python3
"""Brand-aware affiliate tag replacement script.

Replaces broken Amazon Associate tags with correct ones based on
which brand directory a file belongs to.

Correct tags:
  FitOver35:        fitover3509-20
  DailyDealDarling: dailydealdarl-20
  Menopause:        dailydealdarl-20
"""

import os
import sys

# Directory-to-brand mapping (order matters — more specific paths first)
DIR_BRAND_MAP = [
    # FitOver35
    ("outputs/fitover35-website/", "fitover35"),
    ("outputs/infrastructure/fitover35/", "fitover35"),
    ("outputs/content/fitover35/", "fitover35"),
    ("outputs/fit-over-35-pinterest/", "fitover35"),
    ("outputs/fo35_fixes/", "fitover35"),
    ("sites/fitover35/", "fitover35"),
    ("_backup/articles/", "fitover35"),
    # DailyDealDarling
    ("outputs/dailydealdarling-website/", "dailydealdarling"),
    ("outputs/infrastructure/dailydealdarling/", "dailydealdarling"),
    ("outputs/content/dailydealdarling/", "dailydealdarling"),
    ("outputs/daily-deal-darling/", "dailydealdarling"),
    ("dailydealdarling_website/", "dailydealdarling"),
    # Menopause (uses same tag as DDD)
    ("outputs/menopause-planner-website/", "menopause"),
    ("outputs/menopause-planner-co/", "menopause"),
    ("outputs/menopause_planner/", "menopause"),
    ("menopause-planner-site/", "menopause"),
    ("products/menopause_planner/", "menopause"),
    # Anti-Gravity (lifestyle, uses DDD tag)
    ("anti_gravity/", "dailydealdarling"),
    # AI tools hub (general, uses DDD tag)
    ("ai-tools-hub/", "dailydealdarling"),
    # Prompt packs (general, uses DDD tag)
    ("prompt-packs/", "dailydealdarling"),
    # Landing pages
    ("landing_pages/", "dailydealdarling"),
]

BRAND_TAG_MAP = {
    "fitover35": "fitover3509-20",
    "dailydealdarling": "dailydealdarl-20",
    "menopause": "dailydealdarl-20",
}

BROKEN_TAGS = ["dailydealdarling1-20", "fitover35-20"]

# File extensions to process
EXTENSIONS = {".html", ".py", ".js", ".json", ".yml", ".yaml", ".md", ".txt", ".toml"}


def get_brand_for_path(rel_path):
    """Determine brand from file path. Returns None if unknown."""
    for dir_prefix, brand in DIR_BRAND_MAP:
        if rel_path.startswith(dir_prefix):
            return brand
    return None


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)

    total_replacements = 0
    files_changed = 0
    skipped_files = []
    log_entries = []

    for root, dirs, files in os.walk("."):
        # Skip .git and node_modules
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXTENSIONS:
                continue

            fpath = os.path.join(root, fname)
            rel_path = fpath[2:]  # strip "./"

            # Skip pipeline files (already fixed manually)
            skip_dirs = [
                "video_automation/", "automation/", "scripts/", "config/",
                "email_marketing/", ".github/", "monetization/", "analytics/",
                "tiktok_automation/", "core/", "agents/", "overnight-work/",
                "src/", "database/", "monitoring/", "archive/",
            ]
            if any(rel_path.startswith(d) for d in skip_dirs):
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            # Check if file has any broken tags
            if not any(tag in content for tag in BROKEN_TAGS):
                continue

            # Determine brand
            brand = get_brand_for_path(rel_path)
            if brand is None:
                skipped_files.append(rel_path)
                continue

            correct_tag = BRAND_TAG_MAP[brand]
            file_replacements = 0

            new_content = content
            for broken_tag in BROKEN_TAGS:
                if broken_tag in new_content:
                    count = new_content.count(broken_tag)
                    # Safety: don't replace fitover35-20 with dailydealdarl-20 in fitness files
                    # and don't replace dailydealdarling1-20 with fitover3509-20 in deals files
                    new_content = new_content.replace(broken_tag, correct_tag)
                    file_replacements += count
                    log_entries.append(
                        f"  {rel_path}: {broken_tag} -> {correct_tag} ({count}x)"
                    )

            if file_replacements > 0 and new_content != content:
                # Safety check: make sure we didn't corrupt fitover3509-20
                if "fitover350fitover3509-20" in new_content or "fitover3509-2009-20" in new_content:
                    print(f"  CORRUPTION DETECTED in {rel_path} — skipping!")
                    skipped_files.append(f"{rel_path} (corruption risk)")
                    continue

                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                files_changed += 1
                total_replacements += file_replacements

    # Print results
    print("=" * 60)
    print("AFFILIATE TAG FIX — RESULTS")
    print("=" * 60)
    print(f"\nFiles changed: {files_changed}")
    print(f"Total replacements: {total_replacements}")
    print(f"\nReplacement log:")
    for entry in log_entries:
        print(entry)

    if skipped_files:
        print(f"\nSKIPPED (unknown brand — needs manual review):")
        for f in skipped_files:
            print(f"  {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
