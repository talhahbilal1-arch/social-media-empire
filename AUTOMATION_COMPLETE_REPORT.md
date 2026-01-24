# Video-to-Social-Media Automation Pipeline - Complete Report

**Generated:** 2026-01-24
**Updated:** 2026-01-24 (Final Status)
**Status:** Infrastructure Complete - Manual Configuration Required
**Git Commit:** Pushed to main branch on GitHub
**Repository:** https://github.com/talhahbilal1-arch/social-media-empire

---

## Quick Status

| Component | Status | Action Required |
|-----------|--------|-----------------|
| Video Generation | ✅ WORKING | None |
| Karaoke Captions | ✅ WORKING | None |
| Supabase Upload | ✅ WORKING | None |
| Pinterest Posting | ⏳ BLOCKED | Create Make.com webhook |
| YouTube Posting | ⏳ BLOCKED | Run OAuth flow |
| GitHub Actions | ✅ READY | Add secrets after credentials obtained |

---

## Immediate Next Steps

### Step 1: Get YouTube OAuth Credentials (5-10 minutes)

A helper script has been created to simplify this process:

```bash
# First, go to Google Cloud Console and create OAuth credentials
# Then run:
python scripts/get_youtube_oauth.py --client-id YOUR_ID --client-secret YOUR_SECRET
```

Or manually:
1. Go to https://console.cloud.google.com
2. Create/select project, enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app type)
4. Run the helper script with your credentials
5. Add the output to `.env` and GitHub Secrets

### Step 2: Create Make.com Webhook (10-15 minutes)

1. Go to https://us2.make.com
2. Create scenario: "Video to Pinterest"
3. Add Webhook trigger → copy URL
4. Add Router (3 routes for each brand)
5. Add Pinterest "Create Pin" module per route
6. Activate scenario
7. Add webhook URL to `.env` as `MAKE_WEBHOOK_URL`
8. Add to GitHub Secrets

### Step 3: Test Full Pipeline

```bash
# Test with one brand
python cli.py --brand menopause-planner --count 1 --post

# Check results
# - Pinterest: Check your boards
# - YouTube: Check YouTube Studio
```

---

## Executive Summary

The video-to-social-media automation pipeline has been built. All code infrastructure is in place for:
- Generating videos with karaoke-style captions
- Uploading to Supabase storage (working)
- Posting to Pinterest via Make.com webhook (needs webhook URL)
- Posting to YouTube Shorts via API (needs OAuth credentials)

---

## What Was Built

### 1. YouTube Shorts Client
**File:** `src/clients/youtube_shorts.py`

Features:
- OAuth2 authentication using refresh token
- Video upload with resumable uploads (chunked)
- Automatic #Shorts tag addition
- Per-brand configuration (tags, category)
- Quota checking (connectivity test)

```python
from src.clients.youtube_shorts import YouTubeShortsClient

client = YouTubeShortsClient()
result = client.upload_short(
    video_path="path/to/video.mp4",
    title="Amazing Deal!",
    description="Check out this deal...",
    brand="daily-deal-darling"
)
```

### 2. Social Poster Service
**File:** `src/services/social_poster.py`

Features:
- Unified interface for all social platforms
- Supabase upload for video hosting
- Make.com webhook integration for Pinterest
- YouTube Shorts upload
- Automatic hashtag and link insertion per brand
- Emoji support for emotional content

```python
from src.services.social_poster import SocialPoster, VideoMetadata

poster = SocialPoster()
metadata = VideoMetadata(
    brand="menopause-planner",
    title="Health Tip",
    description="Great wellness advice...",
    script="Original script text"
)
results = poster.post_to_all_platforms("video.mp4", metadata)
```

### 3. CLI Updates
**File:** `cli.py`

New flags:
- `--post` - Post to all platforms (Pinterest + YouTube)
- `--post-pinterest` - Post to Pinterest only
- `--post-youtube` - Post to YouTube Shorts only

Examples:
```bash
# Generate and post to all platforms
python cli.py --brand all --count 1 --post

# Generate and post to Pinterest only
python cli.py --brand menopause-planner --count 1 --post-pinterest

# Generate and post to YouTube only
python cli.py --brand daily-deal-darling --count 1 --post-youtube
```

### 4. GitHub Actions Updates
**File:** `.github/workflows/generate-videos.yml`

