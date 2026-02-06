# YouTube Automation Handoff Document

## Current Status: FULLY OPERATIONAL

### What's Been Completed

1. **Full YouTube Pipeline Created** (`scripts/youtube_pipeline.py`)
   - ElevenLabs audio generation (WORKING)
   - D-ID avatar video creation (WORKING)
   - YouTube upload via direct API (WORKING)
   - Falls back to Late.dev if needed

2. **Direct YouTube API Module** (`scripts/youtube_uploader.py`)
   - Created to bypass Late.dev rate limits
   - Uses YouTube Data API v3
   - OAuth token configured and working

3. **Google Cloud Setup**
   - Project: `social-media-empire`
   - YouTube Data API v3: Enabled
   - OAuth Client ID: `365159512738-ekhklidgn5b37l8opbvcodv4e114vu4j.apps.googleusercontent.com`
   - Client secret JSON saved to: `config/youtube_client_secret.json`

4. **YouTube OAuth Complete**
   - OAuth token saved to: `config/youtube_token.pickle`
   - Authorized account: talhah1988
   - Scope: youtube.upload

5. **Supabase Setup**
   - Database connected and working
   - Tables created: `youtube_scripts`, `youtube_automation_errors`
   - Storage bucket "audio" created with PUBLIC access

6. **Test Results (2026-02-03)**
   - Audio generation: WORKING (ElevenLabs)
   - Video generation: WORKING (D-ID with alice.jpg avatar)
   - YouTube upload via direct API: WORKING
   - First successful upload: https://youtube.com/shorts/d7qa04mOU5o

### How to Run the Pipeline

```bash
cd /Users/homefolder/Desktop/social-media-empire/youtube-automation
source <(grep -v '^#' config/.env | grep -v '^$' | sed 's/^/export /') && python3 scripts/youtube_pipeline.py
```

### How to Add New Scripts

Insert scripts into the `youtube_scripts` Supabase table with status `pending`:

```python
from scripts.supabase_client import get_client
client = get_client()
client.table('youtube_scripts').insert({
    'title': 'Your Video Title',
    'script': 'Your video script text here...',
    'status': 'pending'
}).execute()
```

### Key Files

| File | Purpose |
|------|---------|
| `config/.env` | All API credentials (ElevenLabs, D-ID, Supabase, Late.dev) |
| `config/youtube_client_secret.json` | Google OAuth client credentials |
| `config/youtube_token.pickle` | OAuth token (valid and working) |
| `scripts/youtube_pipeline.py` | Main automation pipeline |
| `scripts/youtube_uploader.py` | Direct YouTube API upload module |
| `scripts/supabase_client.py` | Database operations |
| `scripts/supabase_schema.sql` | Database schema |

### API Credentials (in config/.env)

- SUPABASE_URL: https://bjacmhjtpkdcxngkasux.supabase.co
- SUPABASE_SERVICE_KEY: (set)
- LATE_API_KEY: (set, but at rate limit - not needed with direct API)
- LATE_YOUTUBE_ACCOUNT_ID: 697c480a93a320156c422fc8
- ELEVENLABS_API_KEY: (set)
- ELEVENLABS_VOICE_ID: 21m00Tcm4TlvDq8ikWAM
- DID_API_KEY: (set)

### Pipeline Configuration

- `USE_DIRECT_YOUTUBE_API = True` in youtube_pipeline.py (uses direct API instead of Late.dev)
- Default avatar: D-ID's alice.jpg
- Video category: 26 (Howto & Style)
- Videos are tagged as #Shorts automatically

### Optional Future Tasks

1. Clone your voice in ElevenLabs and update ELEVENLABS_VOICE_ID
2. Upload custom avatar photo to D-ID and update DID_AVATAR_IMAGE_URL
3. Create the stats table in Supabase (see scripts/supabase_schema.sql)
4. Set up n8n workflow for scheduled automation
5. Set up GitHub Actions for automated daily uploads

### Refreshing OAuth Token

The OAuth token should auto-refresh. If it expires and needs manual re-auth:

```bash
cd /Users/homefolder/Desktop/social-media-empire/youtube-automation
rm config/youtube_token.pickle
source <(grep -v '^#' config/.env | grep -v '^$' | sed 's/^/export /') && python3 scripts/youtube_uploader.py --setup
```

---

Last Updated: 2026-02-03
Status: Pipeline fully operational
