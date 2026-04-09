# Troubleshooting Guide

## Overview

This guide provides step-by-step diagnostic procedures and solutions for common issues in the Social Media Empire automation system. Issues are organized by category: workflow failures, API issues, database problems, and content generation errors.

## Prerequisites

- SSH/terminal access to run Python commands locally
- Access to GitHub Actions for workflow logs
- Access to Supabase dashboard for database inspection
- Access to Make.com for webhook debugging
- Access to all API provider dashboards

---

## Quick Diagnostic Commands

Before diving into specific issues, run these commands to get an overall system status:

```bash
# Full health check
python -m monitoring.health_checker --full --json

# Error summary
python -m monitoring.error_reporter --summary

# Recent videos status
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
videos = db.get_recent_videos(limit=10)
for v in videos:
    print(f'{v[\"created_at\"]}: {v[\"brand\"]} - {v[\"status\"]} - {v[\"platform\"]}')"

# Test individual APIs
python -c "
from utils.config import get_config
config = get_config()
print('Gemini:', 'OK' if config.gemini_api_key else 'MISSING')
print('Pexels:', 'OK' if config.pexels_api_key else 'MISSING')
print('Supabase:', 'OK' if config.supabase_url else 'MISSING')
print('YouTube:', 'OK' if config.youtube_refresh_token else 'MISSING')
print('Make.com:', 'OK' if config.make_com_pinterest_webhook else 'MISSING')
"
```

---

## Common Error Messages and Fixes

### 1. "GEMINI_API_KEY not configured"

**Symptom:** Health check shows Gemini as unhealthy; video generation fails.

**Cause:** Missing or invalid Gemini API key.

**Solution:**
1. Verify the API key exists:
   ```bash
   echo $GEMINI_API_KEY | head -c 10
   ```
