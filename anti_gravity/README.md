# Anti-Gravity

Home-office / ergonomic-lifestyle affiliate site. Fourth lifestyle brand in the
empire alongside `fitness`, `deals`, and `menopause`.

## Niche

Expert reviews and buying guides for home-office gear — standing desks,
ergonomic chairs, monitor arms, desk accessories, and complete setups.
Amazon-affiliate monetized, targeted at remote workers and WFH enthusiasts.

## Layout

```
anti_gravity/
  main.py                    # CLI entrypoint (generator pipeline)
  core/                      # config + sqlite persistence
  services/
    writer.py                # Article generator (LLM)
    pinterest.py             # Pinterest poster
    wordpress.py             # Legacy WP publisher (unused)
    vercel_deploy.py         # Writes markdown + triggers vercel CLI
  site/                      # Next.js 14 app (the deployable)
    app/                     # Pages (home + /articles/[slug])
    content/articles/        # Markdown articles (gray-matter front matter)
    public/                  # sitemap.xml, robots.txt, static assets
    package.json
    vercel.json              # Vercel framework config + headers + cache
  DEPLOYED_URL.txt           # Written by deploy script after first deploy
```

## Current content (5 articles, ~11.7k words)

- `home-office-setup-guide` — Complete Home Office Setup Under $2,000
- `best-standing-desks-2026`
- `best-ergonomic-chairs-2026`
- `best-monitor-arms-2026`
- `best-desk-accessories-2026`

## Deploy

### One-liner (local)

```bash
VERCEL_TOKEN=xxxxxxxxxxxx bash scripts/deploy_anti_gravity.sh
```

The script:
1. Checks `VERCEL_TOKEN` is set.
2. Installs the Vercel CLI if missing (prompts unless `SKIP_INSTALL_PROMPT=1`).
3. Runs `vercel deploy --prod --yes` from `anti_gravity/site/`.
4. Writes the production URL to `anti_gravity/DEPLOYED_URL.txt`.
5. Prints post-deploy manual steps.

### GitHub Actions

Trigger the workflow `Deploy Anti-Gravity Site` (`.github/workflows/deploy-anti-gravity.yml`)
manually via the Actions tab. Uses secret `VERCEL_BRAND_TOKEN` (same secret
used by `deploy-brand-sites.yml`). Optional secrets:

- `VERCEL_ORG_ID` — team/org scope
- `VERCEL_ANTI_GRAVITY_PROJECT_ID` — bind deploys to an existing project

The workflow writes the deploy URL to the run summary and uploads
`anti_gravity/DEPLOYED_URL.txt` as an artifact.

## Post-deploy manual steps

1. **Custom domain** — Vercel dashboard -> Project -> Settings -> Domains.
2. **GA4 measurement ID** — replace `G-XXXXXXXXXX` in
   `anti_gravity/site/app/layout.tsx` with the Anti-Gravity property ID, then
   redeploy.
3. **Sitemap** — update `<loc>` values in
   `anti_gravity/site/public/sitemap.xml` to the custom domain.
4. **Search Console** — add the property and submit the sitemap.
5. **Pinterest board** — create `anti-gravity` board and map its ID in
   `video_automation/pinterest_boards.py` if bringing this brand into the
   5x-daily pin pipeline.
