# Manual Setup Guide - Complete Social Media Automation

Since the Chrome browser extension isn't connected, follow these steps manually.

---

## Step 1: Make.com Scenario Setup (10-15 minutes)

### 1.1 Create the Scenario

1. Go to https://us2.make.com
2. Click **"Create a new scenario"**

### 1.2 Add Webhook Trigger

1. Click the large **(+)** in the center
2. Search for **"Webhooks"**
3. Select **"Custom webhook"**
4. Click **"Add"**
5. Name it: `video-pinterest-trigger`
6. Click **"Save"**
7. **COPY THE WEBHOOK URL** (looks like: `https://hook.us2.make.com/abc123...`)

### 1.3 Add Router

1. Click the **(+)** after the webhook module
2. Search for **"Router"** (under Flow Control)
3. Add it

### 1.4 Configure Route 1 - Menopause Planner

1. Click on the first route line coming out of the router
2. Click **"Set up a filter"**
3. Condition: `brand` Equal to `menopause-planner`
4. Click **(+)** after this route
5. Search **"Pinterest"**
6. Select **"Create a Pin"**
7. Connect to your **TheMenopausePlanner** Pinterest account
8. Configure:
   - **Board**: Select your target board
   - **Title**: Click and select `{{1.title}}`
   - **Description**: Click and select `{{1.description}}`
   - **Link**: `https://www.etsy.com/shop/TheMenopausePlanner`
   - **Media URL**: Click and select `{{1.video_url}}`

### 1.5 Configure Route 2 - Daily Deal Darling

1. Click **(+)** on the router to add another route
2. Click the route line → Set filter: `brand` Equal to `daily-deal-darling`
3. Add Pinterest module
4. Connect to **DailyDealDarling** Pinterest account
5. Configure same as above, but with:
   - **Link**: `https://dailydealdarling.com`

### 1.6 Activate

1. Click **"Save"** (bottom left)
2. Toggle the scenario **ON** (top left)
3. Copy your webhook URL if you haven't already

---

## Step 2: YouTube OAuth Setup (15-20 minutes)

### 2.1 Enable YouTube API

1. Go to https://console.cloud.google.com
2. Select your project (or create one)
3. Go to **APIs & Services → Library**
4. Search **"YouTube Data API v3"**
5. Click **Enable** (if not already enabled)

### 2.2 Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**
4. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: "Video Automation"
   - Support email: your email
   - Developer email: your email
   - Save and continue through all steps
5. Back to Credentials → Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Video Automation"
   - Click **Create**
6. **COPY the Client ID and Client Secret**

### 2.3 Get Refresh Token via OAuth Playground

1. Go to https://developers.google.com/oauthplayground
2. Click the **gear icon** (⚙️) in the top right
3. Check **"Use your own OAuth credentials"**
4. Enter your **Client ID** and **Client Secret**
5. Close the settings

6. In the left panel, scroll down to find **"YouTube Data API v3"**
7. Select these scopes:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
8. Click **"Authorize APIs"**
9. Sign in with the Google account that owns your YouTube channel
10. Grant all permissions

11. Click **"Exchange authorization code for tokens"**
12. **COPY the Refresh Token** (it's a long string)

---

## Step 3: Add Credentials to .env

Run the helper script:

```bash
python scripts/setup_credentials.py
```

Or manually edit `.env`:

```env
# Make.com Webhook
MAKE_WEBHOOK_URL=https://hook.us2.make.com/YOUR_WEBHOOK_ID

# YouTube OAuth
YOUTUBE_CLIENT_ID=YOUR_CLIENT_ID
YOUTUBE_CLIENT_SECRET=YOUR_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN=YOUR_REFRESH_TOKEN
```

---

## Step 4: Test the Pipeline

### Test Pinterest Only

```bash
python cli.py --brand menopause-planner --count 1 --post-pinterest
```

Expected: Video generates, uploads to Supabase, triggers Make.com webhook → Pin created

### Test YouTube Only

```bash
python cli.py --brand menopause-planner --count 1 --post-youtube
```

Expected: Video generates, uploads to YouTube as a Short

### Test Full Pipeline

```bash
python cli.py --brand menopause-planner --count 1 --post
```

Expected: Video posts to both Pinterest and YouTube

---

## Step 5: Add GitHub Secrets

1. Go to https://github.com/talhahbilal1-arch/social-media-empire/settings/secrets/actions
2. Click **"New repository secret"** for each:

| Secret Name | Value |
|-------------|-------|
| `MAKE_WEBHOOK_URL` | Your Make.com webhook URL |
| `YOUTUBE_CLIENT_ID` | Your OAuth Client ID |
| `YOUTUBE_CLIENT_SECRET` | Your OAuth Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | Your Refresh Token |

---

## Troubleshooting

### Make.com Webhook Not Triggering
- Check scenario is toggled ON
- Check webhook URL is correct in .env
- Check Make.com execution history for errors

### YouTube Upload Fails
- Verify all 3 credentials are set: CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
- Check YouTube quota at https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
- If refresh token expired, regenerate via OAuth Playground

### "No module found" Errors
```bash
pip install google-api-python-client google-auth-oauthlib
```

---

## Verification Checklist

- [ ] Make.com scenario created and ON
- [ ] Webhook URL added to .env
- [ ] YouTube API enabled in Google Cloud
- [ ] OAuth credentials created
- [ ] Refresh token obtained via OAuth Playground
- [ ] All credentials in .env
- [ ] Pinterest test successful
- [ ] YouTube test successful
- [ ] All secrets added to GitHub

---

## After Completion

Once everything works, the automation will:
- Run 3x daily via GitHub Actions (08:00, 14:00, 20:00 UTC)
- Generate videos with karaoke captions
- Upload to Supabase storage
- Post to Pinterest via Make.com
- Post to YouTube Shorts
- Handle all 3 brands automatically