- Added posting support for scheduled runs
- Three daily runs: 08:00, 14:00, 20:00 UTC
- Automatic posting on schedule (configurable)
- Manual workflow dispatch with posting options

### 5. Settings Updates
**File:** `config/settings.py`

Added environment variables:
- `YOUTUBE_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`
- `MAKE_WEBHOOK_URL`

---

## Configuration Required

### Environment Variables (.env)

```env
# Already configured
GEMINI_API_KEY=your_key
PEXELS_API_KEY=your_key
SUPABASE_URL=https://epfoxpgrpsnhlsglxvsa.supabase.co
SUPABASE_KEY=your_key

# YouTube OAuth (REQUIRED for YouTube uploads)
YOUTUBE_API_KEY=AIzaSyAx6Of31F32vmtkiAQuF3LOzOodDHxRipM
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REFRESH_TOKEN=your_refresh_token

# Make.com Webhook (REQUIRED for Pinterest)
MAKE_WEBHOOK_URL=https://hook.us2.make.com/your_webhook_id
```

### GitHub Secrets Required

Add these secrets to your repository:
1. `YOUTUBE_API_KEY` - Already have: `AIzaSyAx6Of31F32vmtkiAQuF3LOzOodDHxRipM`
2. `YOUTUBE_CLIENT_ID` - From Google Cloud Console
3. `YOUTUBE_CLIENT_SECRET` - From Google Cloud Console
4. `YOUTUBE_REFRESH_TOKEN` - From OAuth flow
5. `MAKE_WEBHOOK_URL` - From Make.com scenario

---

## Manual Setup Required

### 1. Make.com Scenario Setup (Pinterest)

**BLOCKER:** Chrome browser extension was not connected. Manual setup required.

**Steps to complete:**

1. Go to https://us2.make.com
2. Create new scenario: "Video to Pinterest - All Brands"
3. Add modules:

   **Module 1: Webhook (Trigger)**
   - Type: Custom Webhook
   - Name: "video-upload-trigger"
   - Copy the webhook URL

   **Module 2: Router**
   - Route 1: brand = "menopause-planner"
   - Route 2: brand = "daily-deal-darling"
   - Route 3: brand = "fitness-made-easy"

   **Module 3: Pinterest - Create Pin (per route)**
   - Connection: Select Pinterest account
   - Board: Select appropriate board
   - Pin Type: Video
   - Video URL: `{{1.video_url}}`
   - Title: `{{1.title}}`
   - Description: `{{1.description}}`
   - Link: `{{1.link}}`

4. Save and activate scenario
5. Copy webhook URL to:
   - `.env` file as `MAKE_WEBHOOK_URL`
   - GitHub Secrets as `MAKE_WEBHOOK_URL`

**Webhook Payload Format:**
```json
{
  "brand": "menopause-planner",
  "video_url": "https://supabase.../video.mp4",
  "title": "Generated pin title",
  "description": "Description with hashtags",
  "link": "https://etsy.com/shop/TheMenopausePlanner",
  "tags": ["tag1", "tag2"],
  "timestamp": "2026-01-24T12:00:00Z"
}
```

### 2. YouTube OAuth Setup

**Steps to complete:**

1. Go to Google Cloud Console
2. Create/select project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Download client secrets

5. Get refresh token using this script:
```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json', SCOPES
)
credentials = flow.run_local_server(port=8080)

print(f"Refresh Token: {credentials.refresh_token}")
```

6. Add to environment:
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

---

## Test Results

### Successful Tests

| Component | Status | Notes |
|-----------|--------|-------|
| Video Generation | ✅ SUCCESS | Karaoke captions working |
| Supabase Upload | ✅ SUCCESS | Videos uploaded correctly |
| CLI --post flag | ✅ SUCCESS | Integration working |
| Pipeline Flow | ✅ SUCCESS | End-to-end flow works |

### Pending Tests (Need Configuration)

| Component | Status | Blocker |
|-----------|--------|---------|
| Pinterest Posting | ⏳ PENDING | Need Make.com webhook URL |
| YouTube Posting | ⏳ PENDING | Need OAuth credentials |

---

## Brand Configuration

