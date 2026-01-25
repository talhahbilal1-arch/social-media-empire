# PROMPT FOR CLAUDE CODE - COMPLETE SOCIAL MEDIA AUTOMATION

Copy everything below this line and paste it into a new Claude Code terminal:

---

## PROJECT CONTEXT

I have a Social Media Empire project that automatically generates videos with AI and posts them to Pinterest and YouTube. The code infrastructure is 100% complete but I need help configuring the external services (Make.com webhook for Pinterest, YouTube OAuth credentials).

**Repository:** /Users/homefolder/social-media-empire
**GitHub:** https://github.com/talhahbilal1-arch/social-media-empire

## WHAT'S ALREADY BUILT (DO NOT REBUILD)

1. **Video Generation Pipeline** - Generates 30-second vertical videos with karaoke-style captions using Gemini AI for scripts, Pexels for stock footage, and MoviePy for rendering

2. **YouTube Shorts Client** (`src/clients/youtube_shorts.py`) - Full OAuth2 implementation with refresh token support, resumable uploads, per-brand configuration

3. **Social Poster Service** (`src/services/social_poster.py`) - Unified interface that:
   - Uploads videos to Supabase storage (WORKING)
   - Posts to Pinterest via Make.com webhook (needs webhook URL)
   - Posts to YouTube Shorts via API (needs OAuth credentials)

4. **CLI with posting flags** (`cli.py`):
   - `--post` posts to all platforms
   - `--post-pinterest` posts to Pinterest only
   - `--post-youtube` posts to YouTube only

5. **GitHub Actions** (`.github/workflows/generate-videos.yml`) - Runs 3x daily at 08:00, 14:00, 20:00 UTC

6. **Helper Scripts**:
   - `scripts/get_youtube_oauth.py` - Gets YouTube refresh token
   - `scripts/setup_credentials.py` - Adds credentials to .env

## CURRENT .ENV STATUS

```
GEMINI_API_KEY=✅ SET (working)
PEXELS_API_KEY=✅ SET (working)
SUPABASE_URL=✅ SET (working)
SUPABASE_KEY=✅ SET (working)
YOUTUBE_API_KEY=✅ SET
YOUTUBE_CLIENT_ID=❌ MISSING - need from Google Cloud Console
YOUTUBE_CLIENT_SECRET=❌ MISSING - need from Google Cloud Console
YOUTUBE_REFRESH_TOKEN=❌ MISSING - need from OAuth flow
MAKE_WEBHOOK_URL=❌ MISSING - need from Make.com scenario
```

## YOUR TASKS - COMPLETE IN ORDER

### TASK 1: CREATE MAKE.COM WEBHOOK SCENARIO

Use Chrome browser automation to:

