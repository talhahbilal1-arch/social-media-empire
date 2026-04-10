# FitOver35 Affiliate Improvement Pass — 2026-04-10

## Mission

User goal: **more affiliate sales** from fitover35.com, via both on-site CRO and better Pinterest traffic quality. The original "overnight fix" prompt described stale problems (404s, placeholder links, missing articles) that had already been fixed on 2026-04-08 — verified via git log, source audit, and live site inspection. This pass instead targeted the **actually unresolved** issues that directly affect affiliate revenue.

## What Shipped

### 1. Pinterest destination URL fix — highest-leverage change
Every pin used to point to `fitover35.com/` (the homepage) regardless of its topic. Root cause of the 0.09% outbound CTR and (indirectly) the 73% impression decline — Pinterest downranks pins with poor destination UX.

**Files:**
- `video_pipeline/pinterest_destination_mapper.py` — new module, 171 lines. `resolve_destination(brand, script_data, board_name)` returns a topic-matched article URL (or site_url fallback) with `utm_source/medium/campaign/content` params.
- `video_pipeline/pinterest_poster.py:327` — swapped `brand.site_url` for `resolve_destination(...)`.
- `video_pipeline/poster.py:136` — same swap in the Make.com webhook payload.

**Topic map:** 20 entries for FitOver35, ordered most-specific-first (`best protein powder` before `protein`, `testosterone booster` before `testosterone`). Covers creatine, pre-workout, testosterone, protein, dumbbells, home gym, resistance bands, compound lifts, belly fat, longevity, motivation, metabolic health, alcohol, limited-equipment training.

**Fallback safety:** If no keyword matches, returns `brand.site_url` (previous behavior) with UTM params. Worst case = same as before, no risk of breaking posting.

**Verification:** Tested 10 sample `script_data` payloads end-to-end with real `BrandConfig.fitover35`. 9/10 mapped to specific articles; 1 (deliberately unmatched) fell back to homepage. All URLs included correct UTM params.

**Activation:** Takes effect on the next scheduled GitHub Actions run (`content-engine.yml` runs at 14:00/17:00/20:00/23:00/03:00 UTC).

### 2. gear.html monetization
Previously a 1,676-word page with **zero** Amazon links — product cards rendered from a JS array and linked to internal articles only.

**Changes:**
- New "Top Gear Picks" section inserted above the article grid, with 6 direct Amazon affiliate cards (Bowflex SelectTech 552 `B0BB8D5VTW`, FITFORT bands `B07WQLDKN2`, TriggerPoint GRID foam roller `B0040EKZDY`, CAP Barbell 300lb set `B001K4OPY2`, Amazon Basics kettlebell `B0FT9YCSJP`, Iron Gym doorway pull-up bar via search URL).
- New `.pick-card` / `.picks-grid` CSS matching existing #d4a843 gold accent and dark palette.
- Existing article grid preserved as secondary "All Gear Reviews" section — users who want the deep-dive still get it.
- Amazon Associates disclosure line under the picks.
- Kept the email-capture block untouched.

**Live verification:** `https://fitover35.com/gear` — "Top Gear Picks" heading present, 6 `tag=fitover3509-20` matches.

### 3. Affiliate products added to 5 tagless commercial articles
These 5 articles had explicit "best X" commercial intent but zero monetization — every affiliate link was `href="#"`.

| Article | Products added |
|---|---|
| `best-creatine-for-men-over-40` | Thorne Creatine (`B00GL2HMES`), Optimum Nutrition, Nutricost |
| `creatine-monohydrate-for-older-men` | Same 3 creatine picks |
| `best-pre-workout-for-men-over-40` | Transparent Labs BULK, Legion Pulse, Cellucor C4 |
| `top-rated-pre-workout-for-35` | Same 3 pre-workout picks |
| `resistance-bands-for-strength-training-at-home` | FITFORT (`B07WQLDKN2`), Fit Simplify (`B01AVDVHTI`), Bodylastics |

Each article got:
- 3 `.pick` cards with Top/Also Great/Budget badges (clickable anchors, not dead divs)
- `final-cta` Check Today's Price link pointing to the Top Pick ASIN
- Mobile sticky bar Check Price link pointing to the same ASIN
- 5 affiliate tag occurrences per article total

