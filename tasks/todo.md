# Article System v3 Overhaul — Todo

**Created:** March 18, 2026
**Scope:** Rewrite 3 files to produce Sleep Foundation / Wirecutter-style product pages

---

## Phase 1: Helpers + Image Functions (low risk)

- [ ] Add `get_pexels_portrait_photos()` to `image_selector.py`
- [ ] Add `_fetch_pexels_video()` to `pin_article_generator.py`
- [ ] Add `_fetch_pexels_batch()` to `pin_article_generator.py` (batch image fetcher, reuse for thumbnails/related)
- [ ] Verify: `python3 -m py_compile` both files

## Phase 2: JSON Prompt + Enrichment Pipeline (medium risk)

- [ ] Rewrite `generate_article_for_pin()` — JSON prompt with structured output
- [ ] Add `_try_parse_json()` helper — strips code fences, handles Gemini quirks
- [ ] Rewrite `article_to_html()` — detect JSON vs markdown, route accordingly
  - JSON path: parse → resolve Amazon URLs → fetch Pexels images/video/portraits → pass structured data to template
  - Markdown fallback: existing v2 path (product cards, FAQ schema, etc.) stays intact
- [ ] Keep Pexels API calls ≤ 10 per article:
  - 1 hero image + 1 hero video = 2
  - Per product (×3 max): 1 image query (hero + thumbnails from same result) + 1 benefit image = 6
  - 1 portrait batch + 1 related products batch = 2
  - Total: 10
- [ ] Verify: `python3 -m py_compile pin_article_generator.py`

## Phase 3: v3 HTML Template (high complexity)

- [ ] Update `TEMPLATE_CONFIG` menopause colors: accent=#3D6B4F, bg=#FDFBF7
- [ ] Update `LEAD_MAGNET_OVERRIDES` with new copy
- [ ] Add routing in `render_article_page()` — check for `_article_data` in pin_data
- [ ] Build `_render_v3_page()` with 22 section helpers:
  1. Sticky nav (brand + EXPERT TESTED badge + share)
  2. Breadcrumbs
  3. Social proof banner
  4. Hero (video/image + dark overlay + metadata)
  5. Before/After cards
  6. Quick verdict box
  7. Urgency banner
  8. Quick picks (clickable product cards)
  9. Trust bar pills
  10. As seen in logos
  11. Email signup (real ConvertKit form_id)
  12. Product sections ×3 (hero image, thumbnails, benefits, pros/cons, testimonials with photos, CTA + payment logos)
  13. Comparison table
  14. How we chose grid
  15. Price drop alert (secondary email capture)
  16. Etsy CTA (menopause only)
  17. FAQ with JSON-LD schema
  18. Related products grid
  19. Share bar (Pinterest, Facebook, WhatsApp)
  20. Expert bio
  21. Final CTA box + payment logos
  22. Footer (disclosure + copyright)
- [ ] All sections use brand colors/fonts from TEMPLATE_CONFIG
- [ ] Verify: `python3 -m py_compile article_templates.py`

## Phase 4: Validation + Ship

- [ ] `python3 -m py_compile video_automation/pin_article_generator.py`
- [ ] `python3 -m py_compile video_automation/article_templates.py`
- [ ] `python3 -m py_compile video_automation/image_selector.py`
- [ ] `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/content-engine.yml'))"`
- [ ] Quick test: JSON parsing + product card regex
- [ ] Commit and push to main

---

## Key Constraints

- Function signatures for `generate_article_for_pin()`, `article_to_html()`, `save_and_register_article()` MUST NOT change
- `BRAND_SITE_CONFIG` structure MUST NOT change
- `AMAZON_AFFILIATE_LINKS` data MUST NOT change
- Markdown fallback path MUST work (existing v2 articles still render)
- Pexels API calls ≤ 10 per article (avoid rate limiting at 15 articles/day)
- ConvertKit forms use real form_ids from BRAND_SITE_CONFIG

## Estimated Size

- `pin_article_generator.py`: ~850 lines (from 739)
- `article_templates.py`: ~1300 lines (from 817 — adding ~500 lines of v3 template)
- `image_selector.py`: ~240 lines (from 208 — adding 1 function)
