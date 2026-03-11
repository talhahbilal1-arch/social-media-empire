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