**The 2 remaining tagless articles (`motivational-monday-stay-consistent`, `progressive-overload-for-beginners-over-35`) are non-product topics and were deliberately left alone.**

### 4. Fixed 15 unclickable pick cards across 5 top "money" articles
Discovered during Phase 4 CRO spot-check: the prominent "Our Pick / Also Great / Budget Pick" showcase at the top of the 5 highest-commercial-intent articles rendered as plain `<div>` elements, not links. Users saw clickable-looking cards that did nothing — pure dead click real estate above the fold.

**Articles fixed:**
- `best-adjustable-dumbbells-2026` (3 picks → 3 anchors)
- `best-home-gym-equipment-under-500` (3 → 3)
- `best-fitness-tracker-weight-training` (3 → 3)
- `best-testosterone-booster-for-men-over-40` (3 → 3)
- `best-protein-powder-for-men-over-50` (3 → 3)

Converted via Python regex script keyed on the `<div class="pick-name">` content. Used verified ASINs where known (Bowflex 552, Optimum Nutrition Gold Standard), Amazon search URLs otherwise — all with `tag=fitover3509-20`.

**Net effect:** 15 previously unclickable above-the-fold cards are now affiliate links. Each article now has 8–9 total affiliate tags vs 5–6 before.

## Deployment

**Important discovery:** the overnight prompt said fitover35.com is hosted on Netlify (site ID `aebf6cb2-bb4e-42b7-8247-db0ca79d9bc0`). That's **wrong**. DNS → `76.76.21.x` (Vercel). Response headers: `server: Vercel`. The Netlify site is a zombie — deploying to it succeeds but doesn't change anything on the live domain.

Correct host: **Vercel**, project `prj_xJ3y2gstjJktWHGtMpVJPAAIUiFy` in `team_h4nMjQJcOXwrnK5fpKHrbJGq`, name `fitover35-website`. Linked in `.vercel/project.json`.

**Deploy commands run (in order):**
1. `netlify deploy --prod --dir=. --site=aebf6cb2-bb4e-42b7-8247-db0ca79d9bc0` → succeeded, zombie site updated but live domain unchanged (wasted but harmless)
2. `vercel --prod --yes` → succeeded, aliased to `https://fitover35.com`. Build time ~11s.

**Vercel deployment URL:** `https://fitover35-website-a6qqn18ei-talhahbilal1s-projects.vercel.app`

## Git

Two logical commits on `talhahbilal1-arch/social-media-empire` main, rebased onto remote (had auto-posts from the content engine in between) and pushed:
- `dd2bcc6` — fix(pinterest): deep-link pins to articles with UTM tracking
- `8308b17` — content(fitover35): monetize gear page + fix 15 unclickable pick cards

## Live Verification (2026-04-10 post-deploy)

| URL | Status | Affiliate tags |
|---|---|---|
| `/` | 200 | 7 |
| `/gear` | 200 | **6** (new) |
| `/articles/best-creatine-for-men-over-40` | 200 | **5** (new) |
| `/articles/creatine-monohydrate-for-older-men` | 200 | **5** (new) |
| `/articles/best-pre-workout-for-men-over-40` | 200 | **5** (new) |
| `/articles/top-rated-pre-workout-for-35` | 200 | **5** (new) |
| `/articles/resistance-bands-for-strength-training-at-home` | 200 | **5** (new) |
| `/articles/best-adjustable-dumbbells-2026` | 200 | **8** (was 5) |
| `/articles/best-home-gym-equipment-under-500` | 200 | **8** (was 5) |
| `/articles/best-fitness-tracker-weight-training` | 200 | **8** (was 5) |
| `/articles/best-testosterone-booster-for-men-over-40` | 200 | **9** (was 6) |
| `/articles/best-protein-powder-for-men-over-50` | 200 | **9** (was 6) |
| (all 11 original prompt URLs) | 200 | — |
| `/sitemap.xml`, `/robots.txt` | 200 | — |

**25/25 URLs return 200. Zero 404s. Zero placeholder links remaining on touched pages.**

Change-specific checks:
- `gear.html` serves "Top Gear Picks" heading ✓
- `gear.html` has 6 Amazon affiliate links ✓
- `best-creatine-for-men-over-40` shows "Thorne Creatine" card ✓
- `best-creatine-for-men-over-40` has 3 clickable `<a class="pick">` anchors ✓

