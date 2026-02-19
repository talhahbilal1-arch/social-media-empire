# TikTok Posting Pipeline - Complete Guide

## Overview

The TikTok posting pipeline automatically posts videos from the `tiktok_queue` table (status: `video_ready`) to TikTok. It handles async video uploads and provides fallback support for manual posting.

## Architecture

```
tiktok_queue (video_ready)
    ↓
tiktok_poster.py
    ↓
TikTok Content Posting API (if token available)
    ├─ POST /post/publish/video/init/
    └─ Poll /post/publish/status/fetch/
    ↓
Update status to 'posted'
```

## Setup Requirements

### 1. Environment Variables (GitHub Secrets)

| Secret | Required | Purpose |
|--------|----------|---------|
| `SUPABASE_TIKTOK_URL` | Yes | Secondary Supabase project URL |
| `SUPABASE_TIKTOK_KEY` | Yes | Secondary Supabase service role key |
| `TIKTOK_ACCESS_TOKEN` | Optional | TikTok API access token (for auto-posting) |

### 2. TikTok API Access

To enable automatic posting to TikTok:

1. **Apply for TikTok Content Posting API:**
   - Visit https://developers.tiktok.com
   - Apply for "TikTok Content Posting API" (requires approved developer account)
   - Get access token from TikTok app settings

2. **Add to GitHub Secrets:**
   - Go to repo Settings → Secrets and variables → Actions
   - Add `TIKTOK_ACCESS_TOKEN` with your token

**If token not available:** Videos will be marked as `video_ready` for manual posting (see Manual Posting section)

### 3. Supabase Setup

Ensure secondary Supabase project is set up with:
- `tiktok_queue` table with proper RLS policies
- `tiktok_analytics` table for tracking

Run migrations if needed:
```sql
-- In Supabase SQL Editor for secondary project
-- Copy contents from tiktok_automation/database/tiktok_schema.sql
```

## Automated Posting (Scheduled)

### How It Works

The `.github/workflows/tiktok-poster.yml` workflow:
- Runs daily at **6 PM UTC (10 AM PST)**
- Fetches up to 5 `video_ready` items
- Posts to TikTok via Content Posting API
- Polls for completion (up to 5 minutes)
- Updates database with TikTok post IDs

### Status Flow

```
video_ready
    ↓
Posting initiated (publish_id obtained)
    ↓
Polling TikTok for completion
    ↓
PUBLISHED ─→ Update to 'posted' ✓
FAILED   ─→ Update to 'failed' ✗
TIMEOUT  ─→ Update to 'failed' (manual retry)
```

### Workflow Triggers

**Automatic Schedule:**
```yaml
Daily at 6 PM UTC (10 AM PST)
```

**Manual Trigger:**
```bash
# Via GitHub UI: Actions → TikTok Video Poster → Run workflow
# Or via CLI:
gh workflow run tiktok-poster.yml \
  -f max_videos=5 \
  -f dry_run=false
```

**With Dry Run:**
```bash
gh workflow run tiktok-poster.yml \
  -f dry_run=true
```

### Monitoring

Check workflow runs:
```bash
gh run list -w tiktok-poster.yml

# View latest run logs
gh run view --log -w tiktok-poster.yml
```

## Manual Posting (When API Unavailable)

When `TIKTOK_ACCESS_TOKEN` is not set, use manual posting helper:

### Step 1: Generate Posting Batch

```bash
python3 tiktok_automation/manual_posting_guide.py \
  --output tiktok_batch.json \
  --max 10
```

This generates a JSON file with:
- Video URLs (Pexels and audio)
- Formatted captions
- Hashtags and affiliate links
- Step-by-step posting instructions

### Step 2: Manual Upload

For each video in the batch:

1. Open TikTok app → Create post
2. Upload video from provided URL (or download first)
3. Copy caption and hashtags from batch file
4. Set privacy to "Public"
5. Post

### Step 3: Mark as Posted

After posting, update Supabase:

```bash
# Via Supabase dashboard:
# 1. Go to tiktok_queue table
# 2. Find the item by topic/date
# 3. Update fields:
#    - status: 'posted'
#    - tiktok_post_id: 'video123456789'  (from URL)
#    - tiktok_post_url: 'https://www.tiktok.com/@username/video/...'
#    - posted_at: NOW()

# Or via SQL:
UPDATE tiktok_queue
SET status = 'posted',
    tiktok_post_id = 'video123456789',
    tiktok_post_url = 'https://www.tiktok.com/@username/video/...',
    posted_at = NOW()
WHERE id = 'queue_item_uuid';
```

## Command Line Usage

### Automatic Posting (with token)

```bash
# Post max 5 videos
python3 tiktok_automation/tiktok_poster.py --max 5

# Post 10 videos
python3 tiktok_automation/tiktok_poster.py --max 10

# Dry run (no actual posting)
python3 tiktok_automation/tiktok_poster.py --dry-run
```

### Manual Posting Setup

```bash
# Generate batch file (JSON)
python3 tiktok_automation/manual_posting_guide.py

# Generate with custom output
python3 tiktok_automation/manual_posting_guide.py \
  --output my_batch.json \
  --max 5

# Only show summary, don't create file
python3 tiktok_automation/manual_posting_guide.py --skip-file
```

## Database Schema

### tiktok_queue Table

Key fields for posting:
- `id` (UUID): Unique identifier
- `status` (TEXT): Current status (video_ready, posted, failed)
- `video_url` (TEXT): Pexels video URL
- `audio_url` (TEXT): ElevenLabs audio URL
- `caption` (TEXT): TikTok caption (max 2200 chars)
- `hashtags` (TEXT[]): Array of hashtags
- `tiktok_post_id` (TEXT): TikTok video ID after posting
- `tiktok_post_url` (TEXT): Full TikTok URL
- `posted_at` (TIMESTAMPTZ): When posted
- `error_message` (TEXT): Error details if failed
- `retry_count` (INTEGER): Number of retry attempts

