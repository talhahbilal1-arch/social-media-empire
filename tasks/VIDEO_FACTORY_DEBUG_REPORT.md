# Video Factory Debug Report

**Date:** January 8, 2026
**Agent:** video_factory.py
**Issue:** Pinterest Idea Pins not working - video URLs always NULL

---

## 1. Current State (Before Fix)

### Did video_factory.py run without errors?
Yes, the agent ran without Python errors, but it was **not completing renders properly**:
- Renders were started but never polled for completion
- `video_url` field: Always NULL
- `idea_pin_url` field: Always NULL
- Videos stuck in "rendering" status forever

### Database State
| Field | Expected | Actual (Before Fix) |
|-------|----------|---------------------|
| `video_url` | Creatomate CDN URL | NULL |
| `idea_pin_url` | Creatomate CDN URL | NULL |
| `idea_pin_render_id` | UUID | Populated |
| `idea_pin_pages` | 2-5 | Populated |
| `status` | "ready" | "rendering" |

---

## 2. Bugs Found

### BUG #1: Creatomate renders never polled for completion (CRITICAL)

**File:** `agents/video_factory.py`
**Lines:** 228-296 (`_start_render`) and 325-398 (`_create_idea_pin`)
**Severity:** Critical

**Description:**
Creatomate API renders are **asynchronous**. When you POST to `/renders`, it returns a `render_id` immediately while the video renders in the background. The code was:
1. Starting renders correctly
2. Saving the `render_id` to database
3. **Never polling for completion**
4. **Never retrieving the final video URL**

The Creatomate workflow should be:
```
POST /renders -> Get render_id (status: "planned")
     |
     v
GET /renders/{id} -> Poll until status = "succeeded"
     |
     v
Extract "url" field -> Save to database
```

**Impact:**
- All `video_url` fields were NULL
- All `idea_pin_url` fields were NULL
- `multi_platform_poster.py` couldn't find video URLs to post
- YouTube uploads failed (no video URL)
- Pinterest Idea Pins couldn't be posted

---

### BUG #2: update_video_idea_pin() missing idea_pin_url parameter

**File:** `core/supabase_client.py`
**Line:** 212
**Severity:** Medium

**Description:**
The `update_video_idea_pin()` method only accepted `idea_pin_render_id` and `idea_pin_pages` parameters. It did not have an `idea_pin_url` parameter, so even if we got the URL, we couldn't save it.

---

## 3. Fixes Applied

### Fix #1: Added render polling method

**File:** `agents/video_factory.py`
**Lines:** 178-226 (new method)

```python
def _poll_render_completion(self, render_id: str) -> Dict:
    """
    Poll Creatomate API until render completes or fails.

    Returns dict with:
    - success: bool
    - url: video URL if successful
    - status: final status
    - error: error message if failed
    """
    start_time = time.time()

    while time.time() - start_time < self.RENDER_MAX_WAIT:
        response = requests.get(
            f"{self.base_url}/renders/{render_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        status = result.get('status', 'unknown')

        if status == 'succeeded':
            return {
                'success': True,
                'url': result.get('url'),
                'status': status
            }
        elif status in ['failed', 'error']:
            return {
                'success': False,
                'status': status,
                'error': result.get('error_message', 'Render failed')
            }

        time.sleep(self.RENDER_POLL_INTERVAL)

    return {'success': False, 'status': 'timeout', 'error': '...'}
```

**Configuration added:**
```python
RENDER_POLL_INTERVAL = 5  # seconds between status checks
RENDER_MAX_WAIT = 300     # 5 minutes max wait per render
```

---

### Fix #2: Updated _start_render() to poll and save URL

**File:** `agents/video_factory.py`
**Method:** `_start_render()`

**Before:**
```python
# Save video record with just render_id
video_record = {
    'content_id': content['id'],
    'creatomate_render_id': render_id,
    'status': 'rendering',  # Never updated!
    ...
}
self.db.save_video(video_record)
return {'success': True, 'render_id': render_id}
```

**After:**
```python
# Save video record
saved = self.db.save_video(video_record)
video_id = saved['id']

# Poll for render completion
poll_result = self._poll_render_completion(render_id)

if poll_result['success']:
    # Update with final URL and status
    self.db.update_video(
        video_id,
        video_url=poll_result['url'],
        status='ready'
    )
    return {'success': True, 'render_id': render_id, 'video_url': poll_result['url']}
else:
    self.db.update_video(video_id, status='failed', error_message=...)
    return {'success': False, 'error': ...}
```