### Menopause Planner
- Pinterest Account: TheMenopausePlanner
- Link: https://www.etsy.com/shop/TheMenopausePlanner
- Hashtags: #menopause #womenshealth #over40 #wellness #healthtips
- YouTube Category: Howto & Style (26)

### Daily Deal Darling
- Pinterest Account: DailyDealDarling
- Link: https://dailydealdarling.com
- Hashtags: #deals #savings #shopping #budget #frugalliving
- YouTube Category: Howto & Style (26)

### Fitness Made Easy
- Pinterest Account: (needs setup)
- Link: https://fitnessmadeeasy.com
- Hashtags: #fitness #workout #health #exercise #motivation
- YouTube Category: Sports (17)

---

## Daily Automation Schedule

| Time (UTC) | Action |
|------------|--------|
| 08:00 | Generate + post videos for all 3 brands |
| 14:00 | Generate + post videos for all 3 brands |
| 20:00 | Generate + post videos for all 3 brands |

**Expected daily output:** 9 videos (3 brands × 3 times)

---

## Files Modified/Created

### Created
- `src/clients/youtube_shorts.py` - YouTube Shorts upload client
- `src/services/social_poster.py` - Social media posting service
- `scripts/get_youtube_oauth.py` - Helper script to obtain YouTube OAuth refresh token
- `AUTOMATION_COMPLETE_REPORT.md` - This report

### Modified
- `cli.py` - Added --post flags
- `config/settings.py` - Added new environment variables
- `.env` - Added YouTube and Make.com placeholders
- `.github/workflows/generate-videos.yml` - Added posting support
- `src/services/__init__.py` - Added social poster exports
- `src/orchestration/video_generator.py` - Added script to result
- `requirements.txt` - Added Google API packages for YouTube integration

---

## Next Steps (Priority Order)

1. **Set up Make.com scenario** (Pinterest)
   - Create scenario in Make.com
   - Get webhook URL
   - Add to `.env` and GitHub Secrets

2. **Set up YouTube OAuth** (use helper script)
   - Create OAuth credentials in Google Cloud Console
   - Run: `python scripts/get_youtube_oauth.py --client-id YOUR_ID --client-secret YOUR_SECRET`
   - Script will open browser for authorization and output credentials
   - Add credentials to `.env` and GitHub Secrets

3. **Test full pipeline**
   ```bash
   python cli.py --brand menopause-planner --count 1 --post
   ```

4. **Verify posts went live**
   - Check Pinterest for new pin
   - Check YouTube for new Short

5. **Enable scheduled runs**
   - Verify GitHub Actions has all secrets
   - Monitor first scheduled run

---

## Troubleshooting

### Pinterest Posting Fails
- Check `MAKE_WEBHOOK_URL` is set
- Verify Make.com scenario is active
- Check Make.com execution history for errors

### YouTube Posting Fails
- Check all OAuth credentials are set
- Verify refresh token is valid (may need to regenerate)
- Check YouTube quota limits

### Supabase Upload Fails
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check if 'videos' bucket exists and is public

---

## Code Architecture

```
social-media-empire/
├── src/
│   ├── clients/
│   │   ├── youtube_shorts.py    # YouTube API client
│   │   └── ...
│   ├── services/
│   │   ├── social_poster.py     # Unified posting service
│   │   └── ...
│   └── orchestration/
│       └── video_generator.py   # Updated with script in result
├── config/
│   └── settings.py              # Updated with new env vars
├── cli.py                       # Updated with --post flags
└── .github/workflows/
    └── generate-videos.yml      # Updated with posting support
```

---

## Maintenance

### Adding a New Platform

1. Create client in `src/clients/`
2. Add posting method to `SocialPoster`
3. Update CLI with new `--post-<platform>` flag
4. Add credentials to Settings and GitHub Secrets

### Changing Posting Schedule

Edit `.github/workflows/generate-videos.yml`:
```yaml
schedule:
  - cron: '0 8 * * *'   # Change times here
  - cron: '0 14 * * *'
  - cron: '0 20 * * *'
```

---

## Support

If issues arise:
1. Check logs in GitHub Actions
2. Test locally with `python cli.py --brand <brand> --count 1 --post`
3. Verify all environment variables are set
4. Check Make.com execution history
5. Check YouTube Studio for upload errors

---

**Report Complete**

The automation infrastructure is fully built. Complete the manual configuration steps above to activate full Pinterest and YouTube posting.
