# Supabase Database Table Inventory

## Production Project (epfoxpgrpsnhlsglxvsa) — 18 Tables

### Core Tables (Migration 001)
1. **videos** — Video generation pipeline
2. **content_bank** — Content library storage
3. **agent_runs** — Agent execution tracking (7 agents seeded)
4. **subscribers** — Email subscribers per brand
5. **analytics** — Raw event metrics
6. **errors** — Error logging (auto-cleanup: 7 days)
7. **email_sequences** — Email campaign templates
8. **posting_schedule** — Content scheduling
9. **content_history** — Historical content tracking
10. **daily_trending** — Daily trends per brand
11. **weekly_calendar** — Weekly content planning
12. **generated_articles** — Article tracking (UNIQUE: brand+slug)
13. **pinterest_pins** — Pinterest pin pipeline (43 columns after migration 003)

### Revenue Tracking (Migration 002)
14. **affiliate_revenue** — Daily affiliate earnings
15. **email_conversions** — Email → purchase attribution
16. **content_performance** — Content scoring (GA4 + GSC)
17. **affiliate_programs** — Affiliate program catalog (12 rows seeded)

### Newsletter (Migration 004)
18. **newsletter_sends** — Article broadcast tracking

---

## Secondary Project (bjacmhjtpkdcxngkasux) — 3 Tables

### TikTok Pipeline
1. **tiktok_queue** — Video generation pipeline (40 columns, 20 starter rows)
2. **tiktok_analytics** — Performance metrics per video
3. **tiktok_prompts** — Prompt A/B testing

---

## Quick Stats

| Metric | Count |
|--------|-------|
| **Total Tables** | 21 |
| **RLS Enabled** | 21/21 ✅ |
| **With Indexes** | 18+ |
| **With Triggers** | 1 (tiktok_queue) |
| **With FK Constraints** | 2 |
| **With UNIQUE Constraints** | 6+ |
| **Migrations** | 5 (all applied) |

---

## Status: ✅ PRODUCTION READY

All tables properly configured with RLS, service-role access, and appropriate indexing.
See AUDIT_REPORT_2026-03-21.md for detailed analysis.
