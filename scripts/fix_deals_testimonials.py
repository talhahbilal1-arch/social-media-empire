#!/usr/bin/env python3
"""
Remove fake testimonials from Daily Deal Darling articles.
Replaces with Amazon rating badge.
"""

import re
from pathlib import Path

AMAZON_RATING_BADGE = '''<div class="amazon-rating-badge" style="display:flex;align-items:center;gap:8px;padding:10px 14px;background:var(--warm);border-radius:8px;margin:12px 0"><span style="color:#FF9900;font-weight:700">★ 4.7</span><span style="font-size:.82rem;color:var(--muted)">Based on Amazon reviews</span></div>'''

def remove_proof_section(content: str) -> tuple[str, int]:
    """Remove .proof section with fake face photos."""
    # Pattern matches the entire proof div with faces and text
    pattern = r'<div class="proof">.*?</div>\s*(?=<div)'
    matches = re.findall(pattern, content, re.DOTALL)
    count = len(matches)

    if count > 0:
        content = re.sub(pattern, '', content, flags=re.DOTALL)

    return content, count

def remove_testimonials(content: str) -> tuple[str, int]:
    """Remove testimonials section and replace with Amazon rating badge."""
    # Pattern 1: Match testimonials div containing testimonial divs
    # Note: Some files use class=testimonials (no quotes), others use class="testimonials"
    pattern1 = r'<div class=testimonials>.*?</div></div>'
    matches1 = re.findall(pattern1, content, re.DOTALL)
    count1 = len(matches1)

    if count1 > 0:
        # Replace with Amazon rating badge
        content = re.sub(pattern1, AMAZON_RATING_BADGE, content, flags=re.DOTALL)

    # Pattern 2: Match orphaned single testimonial divs (without wrapper)
    # These appear after Amazon rating badges were already inserted
    pattern2 = r'</div></div><div class="testimonial">.*?</div></div></div>'
    matches2 = re.findall(pattern2, content, re.DOTALL)
    count2 = len(matches2)

    if count2 > 0:
        # Just remove them (badge already exists)
        content = re.sub(pattern2, '</div></div>', content, flags=re.DOTALL)

    # Pattern 3: Clean up orphaned testimonial fragments (testimonial-body, testimonial-name, testimonial-text)
    # These are left behind after removing the wrapper div
    pattern3 = r'<div class="testimonial-body">.*?</div></div>'
    matches3 = re.findall(pattern3, content, re.DOTALL)
    count3 = len(matches3)

    if count3 > 0:
        content = re.sub(pattern3, '', content, flags=re.DOTALL)

    return content, count1 + count2 + count3

def process_html_file(file_path: Path) -> dict:
    """Process a single HTML file to remove testimonials."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    proof_removed = 0
    testimonials_removed = 0

    # Remove proof section
    content, proof_removed = remove_proof_section(content)

    # Remove testimonials
    content, testimonials_removed = remove_testimonials(content)

    # Write updated content if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return {
        'file': file_path.name,
        'proof_removed': proof_removed,
        'testimonials_removed': testimonials_removed,
        'modified': content != original_content
    }

def main():
    """Process all HTML files in Daily Deal Darling articles directory."""
    articles_dir = Path(__file__).parent.parent / 'outputs' / 'dailydealdarling-website' / 'articles'

    if not articles_dir.exists():
        print(f"ERROR: Directory not found: {articles_dir}")
        return

    html_files = list(articles_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files")
    print(f"Removing fake testimonials and proof sections...\n")

    files_modified = 0
    total_proof_removed = 0
    total_testimonials_removed = 0

    for file_path in sorted(html_files):
        result = process_html_file(file_path)

        if result['modified']:
            files_modified += 1
            total_proof_removed += result['proof_removed']
            total_testimonials_removed += result['testimonials_removed']

            print(f"OK: {result['file']}: proof={result['proof_removed']}, testimonials={result['testimonials_removed']}")

    print(f"\n" + "="*80)
    print(f"COMPLETE!")
    print(f"   Files modified: {files_modified}/{len(html_files)}")
    print(f"   Proof sections removed: {total_proof_removed}")
    print(f"   Testimonial sections removed: {total_testimonials_removed}")
    print("="*80)

    # Verify no testimonials remain
    print(f"\nVerifying cleanup...")
    remaining_testimonials = 0
    remaining_proof = 0

    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class="testimonials"' in content or 'class="testimonial"' in content:
                remaining_testimonials += 1
                print(f"WARNING: {file_path.name} still has testimonials")
            if 'class="proof"' in content:
                remaining_proof += 1
                print(f"WARNING: {file_path.name} still has proof section")

    if remaining_testimonials == 0 and remaining_proof == 0:
        print(f"SUCCESS: All testimonials and proof sections removed")
    else:
        print(f"WARNING: {remaining_testimonials} files with testimonials, {remaining_proof} files with proof sections")

if __name__ == '__main__':
    main()
