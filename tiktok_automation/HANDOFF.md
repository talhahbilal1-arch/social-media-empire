# TikTok Automation Pipeline - Handoff Document

**Created:** 2026-02-05
**Status:** Complete - Ready for deployment
**Commit:** `35d3a2b` on main

---

## What Was Built

A complete faceless TikTok video automation pipeline using Make.com, targeting U.S. women 25-44 in fitness/beauty/lifestyle niche for the TikTok Creativity Program + Amazon affiliates.

### Files Created

```
tiktok_automation/
├── database/
│   └── tiktok_schema.sql           # Supabase tables + 20 starter topics
├── make_scenarios/
│   ├── 1_content_generator.json    # Cron → Claude → Supabase
│   ├── 2_video_renderer.json       # ElevenLabs + HeyGen → video
│   ├── 3_tiktok_poster.json        # Upload to TikTok
│   └── 4_analytics_monitor.json    # Analytics + cross-posting
├── README.md                        # Quick reference
├── SETUP_GUIDE.md                   # Complete setup documentation
└── HANDOFF.md                       # This file
```

### Validation Completed

- [x] SQL syntax validated (21 statements, all passed)
- [x] 20 starter topics with affiliate products validated
- [x] All JSON arrays and ARRAY[] syntax validated
- [x] Make.com scenarios validated (4 files, 50 modules, all passed)
- [x] Module references validated
- [x] Error handling confirmed on all scenarios
- [x] Committed and pushed to GitHub

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DAILY AUTOMATION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SCENARIO 1          SCENARIO 2          SCENARIO 3                 │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐                 │
│  │GENERATOR│───────▶│RENDERER │───────▶│ POSTER  │                 │
│  └─────────┘        └─────────┘        └─────────┘                 │
│       │                  │                  │                       │
│       ▼                  ▼                  ▼                       │
│   Claude API      ElevenLabs TTS      TikTok API                   │
│   (scripts)       + HeyGen Video      (upload)                     │
│       │                  │                  │                       │
│       └──────────────────┼──────────────────┘                       │
│                          ▼                                          │
│                   ┌───────────┐                                     │
│                   │ SUPABASE  │                                     │
│                   │tiktok_queue│                                    │
│                   └───────────┘                                     │
│                          │                                          │
│                          ▼                                          │
│                   SCENARIO 4                                        │
│                   ┌─────────┐                                       │
│                   │ANALYTICS│──▶ YouTube Shorts                     │
│                   │+ MONITOR│──▶ Pinterest                          │
│                   └─────────┘──▶ Prompt Optimization                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Status Flow

```
pending → script_ready → audio_ready → video_ready → posted
                                              ↓
                                           failed
```

---

## Costs & Revenue Summary

### Monthly Costs: ~$65

| Service | Cost |
|---------|------|
| Make.com Pro | $16 |
| ElevenLabs Creator | $22 |
| HeyGen Creator | $24 |
| Claude API | ~$3 |
| **Total** | **~$65** |

### Revenue Projections

| Timeline | Revenue/Month | Net Profit |
|----------|---------------|------------|
| Month 1-2 | $70-200 | $5-135 |
| Month 3-4 | $450-1,175 | $385-1,110 |
| Month 5-6 | $1,375-4,125 | $1,255-4,005 |
| Month 12 | $4,625-12,250 | $4,500-12,000 |

**Break-even:** Week 4-5
**$1K/month target:** Month 4-5
**Year 1 projected net:** ~$18,000

---

## Deployment Steps (To Do)

### 1. Supabase Setup
```bash
# Run in Supabase SQL Editor:
# Copy contents of: tiktok_automation/database/tiktok_schema.sql
```

- [ ] Create Supabase project (or use existing)
- [ ] Run tiktok_schema.sql in SQL Editor
- [ ] Copy **service_role** key (Settings → API)
- [ ] Copy Project URL

### 2. API Keys Needed

| Service | Where to Get |
|---------|--------------|
| Supabase service_role | Dashboard → Settings → API |
| Anthropic (Claude) | console.anthropic.com |
| ElevenLabs | elevenlabs.io → Profile → API Key |
| HeyGen | app.heygen.com → Settings → API |
| TikTok | developers.tiktok.com (needs approval) |
| Amazon Associates | affiliate-program.amazon.com |

### 3. Make.com Import

Import in order:
1. `make_scenarios/1_content_generator.json`
2. `make_scenarios/2_video_renderer.json`
3. `make_scenarios/3_tiktok_poster.json`
4. `make_scenarios/4_analytics_monitor.json`

