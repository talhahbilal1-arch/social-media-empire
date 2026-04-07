# Phase 7: Menopause Article Cleanup — April 7, 2026

## Tasks

### TASK 1: Replace Amazon Search URLs with Direct Product Links
- [ ] Extract all unique Amazon search queries from 96 menopause articles
- [ ] Create `scripts/fix_menopause_links.py` with comprehensive ASIN dictionary
- [ ] Run script and replace all 395 search URLs with direct product links
- [ ] Verify all affiliate tags are `dailydealdarl-20`

### TASK 2: Remove Fake Testimonials
- [ ] Create `scripts/fix_menopause_testimonials.py`
- [ ] Remove 255 `<div class=testimonials>...</div>` sections
- [ ] Replace with Amazon rating badge HTML
- [ ] Verify 0 testimonials remain after cleanup

## Review
(To be filled after completion)
