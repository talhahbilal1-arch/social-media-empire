# Phase 5+6: Internal Linking Audit & Sitemap Regeneration — April 8, 2026

## Context
Current article status: **418 articles total**
- fitness: 183 articles
- deals: 124 articles
- menopause: 111 articles

All scripts exist and are functional. This phase will:
1. Add contextual internal links (up to 5 per article) to improve SEO
2. Regenerate sitemaps with fresh lastmod dates
3. Ping Google & Bing to alert search engines of updates

## Part A: Internal Linking Audit

### Task 1: Run internal linking script on all brands
**Command**: `python3 scripts/add_internal_links.py --brand all`
- Scans all 418 articles
- Builds keyword-to-article relevance map per brand
- Inserts 3-5 contextual internal links per article
- Uses relative paths (all in `/articles/` directory)
- Skips articles with existing links >= 5

**Expected output**:
- ~5-10 links per article × 418 articles = ~2,000-4,000 total links added
- Clear report of articles modified per brand

### Task 2: Verify internal links
- Spot-check 3 articles (1 per brand)
- Verify links are contextually relevant
- Confirm no broken relative paths
- Ensure links use article titles as anchor text

---

## Part B: Sitemap Regeneration

### Task 3: Regenerate sitemaps with fresh lastmod
**Command**: `python3 scripts/regenerate_sitemaps.py --brand all`
- Updates 3 sitemaps (fitness, deals, menopause)
- Sets lastmod to today's date
- Includes all 418 articles at priority 0.7
- Preserves main pages (homepage, about, etc.) at higher priority

**Expected output**:
- 3 sitemap.xml files regenerated
- Each includes main pages + all articles
- Summary line: "Total articles indexed: 418"

### Task 4: Verify sitemaps are valid
- Check each sitemap.xml exists
- Verify XML structure (<?xml>, <urlset>, <url> tags)
- Confirm article count matches actual files
- Verify URLs follow expected format (https://domain/articles/slug.html)

---

## Part C: Search Engine Notification

### Task 5: Ping Google & Bing
**Command**: `python3 scripts/ping_search_engines.py`
- Notifies Google & Bing of sitemap updates
- Pings all 4 domains:
  - fitover35.com
  - dailydealdarling.com
  - menopause-planner-website.vercel.app
  - pilottools.ai
- Logs results to `~/.tall-command-center/briefings/seo-ping-2026-04-08.json`

**Expected output**:
- Success messages for Google and Bing pings
- Summary: "X successful, 0 failed"
- Log file saved

---

## Part D: Git Commit

### Task 6: Commit all changes
- Stage all modified HTML article files
- Commit message: `seo: add internal links and regenerate sitemaps (418 articles)`
- Push to main branch

---

## Review Checklist
- [ ] Internal links added to all 3 brands
- [ ] Links are contextually relevant (spot-checked)
- [ ] Sitemaps regenerated with fresh dates
- [ ] All 418 articles indexed in sitemaps
- [ ] Google & Bing pings successful
- [ ] Changes committed and pushed
- [ ] CLAUDE.md updated with current status

---

## Success Criteria
✅ 2,000+ internal links added across all brands
✅ 3 sitemaps regenerated with today's date
✅ Google & Bing both pinged successfully
✅ All changes committed to main branch
✅ No errors in script execution
