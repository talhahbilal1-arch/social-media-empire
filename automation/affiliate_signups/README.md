# Affiliate Signup Assistant

Playwright-driven, human-in-the-loop affiliate program signup suite. Opens a real browser, pre-fills what it can, pauses for CAPTCHA / review / final submit. Designed for the affiliate programs listed in `PHONE-ACTION-CHECKLIST.md`.

We cannot fully automate these signups (anti-bot, email verification, KYC) — but we can remove 90% of the typing. The human supplies the last 30 seconds (CAPTCHA + "Submit" click + any oddball fields).

## Pre-wired programs

| Slug | Program | Commission | Network |
|------|---------|-----------|---------|
| `semrush` | Semrush | up to $200/sale + $10/trial | Impact |
| `hostinger` | Hostinger Affiliates | 40-60% per sale | In-house |
| `ahrefs` | Ahrefs | 20% lifetime recurring | FirstPromoter |
| `frase` | Frase Partners | 30% recurring 12mo | FirstPromoter |
| `clickbank` | ClickBank Marketplace | 40-75% varies | ClickBank |

Full metadata in `programs.json`. Add more by editing that file.

## One-time setup

```bash
cd automation/affiliate_signups
npm install            # installs playwright + downloads Chromium
```

Then edit `applicant-profile.json` and replace every `YOUR_*` placeholder with your real info (name, email, address, PayPal, tax ID, social handles, etc).

> **IMPORTANT:** `applicant-profile.json` is gitignored at the repo root. It will never be committed. Do NOT remove the gitignore entry.

## Usage

### Apply to a program

```bash
node apply.js --program semrush
```

What happens:
1. Chromium launches with a persistent profile at `./.auth/<slug>/` (first run: you log in / create account manually; subsequent runs remember you).
2. The script navigates to the program's apply URL and pauses.
3. You click whatever "Apply" / "Join" / "Sign up" button surfaces the actual signup form, then press ENTER in the terminal.
4. The script heuristically fills email, name, website, phone, address, paypal, promotion description, social handles, etc.
5. The script pauses again — you review every field, fix anything missed, solve the CAPTCHA.
6. Press ENTER — the script screenshots the full page to `reports/<slug>-<timestamp>.png`.
7. You click **Submit** manually in the browser (the script never auto-submits).
8. You report status back in the terminal — it's appended to `reports/applications.csv`.

### Track follow-ups

```bash
node follow-up-tracker.js
node follow-up-tracker.js --out reports/follow-up.md
node follow-up-tracker.js --stale 14
```

Reads `reports/applications.csv`, emits a markdown report with:
- Pending applications within the normal approval window
- Stale applications (> 14 days by default) that need manual email follow-up
- Errors and approved rows

### CSV format

`reports/applications.csv`:

```
program_slug,program_name,submitted_at,screenshot_path,status,notes
```

`status` values: `submitted`, `pending_user_action`, `error`, `approved` (you can edit the CSV by hand to mark programs approved).

## Constraints

- **Never auto-submits.** Always pauses before the Submit click.
- **Heuristic selectors only.** No hard-coded CSS per program — field names change, so we try `input[name*="email" i]`, `input[type="email"]`, etc.
- **Placeholders in profile JSON are not real data.** If you run the script without editing the profile, it warns before filling placeholders into real forms.
- **Persistent browser context** per slug means login cookies stick around between runs in `.auth/<slug>/` (gitignored).

## Adding a new program

Append an entry to `programs.json`:

```json
"newprogram": {
  "name": "New Program",
  "slug": "newprogram",
  "apply_url": "https://...",
  "signup_url": "https://...",
  "network": "...",
  "commission": "...",
  "approval_time_days": 7,
  "cookie_window_days": 30,
  "payout_methods": ["PayPal"],
  "required_fields": ["email", "full_name", "website"],
  "notes": "..."
}
```

Then `node apply.js --program newprogram`.

## Layout

```
automation/affiliate_signups/
  package.json              # isolated Playwright deps
  applicant-profile.json    # YOUR info (gitignored, edit locally)
  programs.json             # program metadata
  apply.js                  # main assistant
  follow-up-tracker.js      # CSV → markdown report
  README.md                 # this file
  .auth/<slug>/             # persistent browser profiles (gitignored)
  reports/                  # screenshots + applications.csv (gitignored)
```
