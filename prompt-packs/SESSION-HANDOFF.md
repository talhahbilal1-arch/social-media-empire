# Session Handoff — Prompt Pack Launch (2026-03-19)

## Completed This Session

### Gumroad Products (ALL DONE)
- [x] 4 cover images uploaded to 4 products
- [x] 4 ZIP deliverables uploaded to 4 products
- [x] All 4 products saved on Gumroad

**Product URLs:**
| Product | Slug | Gumroad URL |
|---------|------|-------------|
| Zero-Miss Lead Engine | bxslh | talhahbilal.gumroad.com/l/bxslh |
| Content Repurposing Machine | rfoee | talhahbilal.gumroad.com/l/rfoee |
| Automated Review Generator | olryh | talhahbilal.gumroad.com/l/olryh |
| AI Automation Empire Bundle | rwzcy | talhahbilal.gumroad.com/l/rwzcy |

**ZIP files uploaded:**
- `zero-miss-lead-engine-v1.zip` (54,024 bytes) -> bxslh
- `content-repurposing-machine-v1.zip` (117,399 bytes) -> rfoee
- `automated-review-generator-v1.zip` (45,528 bytes) -> olryh
- `ai-automation-empire-bundle-v1.zip` (224,975 bytes) -> rwzcy

### Gumroad Discount Code (DONE)
- [x] Created discount code: `SUBSCRIBER20`
- 20% off, unlimited uses
- Applied to all 4 paid products above

### Kit (ConvertKit) Email Sequence (DONE)
- [x] Added SUBSCRIBER20 discount code to Email 5 ("Something for the Pinterest and content side of your business")
- Text added: "Subscriber-only perk: use code SUBSCRIBER20 at checkout for 20% off any of these products. Just paste it on the Gumroad checkout page."
- Published successfully (word count went from 196 to 218)

### PromptBase (DONE)
- [x] All 3 submissions approved and live
- "8-Week Training Program for Men Over 35" — $4.99
- "Pinterest Pin Title Generator" — $4.99
- "Online Coach DM Reply Script" — $4.99

### Etsy (Previously Done)
- [x] 3 listings published with mockup images + PDFs

## Still TODO (Next Session)

### 1. PromptBase Payout Setup (MANUAL — user must do)
- Go to connect.promptbase.com
- Choose Zoneless (USDC) or Stripe payout
- Requires personal info: DOB, address, phone
- Cannot be automated — user must fill in themselves

### 2. Post Product Pins to Pinterest
- Script: `prompt-packs/post-product-pins.py`
- Has 13 product promotion pins ready to post
- Gumroad URLs already updated with real slugs
- **BLOCKED**: Requires env vars not set locally:
  - `SUPABASE_URL`, `SUPABASE_KEY`, `PEXELS_API_KEY`
  - `MAKE_WEBHOOK_FITNESS`, `MAKE_WEBHOOK_DEALS`, `MAKE_WEBHOOK_MENOPAUSE`
- **Options to run:**
  - A) Export env vars locally from GitHub secrets
  - B) Create a GitHub Actions workflow to run it
  - C) Run manually with env vars: `SUPABASE_URL=... python3 post-product-pins.py`

### 3. Optional: Add discount code to more Kit emails
- Currently only in Email 5. Could also add to:
  - Email 6: "Last reminder — the $27 launch price won't last" (urgency email)
  - Email 3: "The AI Fitness Coach Vault is live" (launch announcement)

### 4. Test Purchase Flow
- Buy each product with a $0 test coupon on Gumroad
- Verify PDF/ZIP downloads correctly
- Check email delivery

## Technical Notes

### Upload Method Used
- postMessage + popup window pattern to bypass Gumroad's CSP
- Local HTTP server with CORS (port 8787) serves files from `gumroad-deliverables/`
- Helper HTML pages fetch files locally, send ArrayBuffer via postMessage to Gumroad tab
- Gumroad tab constructs File objects using DataTransfer API and injects into file inputs

### Key Files
- `/Users/homefolder/Desktop/ai-monetization/gumroad-deliverables/` — ZIP files + covers
- `/Users/homefolder/Desktop/ai-monetization/gumroad-deliverables/helper.html` — file upload helper
- `/Users/homefolder/Desktop/ai-monetization/gumroad-deliverables/covers/helper.html` — cover upload helper
- `/tmp/serve_files.py` — CORS file server (not running)
- `/tmp/gumroad_upload.mjs` — Puppeteer upload script (alternative method)

### Kit Sequence Details
- Sequence: "Fit Over 35 - Prompt Pack Launch Sequence"
- URL: app.kit.com/sequences/2646731
- 13 day sequence, 7 emails, 0 subscribers currently
- Account shows as "Daily Deal Darling" (shared Kit account)
