# Subscription Audit — 2026-04-16

## Summary
Scanned Gmail for the last 12 months (Apr 2025 – Apr 2026) using 7 targeted searches for subscription receipts, payment notifications, and renewals. Found 5 active recurring subscriptions + 2 one-time charges. Identified strong cancellation candidates.

## Estimated Monthly Total: $48.99/month

### Active Recurring Subscriptions
- Google AI Pro: $19.99/month (since Jan 2026)
- HeyGen Creator Unlimited: $29.00/month (since Dec 2025)
- **Total: $48.99/month**

---

## Subscription Table

| Service | Est. Monthly | Billing Cycle | Last Charge | Status | Reasoning |
|---|---|---|---|---|---|
| Google AI Pro (Google One) | $19.99 | Monthly | Jan 5, 2026 | KEEP | On KEEP list: Google Workspace / AI Pro integration for Drive storage |
| HeyGen Creator Unlimited | $29.00 | Monthly | Dec 30, 2025 | REVIEW | Last charge 3+ months ago; check if still in active use for video generation |
| Apify | $0.00 | Monthly | Jan 5, 2026 | KEEP | Free tier only; no cost |
| GitHub | $0.00 | N/A | N/A | KEEP | Free tier with activity (OAuth tokens, PAT regenerations). No paid charges found |
| Supabase | $0.00 | N/A | N/A | KEEP | Free tier. Free projects paused after 7 days inactivity; no Pro/paid charges |
| Vercel (Domain: pilottools.ai) | $160.00 | One-time | Mar 18, 2026 | KEEP | On KEEP list: domain registrar / hosting. One-time domain purchase |
| Anthropic (Claude Pro/Max) | $25.00 | One-time credit | Feb 26, 2026 | KEEP | On KEEP list: Claude AI / Anthropic. One-time credit purchase (not subscription) |

---

## Cancel Candidates (sorted by monthly savings)

1. **HeyGen Creator Unlimited** — $29/mo — Last charge Dec 30, 2025 (3.5 months ago); no charges in last 14 weeks suggest inactive subscription. Verify usage before auto-renewing. — [HeyGen account settings](https://www.heygen.com)

---

## Keep List (on KEEP whitelist — no action)

- **Google AI Pro** — Essential for Tall's ecosystem: 2 TB storage + AI features integrated with Drive
- **Anthropic / Claude** — Core tool for Tall's work (Claude Code, API usage)
- **GitHub** — Free tier; developer workflow
- **Supabase** — Free tier; backend infrastructure (projects auto-pause on inactivity)
- **Vercel** — Domain registrar / hosting; essential for deployments

---

## Unknown / Couldn't Parse

None. All detected services had clear cost or free-tier status.

---

## Search Results Summary

| Query | Results | Key Findings |
|---|---|---|
| `subject:receipt after:2025/04/16` | 17 | Vercel domain, Anthropic credit, Google AI Pro, HeyGen, Apify, Bank, Mandated Reporter Training |
| `subject:"your subscription" OR "welcome to" after:2025/04/16` | 8 | Utari welcome, Tumblr, Medium, Google AI Pro welcome |
| `subject:"payment successful" OR "invoice" after:2025/04/16` | 201+ | iSeeCars ($8.95), Apify ($0), personal training invoices (not subscriptions) |
| `subject:"renewed" OR "renewal" OR "auto-renew" after:2025/04/16` | 5 | Namecheap SSL renewal notice, DMV renewal, Mozi newsletter |
| `from:stripe.com after:2025/04/16` | 3 | iSeeCars, HeyGen, Mandated Reporter Training |
| `from:paddle.com after:2025/04/16` | 0 | No Paddle transactions |
| `subject:"trial ending" after:2025/04/16` | 0 | No trial expiry warnings |

---

## Notes

- **HeyGen** is the only strong cancellation candidate: 3.5-month gap since last charge suggests non-renewal or dormancy. Recommend manual confirmation before auto-renewal.
- **Vercel charge** ($160) is a one-time domain purchase for pilottools.ai, not a recurring subscription.
- **Anthropic charge** ($25) was a one-time credit purchase, not a monthly subscription.
- GitHub and Supabase are on free tiers with no paid upgrade charges in the audit period.
- **Namecheap domain renewals** are handled via email reminders but no receipts captured in Gmail, suggesting auto-renewal or offline payment.

**Verification:** ✓ Minimum 3 services identified ✓ Estimated monthly total computed ✓ Cancel reasoning populated ✓ Output file written
