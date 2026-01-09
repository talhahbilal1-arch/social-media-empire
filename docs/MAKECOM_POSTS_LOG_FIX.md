# Fix: Add posts_log Logging to Make.com Scenarios

## Problem
Make.com Pinterest scenarios post successfully (398+ executions) but don't log to Supabase's `posts_log` table. This means:
- No record of what's been posted
- No analytics tracking
- Rate limiting doesn't work properly

## Solution
Add an HTTP module to each Make.com scenario that calls Supabase after posting.

---

## Step-by-Step Instructions

### Step 1: Open Make.com Scenario

1. Go to https://us2.make.com
2. Sign in
3. Open your Pinterest posting scenario (e.g., "Daily Deal Darling Pinterest")

### Step 2: Add HTTP Module After Pinterest Create Pin

1. Click the **+** button after the "Create a Pin" module
2. Search for **HTTP**
3. Select **Make a request**

### Step 3: Configure HTTP Module

Use these exact settings:

**URL:**
```
https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/posts_log
```

**Method:**
```
POST
```

**Headers:**
| Key | Value |
|-----|-------|
| apikey | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your SUPABASE_KEY) |
| Authorization | `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (same key) |
| Content-Type | `application/json` |
| Prefer | `return=representation` |

**Body type:**
```
Raw
```

**Content type:**
```
JSON (application/json)
```

**Request content (for Daily Deal Darling):**
```json
{
  "brand_id": "YOUR_DAILY_DEAL_DARLING_UUID",
  "platform": "pinterest",
  "platform_post_id": "{{Pinterest.id}}",
  "platform_url": "https://pinterest.com/pin/{{Pinterest.id}}",
  "post_type": "pin",
  "status": "posted",
  "posted_at": "{{now}}"
}
```

**Request content (for Menopause Planner):**
```json
{
  "brand_id": "YOUR_MENOPAUSE_PLANNER_UUID",
  "platform": "pinterest",
  "platform_post_id": "{{Pinterest.id}}",
  "platform_url": "https://pinterest.com/pin/{{Pinterest.id}}",
  "post_type": "pin",
  "status": "posted",
  "posted_at": "{{now}}"
}
```

### Step 4: Get Your Brand UUIDs

Run this query in Supabase SQL Editor:
```sql
SELECT id, name, display_name FROM brands;
```

Replace `YOUR_DAILY_DEAL_DARLING_UUID` and `YOUR_MENOPAUSE_PLANNER_UUID` with the actual UUIDs.

### Step 5: Map Pinterest Variables

In the HTTP module body, click in the `platform_post_id` field and:
1. Click the variable picker (gear icon)
2. Find **Pinterest > Create a Pin > ID**
3. Select it

The `{{Pinterest.id}}` will be replaced with the actual variable path.

### Step 6: Test the Scenario

1. Click **Run once**
2. Check Supabase `posts_log` table for new entry
3. If successful, save and activate the scenario

---

## Alternative: Use Make.com's Supabase Module

Make.com has a native Supabase integration:

1. Search for **Supabase** in the module list
2. Select **Insert a Row**
3. Connect your Supabase account
4. Select table: `posts_log`
5. Map fields:
   - brand_id → (hardcode your brand UUID)
   - platform → `pinterest`
   - platform_post_id → `{{Pinterest.id}}`
   - platform_url → `https://pinterest.com/pin/{{Pinterest.id}}`
   - status → `posted`
   - posted_at → `{{now}}`

---

## Verification

After setting up, verify by:

1. **Check posts_log table:**
```sql
SELECT * FROM posts_log
ORDER BY posted_at DESC
LIMIT 10;
```

2. **Count by platform:**
```sql
SELECT platform, COUNT(*) as count
FROM posts_log
GROUP BY platform;
```

---

## Troubleshooting

### Error: 401 Unauthorized
- Check that apikey header has correct Supabase key
- Ensure Authorization header is `Bearer <key>`

### Error: 400 Bad Request
- Verify JSON format is valid
- Check that brand_id UUID exists in brands table

### Error: 404 Not Found
- URL should end with `/posts_log` (table name)
- Check Supabase project URL is correct

### Pinterest.id is empty
- The Create Pin module must run before the HTTP module
- Check scenario order (Pinterest first, then HTTP)

---

## Backfill Historical Posts

If you want to backfill posts that were made before logging was set up, run this script locally or use the SQL below to estimate:

```sql
-- This doesn't backfill, but shows what should be in posts_log
-- based on content_bank items with status='posted'

SELECT
  cb.id as content_id,
  cb.brand_id,
  'pinterest' as platform,
  'posted' as status,
  cb.updated_at as posted_at
FROM content_bank cb
WHERE cb.status = 'posted'
  AND NOT EXISTS (
    SELECT 1 FROM posts_log pl WHERE pl.content_id = cb.id
  );
```

---

## Summary

1. Open each Make.com Pinterest scenario
2. Add HTTP module after "Create a Pin"
3. Configure to POST to Supabase posts_log
4. Test and save
5. Repeat for all Pinterest scenarios (Daily Deal Darling + Menopause Planner)

**Time required:** ~15-20 minutes per scenario
