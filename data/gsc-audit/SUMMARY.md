# GSC Indexing Audit — Summary (2026-04-27)

- Repo: `/Users/homefolder/Desktop/social-media-empire`
- Deploy dir: `outputs/fitover35-website/` (222 HTML files, 196 articles)
- Sitemap: 189 URLs total, 188 ending in `.html`
- Static `.html` canonicals: **206 of 222** files
- Static `noindex` meta tags: **3 of 222** files
- Crawl: 44 URLs sampled @ 1.0s between requests
- Vercel config: cleanUrls=True trailingSlash=False redirects=0 headers=0

## Bucket totals (in crawl sample)

| Bucket | EXPECTED/INTENTIONAL | BUG | Other |
|---|---|---|---|
| canonical | 2 | **39** | NO_CANONICAL=3 |
| noindex   | 0 | **3** | NO_NOINDEX=41 |
| redirect  | 22 | **0** | REVIEW=0 |

## Proposed actions

- **Canonical fix (mechanical sed)**: 39 crawled URLs flagged BUG. Static check shows **206/222** deployed files have a `.html` canonical. Fix: sed all article HTML + sitemap.xml + 1-line generator change. Estimated files modified: **206 HTML files + 1 sitemap + 1 generator script**.
- **Noindex fix**: 3 URLs flagged BUG. See `noindex-diagnosis.md` for source files. Manual review required before any tag is removed.
- **Redirect**: no chains >1 hop or 4xx final statuses observed in crawl.

## Internal-link cleanup (deferred)

Internal `<a href="/foo.html">` links across the site still produce 1-hop redirects via `cleanUrls`. This is EXPECTED behavior, but the redirect bucket in GSC may not fully empty until those links are also cleaned up. Out of scope for this PR; track as a follow-up if the bucket remains noisy after re-crawl.

## Next step

Review the three `*-diagnosis.md` files and `crawl-results.csv`, then explicitly approve Phase 4 fixes.
