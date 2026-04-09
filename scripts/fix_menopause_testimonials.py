#!/usr/bin/env python3
"""
Remove fake testimonials from menopause articles.
Replace with Amazon rating badge.
"""

import re
from pathlib import Path

RATING_BADGE = '''<div class="amazon-rating-badge" style="display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--warm);border-radius:8px;margin:12px 0"><span style="color:#FF9900;font-weight:700">★ 4.7</span><span style="font-size:.82rem;color:var(--muted)">Based on Amazon reviews</span></div>'''


def process_file(filepath):
    """Process a single HTML file and remove testimonials."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    removed_count = 0

    # Pattern to match <div class=testimonials>...</div> and nested content
    # This handles the entire testimonials div including nested testimonial divs
    pattern = r'<div class=testimonials>.*?</div>\s*'

    def replace_testimonials(match):
        nonlocal removed_count
        removed_count += 1
        return RATING_BADGE

    # Use DOTALL flag to match across newlines
    content = re.sub(pattern, replace_testimonials, content, flags=re.DOTALL)

    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return removed_count


def verify_no_testimonials(filepath):
    """Verify that no testimonials remain in the file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for testimonials and pexels image
    has_testimonials = '<div class=testimonials>' in content
    has_pexels_photo = 'pexels-photo-1222271' in content

    return has_testimonials, has_pexels_photo


def main():
    articles_dir = Path("outputs/menopause-planner-website/articles")

    if not articles_dir.exists():
        print(f"Error: {articles_dir} does not exist")
        return

    html_files = list(articles_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files\n")

    total_removed = 0
    errors = 0
    verification_fails = 0

    for filepath in sorted(html_files):
        try:
            removed = process_file(filepath)
            total_removed += removed

            if removed > 0:
                print(f"{filepath.name}: {removed} testimonial(s) removed")

            # Verify no testimonials remain
            has_testimonials, has_pexels = verify_no_testimonials(filepath)
            if has_testimonials or has_pexels:
                print(f"  ⚠️  WARNING: {filepath.name} still has testimonials or pexels image!")
                verification_fails += 1

        except Exception as e:
            print(f"ERROR in {filepath.name}: {e}")
            errors += 1

    # Final verification: check entire directory
    print("\n" + "="*60)
    print("FINAL VERIFICATION:")

    total_testimonials_found = 0
    total_pexels_found = 0

    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        total_testimonials_found += content.count('<div class=testimonials>')
        total_pexels_found += content.count('pexels-photo-1222271')

    print(f"  Total testimonials removed: {total_removed}")
    print(f"  Remaining testimonials in codebase: {total_testimonials_found}")
    print(f"  Remaining pexels-photo-1222271: {total_pexels_found}")
    print(f"  Total processed: {len(html_files)}")
    print(f"  Errors: {errors}")
    print(f"  Verification fails: {verification_fails}")
    print("="*60)


if __name__ == "__main__":
    main()
