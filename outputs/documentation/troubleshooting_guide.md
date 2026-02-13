# Troubleshooting Guide -- Pinterest Empire

Comprehensive guide for diagnosing and resolving issues across all system components: Make.com, Claude API, Pexels, Pinterest, Supabase, and Netlify.

---

## Table of Contents

1. [Make.com Scenario Fails with 400 Error](#1-makecom-scenario-fails-with-400-error)
2. [Make.com Scenario Fails with 429 (Rate Limit)](#2-makecom-scenario-fails-with-429-rate-limit)
3. [Pexels Returns No Images](#3-pexels-returns-no-images)
4. [Claude API Returns Malformed JSON](#4-claude-api-returns-malformed-json)
5. [Pinterest Pin Not Appearing](#5-pinterest-pin-not-appearing)
6. [Pinterest Account Suspended or Warned](#6-pinterest-account-suspended-or-warned)
7. [Duplicate Content Generated](#7-duplicate-content-generated)
8. [Scheduled Inline Pins Not Posting](#8-scheduled-inline-pins-not-posting)
9. [Supabase Connection Errors](#9-supabase-connection-errors)
10. [Netlify Deployment Fails](#10-netlify-deployment-fails)
11. [Images Not Loading on Subdomain Sites](#11-images-not-loading-on-subdomain-sites)
12. [Pin Performance Suddenly Drops](#12-pin-performance-suddenly-drops)
13. [Content Sounds Repetitive Despite Dedup](#13-content-sounds-repetitive-despite-dedup)
14. [Board IDs Changed After Pinterest Update](#14-board-ids-changed-after-pinterest-update)
15. [General Debugging Procedures](#general-debugging-procedures)

---

## 1. Make.com Scenario Fails with 400 Error

### Symptom
Make.com scenario run shows a red "400 Bad Request" error on one of the HTTP modules (Claude API, Pexels API, Supabase RPC, or Pinterest API).

### Likely Cause
- **Claude module (400)**: Malformed JSON in the request body. Common causes: unescaped quotes in the prompt, double-encoded JSON, template variables resolving to `null` or containing newlines that break the JSON structure.
- **Pexels module (400)**: Empty or invalid search query parameter.
- **Supabase module (400)**: Wrong column names, wrong data types, or missing required fields in an INSERT/UPDATE.
- **Pinterest module (400)**: Invalid board ID, image URL not accessible, or missing required fields.

### Fix Steps

**For Claude 400 errors:**
1. Open the failed run in Make.com and click the red module
2. Go to the "Input" tab -- check the full request body
3. Copy the JSON body and paste it into a JSON validator (e.g., jsonlint.com)
4. Common fixes:
   - Wrap template variables that might contain quotes with `replace()`: `{{replace(3.title; "\""; "'")}}`
   - Ensure `join()` and `map()` outputs don't break the JSON string
   - Add a `toString()` wrapper around complex mapped values
5. Test the fixed body by running the scenario on a single item

**For Supabase 400 errors:**
1. Check the error message body -- Supabase PostgREST returns descriptive errors
2. Common messages:
   - `"Could not find a relationship"` -- Table name is wrong
   - `"null value in column X violates not-null constraint"` -- A required field is empty
   - `"invalid input syntax for type"` -- Data type mismatch (e.g., sending a string to an integer column)
3. Fix the field mappings in the Make.com module

**For Pinterest 400 errors:**
1. Check if the board_id is still valid (boards can be deleted or renamed)
2. Verify the image URL is publicly accessible (try opening it in an incognito browser)
3. Check that the pin title is not empty and does not exceed 100 characters
4. Ensure the link URL is a valid HTTPS URL

### Prevention
- Add a "Set variable" module before each HTTP module that validates inputs
- Use Make.com's built-in "ifempty()" function for fallback values
- Test scenario changes with manual runs before activating the schedule

---

## 2. Make.com Scenario Fails with 429 (Rate Limit)

### Symptom
HTTP module returns 429 status code. The error message typically includes "rate limit exceeded" or "too many requests."

### Likely Cause
- **Claude API**: Exceeding 60 requests per minute on the Sonnet tier
- **Pexels API**: Exceeding 200 requests per hour (free tier)
- **Pinterest API**: Exceeding per-app rate limits (varies by endpoint)
- **Supabase**: Exceeding PostgREST connection limits on free tier

### Fix Steps

1. **Immediate fix**: Re-run the failed execution after 60 seconds
   - In Make.com, go to the scenario's "Incomplete executions" tab
   - Re-run the failed execution

2. **Add retry logic to the scenario**:
   - On the HTTP module, set "Automatically retry" to `Yes`
   - Set retry count: `3`
   - Set retry interval: `60` seconds
   - Alternatively, attach a "Retry" error handler with a 60-second delay

3. **Reduce request frequency**:
   - For Claude: Add a 2-second Sleep module between Claude API calls in iterators
   - For Pexels: Reduce `per_page` from 40 to 15 (still enough for uniqueness)
   - For Pinterest: Space out pin creation with a 5-second Sleep between pins

4. **Check for runaway scenarios**:
   - Ensure the scenario is not running overlapping executions
   - Set "Sequential processing" to ON in scenario settings
   - Set "Max number of cycles" to 1

### Prevention
- Enable "Sequential processing" on all scenarios
- Add Sleep modules (2-5 seconds) between external API calls inside iterators
- Set Make.com scenario to "Max errors: 3" to prevent runaway retries
- Monitor API usage dashboards weekly

---

## 3. Pexels Returns No Images

### Symptom
The Pexels API module returns successfully (200) but the `photos` array is empty, or the module returns a 200 with `"total_results": 0`.

### Likely Cause
- Search query is too specific or uses niche jargon Pexels doesn't index
- Search query contains blocked terms that Pexels filters out
- Brand-specific image validation in `image_selector.py` replaced the query with a fallback that also returned no results
- Pexels is temporarily having indexing issues (rare)

### Fix Steps

1. **Test the query manually**: Go to https://www.pexels.com/search/YOUR_QUERY/ and see if results appear
2. **Simplify the query**: If Claude generated a query like "close up muscular forearms gripping barbell gym dramatic lighting," try "man lifting barbell gym"
3. **Add a fallback in Make.com**:
   - After the Pexels module, add a Router
   - Route 1: `{{length(7.data.photos)}}` > 0 -- continue normally
   - Route 2: `{{length(7.data.photos)}}` = 0 -- make a second Pexels call with a simplified query
   - Simplified query: Use only the first 2-3 words + the brand's fallback term
4. **Check the image_selector.py guardrails**: The `BRAND_IMAGE_RULES` dict may be stripping relevant terms. If a query is being replaced with a fallback, check the `blocked_terms` and `allowed_themes` lists.

### Prevention
- Instruct Claude (in the prompt) to use common, searchable terms for image queries
- Add examples of good queries in the prompt: "Use terms like 'woman organizing kitchen' not 'aesthetic minimalist pantry reorganization'"
- Cache successful queries and reuse them as fallbacks
- Keep `per_page` at 15-40 to maximize the chance of finding usable images

---

## 4. Claude API Returns Malformed JSON

### Symptom
The JSON Parse module fails with "Invalid JSON" error. The Claude response contains markdown formatting, extra text before/after the JSON, nested backticks, or truncated output.

### Likely Cause
- Claude sometimes wraps JSON in markdown code fences despite being told not to
- Claude occasionally adds explanatory text before or after the JSON
- The `max_tokens` limit was hit, truncating the response mid-JSON
- Special characters in the prompt (unescaped quotes, backslashes) caused Claude to misinterpret the format

### Fix Steps

1. **Check the raw Claude output**: Open the failed run, click the HTTP module, check the response body under `data.content[0].text`

2. **If wrapped in markdown code fences** (` ```json ... ``` `):
   - Add a "Text parser > Replace" module between Claude and JSON Parse
   - Pattern: `` ```json?\n?([\s\S]*?)``` ``
   - Replace with: `$1`
   - Or use: `{{replace(replace(4.data.content[].text; "```json"; ""); "```"; "")}}`

3. **If preceded by explanatory text**:
   - Use a Regex match to extract JSON: `{{first(match(4.data.content[].text; "\{[\s\S]*\}"))}}`
   - The content_brain.py already handles this with `re.search(r'\{.*\}', content, re.DOTALL)`

4. **If truncated** (ends with `...` or incomplete JSON):
   - Increase `max_tokens` in the Claude request body
   - For listicle generation: use `4000` tokens minimum
   - For title generation: use `300` tokens minimum
   - Simplify the prompt to require less output

5. **If the issue persists**, add a validation step:
   - After JSON Parse, add a Router
   - Check that required fields exist: `{{ifempty(5.title; "MISSING")}}`
   - If any field is "MISSING", trigger a retry with a simplified prompt

### Prevention
- Always include "Return ONLY this JSON, no markdown, no backticks, no explanation" in prompts
- Set `max_tokens` generously (2x expected output length)
- Add the JSON extraction regex as a standard post-processing step
- Use `temperature: 0` for more predictable formatting (add to Claude request body: `"temperature": 0`)

---

## 5. Pinterest Pin Not Appearing

### Symptom
The Make.com scenario shows success (200 response from Pinterest API), the `pin_id` is stored in Supabase, but the pin is not visible on the Pinterest board.

### Likely Cause
- Pinterest's processing delay (pins can take 5-30 minutes to appear)
- The pin was flagged for review by Pinterest's automated system
- The pin was posted to the wrong board
- The image URL was not accessible to Pinterest's servers (expired Pexels URL)
- The pin was shadow-suppressed for policy reasons

### Fix Steps

1. **Wait 30 minutes** -- Pinterest processes pins asynchronously. Check again after a delay.

2. **Check pin status via API**:
   ```
   GET https://api.pinterest.com/v5/pins/{pin_id}
   Authorization: Bearer YOUR_TOKEN
   ```
   - Status `"active"` = visible
   - Status `"processing"` = still being processed
   - Status `"flagged"` = under review

3. **Verify the board**:
   - Check that the pin_id maps to the correct board in your Pinterest dashboard
   - If using board IDs in Make.com, verify they haven't changed

4. **Check the image URL**:
   - Pexels URLs are typically stable, but try opening the image URL in a browser
   - If expired, the pin may have been created with a broken image

5. **Check Pinterest notifications**:
   - Look for any notices about the pin being removed or flagged
   - Check your email for Pinterest policy notifications

6. **If the pin was shadow-suppressed**:
   - Review the pin content for potential policy violations
   - Common triggers: misleading titles, spammy descriptions, blocked URLs
   - Delete and recreate the pin with adjusted content

### Prevention
- Use high-quality, original-looking images (avoid overused stock photos)
- Ensure descriptions are genuinely informative, not clickbait
- Vary posting patterns to avoid appearing automated
- Use 2-3 different destination URLs (not always the same one)
- Keep a 5-minute minimum gap between pins to the same board

---

## 6. Pinterest Account Suspended or Warned

### Symptom
Pinterest shows a warning banner when logging in, pins are no longer showing in search, or the account is fully suspended with an email notification.

### Likely Cause
- **Spam detection**: Posting too many pins too quickly (especially the same URL)
- **Policy violation**: Misleading content, broken links, or prohibited content
- **Automated behavior detection**: Pinterest detected the Make.com automation pattern
- **Copyright claims**: Using images that triggered a copyright match
- **URL flagged**: The destination domain was flagged as spam or unsafe

### Fix Steps

**For warnings (account still active):**
1. **IMMEDIATELY pause both Make.com scenarios** (Agent 2A and 2B)
2. Review the warning message carefully -- note the specific reason
3. Reduce posting frequency: Change Agent 2A from 3x/day to 1x/day
4. Space out Agent 2B pins: add 30-minute Sleep between each pin
5. Wait 48 hours before reactivating at reduced frequency
6. Diversify: pin to more different boards, vary destination URLs

**For suspension:**
1. Pause ALL automation immediately
2. Read the suspension email for the specific reason
3. File an appeal through Pinterest's appeal form:
   - https://help.pinterest.com/en/business/article/account-suspension
4. While waiting for appeal:
   - Audit all recent pins for policy violations
   - Check all destination URLs are working and compliant
   - Review content for anything that could be seen as misleading
5. After reinstatement:
   - Start with manual pinning for 1 week
   - Reintroduce automation at 50% of previous volume
   - Gradually increase over 2-3 weeks

**URL domain flagged:**
1. Check if the domain is on any blocklists: https://transparencyreport.google.com/safe-browsing/search
2. If flagged, request a review through Google Safe Browsing
3. Temporarily switch to a different destination URL
4. Ensure the site has proper SSL, privacy policy, and no malware

### Prevention
- Maximum 25 pins per day per account (even Pinterest's own recommendation)
- Minimum 2-minute gap between pins
- Never post the same image to multiple boards in one day
- Vary destination URLs (use subdomains to create variety)
- Mix in manual pins (repin others' content) periodically
- Use the "Smart Feed" friendly approach: focus on quality signals (saves, clicks) over volume
- Maintain a 70/30 ratio: 70% original pins, 30% repins

---

## 7. Duplicate Content Generated

### Symptom
Multiple pins have the same or very similar titles, descriptions, or images. The deduplication system is not preventing repeats.

### Likely Cause
- The Supabase query for recent pins is failing silently (returns empty array)
- The `content_history` table is not being populated correctly
- Claude is ignoring the "recently used titles" list in the prompt
- The dedup window is too small (only checking last 10-30 pins)
- After a long gap in posting, the dedup history was purged by cleanup

### Fix Steps

1. **Check content_history table**:
   ```sql
   -- Verify recent entries exist
   SELECT brand, title, created_at
   FROM content_history
   ORDER BY created_at DESC
   LIMIT 20;
   ```
   If empty, the `log_pin_to_history()` function is failing.

2. **Check for duplicate titles specifically**:
   ```sql
   SELECT title, COUNT(*) as count
   FROM content_history
   WHERE created_at > NOW() - INTERVAL '30 days'
   GROUP BY title
   HAVING COUNT(*) > 1
   ORDER BY count DESC;
   ```

3. **In Make.com**: Verify that module 3 (Get Recent Pins) is returning data:
   - Check the module's output in a test run
   - If it returns 0 records, check the filter (brand matching, table name)

4. **Increase the dedup window**: In the Claude prompt, include more recent titles (20-30 instead of 10)

5. **Add explicit instructions to Claude**: Add to the prompt: "If any of your output closely resembles these recent titles, regenerate with a completely different approach."

### Prevention
- Always verify that `log_pin_to_history()` succeeds after each pin post
- Include at least 20 recent titles in the Claude prompt
- Add a post-generation check: before posting, query Supabase for title similarity
- Set up a weekly alert for duplicate detection (see the SQL query above)

---

## 8. Scheduled Inline Pins Not Posting

### Symptom
The `scheduled_inline_pins` table has rows with `pinned = false` for past dates. Agent 2B is running but not picking them up, or not posting them.

### Likely Cause
- Agent 2B scenario is paused or not scheduled
- The `get_todays_scheduled_pins()` RPC function does not exist or returns wrong data
- The `scheduled_date` column has timezone issues (UTC vs. local)
- The Pinterest OAuth token has expired
- Agent 2B runs at times that don't overlap with the scheduled times

### Fix Steps

1. **Check Agent 2B scenario status**: Is it Active? Check last run time.

2. **Test the RPC function directly**:
   ```sql
   -- Run in Supabase SQL Editor
   SELECT * FROM get_todays_scheduled_pins();
   ```
   - If it returns no rows but there ARE unposted pins for today, the function has a bug
   - Check the `scheduled_date` format: it should be a DATE, not a TIMESTAMP

3. **Check for timezone mismatch**:
   ```sql
   -- Compare dates
   SELECT CURRENT_DATE, NOW(), NOW() AT TIME ZONE 'America/Los_Angeles';
   ```
   - Supabase uses UTC by default
   - If pins are scheduled in PST but the function checks UTC dates, there's a window where pins won't match
   - Fix: Use `CURRENT_DATE AT TIME ZONE 'America/Los_Angeles'` in the function

4. **Check Pinterest OAuth**:
   - Make a test Pinterest API call from Make.com
   - If 401 error: the token has expired -- reconnect the Pinterest connection in Make.com

5. **Manually post overdue pins**:
   ```sql
   -- Find overdue pins
   SELECT id, brand, image_url, original_title, board_name, destination_url
   FROM scheduled_inline_pins
   WHERE scheduled_date < CURRENT_DATE AND pinned = FALSE;
   ```
   - Either run Agent 2B manually or update the dates to today and wait for the next run

### Prevention
- Set Agent 2B to run every 4-6 hours to catch any missed windows
- Add an alert (via the errors table) when the overdue pin count exceeds 5
- Use UTC consistently for all date operations
- Check Pinterest OAuth token validity in the Monday maintenance check

---

## 9. Supabase Connection Errors

### Symptom
Make.com Supabase modules fail with connection errors, timeouts, or "503 Service Unavailable." GitHub Actions workflows fail with Supabase-related errors.

### Likely Cause
- **Free tier auto-pause**: Supabase free tier projects pause after 1 week of inactivity
- **Connection pool exhaustion**: Too many concurrent connections
- **API key expired or rotated**: The service_role key was regenerated
- **PostgREST cache stale**: New tables/functions not recognized
- **Region-specific outage**: Check Supabase status page

### Fix Steps

1. **Check Supabase status**: https://status.supabase.com/

2. **If the project is paused** (free tier):
   - Go to Supabase Dashboard > Settings > General
   - Click "Restore project"
   - Wait 5-8 minutes for full restart
   - Test with a simple query before reactivating automation

3. **If connection pool is exhausted**:
   - Check how many connections are open:
     ```sql
     SELECT count(*) FROM pg_stat_activity;
     ```
   - Free tier limit: 60 connections
   - If near the limit, check for leaked connections from failed Make.com runs
   - Restart the Supabase project from Dashboard > Settings > General > Restart Project

4. **If API key issue**:
   - Go to Supabase Dashboard > Settings > API
   - Copy the current `service_role` key
   - Update the key in:
     - Make.com Supabase connections
     - GitHub Secrets (SUPABASE_KEY)
     - Any local .env files

5. **If new tables/functions not recognized**:
   - Run `NOTIFY pgrst, 'reload schema'` in SQL Editor (unreliable on free tier)
   - Better: Restart the project from Dashboard > Settings > General
   - Wait 5-8 minutes after restart

### Prevention
- Keep the Supabase project active by having at least one query per week (the weekly-maintenance workflow handles this)
- Use the `service_role` key (not the `anon` key) for server-side operations
- After creating new tables, always restart the Supabase project
- After creating new tables, always run `GRANT ALL ON table_name TO anon, authenticated, service_role`

---

## 10. Netlify Deployment Fails

### Symptom
The GitHub Actions `toolpilot-deploy.yml` or Netlify auto-deploy fails. The Netlify dashboard shows a failed deploy with build errors.

### Likely Cause
- Build command failed (syntax errors in HTML/JS)
- Node.js version mismatch
- Deployment artifact too large (free tier limit: 100MB per deploy)
- Netlify API token expired
- Git branch mismatch (deploying from wrong branch)

### Fix Steps

1. **Check Netlify deploy logs**:
   - Go to Netlify Dashboard > [Site] > Deploys > Click the failed deploy
   - Read the build log for specific error messages

2. **Common build errors**:
   - `"command not found"`: Check the build command in `netlify.toml`
   - `"Module not found"`: Check package.json dependencies
   - `"ENOMEM"`: Build ran out of memory -- simplify the build or split into multiple deploys

3. **If API token expired**:
   - Generate a new token: Netlify Dashboard > User Settings > Applications > Personal access tokens
   - Update `NETLIFY_API_TOKEN` in GitHub Secrets

4. **If deployment artifact too large**:
   - Check what's being included: run `du -sh` on the publish directory locally
   - Add large files to `.netlifyignore`
   - Ensure `node_modules/` and other build artifacts are not in the publish directory

5. **Force redeploy from Netlify**:
   - Go to Netlify Dashboard > [Site] > Deploys
   - Click "Trigger deploy" > "Deploy site"

### Prevention
- Pin Node.js version in `netlify.toml`: `[build.environment] NODE_VERSION = "18"`
- Test builds locally before pushing: `netlify build` (install Netlify CLI)
- Keep deploy artifacts small (static sites should be well under 50MB)
- Set up deploy notifications in Netlify (Slack or email)

---

## 11. Images Not Loading on Subdomain Sites

### Symptom
Subdomain websites load but images show broken image icons or placeholders. The HTML source contains image URLs that return 404 or CORS errors.

### Likely Cause
- Pexels image URLs expired or changed (rare but possible)
- The image URL stored in the database points to a non-existent resource
- CORS policy on the subdomain blocks loading images from pexels.com
- The Netlify site was deployed without the images directory
- The HTML template references local image paths that don't exist on the server

### Fix Steps

1. **Check the image URL directly**: Copy the broken image URL and open it in a new browser tab
   - If 404: The image was removed from Pexels. Need to replace with a new image.
   - If CORS error: Check the browser console for the specific error message.

2. **If images are hosted locally (not Pexels)**:
   - Verify the images directory exists in the Netlify publish directory
   - Check file paths are correct (case-sensitive on Linux/Netlify)
   - Ensure image files were committed to git

3. **If CORS issue**:
   - Add headers to `netlify.toml`:
     ```toml
     [[headers]]
       for = "/*"
       [headers.values]
         Access-Control-Allow-Origin = "*"
     ```

4. **If Pexels URLs expired** (very rare):
   - Update the image URLs in the database or HTML files
   - Re-fetch from Pexels using the stored `pexels_photo_id`

5. **Bulk fix for missing images**:
   ```sql
   -- Find pins with potentially broken images
   SELECT id, brand, title, image_url
   FROM pinterest_pins
   WHERE image_url IS NOT NULL
   ORDER BY created_at DESC
   LIMIT 50;
   ```
   - Test each URL -- replace any that return 404

### Prevention
- Use Pexels' `src.large2x` URLs (they are permanent CDN URLs)
- Consider downloading and self-hosting critical images
- Add image loading error handlers in HTML: `<img onerror="this.src='fallback.jpg'" />`
- Test image loading on all sites during the weekly Friday review

---

## 12. Pin Performance Suddenly Drops

### Symptom
Pinterest analytics show a sudden decline in impressions, saves, or clicks compared to the previous week. This is not a gradual decline but a noticeable drop.

### Likely Cause
- **Pinterest algorithm change**: Pinterest periodically updates its distribution algorithm
- **Account penalty**: Shadow suppression due to spam-like behavior
- **Content quality issue**: Recent pins are lower quality or less relevant
- **Seasonal shift**: The niche topic naturally declines at certain times of year
- **Board health**: A board was flagged or deprioritized
- **Competition increase**: More creators posting similar content
- **Technical issue**: Pins are being created but with broken links or images

### Fix Steps

1. **Rule out technical issues first**:
   - Check that recent pins have working images and destination links
   - Verify pins are appearing on the correct boards
   - Test destination URLs in incognito browser

2. **Check for account penalties**:
   - Look for any Pinterest notifications or emails
   - Check if your profile is visible in Pinterest search (search for your exact username)
   - Ask a friend to search for one of your recent pin titles -- does it appear?

3. **Analyze the timing**:
   - When exactly did the drop start? Correlate with any changes you made
   - Did you increase posting frequency recently?
   - Did you change the content type or style?

4. **Content quality audit**:
   - Review the last 20 pins manually
   - Are titles still creating curiosity gaps?
   - Are images high-quality and relevant?
   - Are descriptions keyword-rich but natural?

5. **Recovery actions**:
   - Reduce posting frequency by 50% for 1 week
   - Focus on your best-performing content types
   - Manually engage with Pinterest (browse, repin, comment)
   - Create 2-3 "hero pins" manually with extra attention to quality
   - After 1 week, gradually increase automation back to normal

### Prevention
- Monitor analytics weekly (Wednesday check in the SOP)
- Set up a simple threshold alert: if weekly impressions drop >30%, investigate
- Maintain posting quality over quantity
- Regularly audit content quality (monthly SOP)
- Stay updated on Pinterest algorithm changes (follow Pinterest's blog and creator community)

---

## 13. Content Sounds Repetitive Despite Dedup

### Symptom
Pins are technically unique (different titles, different topics) but they "feel" the same. The voice, structure, or approach lacks variety. Users or manual review notices a pattern.

### Likely Cause
- Claude is falling into a pattern with similar sentence structures
- The hook frameworks in `content_brain.py` are not being rotated effectively
- The description opener rotation is not working (always picking the same style)
- The visual styles are not rotating
- The topic categories are not being varied (same category picked multiple times in a row)
- The Claude prompt is too rigid, producing templated output

### Fix Steps

1. **Audit recent content for patterns**:
   ```sql
   SELECT title, description_opener, visual_style, angle_framework, category, board
   FROM content_history
   WHERE brand = 'deals'
   ORDER BY created_at DESC
   LIMIT 30;
   ```
   Look for:
   - Same `description_opener` appearing frequently
   - Same `visual_style` dominating
   - Same `category` appearing in clusters
   - Titles all starting with similar words

2. **Increase rotation enforcement**:
   - In `content_brain.py`, increase the "not used in last N" thresholds:
     - Topics: from 10 to 15
     - Angles: from 5 to 8
     - Visual styles: from 4 to all (cycle through all before repeating)
     - Openers: from 5 to all
     - Boards: from 3 to 5

3. **Add variety to the Claude prompt**:
   - Include a "Today's creative constraint" that changes daily:
     - Monday: "Use humor or wit in the title"
     - Tuesday: "Use a number or statistic in the title"
     - Wednesday: "Challenge a common belief"
     - Thursday: "Tell a personal story"
     - Friday: "Ask a provocative question"
     - Saturday: "Use a before/after framing"
     - Sunday: "Start with a bold claim"
   - Add "Your last 5 pins started with [words]. This one MUST start differently."

4. **Diversify hook frameworks**: Add 10-15 new hook frameworks to `content_brain.py` for each brand

5. **Use temperature variation**: Occasionally set Claude's temperature to 0.8-1.0 (default is 1.0) for more creative output, or add a randomized "creative mode" instruction

### Prevention
- Audit content for variety monthly (part of the monthly SOP)
- Rotate hook frameworks on a longer cycle (20+ before repeating)
- Add new hook frameworks quarterly
- Mix up the Claude prompt itself periodically (rephrase instructions, add new constraints)
- Consider using different prompt templates for different days of the week

---

## 14. Board IDs Changed After Pinterest Update

### Symptom
Pins are being posted to the wrong board, or Pinterest API returns "Board not found" errors. Make.com scenarios fail when trying to create pins on specific boards.

### Likely Cause
- Pinterest board IDs can change if a board is renamed, moved, or recreated
- Board merges or archive/unarchive operations can generate new IDs
- Pinterest API version change altered the ID format
- The board was deleted and recreated with the same name but a new ID

### Fix Steps

1. **Get current board IDs via API**:
   ```
   GET https://api.pinterest.com/v5/boards
   Authorization: Bearer YOUR_TOKEN
   ```
   Or use a quick Make.com HTTP module to call this endpoint.

2. **Map board names to new IDs**:

   | Board Name | Old ID | New ID |
   |-----------|--------|--------|
   | | | |
   | | | |

3. **Update IDs in all locations**:
   - Make.com scenarios (Agent 2A and 2B) -- update board_id values
   - GitHub Secrets (`PINTEREST_FITNESS_BOARD_ID`, etc.)
   - Any hardcoded IDs in Python code
   - Supabase records referencing old board IDs (optional cleanup)

4. **If using board names instead of IDs**:
   - Add a board name-to-ID lookup step in the Make.com scenario
   - Before creating a pin, call `GET /v5/boards` and search for the matching board name
   - Cache the mapping in a Make.com data store to avoid repeated lookups

### Prevention
- Use a Make.com Data Store to store board ID mappings (easily updatable)
- Add a board validation step in Agent 2A that checks board existence before pinning
- Check board IDs during the Monday maintenance check
- Set up a simple monthly board audit: call the boards API and compare with stored IDs

---

## General Debugging Procedures

### How to Read Make.com Error Logs

1. Open the scenario in Make.com
2. Click the clock icon (History) in the bottom bar
3. Click on a failed run (red)
4. The failed module is highlighted in red -- click it
5. The "Input" tab shows what was sent
6. The "Output" tab shows the error response
7. The "Logs" tab shows the full request/response cycle

### How to Check Supabase Errors

```sql
-- Recent errors from any source
SELECT id, error_type, error_message,
       context::text as context,
       created_at, resolved
FROM errors
ORDER BY created_at DESC
LIMIT 30;

-- Errors by type (find patterns)
SELECT error_type, COUNT(*), MAX(created_at) as latest
FROM errors
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY error_type
ORDER BY count DESC;
```

### How to Check GitHub Actions Workflow Logs

1. Go to the repository on GitHub
2. Click "Actions" tab
3. Click on the workflow (e.g., "Content Engine")
4. Click on a failed run
5. Click on the job name to see logs
6. Look for red error messages in the log output

### Quick Health Check

Run this sequence to validate all components:

1. **Supabase**: `SELECT 1;` in SQL Editor -- should return instantly
2. **Make.com**: Check scenario status (Active/Inactive) and last run time
3. **Pinterest**: Log in to each account -- no warnings?
4. **Netlify**: Open each site URL -- loads correctly?
5. **GitHub Actions**: Check last workflow run in Actions tab
6. **Claude API**: Check console.anthropic.com for any usage alerts
7. **Pexels**: Check pexels.com/api/dashboard for rate limit status

### Escalation Path

If an issue cannot be resolved with this guide:

1. Check the project's MEMORY.md and CLAUDE.md for known issues
2. Search the errors table for similar past errors
3. Check the respective service's status page
4. Check the respective service's documentation for API changes
5. File a support ticket with the relevant service
