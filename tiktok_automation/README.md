# TikTok Faceless Video Pipeline

Automated faceless TikTok content creation for fitness/beauty/lifestyle niche targeting U.S. women 25-44.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TIKTOK AUTOMATION PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Scenario 1 │    │  Scenario 2 │    │  Scenario 3 │    │  Scenario 4 │  │
│  │  GENERATOR  │───▶│  RENDERER   │───▶│   POSTER    │───▶│  MONITOR    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        │                  │                  │                  │          │
│        ▼                  ▼                  ▼                  ▼          │
│   ┌─────────┐       ┌──────────┐       ┌─────────┐       ┌──────────┐     │
│   │ Claude  │       │ElevenLabs│       │ TikTok  │       │Analytics │     │
│   │   API   │       │ + HeyGen │       │   API   │       │+ CrossPost│    │
│   └─────────┘       └──────────┘       └─────────┘       └──────────┘     │
│        │                  │                  │                  │          │
│        └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                        │
│                             ┌──────▼──────┐                                │
│                             │  SUPABASE   │                                │
│                             │ tiktok_queue│                                │
│                             └─────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Database Setup
```bash
# Run in Supabase SQL Editor
cat database/tiktok_schema.sql
```

### 2. Import Make.com Scenarios
Import in order:
1. `make_scenarios/1_content_generator.json`
2. `make_scenarios/2_video_renderer.json`
3. `make_scenarios/3_tiktok_poster.json`
4. `make_scenarios/4_analytics_monitor.json`

### 3. Configure Connections
See `SETUP_GUIDE.md` for detailed API setup.

## Files

| File | Purpose |
|------|---------|
| `database/tiktok_schema.sql` | Supabase tables + 20 starter topics |
| `tiktok_pipeline.py` | Content generation (Claude → ElevenLabs → Pexels) |
| `tiktok_poster.py` | Posts video_ready items to TikTok via Content Posting API |
| `manual_posting_guide.py` | Formats videos for manual TikTok upload (fallback) |
| `make_scenarios/1_content_generator.json` | Make.com reference: Cron → Claude → Supabase |
| `make_scenarios/2_video_renderer.json` | Make.com reference: ElevenLabs TTS + HeyGen |
| `make_scenarios/3_tiktok_poster.json` | Make.com reference: Upload to TikTok |
| `make_scenarios/4_analytics_monitor.json` | Make.com reference: Analytics + cross-post |
| `SETUP_GUIDE.md` | Complete setup documentation |
| `POSTING_GUIDE.md` | TikTok posting pipeline setup & troubleshooting |
| `HANDOFF.md` | Project handoff & next steps |

## Workflow Status Flow

```
pending → script_ready → audio_ready → video_ready → posted
                                   ↓
                                failed (retry_count++)
```

## Target Metrics

| Metric | Goal |
|--------|------|
| Videos/day | 5-10 |
| Cost/month | <$65 |
| Revenue/month | $1,000+ |
| Break-even | Week 4-5 |

## Revenue Streams

1. **TikTok Creativity Program**: $0.25/1K views
2. **Amazon Affiliates**: 4-8% commission
3. **Cross-post monetization**: YouTube, Pinterest

## Tech Stack

- **Content**: Claude claude-sonnet-4-20250514
- **Voice**: ElevenLabs Turbo v2.5
- **Video**: HeyGen API v2 or Pexels (stock video)
- **Database**: Supabase PostgreSQL
- **Automation**: GitHub Actions + Python scripts
- **Posting**: TikTok Content Posting API (async via polling)

## Posting Pipeline (NEW)

### Automated Posting
```bash
# Scheduled: Daily 6 PM UTC
python3 tiktok_automation/tiktok_poster.py --max 5
```

Features:
- Reads `video_ready` items from `tiktok_queue`
- Posts to TikTok via Content Posting API
- Polls for completion (up to 5 minutes)
- Updates database with post IDs
- Requires `TIKTOK_ACCESS_TOKEN` secret

Workflow: `.github/workflows/tiktok-poster.yml` (daily at 6 PM UTC)

### Manual Posting (Fallback)
```bash
# Generate batch for manual upload
python3 tiktok_automation/manual_posting_guide.py
```

Use when `TIKTOK_ACCESS_TOKEN` unavailable:
1. Format videos with captions & hashtags
2. Upload manually via TikTok app
3. Update Supabase after posting

See `POSTING_GUIDE.md` for complete details.

---

## Getting Started

**New to TikTok posting?** Start here:
1. Read `POSTING_GUIDE.md` for full setup
2. Ensure Supabase secondary project is configured
3. Add `TIKTOK_ACCESS_TOKEN` to GitHub Secrets (optional)
4. Workflow runs automatically daily at 6 PM UTC

**Without API token?** Use manual posting:
```bash
python3 tiktok_automation/manual_posting_guide.py --output batch.json
# Then upload videos manually from the batch file
```

See `SETUP_GUIDE.md` and `POSTING_GUIDE.md` for complete documentation.
