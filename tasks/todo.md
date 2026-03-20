# PilotTools.ai Marketing Execution Plan
## From 0 → 50K Monthly Visitors

**Created:** 2026-03-20
**Status:** Planning — awaiting user approval

---

## Phase 1: SEO Content Machine Scale-Up (HIGHEST ROI)
*Your existing workflows already do this — we're expanding the keyword targets and increasing volume*

- [ ] **1.1** Update `ai-tools-hub/config/content-calendar.json` with Week 1-4 priority keywords:
  - `[Tool] pricing 2026` (one per tool = 20+ items)
  - `[Tool A] vs [Tool B]` (remaining comparison pairs)
  - `Is [Tool] worth it in 2026?` (one per tool)
  - `[Tool] alternatives` (one per tool)
  - `[Tool] free trial / free plan guide`
  - Target: 80+ new content calendar items
- [ ] **1.2** Add Week 5-8 keywords (profession + task pages):
  - `Best AI tools for [profession]` (25 professions)
  - `Best AI tools for [task]` (25 tasks)
  - `Best free AI [category] tools 2026`
  - Target: 55+ new items
- [ ] **1.3** Increase `toolpilot-content.yml` generation from 1/day to 2-3/day
- [ ] **1.4** Update `scripts/generate-content.js` quality rules:
  - 2,000+ words minimum
  - Direct answer in first 200 words (GEO optimization)
  - 2+ internal links per article
  - First-person language ("We tested", "In our review")
  - No filler phrases
- [ ] **1.5** Add Week 9-12 keywords (how-to + niche reviews)

**Target: 300+ indexed pages by Month 3**

---

## Phase 2: Pinterest Integration (LOWEST EFFORT, HIGH ROI)
*Replicate existing 3-brand pipeline for PilotTools*

- [ ] **2.1** Add PilotTools as 4th brand in Make.com pipeline:
  - New webhook scenario + `MAKE_WEBHOOK_PILOTTOOLS` secret
  - Pinterest business account + 5 boards
- [ ] **2.2** Create `pilottools_pin_generator.py` (reads from tools.json + articles.json)
- [ ] **2.3** Add PilotTools to pin posting workflow (3-5 pins/day)

---

## Phase 3: X/Twitter Automation (FASTEST NEW CHANNEL)
*New automation — daily posts from articles + tool data*

- [ ] **3.1** Set up X/Twitter developer account + API keys for PilotTools
- [ ] **3.2** Create `twitter_poster.py`:
  - 4 post types: Tool Tips, Comparisons/Hot Takes, New Tool Alerts, Thread Reviews
  - Gemini-generated copy from article/tool data
- [ ] **3.3** Create `toolpilot-twitter.yml` workflow (2-3 posts/day)
- [ ] **3.4** Create `twitter_posts` Supabase table for tracking

---

## Phase 4: Content Repurposing Engine (MULTIPLIER)
*1 article → 10+ social touchpoints*

- [ ] **4.1** Create `content_repurposer.py`:
  - Input: article slug → Output: X thread, X tweets, LinkedIn post, Pinterest pins, newsletter segment
  - Gemini adapts tone per platform
- [ ] **4.2** Integrate into `toolpilot-content.yml` (auto-generate social posts after article)
  - Store in `social_content_queue` Supabase table

---

## Phase 5: LinkedIn Automation (B2B AUDIENCE)
*3-4 posts/week targeting decision-makers*

- [ ] **5.1** Set up LinkedIn API credentials for PilotTools
- [ ] **5.2** Create `linkedin_poster.py` (Tool of Week, AI for Business, Industry Observations)
- [ ] **5.3** Create `toolpilot-linkedin.yml` (Mon/Wed/Fri 10AM PST)

---

## Phase 6: Email List Growth (OWNED AUDIENCE)
*Newsletter exists — needs lead magnet + growth*

- [ ] **6.1** Create "2026 AI Tools Pricing Cheat Sheet" PDF lead magnet
- [ ] **6.2** Update `NewsletterSignup.js` with lead magnet offer + exit-intent popup
- [ ] **6.3** Set up ConvertKit welcome automation with PDF delivery

---

## Phase 7: YouTube Shorts (ALGORITHMIC DISCOVERY)
*Lower priority — needs most new infrastructure*

- [ ] **7.1** Assess Remotion pipeline adaptation for tech content
- [ ] **7.2** Create text-overlay Shorts template (tool + rating + features + verdict)
- [ ] **7.3** Create `toolpilot-shorts.yml` (3-5 videos/week)

---

## Phase 8: Backlink Assets (AUTHORITY)
*Linkable assets + outreach templates*

- [ ] **8.1** Create "2026 AI Tools Pricing Index" dynamic page on pilottools.ai
- [ ] **8.2** Create outreach email templates (testimonial, resource page, guest post)

---

## Manual Tasks (NOT Automated — Your Daily Routine)

| Time | Action | Platform |
|------|--------|----------|
| Morning 10 min | Post 1 X reply + engage 5 conversations | X/Twitter |
| Midday 10 min | LinkedIn update OR Reddit comment | LinkedIn/Reddit |
| Evening 10 min | Post 1 X reply + check affiliate dashboards | X/Twitter |
| Whenever 15 min | Record 1 YouTube Short (batch on weekends) | YouTube/TikTok |

**Weekly:** Reddit contribution (Wed), GSC review (Fri), spot-check articles
**Monthly:** Update tool pricing, check affiliate dashboards, send 5 outreach emails, GEO audit

---

## Implementation Priority

| Order | Phase | Build Time | Impact |
|-------|-------|------------|--------|
| 1 | Phase 1 (SEO) | 2-3 hrs | Highest — compounds |
| 2 | Phase 2 (Pinterest) | 1-2 hrs | High — reuses infra |
| 3 | Phase 4 (Repurposer) | 2-3 hrs | High — multiplies all |
| 4 | Phase 3 (X/Twitter) | 3-4 hrs | High — new audience |
| 5 | Phase 5 (LinkedIn) | 2-3 hrs | Medium — B2B |
| 6 | Phase 6 (Email) | 1-2 hrs | Medium — owned list |
| 7 | Phase 8 (Backlinks) | 1-2 hrs | Medium — authority |
| 8 | Phase 7 (YouTube) | 4-6 hrs | Lower — most new infra |

**Total: ~20-25 hours across sessions**

---

## Review Notes
*(To be filled after implementation)*
