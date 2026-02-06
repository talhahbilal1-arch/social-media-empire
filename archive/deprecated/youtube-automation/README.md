# YouTube Shorts Automation System

Automated pipeline for creating and publishing YouTube Shorts using AI-powered voice and avatar generation.

## Overview

This system automates the entire YouTube Shorts creation workflow:

1. **Script Storage** → Google Sheets holds your pre-written scripts
2. **Voice Generation** → ElevenLabs converts text to your cloned voice
3. **Avatar Video** → D-ID creates lip-synced talking head videos
4. **Publishing** → Late.dev uploads and schedules to YouTube
5. **Orchestration** → n8n runs everything on autopilot

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Google Sheets  │────▶│    ElevenLabs   │────▶│   Google Drive  │
│   (Scripts)     │     │  (Voice Audio)  │     │  (Audio Store)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     YouTube     │◀────│    Late.dev     │◀────│      D-ID       │
│   (Published)   │     │   (Scheduler)   │     │  (Avatar Video) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Prerequisites

- **n8n account** (cloud at n8n.io or self-hosted)
- **ElevenLabs account** with API access ($5+/month)
- **D-ID account** with API credits ($25+/month)
- **Late.dev account** with YouTube connected
- **Google Cloud project** with Sheets & Drive APIs enabled
- **Slack workspace** (optional, for notifications)

## Quick Start

### 1. Clone and Configure

```bash
cd youtube-automation
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

### 2. Test API Connections

```bash
# Set environment variables
export $(cat config/.env | xargs)

# Test each API
python scripts/test_elevenlabs.py
python scripts/test_did.py
python scripts/test_late.py
```

### 3. Set Up Google Sheet

Create a new Google Sheet with a "Scripts" tab containing these columns:

| Column | Type | Description |
|--------|------|-------------|
| row_id | Number | Auto-increment ID |
| title | Text | Video title (<60 chars) |
| script_text | Text | Full script content |
| description | Text | YouTube description |
| hashtags | Text | Space-separated hashtags |
| thumbnail_text | Text | Text for thumbnail |
| status | Text | pending/processing/published |
| created_date | Date | When added |
| published_date | Date | Auto-filled |
| youtube_post_id | Text | Auto-filled |
| video_url | Text | Auto-filled |

### 4. Import n8n Workflow

1. Go to n8n → Workflows → Import from file
2. Upload `n8n/workflow.json`
3. Update credential IDs in each node
4. Set environment variables in n8n Settings → Variables
5. Activate the workflow

### 5. Add Your First Script

Add a row to the Google Sheet:
- title: `Stop Taking Zinc for Testosterone`
- script_text: `[Your script here]`
- description: `[Your description]`
- hashtags: `#testosterone #fitness #health`
- status: `pending`

### 6. Test Run

Trigger the workflow manually via webhook or wait for the scheduled run.

## Detailed Setup

### ElevenLabs Voice Cloning

1. Record 2-3 minutes of yourself speaking naturally
2. Upload to ElevenLabs Voice Lab
3. Create instant voice clone
4. Copy the Voice ID to your `.env`

**Recording Tips:**
- Use a quiet room
- Speak in your natural presenting voice
- Include varied tones and emotions
- Avoid background noise

### D-ID Avatar Setup

1. Take a high-quality headshot:
   - Front-facing, eyes looking at camera
   - Good lighting (natural light preferred)
   - Neutral expression
   - Shoulders visible
   - Solid background

2. Upload via the test script or D-ID dashboard
3. Save the hosted image URL to your `.env`

### Late.dev YouTube Connection

