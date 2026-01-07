# Agent 2: Video Distribution Setup

**Date:** January 6, 2026
**Status:** Partially Complete - Manual Steps Required

---

## COMPLETED

### 1. YouTube OAuth Client Code
- Created `core/youtube_client.py` with full OAuth 2.0 flow
- Updated `agents/multi_platform_poster.py` to use YouTube client
- Code supports video upload to YouTube Shorts

### 2. Google Cloud Project Created
- Project Name: `social-media-empire`
- YouTube Data API v3: Enabled
- OAuth Consent Screen: Configuration started

---

## MANUAL STEPS REQUIRED

### YouTube OAuth Setup (Continue in Google Cloud Console)

1. **Complete OAuth Consent Screen Configuration**
   - Go to: https://console.cloud.google.com/auth/overview?project=social-media-empire
   - App name: Social Media Empire
   - User support email: talhahbilal1@gmail.com
   - Select "External" user type
   - Add scopes:
     - `https://www.googleapis.com/auth/youtube.upload`
     - `https://www.googleapis.com/auth/youtube`
   - Add test users (your email)

2. **Create OAuth 2.0 Credentials**
   - Go to: https://console.cloud.google.com/apis/credentials?project=social-media-empire
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: Desktop app
   - Name: Social Media Empire Desktop
   - Download `client_secret.json`

3. **Get Refresh Token**
   - Place `client_secret.json` in the project root
   - Run: `python core/youtube_client.py`
   - Follow browser prompts to authorize
   - Copy the output credentials

4. **Add to GitHub Secrets**
   - Go to: https://github.com/talhahbilal1-arch/social-media-empire/settings/secrets/actions
   - Add these secrets:
     - `YOUTUBE_CLIENT_ID` - from OAuth credentials
     - `YOUTUBE_CLIENT_SECRET` - from OAuth credentials
     - `YOUTUBE_REFRESH_TOKEN` - from step 3

---

## Repurpose.io Setup (Manual)

**Why Manual:** Account creation requires human verification. I cannot create accounts.

### Setup Steps:

1. **Sign Up**
   - Go to: https://repurpose.io
   - Start free trial
   - Email: Use your business email

2. **Connect Source (Where Videos Come From)**
   - Option A: Dropbox folder (recommended)
   - Option B: Google Drive folder
   - Option C: Direct URL webhook

3. **Connect Destinations**
   - TikTok: Daily Deal Darling account
   - Instagram: Daily Deal Darling account
   - Connect via OAuth (follow prompts)

4. **Create Workflow**
   ```
   Source: [Your chosen source]
       ↓
   Destination 1: TikTok (auto-post)
       ↓
   Destination 2: Instagram Reels (auto-post)
   ```

5. **Video Source Integration**
   - Our videos are stored in Supabase `videos` table
   - Video Factory creates videos via Creatomate
   - Videos have `output_url` field with downloadable link

   **Option A - Manual Upload:**
   - Download videos from Supabase
   - Upload to Repurpose.io source folder

   **Option B - Webhook Integration:**
   - Set up Repurpose.io webhook URL
   - Modify Video Factory to POST to webhook after render

---

## Code Changes Made

### New File: `core/youtube_client.py`
- OAuth 2.0 token management
- Video upload with resumable upload protocol
- Automatic #Shorts tag addition
- Refresh token helper script

### Modified: `agents/multi_platform_poster.py`
- Import YouTubeClient
- Check `oauth_configured` instead of API key
- Full video upload via OAuth
- Adds affiliate links to description

---

## Testing YouTube Upload

Once GitHub Secrets are configured:

1. **Manual Test:**
   ```bash
   cd /path/to/social-media-empire
   export YOUTUBE_CLIENT_ID="your_client_id"
   export YOUTUBE_CLIENT_SECRET="your_client_secret"
   export YOUTUBE_REFRESH_TOKEN="your_refresh_token"
   python -c "from core.youtube_client import YouTubeClient; c = YouTubeClient(); print('Configured:', c.oauth_configured)"
   ```

2. **GitHub Action Test:**
   - Go to Actions > Multi-Platform Poster
   - Click "Run workflow"
   - Check logs for YouTube upload results

---

## Current Posting Flow

```
Video Factory (8 AM UTC)
    ↓
Creates videos via Creatomate
    ↓
Stores in Supabase `videos` table
    ↓
Multi-Platform Poster (9 AM, 1 PM, 9 PM UTC)
    ↓
├── Pinterest: Via Make.com webhooks (WORKING)
├── YouTube Shorts: Via OAuth (NEEDS SECRETS)
└── TikTok/Instagram: Via Repurpose.io (NEEDS SETUP)
```

---

## Cost Estimates

| Service | Cost | Notes |
|---------|------|-------|
| Repurpose.io | $0-20/mo | Free tier: 10 videos/mo |
| YouTube API | Free | 10,000 quota units/day |
| TikTok API | N/A | Via Repurpose.io |
| Instagram API | N/A | Via Repurpose.io |

---

## Files Changed

1. `core/youtube_client.py` - NEW
2. `agents/multi_platform_poster.py` - MODIFIED
3. `tasks/agent2-video-distribution.md` - NEW (this file)

---

## Next Steps

1. [ ] Complete YouTube OAuth setup in Google Cloud Console
2. [ ] Add YouTube secrets to GitHub
3. [ ] Test YouTube Shorts upload
4. [ ] Sign up for Repurpose.io
5. [ ] Connect TikTok and Instagram accounts
6. [ ] Create auto-posting workflow
7. [ ] Test full video distribution pipeline