2. If missing, get a new key from [Google AI Studio](https://aistudio.google.com/)
3. Update GitHub secret:
   - Go to Repository > Settings > Secrets and variables > Actions
   - Update `GEMINI_API_KEY`
4. For local testing, add to `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   ```

**Verification:**
```bash
python -c "
from utils.api_clients import GeminiClient
client = GeminiClient(api_key='YOUR_KEY')
print(client.generate_content('Say hello', max_tokens=10))
"
```

---

### 2. "PEXELS_API_KEY not configured" or 401 Errors

**Symptom:** Background video/image fetching fails; rate limit errors.

**Cause:** Missing, invalid, or rate-limited Pexels API key.

**Solution:**
1. Check current key validity:
   ```bash
   curl -H "Authorization: $PEXELS_API_KEY" \
        "https://api.pexels.com/v1/search?query=test&per_page=1"
   ```
2. If 401 error, key is invalid - get new key from [Pexels API](https://www.pexels.com/api/)
3. If rate limited (429), wait for rate limit reset (usually 1 hour)
4. Update the key in GitHub secrets and local environment

**Rate Limit Handling:**
The system has built-in retry logic with exponential backoff. If still failing:
- Reduce `per_page` parameter in requests
- Add delays between batch operations
- Consider upgrading Pexels plan

---

### 3. "Pinterest client not configured. Set MAKE_COM_PINTEREST_WEBHOOK"

**Symptom:** Pinterest posting fails; webhook errors.

**Cause:** Make.com webhook URL not configured or scenario is disabled.

**Solution:**
1. Verify webhook URL is set:
   ```bash
   echo $MAKE_COM_PINTEREST_WEBHOOK | head -c 30
   ```
2. If missing, get from Make.com:
   - Open your Pinterest posting scenario
   - Click on the Webhook module
   - Copy the webhook URL
3. Test the webhook:
   ```bash
   curl -X POST "$MAKE_COM_PINTEREST_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d '{"test": true}'
   ```
4. Update GitHub secret `MAKE_COM_PINTEREST_WEBHOOK`

---

### 4. "Token refresh failed" (YouTube)

**Symptom:** YouTube uploads fail; OAuth errors.

**Cause:** YouTube refresh token expired or revoked.

**Solution:**
1. Check if token can be refreshed:
   ```bash
   python -c "
   from utils.api_clients import YouTubeClient
   from utils.config import get_config
   config = get_config()
   client = YouTubeClient(
       client_id=config.youtube_client_id,
       client_secret=config.youtube_client_secret,
       refresh_token=config.youtube_refresh_token
   )
   print(client._refresh_access_token())
   "
   ```
2. If token refresh fails, regenerate:
   ```bash
   python scripts/get_youtube_oauth.py
   ```
3. Follow the OAuth flow to get a new refresh token
4. Update `YOUTUBE_REFRESH_TOKEN` in GitHub secrets

**Prevention:**
- YouTube refresh tokens don't expire if used regularly
- If app is in "testing" mode in Google Cloud, tokens expire in 7 days
- Move app to "production" mode for long-lived tokens

---

### 5. "Supabase connection failed" or "SUPABASE_URL not configured"

**Symptom:** Database operations fail; logging errors.

**Cause:** Invalid Supabase credentials or network issues.

**Solution:**
1. Verify credentials:
   ```bash
   curl "$SUPABASE_URL/rest/v1/" \
        -H "apikey: $SUPABASE_KEY" \
        -H "Authorization: Bearer $SUPABASE_KEY"
   ```
2. Expected response: Empty array `[]` or list of tables
3. If 401/403:
   - Check SUPABASE_KEY is the "anon" key (not service role)
   - Verify RLS policies aren't blocking access
4. If connection refused:
   - Check Supabase project is not paused (free tier pauses after inactivity)
   - Log into Supabase dashboard and unpause if needed

**Common Supabase Issues:**
- Free tier projects pause after 1 week of inactivity
- Row-level security (RLS) can block operations
- API key vs Service Role key confusion

---

### 6. "Render failed" (Creatomate)

**Symptom:** Video rendering fails; incomplete videos.

**Cause:** Invalid template, media URLs, or API issues.

**Solution:**
1. Check render status:
   ```bash
   curl "https://api.creatomate.com/v1/renders/RENDER_ID" \
        -H "Authorization: Bearer $CREATOMATE_API_KEY"
   ```
2. Common render failures:
   - **"Invalid template"**: Template ID doesn't exist
   - **"Media download failed"**: Source video/image URL is inaccessible
   - **"Timeout"**: Render took too long

3. Fix invalid template:
   - Verify template ID in Creatomate dashboard
   - Update template ID in `/video_automation/templates/*.json`

4. Fix media download issues:
   - Test media URL accessibility
   - Ensure Pexels URLs are fresh (they can expire)
   - Use direct download URLs, not preview URLs

5. For timeout issues:
   - Reduce video complexity
   - Use shorter background clips
   - Contact Creatomate support for extended timeouts

---

### 7. "Failed to send email" (Resend)

**Symptom:** Email alerts not received; subscriber emails not sent.

**Cause:** Invalid API key, domain not verified, or rate limits.

**Solution:**
1. Verify API key:
   ```bash
   curl "https://api.resend.com/domains" \
        -H "Authorization: Bearer $RESEND_API_KEY"
   ```
2. Check domain verification:
   - Log into Resend dashboard
   - Ensure sending domain has verified DNS records

3. Rate limit issues (free tier: 100 emails/day):
   - Check daily email count in Resend dashboard
   - Upgrade plan or reduce non-essential alerts

4. Update from address if domain changed:
   - Edit `/monitoring/error_reporter.py`
   - Change `from` address to verified domain

---

## Make.com Scenario Failures

### Scenario Stopped Running

**Symptoms:**
- No new Pinterest posts despite successful webhook calls
- Scenario shows "OFF" in Make.com dashboard

**Diagnostic Steps:**
1. Log into Make.com
2. Navigate to Scenarios
3. Check scenario status (ON/OFF)
4. Review "History" tab for errors

**Common Causes and Fixes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| Scenario disabled | Too many errors | Fix root cause, re-enable |
| Operations limit reached | Monthly limit exceeded | Upgrade plan or wait for reset |
| Pinterest connection expired | OAuth token expired | Reconnect Pinterest account |
| Webhook URL changed | Scenario was edited | Update webhook URL in GitHub secrets |

### Pinterest OAuth Expired

**Symptoms:**
- Scenario runs but posts fail
- Error: "Invalid access token" or "Authorization required"

**Fix:**
1. In Make.com, open the Pinterest scenario
2. Click on the Pinterest module
3. Click "Reconnect" or "Add connection"
4. Complete OAuth flow
5. Test with a manual run

### Webhook Not Receiving Data

**Symptoms:**
- Scenario shows no executions
- Local webhook tests succeed but production fails

**Diagnostic:**
```bash
# Test webhook from your machine
curl -X POST "YOUR_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"type":"idea_pin","board_id":"test","title":"Test Pin","pages":[{"media_url":"https://example.com/video.mp4"}]}'
```

**Fixes:**
- Verify webhook URL is exactly correct (no trailing slashes)
- Check Make.com is not in maintenance
- Verify scenario is active and webhook module is first
- Check Make.com execution logs for incoming requests

---

## Pinterest API Issues

### Video Pin Creation Fails

**Symptoms:**
- Webhook succeeds but pin not visible
- Make.com shows Pinterest API error

**Common Errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| "Invalid media" | Video format not supported | Use MP4, max 15 minutes |
| "Board not found" | Wrong board ID | Verify board ID in Pinterest |
| "Rate limit exceeded" | Too many requests | Wait and retry |
| "Media too large" | File size exceeded | Compress video under 2GB |

### Finding Correct Board ID

1. Go to Pinterest and open the target board
2. Look at the URL: `pinterest.com/username/board-name/`
3. The board ID format is the board-name slug (e.g., "daily-deal-darling-tips")
4. For Make.com, you may need the numeric ID - find it in the board settings

### Late API Integration Issues

If using Late API for Pinterest video posting:

**Symptoms:**
- Late API client initialization fails
- Videos not appearing on Pinterest

**Diagnostic:**
```bash
python -c "
from src.clients.late_api import LateAPIClient
client = LateAPIClient()
print('Late API configured:', client.is_configured())
"
```

**Fixes:**
- Verify `LATE_API_KEY` is set in environment
- Check Late API dashboard for posting status
- Review Late API documentation for video requirements

---

## Supabase Connection Problems

### Connection Timeout

**Symptoms:**
- Intermittent database failures
- "Connection timed out" errors

**Causes:**
- Network issues
- Supabase project paused
- Too many concurrent connections

**Fixes:**
1. Check if project is paused (Supabase dashboard)
2. Verify network connectivity:
   ```bash
   curl -I "$SUPABASE_URL/rest/v1/"
   ```
3. Reduce connection pooling if too many connections
4. Consider upgrading from free tier for better performance

### Row Level Security (RLS) Blocking

**Symptoms:**
- Operations return empty results
- Insert/update operations fail silently

**Diagnostic:**
```sql
-- In Supabase SQL Editor
-- Check RLS policies on videos table
SELECT * FROM pg_policies WHERE tablename = 'videos';
```

**Fixes:**
1. For API access, ensure policies allow operations with anon key:
   ```sql
   -- Example permissive policy
   CREATE POLICY "Allow all operations" ON videos
   FOR ALL
   USING (true)
   WITH CHECK (true);
   ```
2. Or use service role key (not recommended for client-side)

### Table Doesn't Exist

**Symptoms:**
- "relation does not exist" error

**Fix:**
Run the schema creation script:
```sql
-- From /database/schemas.sql in Supabase SQL Editor
-- Or check if tables exist:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

---

## Image/Video Generation Failures

### No Background Media Found

**Symptoms:**
- Videos created without background
- "No results found" from Pexels

**Causes:**
- Search query too specific
- Pexels API rate limited
- Incorrect orientation parameter

**Fixes:**
1. Test search query directly:
   ```bash
   curl "https://api.pexels.com/videos/search?query=lifestyle&per_page=1&orientation=portrait" \
        -H "Authorization: $PEXELS_API_KEY"
   ```
2. Broaden search terms in content config
3. Add fallback queries for each brand:
   ```python
   # In video_content_generator.py
   brand_backgrounds = {
       "daily_deal_darling": [
           "aesthetic lifestyle",
           "cozy home",
           "shopping",
           "woman happy"  # Fallback
       ]
   }
   ```

### Video Rendering Timeout

**Symptoms:**
- Creatomate render stuck in "processing"
- Workflow timeout after 30 minutes

**Fixes:**
1. Reduce video complexity
2. Use shorter background clips (max 30 seconds)
3. Check Creatomate status page for outages
4. Increase workflow timeout if needed:
   ```yaml
   # In .github/workflows/*.yml
   timeout-minutes: 45  # Increase from 30
   ```

### Text Overlay Issues

**Symptoms:**
- Text cut off in videos
- Wrong font or colors

**Fixes:**
1. Check template configuration:
   ```bash
   cat video_automation/templates/deal_alert.json
   ```
2. Verify text length limits:
   - Hook: max 50 characters recommended
   - Body points: max 60 characters each
   - CTA: max 40 characters
3. Update Creatomate template for longer text support

---

## Step-by-Step Diagnostic Procedures

### Procedure 1: Complete System Diagnostic

When multiple things seem broken, run this full diagnostic:

```bash
#!/bin/bash
# Full system diagnostic

echo "=== Environment Variables ==="
env | grep -E "(GEMINI|PEXELS|SUPABASE|YOUTUBE|MAKE_COM|LATE_API|RESEND)" | sed 's/=.*/=***/'

echo -e "\n=== Health Check ==="
python -m monitoring.health_checker --full

echo -e "\n=== Error Summary ==="
python -m monitoring.error_reporter --summary

echo -e "\n=== Recent Errors ==="
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
errors = db.get_unresolved_errors(limit=5)
for e in errors:
    print(f'  {e[\"error_type\"]}: {e[\"error_message\"][:80]}')
"

echo -e "\n=== Recent Videos ==="
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
videos = db.get_recent_videos(limit=5)
for v in videos:
    print(f'  {v[\"brand\"]} - {v[\"status\"]} - {v[\"platform\"]}')
"

echo -e "\n=== GitHub Actions Status ==="
echo "Check manually at: https://github.com/YOUR_REPO/actions"
```

### Procedure 2: Debug Specific Workflow Run

1. Go to GitHub Actions
2. Find the failed workflow run
3. Click to expand the failed job
4. Look for the specific step that failed
5. Check the error message
6. Cross-reference with this troubleshooting guide

### Procedure 3: Test Single Video Generation

```bash
# Test content generation without posting
python -m video_automation.daily_video_generator \
    --brand daily_deal_darling \
    --dry-run

# Check output for:
# - Content generation success
# - Background media fetching
# - Template configuration
```

### Procedure 4: Test Platform Posting

```bash
# Test Pinterest posting only
python -c "
from video_automation.pinterest_idea_pins import PinterestIdeaPinCreator
poster = PinterestIdeaPinCreator()
print('Pinterest configured:', poster.is_configured())

# Test with a sample video URL (use a real accessible URL)
result = poster.create_video_idea_pin(
    board_id='your-test-board',
    title='Test Pin',
    description='Testing automation',
    video_url='https://example.com/test-video.mp4'
)
print('Result:', result)
"
```

---

## Error Escalation Path

### Level 1: Self-Service (This Guide)
- Use diagnostic commands
- Check common solutions
- Review workflow logs

### Level 2: Documentation
- Review CLAUDE.md for code patterns
- Check API provider documentation
- Search GitHub issues

### Level 3: Investigation
- Enable debug logging
- Test components individually
- Check external service status pages

### Level 4: Code Changes Required
- Create GitHub issue with:
  - Error message
  - Steps to reproduce
  - Diagnostic output
  - Attempted solutions

---

## Related Procedures

- [Weekly Maintenance Checklist](weekly-maintenance-checklist.md)
- [Add New Pinterest Boards](add-new-pinterest-boards.md)
- [Performance Monitoring](performance-monitoring.md)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-27 | 1.0 | Initial creation |
