# TikTok Faceless Video Pipeline - Complete Setup Guide

Production-ready Make.com automation for faceless TikTok content targeting U.S. women 25-44 in fitness/beauty/lifestyle.

## Quick Start Checklist

- [ ] Run SQL schema in Supabase
- [ ] Configure API connections
- [ ] Import 4 Make.com scenarios
- [ ] Test with 3 rows end-to-end
- [ ] Enable scheduling

---

## 1. Supabase Setup

### Step 1: Run the Schema

1. Open Supabase Dashboard → SQL Editor
2. Copy entire contents of `database/tiktok_schema.sql`
3. Click **Run** - creates tables, indexes, RLS policies, and 20 starter rows

### Step 2: Get Service Role Key

**CRITICAL: Use service_role key, NOT anon key**

1. Supabase Dashboard → Settings → API
2. Copy **service_role** key (starts with `eyJ...`)
3. Copy Project URL (e.g., `https://xxxxx.supabase.co`)

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 3: Verify Tables

Run this query to verify setup:

```sql
SELECT
    (SELECT COUNT(*) FROM tiktok_queue) as queue_rows,
    (SELECT COUNT(*) FROM tiktok_analytics) as analytics_rows,
    (SELECT COUNT(*) FROM tiktok_prompts) as prompts_rows;
-- Expected: 20, 0, 0
```

---

## 2. ElevenLabs Setup

### Step 1: Get API Key

1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up/Login → Profile icon → Profile + API Key
3. Copy API Key

### Step 2: Choose Voice

Recommended voices for fitness/beauty niche:

| Voice ID | Name | Style | Best For |
|----------|------|-------|----------|
| `EXAVITQu4vr4xnSDxMaL` | Sarah | Friendly, warm | Default - general content |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Professional | Tutorial content |
| `AZnzlk1XvdvUeBnXmlld` | Domi | Energetic | Workout motivation |
| `MF3mGyEYCl7XYWbV9V6O` | Elli | Young, upbeat | Beauty/trends |

### Step 3: Clone Custom Voice (Optional)

For unique branding:

1. ElevenLabs → Voices → Add Voice → Voice Cloning
2. Upload 1-5 minutes of clear audio
3. Get the Voice ID from voice settings

### Pricing

| Plan | Characters/month | Cost | ~Videos |
|------|------------------|------|---------|
| Free | 10,000 | $0 | ~20 |
| Starter | 30,000 | $5/mo | ~60 |
| Creator | 100,000 | $22/mo | ~200 |
| Pro | 500,000 | $99/mo | ~1000 |

Average script: ~500 characters = 30 seconds of audio

---

## 3. HeyGen Setup

### Step 1: Get API Key

