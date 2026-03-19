# Task: Fix fitover35.com Domain — Reassign to fitover35-website Project

**For User (Manual — Vercel Dashboard):** This is the ONE manual step needed to fix fitover35.com articles.

**Background:** The standalone `fitover35` Vercel project (created March 10 from the `talhahbilal1-arch/fitover35` repo) stole the `fitover35.com` domain from the `fitover35-website` project (deploys from social-media-empire with 153 articles). Articles have been 404 on fitover35.com ever since.

---

## Steps

### Step 1: Remove domain from wrong project
1. Go to https://vercel.com/talhahbilal1s-projects/fitover35/settings/domains
2. Remove `fitover35.com` from this project
3. Remove `www.fitover35.com` from this project

### Step 2: Add domain to correct project
1. Go to https://vercel.com/talhahbilal1s-projects/fitover35-website/settings/domains
2. Add `fitover35.com`
3. Add `www.fitover35.com` (redirect to fitover35.com)
4. Wait for DNS verification (should be instant since DNS already points to Vercel)

### Step 3: Verify articles are live
Test these URLs — all should return 200:
- https://fitover35.com/articles/training-around-injuries
- https://fitover35.com/articles/top-testosterone-boosters-for-muscle-growth
- https://fitover35.com/articles/compound-lifts-vs-isolation-exercises-efficiency-after-35

### Step 4: Disable auto-deploy on standalone repo (prevent recurrence)
1. Go to https://vercel.com/talhahbilal1s-projects/fitover35/settings/git
2. Either disconnect the GitHub integration OR disable auto-deploy
3. This prevents future pushes to `talhahbilal1-arch/fitover35` from stealing the domain back

---

## What Was Already Fixed (Pushed to GitHub)

### Fix 1: Subdomain deploy path filter (`subdomain-deploy.yml`)
- Changed trigger from `push: main` (every push) to `push: main + paths: outputs/infrastructure/**`
- Saves 30-50 Vercel deploys/day — was the main cause of hitting the 100/day free tier limit

### Fix 2: Deploy failure detection (`content-engine.yml`)
- Deploy step now tracks failures per brand via `/tmp/deploy_failures`
- New "Update pin URLs if deploy failed" step: falls back to homepage + logs error to Supabase

### Fix 3: Article URL validation (`content-engine.yml`)
- REMOVED the `is_fresh_article` bypass that skipped validation for new articles
- ALL article URLs are now verified with HTTP HEAD before posting to Pinterest
- If URL returns 404, pin falls back to homepage + logs `article_url_404` error

### Fix 4: Increased deploy propagation wait
- Changed `time.sleep(60)` to `time.sleep(90)` before pin posting

---

## Architecture Notes
- `fitover35-website` project (prj_xJ3y...) = source of truth for fitover35.com, deployed from `social-media-empire/outputs/fitover35-website/`
- `fitover35` project (prj_WYcq...) = standalone repo, only 11 old articles, should NOT own the domain
- The standalone repo is useful for manual site updates (GSC verification, etc.) but all automated content goes through social-media-empire

## Do NOT
- Delete the standalone `fitover35` project — it has GSC verification files. Just remove its custom domain.
- Re-enable `push` trigger on `subdomain-deploy.yml` without path filters
- Re-add the `is_fresh_article` validation bypass in content-engine