1. Sign up at [late.dev](https://late.dev)
2. Connect your YouTube channel via OAuth
3. Copy your Account ID from the dashboard
4. Generate an API key
5. Add both to your `.env`

### n8n Credential Setup

Create these credentials in n8n:

**HTTP Header Auth - ElevenLabs:**
- Header Name: `xi-api-key`
- Header Value: `[your ElevenLabs API key]`

**HTTP Header Auth - D-ID:**
- Header Name: `Authorization`
- Header Value: `Basic [base64 encoded "apikey:"]`

**HTTP Header Auth - Late.dev:**
- Header Name: `Authorization`
- Header Value: `Bearer [your Late.dev API key]`

**Google Sheets OAuth2:**
- Follow n8n's Google OAuth setup guide

**Google Drive OAuth2:**
- Use same Google Cloud project

**Slack Webhook:**
- Create incoming webhook in Slack

## Environment Variables

### Required

```env
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_cloned_voice_id
DID_API_KEY=your_key_here
DID_AVATAR_IMAGE_URL=https://your-hosted-image.jpg
LATE_API_KEY=your_key_here
LATE_YOUTUBE_ACCOUNT_ID=your_channel_id
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```

### Optional

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
N8N_URL=https://your-n8n-instance.com
ALERT_EMAIL=you@example.com
```

## Daily Operation

### Workflow Schedule

- **8:00 AM**: Workflow runs, processes first pending script
- **Processing**: Audio → Video → Upload (5-10 minutes)
- **12:00 PM next day**: Video goes live on YouTube

### Adding Scripts

1. Write scripts using `templates/script_template.md` as guide
2. Add to Google Sheet with status = `pending`
3. Workflow will process oldest pending script first

### Monitoring

- Check Slack for success/error notifications
- View execution logs in n8n
- Check "Errors" sheet for logged failures

## Troubleshooting

### Audio Not Generating

- Check ElevenLabs API quota
- Verify voice ID exists
- Ensure script_text isn't empty or too long

### Video Stuck Processing

- D-ID renders take 2-5 minutes
- Check D-ID dashboard for errors
- Verify audio URL is publicly accessible

### YouTube Upload Fails

- Verify Late.dev connection is active
- Check video URL is accessible
- Ensure title length < 100 characters
- Check for rate limits

### Workflow Not Triggering

- Verify workflow is active in n8n
- Check schedule trigger settings
- Ensure timezone is correct

## Cost Estimation

Monthly costs for daily video production:

| Service | Usage | Est. Cost |
|---------|-------|-----------|
| ElevenLabs | ~3,000 chars/day | $5-22/month |
| D-ID | ~30 min/month | $25-50/month |
| Late.dev | 30 posts/month | $10-20/month |
| n8n Cloud | 1 workflow | $0-20/month |
| **Total** | | **$40-112/month** |

## Advanced Configuration

### Multiple Videos Per Day

Modify the workflow to loop through multiple pending scripts:
1. Change Google Sheets node to return all pending
2. Add SplitInBatches node
3. Process each script sequentially

### Caption Generation

Add after D-ID video creation:
1. Use AssemblyAI or Whisper for transcription
2. Burn captions with FFmpeg
3. Upload captioned version

### A/B Testing Titles

1. Add `title_variants` column to sheet
2. Randomly select variant
3. Track performance in separate sheet

## Files Reference

```
youtube-automation/
├── config/
│   ├── .env.example      # Environment template
│   └── settings.json     # App configuration
├── scripts/
│   ├── test_elevenlabs.py  # Voice API test
│   ├── test_did.py         # Avatar API test
│   └── test_late.py        # Upload API test
├── n8n/
│   ├── workflow.json       # Main automation workflow
│   └── error-handler.json  # Error notification workflow
├── templates/
│   ├── script_template.md    # Script writing guide
│   └── thumbnail_template.json  # Thumbnail specs
├── assets/
│   └── avatar_photo.jpg    # Your headshot (add this)
├── output/
│   └── .gitkeep            # Test output directory
└── README.md               # This file
```

## Support

- **ElevenLabs**: [docs.elevenlabs.io](https://docs.elevenlabs.io)
- **D-ID**: [docs.d-id.com](https://docs.d-id.com)
- **Late.dev**: [docs.getlate.dev](https://docs.getlate.dev)
- **n8n**: [docs.n8n.io](https://docs.n8n.io)

## License

MIT - Use freely for personal and commercial projects.