## Impact Summary

| Metric | Before | After |
|---|---|---|
| Articles with `fitover3509-20` tag | 167 / 174 (96%) | 172 / 174 (99%) |
| `gear.html` direct Amazon links | 0 | 6 |
| Unclickable above-fold pick cards on money articles | 15 | 0 |
| Affiliate tags on 5 top money articles | 5–6 per article | 8–9 per article |
| Pinterest pin destinations | 100% homepage | Topic-matched deep links + UTM |

## Known Caveats

1. **Pinterest fix activation is asynchronous.** The code change ships with the commit, but the actual pins generated between deploys and the next GitHub Action run will still use the old hardcoded-homepage behavior. First deep-linked pin will appear at the next scheduled run.
2. **Netlify zombie.** The Netlify site ID `aebf6cb2-bb4e-42b7-8247-db0ca79d9bc0` is not the live host. Any automation that still deploys there will silently fail to update the actual site. Consider deleting that Netlify site or updating any scripts that reference it.
3. **Search URLs vs ASIN links.** Where I wasn't 100% sure of an ASIN (pre-workout products, some kettlebells), I used Amazon search URLs like `https://www.amazon.com/s?k=legion+pulse&tag=fitover3509-20`. These still credit the affiliate tag but have slightly lower conversion rates than direct ASIN links.
4. **Two tagless articles intentionally untouched.** `motivational-monday-stay-consistent` and `progressive-overload-for-beginners-over-35` are non-product topics; adding affiliate blocks would feel spammy. If you want them monetized anyway (e.g. gym journal, notebook), that's a separate decision.

## Next-Session Recommendations

1. **Validate Pinterest Rich Pins** using Pinterest's Rich Pin Validator on 2–3 article URLs. Meta tags are present, but confirming Pinterest actually reads them is a manual step.
2. **Watch Pinterest Analytics for 7–14 days** after the deep-link fix rolls out via the next GitHub Action run. Expect outbound CTR to climb from 0.09% into the 1–3% range if the topic mapping is hitting well. If CTR stays flat, investigate whether the pins' images/titles match the destination content (a second root cause).
3. **Add UTM tracking dashboards** in GA4 to measure `utm_source=pinterest` traffic by `utm_campaign` (board) and `utm_content` (pin title slug). Use this to identify which boards / pin topics actually convert.
4. **Audit the 7 non-tagless product articles** that may still be missing deep product placements (beyond the `grep -L` we did). Some may have affiliate tags in passing but no top-of-article product showcase.
5. **Gear page A/B:** Consider testing whether the "Top Gear Picks" section converts better at the top of the hero or directly in the hero itself (above the fold on mobile — currently it's ~1 screen down).
6. **Delete or formally archive the Netlify zombie** (`netlify sites:delete aebf6cb2-bb4e-42b7-8247-db0ca79d9bc0`) to prevent future confusion about where the site actually lives.

## Files Changed (11 HTML + 3 Python)

**Python (Pinterest automation):**
- `video_pipeline/pinterest_destination_mapper.py` (new)
- `video_pipeline/pinterest_poster.py` (2 lines)
- `video_pipeline/poster.py` (2 lines)

**HTML (fitover35 site):**
- `outputs/fitover35-website/gear.html`
- `outputs/fitover35-website/articles/best-creatine-for-men-over-40.html`
- `outputs/fitover35-website/articles/creatine-monohydrate-for-older-men.html`
- `outputs/fitover35-website/articles/best-pre-workout-for-men-over-40.html`
- `outputs/fitover35-website/articles/top-rated-pre-workout-for-35.html`
- `outputs/fitover35-website/articles/resistance-bands-for-strength-training-at-home.html`
- `outputs/fitover35-website/articles/best-adjustable-dumbbells-2026.html`
- `outputs/fitover35-website/articles/best-home-gym-equipment-under-500.html`
- `outputs/fitover35-website/articles/best-fitness-tracker-weight-training.html`
- `outputs/fitover35-website/articles/best-testosterone-booster-for-men-over-40.html`
- `outputs/fitover35-website/articles/best-protein-powder-for-men-over-50.html`