1. Navigate to https://us2.make.com
2. Log in if needed (user should already be logged in)
3. Click "Create a new scenario"
4. Add a **Webhook** module:
   - Click the (+) in center
   - Search "Webhooks" → Select "Custom webhook"
   - Click "Add" → Name it "video-pinterest-trigger"
   - Click "Save"
   - **COPY THE WEBHOOK URL** (format: https://hook.us2.make.com/...)

5. Add a **Router** module:
   - Click (+) after webhook
   - Search "Router" (under Flow Control)
   - Add it

6. Configure **Route 1 - Menopause Planner**:
   - Click the route line → "Set up a filter"
   - Label: "Menopause Planner"
   - Condition: `brand` (from webhook) Equal to `menopause-planner`
   - Click (+) after filter → Search "Pinterest" → "Create a Pin"
   - Connect Pinterest account (TheMenopausePlanner)
   - Board: Select any board
   - Title: Map to `{{1.title}}`
   - Description: Map to `{{1.description}}`
   - Link: `https://www.etsy.com/shop/TheMenopausePlanner`
   - Media source: URL → `{{1.video_url}}`

7. Configure **Route 2 - Daily Deal Darling**:
   - Click (+) on router to add second route
   - Set filter: `brand` Equal to `daily-deal-darling`
   - Add Pinterest "Create a Pin" module
   - Connect Pinterest account (DailyDealDarling)
   - Same mapping as above but Link: `https://dailydealdarling.com`

8. Save scenario (bottom left)
9. Turn scenario ON (toggle top left)
10. Copy the webhook URL

11. **Add to .env file:**
```bash
# In the project directory, update .env:
MAKE_WEBHOOK_URL=https://hook.us2.make.com/YOUR_WEBHOOK_ID
```

### TASK 2: GET YOUTUBE OAUTH CREDENTIALS

Use Chrome browser automation to:

1. Navigate to https://console.cloud.google.com
2. Select existing project or create new one
3. Go to "APIs & Services" → "Library"
4. Search "YouTube Data API v3" → Enable it if not already

5. Go to "APIs & Services" → "Credentials"
6. Click "Create Credentials" → "OAuth client ID"
7. If prompted for consent screen:
   - User Type: External
   - App name: "Video Automation"
   - Support email: user's email
   - Save and continue through steps
8. Application type: Desktop app
9. Name: "Video Automation"
10. Click Create
11. **COPY Client ID and Client Secret**

12. Navigate to https://developers.google.com/oauthplayground
13. Click gear icon (⚙️) top right
14. Check "Use your own OAuth credentials"
15. Enter the Client ID and Client Secret you just copied
16. Close settings

17. In left panel, find "YouTube Data API v3"
18. Check these scopes:
    - `https://www.googleapis.com/auth/youtube.upload`
    - `https://www.googleapis.com/auth/youtube`
19. Click "Authorize APIs"
20. Sign in with the Google account that owns the YouTube channel
21. Allow all permissions
22. Click "Exchange authorization code for tokens"
23. **COPY the Refresh Token**

24. **Add to .env file:**
```bash
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here
```

### TASK 3: TEST THE AUTOMATION

After both credentials are configured, run these tests:

```bash
cd /Users/homefolder/social-media-empire
source venv/bin/activate

# Test 1: Verify credentials are loaded
python -c "
from src.services.social_poster import SocialPoster
import os
poster = SocialPoster()
print('Supabase:', 'OK' if poster._supabase else 'FAIL')
print('YouTube:', 'OK' if poster.youtube_client else 'FAIL')
print('Pinterest:', 'OK' if poster.make_webhook_url else 'FAIL')
"

# Test 2: Test Pinterest posting (generates video + posts)
python cli.py --brand menopause-planner --count 1 --post-pinterest

# Test 3: Test YouTube posting (generates video + posts)
python cli.py --brand menopause-planner --count 1 --post-youtube

# Test 4: Test full pipeline (both platforms)
python cli.py --brand menopause-planner --count 1 --post
```

### TASK 4: FIX ANY ERRORS

If tests fail:

**Pinterest errors:**
- Check Make.com scenario is turned ON
- Check webhook URL is correct in .env (no quotes, no trailing spaces)
- Check Make.com execution history for error details

**YouTube errors:**
- Verify all 3 credentials are set (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
- If "invalid_grant" error: refresh token expired, regenerate via OAuth Playground
- Check YouTube quota at https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

**Import errors:**
```bash
pip install google-api-python-client google-auth-oauthlib
```

### TASK 5: ADD GITHUB SECRETS

After tests pass, use Chrome to:

1. Navigate to https://github.com/talhahbilal1-arch/social-media-empire/settings/secrets/actions
2. Click "New repository secret" for each:

| Name | Value |
|------|-------|
| MAKE_WEBHOOK_URL | The webhook URL from Make.com |
| YOUTUBE_CLIENT_ID | The OAuth Client ID |
| YOUTUBE_CLIENT_SECRET | The OAuth Client Secret |
| YOUTUBE_REFRESH_TOKEN | The Refresh Token |

### TASK 6: UPDATE DOCUMENTATION

After everything works:

1. Update `AUTOMATION_COMPLETE_REPORT.md` with:
   - Change status from "Pending" to "Complete" for Pinterest and YouTube
   - Add the test results
   - Note any issues encountered and how they were fixed

2. Commit and push:
```bash
git add -A
git commit -m "feat: complete automation setup with Make.com and YouTube OAuth"
git push origin main
```

## SUCCESS CRITERIA

The automation is complete when:

1. ✅ `python cli.py --brand menopause-planner --count 1 --post-pinterest` successfully creates a Pinterest pin
2. ✅ `python cli.py --brand menopause-planner --count 1 --post-youtube` successfully uploads a YouTube Short
3. ✅ `python cli.py --brand menopause-planner --count 1 --post` successfully posts to BOTH platforms
4. ✅ All 4 GitHub secrets are added
5. ✅ Documentation is updated

## WEBHOOK PAYLOAD FORMAT (FOR REFERENCE)

The code sends this JSON to Make.com:
```json
{
  "brand": "menopause-planner",
  "video_url": "https://epfoxpgrpsnhlsglxvsa.supabase.co/storage/v1/object/public/videos/...",
  "title": "AI-generated title",
  "description": "Description with hashtags #menopause #wellness",
  "link": "https://www.etsy.com/shop/TheMenopausePlanner",
  "tags": ["menopause", "wellness", "health"],
  "timestamp": "2026-01-24T12:00:00Z"
}
```

## BRANDS CONFIGURATION

| Brand | Pinterest Account | Destination Link |
|-------|------------------|------------------|
| menopause-planner | TheMenopausePlanner | https://www.etsy.com/shop/TheMenopausePlanner |
| daily-deal-darling | DailyDealDarling | https://dailydealdarling.com |
| fitness-made-easy | (not yet set up) | https://fitnessmadeeasy.com |

## IMPORTANT FILES

- `.env` - Environment variables (add credentials here)
- `src/services/social_poster.py` - Main posting logic
- `src/clients/youtube_shorts.py` - YouTube upload client
- `cli.py` - Command line interface with --post flags
- `AUTOMATION_COMPLETE_REPORT.md` - Full documentation
- `MANUAL_SETUP_GUIDE.md` - Step-by-step manual instructions

## START NOW

1. First, use Chrome browser automation (mcp__claude-in-chrome__*) to complete Task 1
2. Then complete Task 2
3. Then run all tests in Task 3
4. Fix any errors (Task 4)
5. Add GitHub secrets (Task 5)
6. Update docs and commit (Task 6)

Do not stop until all success criteria are met. If browser automation doesn't work, inform me immediately.
