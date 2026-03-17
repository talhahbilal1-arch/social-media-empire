# Pinterest Automation System - Prioritized Action Plan
**Created:** February 12, 2026

---

## Immediate (Do Right Now)

- [x] **Pull remote changes:** `git pull origin main` - Synced local repo with remote
- [x] **Verify posts_log table** - Confirmed posts_log had 0 rows. Fixed by adding HTTP POST module to all 3 active Pinterest scenarios via Make.com API:
  - The Menopause Planner (ID: 3825384) - Added module 9 → POST to posts_log
  - Fit Over 35 (ID: 3982828) - Added module 11 → POST to posts_log
  - Agent 2: Pinterest Value Pins/DDD (ID: 3798284) - Added module 9 → POST to posts_log
- [x] **Fix obvious Amazon affiliate tag typos** - Cleaned up 2 typo variants:
  - `dailydealdar-20` (3 occurrences) → fixed to `dailydealdarl-20`
  - `googhydr-20` (1 occurrence, wrong network) → fixed to `dailydealdarl-20`
  - All in `dailydealdarling_website/articles/kitchen-tools-every-home-cook-needs.html`
- [x] **Standardize Amazon affiliate tags** - Replaced `dailydealdarling1-20` → `dailydealdarl-20` across 27 files (131 occurrences). All active code now uses the registered tag.

---

## DailyDealDarling.com — 5-Hack Visual Upgrade Plan (March 11, 2026)

### Status: COMPLETE

### Hack 1 — Typography & White Space
- [x] Verify Playfair Display + Source Sans 3 loading correctly (weights 400/600/700 + italic, with preconnect hints)
- [x] Section padding already 80px (`--space-2xl: 5rem`) — sufficient for editorial feel
- [x] Heading hierarchy verified: h1 (clamp 2.25-3.75rem) → h2 (1.75-2.75rem) → h3 (1.2-1.6rem) → h4 (1.05-1.2rem)
- [x] Body line-height 1.7 ✓, paragraph 1.75 ✓, heading line-height 1.15 ✓, hero h1 1.08 ✓