---

### Fix #3: Updated _create_idea_pin() to poll and save URL

**File:** `agents/video_factory.py`
**Method:** `_create_idea_pin()`

**Before:**
```python
render_id = result[0]['id']
self.db.update_video_idea_pin(
    content_id=content['id'],
    idea_pin_render_id=render_id,
    idea_pin_pages=len(pages)
)
# idea_pin_url never set!
```

**After:**
```python
render_id = result[0]['id']

# Poll for render completion
poll_result = self._poll_render_completion(render_id)

if poll_result['success']:
    self.db.update_video_idea_pin(
        content_id=content['id'],
        idea_pin_render_id=render_id,
        idea_pin_pages=len(pages),
        idea_pin_url=poll_result['url']  # Now saved!
    )
```

---

### Fix #4: Added idea_pin_url parameter to database method

**File:** `core/supabase_client.py`
**Method:** `update_video_idea_pin()`

**Before:**
```python
def update_video_idea_pin(self, content_id: str, idea_pin_render_id: str, idea_pin_pages: int) -> None:
    self.client.table('videos').update({
        'idea_pin_render_id': idea_pin_render_id,
        'idea_pin_pages': idea_pin_pages
    }).eq('content_id', content_id).execute()
```

**After:**
```python
def update_video_idea_pin(self, content_id: str, idea_pin_render_id: str, idea_pin_pages: int, idea_pin_url: str = None) -> None:
    update_data = {
        'idea_pin_render_id': idea_pin_render_id,
        'idea_pin_pages': idea_pin_pages
    }
    if idea_pin_url:
        update_data['idea_pin_url'] = idea_pin_url
    self.client.table('videos').update(update_data).eq('content_id', content_id).execute()
```

---

## 4. Testing Results

### Pre-Fix Verification
- [x] Database schema has `idea_pin_url`, `idea_pin_render_id`, `idea_pin_pages` columns
- [x] `update_video_idea_pin()` method exists in supabase_client.py
- [x] GitHub workflow passes environment variables correctly
- [x] Creatomate API key is configured

### Expected Post-Fix Behavior
After deploying these fixes:

1. **Video Factory runs:**
   - Starts Creatomate render
   - Polls every 5 seconds for up to 5 minutes
   - When render completes, saves URL to `video_url`
   - Updates status to "ready"

2. **Idea Pin creation:**
   - Starts separate render for Idea Pin
   - Polls for completion
   - Saves URL to `idea_pin_url`

3. **Multi-Platform Poster can now:**
   - Find videos with `video_url` populated
   - Upload to YouTube Shorts
   - Post Idea Pins to Pinterest

### Manual Test Command
```bash
# From repository root
python -m agents.video_factory
```

---

## 5. Remaining Issues

### None Critical

All identified bugs have been fixed. The system should now:
1. Render videos
2. Poll for completion
3. Save video URLs
4. Enable posting to platforms

### Potential Future Improvements

1. **Webhook-based completion** (optional optimization)
   - Instead of polling, configure Creatomate webhook
   - Faster notification, less API calls
   - Requires additional webhook endpoint

2. **Parallel render polling**
   - Currently renders are sequential (render -> poll -> next)
   - Could start all renders, then poll all in parallel
   - Would speed up batch processing

3. **Retry failed renders**
   - If render fails, could retry once
   - Currently just marks as failed

---

## 6. Files Changed

| File | Changes |
|------|---------|
| `agents/video_factory.py` | Added `_poll_render_completion()`, updated `_start_render()` and `_create_idea_pin()` to poll and save URLs |
| `core/supabase_client.py` | Added `idea_pin_url` parameter to `update_video_idea_pin()` |

---

## 7. Deployment Checklist

- [ ] Push changes to GitHub
- [ ] Trigger manual Video Factory workflow run
- [ ] Verify `videos` table has `video_url` populated
- [ ] Verify `videos` table has `idea_pin_url` populated
- [ ] Verify `status` changes from "rendering" to "ready"
- [ ] Check Multi-Platform Poster can find and post videos

---

*Report generated by Claude Code debugging agent*
