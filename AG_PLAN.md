# Task: Prompt Pack Launch — Remaining Steps

## Context
Gumroad products are fully set up (covers, ZIPs, discount code). Kit email sequence has SUBSCRIBER20 discount code added to Email 5. PromptBase listings approved. Next steps are minor cleanup items.

## Steps
- [ ] Step 1: Post product pins to Pinterest — `prompt-packs/post-product-pins.py`
  - What to do: Export required env vars locally (SUPABASE_URL, SUPABASE_KEY, PEXELS_API_KEY, MAKE_WEBHOOK_FITNESS/DEALS/MENOPAUSE) and run the script, OR create a GH Actions workflow for it
  - Acceptance: 13 pins posted across 3 brands

- [ ] Step 2: (Optional) Add SUBSCRIBER20 to Kit Email 6 — "Last reminder" email
  - What to do: Open app.kit.com/sequences/2646731, click Email 6, add discount text before sign-off
  - Acceptance: Email 6 published with discount code

- [ ] Step 3: Test purchase flow on Gumroad
  - What to do: Create a 100% off test coupon, buy each product, verify ZIP downloads
  - Acceptance: All 4 products deliver correctly

- [ ] Step 4: Set up PromptBase payouts (MANUAL)
  - What to do: Go to connect.promptbase.com, fill in personal info (DOB, address, phone)
  - Acceptance: Payout method configured

## Architecture Notes
- All Gumroad product slugs: bxslh, rfoee, olryh, rwzcy
- Discount code: SUBSCRIBER20 (20% off, unlimited uses, 4 products)
- Kit sequence: 2646731 (7 emails, 13 days)

## Do NOT
- Run post-product-pins.py without env vars — it will crash
- Delete the SESSION-HANDOFF.md — it has full context for the next session