### Hack 2 — Color & Contrast
- [x] Hero description (#6B6B6B on #F7F3ED): 5.14:1 — passes AA
- [x] Editorial labels: changed from brass (#B8956A, 2.75:1) to brass-text (#7D6544, ~4.97:1) — passes AA
- [x] Hero badge: changed from brass-dark (#9A7B55, 3.92:1) to brass-text (#7D6544) — passes AA
- [x] Section numbers: changed from brass-dark to brass-text — passes AA
- [x] Product categories: changed from brass-dark to brass-text — passes AA on white
- [x] Announcement CTA: changed from forest-on-brass (3.80:1) to forest-on-cream (10.44:1) — passes AA
- [x] Newsletter button: changed from forest-on-brass to forest-on-cream — passes AA
- [x] Announcement bar text (cream on forest): 10.44:1 — passes AA
- [x] Newsletter text (rgba 0.65 on forest): 5.53:1 — passes AA
- [x] Rating count: changed from pewter (#999, 2.85:1) to slate (#6B6B6B, 5.14:1) — passes AA
- [x] Footer brand text: bumped rgba opacity from 0.45 to 0.55
- [x] Footer disclosure: bumped rgba opacity from 0.35 to 0.55
- [x] Footer copyright: bumped rgba opacity from 0.3 to 0.55
- [x] Deal badges: added explicit text colors (white on terracotta, ink on brass)

### Hack 3 — Micro-Interactions & Animations
- [x] Scroll-reveal IntersectionObserver verified (opacity 0→1, translateY 24px→0, 0.7s)
- [x] Card hover states: product (-6px + shadow-lg), article (-4px), category (scale 1.06)
- [x] Button hover/active states present on all .btn variants
- [x] Announcement pulse animation verified (subtle 2s infinite)
- [x] Added `:focus-visible` global state with forest outline for keyboard accessibility
- [x] Added `@media (prefers-reduced-motion: reduce)` to disable animations for accessibility

### Hack 4 — Component Polish
- [x] Category cards: border-radius, shadows, overlay gradients, internal spacing verified
- [x] Product cards: moved product-image and prime-badge inline styles to CSS
- [x] Buttons: min-height 44px+ via padding, consistent hover transitions
- [x] Newsletter inputs: styled with focus states, brand-matching dark theme
- [x] Quiz CTA buttons: moved inline styles to CSS (.quiz-buttons class)
- [x] Removed ALL inline styles from index.html (11 occurrences)

### Hack 5 — Layout & Spacing
- [x] Max content width 1200px on .container, 1400px on header — consistent
- [x] Responsive tested at 375px and 1440px via Puppeteer screenshots
- [x] Section background classes (.section-cream, .section-parchment) replace inline styles
- [x] Footer social margin moved to CSS
- [x] Mobile-first breakpoints: 480px, 600px, 640px, 768px, 960px — all verified

### Review
Changes made:
1. **Contrast fixes** (css/styles.css): Added `--color-brass-text: #7D6544` for all decorative text on light backgrounds. Updated `.editorial-label`, `.hero-badge`, `.section-number`, `.product-category` to use it. Changed announcement CTA and newsletter button from brass bg to cream bg. Bumped footer text opacities (0.30-0.45 → 0.55). Changed `.rating-count` from pewter to slate.
2. **Focus-visible** (css/styles.css): Added global `:focus-visible` rule with forest outline
3. **Reduced motion** (css/styles.css): Added `@media (prefers-reduced-motion: reduce)` query
4. **Inline style cleanup** (index.html + css/styles.css): Removed all 11 remaining inline styles, moved to CSS classes (`.section-cream`, `.section-parchment`, `.deal-hot`, `.deal-value`, `.quiz-buttons`, `.newsletter .editorial-label`, `.newsletter p strong`, `.footer-social` margin)
5. **Product/badge fixes** (css/styles.css): Added `.product-image` bg/padding, `.prime-badge`, explicit text colors on deal badges

---

## Previous Work (preserved below)

### DDD Redesign - Initial Pass (March 11, 2026)
Design Direction: Moved from generic pink/red template to editorial magazine aesthetic ("The Edit") — warm, tactile, distinctive. See changes summary in previous entry.

### Remaining Tasks (from prior sessions)
- [ ] Connect FitOver35 Pinterest via Make.com
- [ ] Deploy subdomain sites
- [ ] Build Pinterest Analytics
- [ ] List remaining Etsy products

---

## Anthropic to Gemini Migration (March 17, 2026)

### Status: COMPLETE

Migrated ALL Python + JS files from Anthropic Claude SDK to Google Gemini SDK.
Pattern: `from google import genai` + `genai.Client(api_key=...)` + `client.models.generate_content(model="gemini-2.0-flash", ...)` + `response.text`
All files have 429 retry logic (3 attempts, 15s/30s/45s waits) and GEMINI_API_KEY fallback to ANTHROPIC_API_KEY.

**Python files migrated (12):**
- [x] 1. `automation/articles/fitover35_article_generator.py`
- [x] 2. `video_automation/seo_content_machine.py`
- [x] 3. `video_automation/daily_trend_scout.py`
- [x] 4. `video_automation/trend_discovery.py`
- [x] 5. `video_automation/video_content_generator.py`
- [x] 6. `video_automation/pin_article_generator.py` — ALREADY DONE (uses Gemini)
- [x] 7. `email_marketing/menopause_newsletter.py`
- [x] 8. `video_automation/revenue_intelligence.py`
- [x] 9. `video_automation/revenue_activation.py`
- [x] 10. `tiktok_automation/tiktok_pipeline.py`
- [x] 11. `video_automation/article_generator.py`
- [x] 12. `core/claude_client.py`
- [x] 13. `monitoring/health_checker.py` — removed check_anthropic(), uses existing check_gemini()

**JS files migrated (4):**
- [x] `ai-tools-hub/scripts/generate-content.js`
- [x] `ai-tools-hub/scripts/generate-newsletter.js`
- [x] `ai-tools-hub/scripts/discover-ai-trends.js`
- [x] `ai-tools-hub/scripts/generate-blog-posts.js`

**Workflow YAML files:** All 19 active workflows already used GEMINI_API_KEY. Only archived workflows reference ANTHROPIC_API_KEY.

**Other fixes applied:**
- Fixed `fitness-articles.yml` broken day-of-week filtering (removed broken `contains()` check)
- Verified `check-affiliate-links.yml` paths are correct

---

## Affiliate Link Health Check System (March 11, 2026)

### Status: COMPLETE

### Step 1 — Create `automation/links/check_links.py`
- [x] Create standalone link checker that reuses `extract_asins.py`
- [x] HTTP HEAD check for ASIN-based URLs (no API key needed)
- [x] Optional Rainforest API verification if `RAINFOREST_API_KEY` is set
- [x] Output JSON report + markdown summary
- [x] Exit code 1 if broken links found

### Step 2 — Create `.github/workflows/check-affiliate-links.yml`
- [x] Weekly cron (Monday 8 AM UTC) + manual `workflow_dispatch`
- [x] Runs `check_links.py` against both website directories
- [x] Auto-creates GitHub issue if broken links found

### Step 3 — Add pre-publish validation to article generators
- [x] Add `validate_affiliate_links()` to `fitover35_article_generator.py`
- [x] Add `validate_affiliate_links()` to `dailydealdarling_article_generator.py`
- [x] Warn on broken links but don't block publishing

### Review
Changes made:
1. **`automation/links/check_links.py`** (NEW, 407 lines) — Standalone CLI link checker. Reuses `extract_asins.py` for ASIN discovery and `verify_asins.py`'s `generate_github_issue_body()` for issue formatting. Two modes: HTTP HEAD (default, no API key) or Rainforest API (if `RAINFOREST_API_KEY` set). Outputs `link_report.json`, `link_report.md`, and `github_issue_body.md` to `automation/links/reports/`. 1s rate limit between HTTP requests.
2. **`.github/workflows/check-affiliate-links.yml`** (NEW, 47 lines) — Weekly cron (Monday 8am UTC) + manual trigger. Scans both website dirs, auto-creates GitHub issue via `peter-evans/create-issue-from-file@v5` when broken links found, uploads reports as artifacts (30-day retention).
3. **`automation/articles/fitover35_article_generator.py`** (MODIFIED) — Added `validate_affiliate_links()` function (~60 lines) before `main()`. Called after article HTML is written to disk. HTTP HEAD checks each ASIN with 1s rate limit, logs warnings for broken links. Never blocks the pipeline.
4. **`automation/articles/dailydealdarling_article_generator.py`** (MODIFIED) — Same `validate_affiliate_links()` pattern as FitOver35. Added before `main()`, called after file write.
