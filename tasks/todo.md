# Article Template Rebuild — 3 Clean Brand Designs (April 17, 2026)

## Plan

### 1. Rewrite Gemini prompts in `generate_article_for_pin()` (pin_article_generator.py)
- [ ] Replace single Wirecutter-style JSON prompt with 3 brand-specific prompts
- [ ] **Deals**: First-person product review, PAS intro, 2-4 products with honest reviews, conversational tone. JSON: title, meta_description, intro_paragraphs, products[], verdict_text, faq[]
- [ ] **Fitness**: Educational article, actionable advice, gear recommendations at end only. JSON: title, meta_description, intro_hook, sections[], gear_recommendations[]
- [ ] **Menopause**: Wellness-focused, warm tone, free resource CTA, Etsy product. JSON: title, meta_description, intro_hook, sections[], free_resource_cta, etsy_product_section
- [ ] Keep markdown fallback prompts brand-specific too

### 2. Rewrite HTML builders (template_renderer.py)
- [ ] Replace `render_article_from_template()` with 3 brand-specific builders
- [ ] **Deals**: Clean blog, Lora + Inter fonts, #FAFAFA bg, #C47D8E accent, white product cards, winner card with "The one I bought", no before/after, no comparison tables, no trust badges
- [ ] **Fitness**: Dark theme #111 bg, #E8C547 yellow accent, Space Grotesk + Inter, 90% education with "The fix" tip boxes, compact "What I use" product section at bottom only
- [ ] **Menopause**: Warm #FAF7F0 bg, #6B705C sage, DM Serif Display + Outfit, value-first wellness, free tracker download CTA, Etsy planner at end
- [ ] Remove: before/after cards, comparison tables, trust badges, payment icons, fake social proof, sticky bars, methodology sections

### 3. Add Amazon link validation (pin_article_generator.py)
- [ ] Add `validate_amazon_links(html_content, brand_key)` function
- [ ] HTTP HEAD request to each Amazon URL (browser user-agent, 10s timeout)
- [ ] Replace 404s/search-redirects with verified ASIN from AMAZON_AFFILIATE_LINKS
- [ ] Reject `amazon.com/s?k=` search URLs — replace with `/dp/ASIN` or remove
- [ ] Verify correct affiliate tag per brand
- [ ] Enhance `_sanitize_affiliate_links()` to also reject search URLs

### 4. Fix content-engine.yml Phase 2
- [ ] Retry article generation once on failure before giving up
- [ ] Fall back to `/articles/` index page (not homepage) when article fails
- [ ] Log warning to Supabase errors table on fallback
- [ ] Ensure every pin with a topic gets an article URL (not homepage)

### 5. Test & Commit
- [ ] `python3 -m py_compile video_automation/pin_article_generator.py`
- [ ] `python3 -m py_compile video_automation/template_renderer.py`
- [ ] Validate content-engine.yml YAML
- [ ] Commit 1: `feat(articles): rebuild templates for 3 brands — clean designs, value-first format`
- [ ] Commit 2: `feat(articles): add Amazon link validation — reject search URLs, verify ASINs`
- [ ] Commit 3: `fix(content-engine): ensure every pin gets a real article, no homepage fallbacks`
- [ ] Push to main

## Review
_(to be filled after execution)_