1. Go to [app.heygen.com](https://app.heygen.com)
2. Settings → API Access
3. Copy API Key

### Step 2: Choose Faceless Template

**Recommended for faceless content:**

| Template Type | Use Case |
|--------------|----------|
| Stock footage background | Generic wellness |
| Animated graphics | Product showcases |
| Split-screen text | List-style content |
| Gradient backgrounds | Minimalist aesthetic |

### Step 3: Create Custom Template (Optional)

1. HeyGen → Templates → Create
2. Design 9:16 vertical layout
3. Add text placeholders for:
   - Title (top)
   - Key points (middle)
   - CTA (bottom)
4. Save and copy Template ID

### Faceless Avatar Options

For non-talking-head videos:

```json
{
  "avatar_id": "josh_lite3_20230714",
  "avatar_style": "background_only"
}
```

Or use **Audio-only** mode:
```json
{
  "character": {
    "type": "audio_only"
  },
  "background": {
    "type": "video",
    "url": "https://your-stock-footage.mp4"
  }
}
```

### Pricing

| Plan | Credits/month | Cost | ~Videos |
|------|---------------|------|---------|
| Free | 1 credit | $0 | 1 |
| Creator | 15 credits | $24/mo | 15 |
| Business | 30 credits | $72/mo | 30 |
| Enterprise | Custom | Contact | Custom |

1 credit = 1 minute of video

---

## 4. TikTok Developer Setup

### Step 1: Apply for Content Posting API

1. Go to [developers.tiktok.com](https://developers.tiktok.com)
2. Create Developer Account
3. Create App → Select scopes:
   - `video.upload`
   - `video.publish`
   - `video.list` (for analytics)
4. Submit for approval (1-5 business days)

### Step 2: Configure OAuth

1. Set Redirect URI: `https://www.make.com/oauth/tiktok/callback`
2. Note your Client Key and Client Secret

### Step 3: Connect in Make.com

1. Make.com → Add TikTok module
2. Create connection using OAuth
3. Authorize with your TikTok Business Account

### Content Posting Requirements

| Requirement | Specification |
|-------------|---------------|
| Format | MP4 |
| Aspect Ratio | 9:16 (vertical) |
| Duration | 3-60 seconds |
| Max Size | 287.6 MB |
| Resolution | 720p minimum |

### Rate Limits

| Tier | Posts/day | Videos/month |
|------|-----------|--------------|
| Basic | 20 | 600 |
| Advanced | 100 | 3,000 |
| Partner | Custom | Custom |

---

## 5. Make.com Scenario Import

### Step 1: Create Connections

Before importing, create these connections in Make.com:

1. **Supabase** (HTTP with API Key):
   - Type: API Key Auth
   - Header: `apikey`
   - Value: Your service_role key

2. **Anthropic** (HTTP with API Key):
   - Header: `x-api-key`
   - Value: Your Claude API key

3. **ElevenLabs** (HTTP with API Key):
   - Header: `xi-api-key`
   - Value: Your ElevenLabs API key

4. **HeyGen** (HTTP with API Key):
   - Header: `X-Api-Key`
   - Value: Your HeyGen API key

5. **TikTok** (OAuth):
   - Use Make.com's TikTok module

### Step 2: Import Scenarios

For each scenario in `make_scenarios/`:

1. Make.com → Create new scenario
2. Click ⋮ menu → Import Blueprint
3. Upload JSON file
4. **Important:** Reconnect all modules to your connections

### Import Order

1. `1_content_generator.json` - Generates scripts
2. `2_video_renderer.json` - Creates videos
3. `3_tiktok_poster.json` - Posts to TikTok
4. `4_analytics_monitor.json` - Tracks and optimizes

### Step 3: Update Variables

In each scenario, update:

```
supabase_url → Your Supabase URL
supabase_service_key → Your service_role key
elevenlabs_voice_id → Your chosen voice
heygen_avatar_id → Your template/avatar
amazon_affiliate_tag → Your Amazon Associates tag
```

---

## 6. End-to-End Testing

### Test 1: Content Generator

1. Run scenario `1_content_generator` once manually
2. Check Supabase `tiktok_queue` table
3. Verify new rows with `status = 'script_ready'`

**Expected output:**
```json
{
  "topic": "5-min abs for busy moms - no equipment needed",
  "script": "Hey mama, I know you only have 5 minutes...",
  "status": "script_ready"
}
```

### Test 2: Video Renderer

1. Ensure at least 1 row has `status = 'script_ready'`
2. Run scenario `2_video_renderer` manually
3. Wait 2-3 minutes for HeyGen processing
4. Verify `status = 'video_ready'` and `video_url` populated

### Test 3: TikTok Poster

1. Ensure at least 1 row has `status = 'video_ready'`
2. Run scenario `3_tiktok_poster` manually
3. Check TikTok account for new video
4. Verify `status = 'posted'` in database

### Test 4: Full Pipeline

1. Reset 3 test rows:
```sql
UPDATE tiktok_queue
SET status = 'pending',
    script = NULL,
    audio_url = NULL,
    video_url = NULL
WHERE id IN (SELECT id FROM tiktok_queue LIMIT 3);
```

2. Run all scenarios in sequence
3. Verify 3 videos posted to TikTok

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad API key | Check key format, no extra spaces |
| 403 Forbidden | Wrong Supabase key | Use service_role, not anon |
| HeyGen timeout | Video processing slow | Increase sleep duration to 120s |
| TikTok rate limit | Too many posts | Add delays between posts |
| JSON parse error | Claude malformed output | Add retry logic to prompt |

---

## 7. Cost Analysis & ROI

### Monthly Costs (5-10 videos/day)

| Service | Usage | Cost |
|---------|-------|------|
| Make.com Pro | 10,000 ops | $16/mo |
| ElevenLabs Creator | 100K chars | $22/mo |
| HeyGen Creator | 15 credits | $24/mo |
| Claude API | ~300K tokens | ~$3/mo |
| **Total** | | **~$65/mo** |

### Scaling Costs

| Videos/day | Monthly Cost |
|------------|--------------|
| 5 | ~$45 |
| 10 | ~$65 |
| 20 | ~$120 |
| 50 | ~$250 |

### Revenue Projections

**TikTok Creativity Program:**
- Rate: $0.20-$1.00 per 1K views
- Conservative: $0.25/1K

| Scenario | Views/video | Videos/mo | Monthly Revenue |
|----------|-------------|-----------|-----------------|
| Low | 1,000 | 150 | $37.50 |
| Medium | 5,000 | 150 | $187.50 |
| Good | 10,000 | 150 | $375.00 |
| Viral mix | 25,000 avg | 150 | $937.50 |

**Amazon Affiliates:**
- Average conversion: 1-3% of video viewers
- Average commission: $2-10 per sale

| Scenario | Clicks/video | Conversions | Avg Commission | Monthly |
|----------|--------------|-------------|----------------|---------|
| Low | 50 | 0.5 | $3 | $225 |
| Medium | 200 | 2 | $4 | $1,200 |
| Good | 500 | 5 | $5 | $3,750 |

### 60-Day ROI Timeline

| Week | Action | Investment | Revenue |
|------|--------|------------|---------|
| 1-2 | Setup + Testing | $130 | $0 |
| 3-4 | Ramp up (5 vids/day) | $65 | $50-100 |
| 5-6 | Scale (10 vids/day) | $65 | $200-400 |
| 7-8 | Optimize winners | $65 | $500-1000 |
| **Total** | | **$325** | **$750-1500** |

**Break-even: Week 4-5**
**Target $1K/month: Week 8**

---

## 8. Monetization Strategy

### Phase 1: Creativity Program (Now)

1. Apply at [tiktok.com/creators/creator-portal](https://www.tiktok.com/creators/creator-portal)
2. Requirements:
   - 10,000 followers
   - 100,000 views in last 30 days
   - Original content
   - 18+ years old

### Phase 2: Affiliate Marketing (Now)

1. **Amazon Associates**
   - Sign up: [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
   - Create tag: `fitnessquick-20`
   - Add products to `affiliate_products` JSONB column

2. **Link in Bio Strategy**
   - Use Linktree or Stan Store
   - Feature top affiliate products
   - Include email signup

### Phase 3: Sponsored Content (3-6 months)

1. Build media kit with analytics
2. Reach out to fitness/beauty brands
3. Rate: $200-$2000 per sponsored video (50K+ followers)

### Phase 4: UGC for Brands (3-6 months)

1. Repurpose best-performing content
2. Pitch to brands as UGC creator
3. Rate: $150-$500 per video

---

## 9. Optimization Tips

### Content That Performs

**Hook Styles (first 3 seconds):**
- "Stop scrolling if you..."
- "Nobody talks about this..."
- "I wish I knew this sooner..."
- "The hack that changed my [X]..."

**Optimal Video Length:**
- 15-21 seconds: Highest completion rate
- 45-60 seconds: Higher engagement for tutorials

**Best Posting Times (PST):**
- 6:00 AM - Early risers
- 12:00 PM - Lunch break
- 6:00 PM - Post-work
- 9:00 PM - Prime time

### Prompt Optimization

After 2 weeks, run this query to find winning topics:

```sql
SELECT
    topic,
    views,
    likes,
    ROUND((likes + comments + shares)::numeric / NULLIF(views, 0) * 100, 2) as engagement_rate
FROM tiktok_queue
WHERE status = 'posted'
ORDER BY views DESC
LIMIT 10;
```

Use insights to refine Claude prompts in Scenario 1.

### A/B Testing

1. Create prompt variations in `tiktok_prompts` table
2. Assign `test_group = 'A'` or `'B'`
3. Compare performance after 50+ videos each

---

## 10. Troubleshooting

### Scenario Not Triggering

1. Check Make.com scenario is ON
2. Verify Supabase has rows matching filter
3. Check Make.com execution history for errors

### Videos Not Rendering

1. Check ElevenLabs quota
2. Verify HeyGen credits remaining
3. Check audio URL is publicly accessible

### TikTok Upload Failing

1. Verify video is MP4, 9:16, under 60s
2. Check TikTok API quota
3. Ensure OAuth token not expired

### Database Updates Failing

1. Confirm using service_role key
2. Check RLS policies are created
3. Verify table column names match

---

## File Structure

```
tiktok_automation/
├── database/
│   └── tiktok_schema.sql          # Run in Supabase SQL Editor
├── make_scenarios/
│   ├── 1_content_generator.json   # Claude → Supabase
│   ├── 2_video_renderer.json      # ElevenLabs + HeyGen → Supabase
│   ├── 3_tiktok_poster.json       # Supabase → TikTok
│   └── 4_analytics_monitor.json   # Analytics + Cross-posting
└── SETUP_GUIDE.md                 # This file
```

---

## Support Resources

- **Make.com Docs**: [make.com/en/help](https://www.make.com/en/help)
- **ElevenLabs Docs**: [docs.elevenlabs.io](https://docs.elevenlabs.io)
- **HeyGen API Docs**: [docs.heygen.com](https://docs.heygen.com)
- **TikTok API Docs**: [developers.tiktok.com/doc](https://developers.tiktok.com/doc)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)

---

*Last Updated: 2026-02-04*
*Version: 1.0*
