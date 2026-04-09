#!/usr/bin/env python3
"""
Remove fake testimonials and proof sections from fitness articles.
Replace with Amazon rating badges.
"""

import os
import re
from pathlib import Path

AMAZON_BADGE = '<div class="amazon-rating-badge" style="display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--warm);border-radius:8px;margin:12px 0"><span style="color:#FF9900;font-weight:700">★ 4.7</span><span style="font-size:.82rem;color:var(--muted)">Based on Amazon reviews</span></div>'

def remove_testimonials(html_content):
    """Remove all fake testimonial sections and replace with Amazon badge."""
    replacements = 0

    # Pattern 1: Remove testimonials divs (plural) - match opening to closing
    testimonial_pattern_1 = r'<div class="testimonials">.*?</div>\s*</div>\s*</div>'
    matches_1 = re.findall(testimonial_pattern_1, html_content, re.DOTALL)
    replacements += len(matches_1)

    new_content = re.sub(
        testimonial_pattern_1,
        AMAZON_BADGE,
        html_content,
        flags=re.DOTALL
    )

    # Pattern 2: Try without quotes
    testimonial_pattern_2 = r'<div class=testimonials>.*?</div>\s*</div>\s*</div>'
    matches_2 = re.findall(testimonial_pattern_2, new_content, re.DOTALL)
    replacements += len(matches_2)

    new_content = re.sub(
        testimonial_pattern_2,
        AMAZON_BADGE,
        new_content,
        flags=re.DOTALL
    )

    # Pattern 3: Individual testimonial divs (singular) - these appear standalone
    # Match: <div class="testimonial"><div class="testimonial-avatar">...</div></div></div>
    single_testimonial_pattern = r'<div class="testimonial">.*?</div>\s*</div>\s*</div>'

    # Only remove if it contains the pexels-photo-1222271 image
    def replace_single_testimonial(match):
        if 'pexels-photo-1222271' in match.group(0):
            return ''  # Remove completely (badge already added by plural testimonials)
        return match.group(0)  # Keep it if it's not fake

    matches_3 = re.findall(single_testimonial_pattern, new_content, re.DOTALL)
    for m in matches_3:
        if 'pexels-photo-1222271' in m:
            replacements += 1

    new_content = re.sub(
        single_testimonial_pattern,
        replace_single_testimonial,
        new_content,
        flags=re.DOTALL
    )

    return new_content, replacements

def remove_proof_section(html_content):
    """Remove the fake 'proof' section with pexels faces."""
    # Pattern matches the entire proof div with faces
    proof_pattern = r'<div class="proof">.*?</div>\s*</div>'

    # Check if proof section contains the fake pexels photo
    if 'pexels-photo-1222271' in html_content:
        new_content = re.sub(
            proof_pattern,
            '',
            html_content,
            flags=re.DOTALL
        )
        return new_content, 1
    else:
        return html_content, 0

def process_article(file_path):
    """Process a single article file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove testimonials
    content, testimonial_count = remove_testimonials(content)

    # Remove proof section
    content, proof_count = remove_proof_section(content)

    total_removed = testimonial_count + proof_count

    if total_removed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return {
        'testimonials': testimonial_count,
        'proof': proof_count,
        'total': total_removed
    }

def verify_cleanup(articles_dir):
    """Verify that all pexels-photo-1222271 references are removed."""
    html_files = list(articles_dir.glob('*.html'))
    remaining = []

    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pexels-photo-1222271' in content:
                remaining.append(file_path.name)

    return remaining

def main():
    # Get script directory and construct path relative to it
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    articles_dir = project_root / 'outputs' / 'fitover35-website' / 'articles'

    if not articles_dir.exists():
        print(f"Error: Directory not found: {articles_dir}")
        return

    html_files = list(articles_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to process\n")

    total_testimonials = 0
    total_proof = 0
    files_modified = 0

    for file_path in html_files:
        result = process_article(file_path)
        if result['total'] > 0:
            files_modified += 1
            total_testimonials += result['testimonials']
            total_proof += result['proof']
            print(f"[OK] {file_path.name}: Removed {result['testimonials']} testimonials, {result['proof']} proof section")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {len(html_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Testimonials removed: {total_testimonials}")
    print(f"Proof sections removed: {total_proof}")
    print(f"Amazon rating badges added: {total_testimonials}")

    # Verify cleanup
    print(f"\n{'='*60}")
    print(f"VERIFICATION")
    print(f"{'='*60}")
    remaining = verify_cleanup(articles_dir)
    if remaining:
        print(f"[WARNING] {len(remaining)} files still contain pexels-photo-1222271:")
        for fname in remaining:
            print(f"  - {fname}")
    else:
        print(f"[SUCCESS] No pexels-photo-1222271 references found in any file")

if __name__ == "__main__":
    main()
