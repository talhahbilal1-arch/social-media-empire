# Playwright Automation — Gumroad + PromptBase

Isolated Node/Playwright package that drives two browser-only workflows:

1. **Gumroad ZIP uploads** — Gumroad has no file-upload API, so we automate the
   dashboard to attach the 8 prompt-pack ZIPs to their published-but-empty
   products.
2. **PromptBase listings** — PromptBase has no public API at all, so we script
   `promptbase.com/sell` to submit 7 individual prompt packs as drafts.

Everything lives in this directory. The scripts do not touch the rest of the
repo; they read ZIPs from `../../prompt-packs/...` via relative paths recorded
in the manifests.

## 1. One-time setup

```bash
cd automation/playwright
npm install
npx playwright install chromium
```

Nothing else is installed globally. `playwright` is pinned as a local dep.

## 2. Log in once (persistent context)

Both scripts launch Chromium with a **persistent user-data dir** at `./.auth/`.
That means your Gumroad and PromptBase sessions are stored on disk and reused
on every subsequent run — you only log in once per site per machine.

The easiest way to seed the session:

```bash
node gumroad-zip-uploader.js --dry-run
```

- Chromium opens (headed, slow-mo). It will navigate to the first product's
  edit URL and get bounced to `/login`.
- Log in manually, complete 2FA, and let Gumroad land on the dashboard.
- The script will continue, the session is now persisted, and `--dry-run`
  means nothing is actually submitted.
- Repeat the same trick with `node promptbase-lister.js --dry-run`.

From then on `./.auth/` holds the cookies and both scripts run unattended.

## 3. Real runs

```bash
# Upload all 8 ZIPs to Gumroad (skips products that already have a file)
node gumroad-zip-uploader.js

# Submit 7 prompt packs as drafts on PromptBase
node promptbase-lister.js
```

Or via npm scripts:

```bash
npm run gumroad       # real upload
npm run gumroad:dry   # dry-run
npm run promptbase    # real submit
npm run promptbase:dry
```

## 4. Dry-run flag

Every script honors `--dry-run`:

- Gumroad: navigates, opens the Content tab, checks for an existing file, logs
  what *would* be uploaded. No `setInputFiles` call, no Save click.
- PromptBase: navigates to `/sell`, fills the form fields in memory, logs
  what would be submitted. No Save Draft click.

## 5. Output — CSV reports

Each run writes a timestamped CSV to `./reports/`:

- `reports/gumroad-uploads-<ISO-timestamp>.csv`
  — columns: `slug,title,zip,status,detail,durationMs`
  — statuses: `uploaded | skipped_has_file | needs_login | missing_zip | dry_run | error`
- `reports/promptbase-listings-<ISO-timestamp>.csv`
  — columns: `slug,title,price,status,detail,durationMs`
  — statuses: `submitted | needs_login | dry_run | error`

On failure, a full-page screenshot is also written to `./artifacts/` so you
can see exactly what the script saw.

## 6. Manifests

- `gumroad-manifest.json` — 8 products, each with `{ slug, title, zip }`. The
  `zip` path is resolved relative to this directory (so `../../prompt-packs/...`
  walks up to the repo root).
- `promptbase-manifest.json` — 7 prompt-pack entries with `{ slug, title,
  description, example_prompt, price }` plus shared `defaults` (category,
  model, visibility). The mega bundle is intentionally **not** on PromptBase —
  it only sells as a Gumroad upsell.
- `screenshots/<slug>.png` — optional. If present, the PromptBase script
  attaches it as the example-output image. PromptBase requires one for final
  approval; drafts can be saved without it.

## 7. Known fragility points

These are UI-driven scripts. Expect to tweak selectors when sites redesign.

- **Gumroad Content tab** — currently found via `getByRole('tab', { name: /content/i })`
  with a `getByRole('link', ...)` fallback. If Gumroad moves to a sidebar-only
  layout, update the tab selector in `gumroad-zip-uploader.js`.
- **Gumroad file input** — the script grabs the first `input[type=file]` on the
  page after the Content tab is open. Gumroad sometimes lazy-renders the
  drop-zone; if uploads fail, add `await page.waitForSelector('input[type=file]')`
  with an explicit container selector.
- **Gumroad "already has a file" detection** — heuristic, matches any of
  `Replace file`, `Download file`, or a visible `.zip` substring. False
  positives will skip a product; false negatives will re-upload (Gumroad
  tolerates replacement).
- **Gumroad Save button** — matched by accessible name `/^save( changes)?$/i`.
  If Gumroad renames it ("Publish changes", "Update"), extend the regex.
- **PromptBase form labels** — the lister probes `getByLabel`, `getByPlaceholder`,
  and `getByRole('textbox')` in sequence for each field. PromptBase renames
  labels roughly every 6 months; update the regex list in
  `fillByLabelOrPlaceholder` calls when fields stop filling.
- **PromptBase Save Draft** — matched by `/save (as )?draft|save draft/i`.
  Falls back to `/submit|publish/i` if no draft button exists, which will send
  the listing into review instead of draft. Watch the report status.
- **Rate limits / captchas** — PromptBase may show a Cloudflare challenge on
  first visit. Solve it manually in the headed window; the persistent context
  remembers the challenge token.
- **Gumroad slugs** — the manifest assumes the edit URL is
  `gumroad.com/products/<slug>/edit`. If your actual product slugs differ
  (Gumroad sometimes appends a random suffix), update
  `gumroad-manifest.json`. The slugs currently in the manifest are inferred
  from the ZIP filenames.

## 8. File map

```
automation/playwright/
  package.json                  # local deps (playwright only)
  playwright.config.js          # shared config (userDataDir, slowMo, timeouts)
  gumroad-manifest.json         # 8 Gumroad products -> ZIP paths
  gumroad-zip-uploader.js       # driver for Gumroad uploads
  promptbase-manifest.json      # 7 PromptBase prompt packs
  promptbase-lister.js          # driver for PromptBase submissions
  screenshots/                  # optional example-output PNGs (create yourself)
  .auth/                        # persistent browser profile (auto-created)
  reports/                      # CSV run reports (auto-created)
  artifacts/                    # failure screenshots/videos (auto-created)
```

## 9. Troubleshooting

- `needs_login` on every row → delete `./.auth/` and re-seed with `--dry-run`.
- `missing_zip` → confirm the ZIP exists at the manifest path. Run
  `ls ../../prompt-packs/products/*.zip` from this directory.
- Upload hangs → the script polls 5 minutes for the filename badge, then
  proceeds to the Save click. If Gumroad's upload is slower than that, bump
  the `uploadDeadline` constant in `gumroad-zip-uploader.js`.
- Headless CI → set `headless: true` in `playwright.config.js`. You must first
  seed `.auth/` on a desktop machine and copy the directory to the CI runner.