### tiktok_analytics Table

Tracks performance of posted videos:
- `tiktok_queue_id` (UUID): Reference to tiktok_queue
- `tiktok_post_id` (TEXT): TikTok video ID
- `views` (INTEGER)
- `likes` (INTEGER)
- `comments` (INTEGER)
- `shares` (INTEGER)
- `engagement_rate` (NUMERIC)

## TikTok API Details

### Posting Flow

1. **Initialize Upload:**
   ```
   POST https://open.tiktokapis.com/v2/post/publish/video/init/
   {
     "source_info": {
       "source": "PULL_FROM_URL",
       "video_url": "https://..."
     },
     "post_info": {
       "title": "caption",
       "privacy_level": "PUBLIC_TO_EVERYONE"
     }
   }
   ```
   Returns: `publish_id`

2. **Poll Status:**
   ```
   POST https://open.tiktokapis.com/v2/post/publish/status/fetch/
   {
     "publish_id": "publish_id_from_init"
   }
   ```
   Returns: Status (UPLOAD_IN_PROGRESS, PROCESSING, PUBLISHED, FAILED)

3. **Complete:**
   When status = PUBLISHED, video is live

### Rate Limits

- **New apps:** 100 posts/day
- **Established apps:** 500+ posts/day (negotiated)
- **Per-request timeout:** 30 seconds
- **Polling interval:** 5 seconds (up to 5 minutes)

### Video Requirements

- **Format:** MP4
- **Aspect Ratio:** 9:16 (vertical, portrait)
- **Duration:** 3-60 seconds
- **File Size:** Max 287.6 MB

## Troubleshooting

### "TIKTOK_ACCESS_TOKEN not set"

**Issue:** Workflow posts nothing because token is missing

**Solution:**
1. Get TikTok access token from developer.tiktok.com
2. Add to GitHub Secrets as `TIKTOK_ACCESS_TOKEN`
3. Re-run workflow

**Interim:** Use manual posting via `manual_posting_guide.py`

### "TikTok API init failed"

**Issue:** POST to /post/publish/video/init/ returned error

**Likely Causes:**
- Token is invalid or expired
- App not approved for Content Posting API
- Video URL is broken or behind auth
- Request format incorrect

**Fix:**
- Check token expiry in TikTok app settings
- Verify app status in TikTok Developer Console
- Test video URL manually in browser
- Check logs for exact error message

### "Polling timeout after 5 minutes"

**Issue:** Video processing took too long

**Cause:** TikTok processing queue is busy

**Fix:**
- Retry will happen automatically in next workflow run
- Item status will be set to 'failed' with error
- Can manually retry by re-setting status to 'video_ready'

### "Missing video_url"

**Issue:** Item in tiktok_queue has no video_url

**Cause:** Video generation failed (audio_ready instead of video_ready)

**Fix:**
- Check tiktok-content.yml workflow to see if video generation succeeded
- Regenerate video using tiktok_pipeline.py

### "Update to Supabase failed"

**Issue:** Posted successfully but database update failed

**Cause:** Supabase connectivity or RLS policy issue

**Fix:**
- Verify Supabase credentials in GitHub Secrets
- Check table RLS policies allow service_role writes
- Manually update Supabase after verifying TikTok post was created

## Performance

### Expected Timings

- **Fetch from Supabase:** <1 second
- **TikTok API init:** 1-3 seconds
- **Polling for completion:** 30-120 seconds (avg)
- **Update Supabase:** <1 second
- **Total per video:** 1-3 minutes

### Scaling

For more videos per run:
1. Increase `--max` parameter
2. Increase workflow timeout (currently 30 minutes)
3. Monitor TikTok API rate limits

## Integration with Other Systems

### Related Workflows

- **tiktok-content.yml:** Generates content (script, audio, video)
- **weekly-discovery.yml:** Discovers trends (feeds tiktok-content.yml)
- **tiktok-poster.yml:** Posts generated videos (this workflow)

### Database Tables Used

- `tiktok_queue`: Main queue (read/write)
- `tiktok_analytics`: Performance tracking (write)
- `tiktok_prompts`: Prompt templates (read)

### Cross-Platform Publishing

After TikTok posting succeeds, consider:
- Reposting to YouTube Shorts
- Reposting to Instagram Reels
- Adding to Pinterest board

See `tiktok_automation/HANDOFF.md` for architecture.

## Cost Summary

**Monthly Costs (TikTok Posting Only):**
- TikTok API: Free (no charges for posts)
- GitHub Actions: Included in free tier
- Supabase: Included in your plan

**Total:** $0 (no additional cost for posting)

## Next Steps

1. **If you have TikTok API access:**
   - Add token to GitHub Secrets
   - Workflow will auto-run daily at 6 PM UTC
   - Check logs for any errors

2. **If you don't have TikTok API access:**
   - Use `manual_posting_guide.py` to format videos
   - Post manually via TikTok app
   - Update database after each post

3. **Monitor Performance:**
   - Check `tiktok_analytics` table for views/engagement
   - Review workflow logs weekly
   - Adjust timing/quantity as needed

## Resources

- **TikTok Developer Docs:** https://developers.tiktok.com/doc/
- **TikTok Content Posting API:** https://developers.tiktok.com/doc/tiktok-api/content-posting-api/overview
- **GitHub Actions:** https://docs.github.com/en/actions

---

**Last Updated:** 2026-02-19
