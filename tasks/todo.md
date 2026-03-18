# Article System v3 Overhaul — Todo

**Created:** March 18, 2026
**Status:** COMPLETE ✅

---

## Phase 1: Helpers + Image Functions ✅

- [x] Add `get_pexels_portrait_photos()` to `image_selector.py`
- [x] Add `_fetch_pexels_video()` to `pin_article_generator.py`
- [x] Add `_fetch_pexels_batch()` to `pin_article_generator.py`
- [x] Verify: `python3 -m py_compile` both files

## Phase 2: JSON Prompt + Enrichment Pipeline ✅

- [x] Rewrite `generate_article_for_pin()` — JSON prompt with structured output
- [x] Add `_try_parse_json()` helper — strips code fences, handles Gemini quirks
- [x] Rewrite `article_to_html()` — detect JSON vs markdown, route accordingly
- [x] JSON path: parse → resolve Amazon URLs → fetch Pexels images/video/portraits → pass structured data
- [x] Markdown fallback: existing v2 path preserved intact
- [x] Pexels API calls ≤ 10 per article
- [x] Verify: `python3 -m py_compile pin_article_generator.py`

## Phase 3: v3 HTML Template ✅

- [x] Update `TEMPLATE_CONFIG` menopause colors: accent=#3D6B4F, bg=#FDFBF7
- [x] Update `LEAD_MAGNET_OVERRIDES` with new copy
- [x] Add routing in `render_article_page()` — check for `_article_data` in pin_data
- [x] Build `_render_v3_page()` with 22 section helpers
- [x] All sections use brand colors/fonts from TEMPLATE_CONFIG
- [x] Verify: `python3 -m py_compile article_templates.py`

## Phase 4: Validation + Ship ✅

- [x] `python3 -m py_compile video_automation/pin_article_generator.py` ✅
- [x] `python3 -m py_compile video_automation/article_templates.py` ✅
- [x] `python3 -m py_compile video_automation/image_selector.py` ✅
- [x] `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/content-engine.yml'))"` ✅
- [x] Quick test: JSON parsing + v3 template rendering ✅
- [x] Commit and push to main ✅
- [x] Saved to project memory for persistence ✅

---

## Review

### Changes made:
1. **`pin_article_generator.py`** (+117 lines): JSON-first Gemini prompt with `response_mime_type: "application/json"`, `_fetch_pexels_video()`, `_fetch_pexels_batch()`, `_try_parse_json()` with code fence stripping, `_build_v3_article()` enrichment pipeline (resolves Amazon URLs, fetches images/video/portraits), `_build_v2_article()` markdown fallback. All existing code preserved.

2. **`article_templates.py`** (+505 lines): `_render_v3_page()` with 22-section template (sticky nav, breadcrumbs, social proof, hero video/image, before/after, quick verdict, urgency, quick picks, trust bar, as-seen-in, email signup, product sections with testimonials/pros-cons/CTA/payment logos, comparison table, methodology grid, price alert, Etsy CTA, FAQ with JSON-LD, related products, share bar, expert bio, final CTA, footer, mobile sticky). Updated fonts (Fraunces), menopause colors (#3D6B4F), lead magnets. All v2 code preserved as fallback.

3. **`image_selector.py`** (+38 lines): `get_pexels_portrait_photos()` for brand-specific testimonial headshots.

### System preserved for all future articles:
- v3 template architecture saved to `memory/article_system_v3.md`
- MEMORY.md updated with v3 system summary
- All future articles automatically route to v3 when JSON output succeeds
- v2 fallback ensures zero pipeline disruption if JSON parsing fails
