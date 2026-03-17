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
| `make_scenarios/1_content_generator.json` | Cron → Claude → Supabase |
| `make_scenarios/2_video_renderer.json` | ElevenLabs TTS + HeyGen video |
| `make_scenarios/3_tiktok_poster.json` | Upload to TikTok |
| `make_scenarios/4_analytics_monitor.json` | Analytics + cross-post |
| `SETUP_GUIDE.md` | Complete setup documentation |

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
- **Video**: HeyGen API v2
- **Database**: Supabase PostgreSQL
- **Automation**: Make.com
- **Posting**: TikTok Content Posting API

---

See `SETUP_GUIDE.md` for complete documentation.