After import:
- [ ] Reconnect all modules to your connections
- [ ] Update `amazon_affiliate_tag` to your tag
- [ ] Update `tiktok_username` to your username
- [ ] Set ElevenLabs voice_id (default: Sarah `EXAVITQu4vr4xnSDxMaL`)

### 4. Test Pipeline

```sql
-- Verify starter data loaded
SELECT COUNT(*) FROM tiktok_queue; -- Should be 20

-- Test with first 3 rows
SELECT id, topic, status FROM tiktok_queue LIMIT 3;
```

1. Run Scenario 1 manually → check `status = 'script_ready'`
2. Run Scenario 2 manually → check `status = 'video_ready'`
3. Run Scenario 3 manually → check `status = 'posted'`
4. Verify video appears on TikTok

### 5. Enable Scheduling

| Scenario | Schedule |
|----------|----------|
| 1. Generator | 3x daily (5am, 9am, 2pm PST) |
| 2. Renderer | Watch trigger (auto) |
| 3. Poster | Watch trigger (auto) |
| 4. Analytics | 2x weekly (Mon/Thu 9am) |

---

## Key Configuration Values

### Default Voice (ElevenLabs)
```
Voice ID: EXAVITQu4vr4xnSDxMaL (Sarah - friendly female)
Model: eleven_turbo_v2_5
```

### Default Avatar (HeyGen)
```
Avatar ID: josh_lite3_20230714 (faceless/background)
Dimensions: 1080x1920 (9:16 vertical)
```

### Amazon Affiliate
```
Tag: fitnessquick-20 (UPDATE TO YOUR TAG)
Link format: https://www.amazon.com/dp/{ASIN}?tag={TAG}
```

### Cross-posting Thresholds
```
YouTube Shorts: >10K views
Pinterest: >5K views
Viral analysis: >50K views
```

---

## Starter Content Topics (20)

**Quick Workouts (5):**
1. 5-min abs for busy moms
2. 3 arm exercises at your desk
3. Morning stretch for posture
4. Booty burn workout anywhere
5. 4 exercises for flat stomach

**Beauty Hacks (5):**
6. Ice roller depuff trick
7. 5-minute makeup look
8. Gua sha face lift technique
9. Hair growth serum application
10. Lip plumping without injections

**Wellness (5):**
11. 30-second breathing for calm
12. Morning water routine
13. Meal prep hack saves 3 hours
14. Sleep posture for back pain
15. Walking burns more than running

**Product Reviews (5):**
16. Amazon finds under $20
17. Gym bag essentials
18. Self-care products
19. Kitchen gadget healthy eating
20. Desk setup WFH productivity

---

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check API key, no extra spaces |
| 403 Supabase | Use service_role key, not anon |
| HeyGen timeout | Increase sleep to 120s |
| TikTok rate limit | Add delays between posts |
| JSON parse error | Claude output malformed, retry |
| Video not posting | Check MP4 format, 9:16, <60s |

---

## Next Steps for Future Sessions

### Immediate (Deploy)
- [ ] Run SQL schema in Supabase
- [ ] Import 4 Make.com scenarios
- [ ] Connect all API keys
- [ ] Test with 3 videos
- [ ] Enable scheduling

### Week 1-2 (Optimize)
- [ ] Monitor first 50 videos
- [ ] Identify top-performing topics
- [ ] Refine Claude prompts based on engagement
- [ ] A/B test different hooks

### Month 1 (Scale)
- [ ] Analyze analytics data
- [ ] Add more niche topics to content bank
- [ ] Set up Amazon product tracking
- [ ] Apply for TikTok Creativity Program (need 10K followers)

### Month 2+ (Expand)
- [ ] Add more affiliate products
- [ ] Explore sponsorship opportunities
- [ ] Consider second TikTok account for different niche
- [ ] Implement UGC repurposing

---

## Repository Reference

**Repo:** github.com/talhahbilal1-arch/social-media-empire
**Branch:** main
**Commit:** 35d3a2b

```bash
# Clone and navigate
git clone https://github.com/talhahbilal1-arch/social-media-empire.git
cd social-media-empire/tiktok_automation
```

---

## Contact Context

This pipeline was built for automated faceless TikTok content creation:
- **Target audience:** U.S. women 25-44
- **Niche:** Fitness, beauty, lifestyle hacks
- **Content style:** Quick tips, product recommendations
- **Monetization:** TikTok Creativity Program + Amazon affiliates
- **Goal:** 5-10 videos/day, $1K+/month by month 4-5

---

*Handoff document generated 2026-02-05*
