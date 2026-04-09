# Agent 2B Setup Guide -- Scheduled Inline Image Pinner

Step-by-step guide to build the Agent 2B Scheduled Pinner scenario in Make.com from scratch. This scenario works in tandem with Agent 2A -- it picks up the inline images that Agent 2A scheduled and pins them to Pinterest at their designated times with unique, Claude-generated titles.

---

## Architecture Overview

```mermaid
flowchart TD
    A[Schedule Trigger\nEvery 6 hours] --> B[Supabase RPC:\nGet Due Scheduled Pins]
    B --> C{Any pins\ndue?}
    C -->|No| D[Stop - Nothing to do]
    C -->|Yes| E[Iterator: Loop Through\nEach Due Pin]
    E --> F[Claude API: Generate\nUnique Pin Title]
    F --> G[Pinterest API:\nCreate Pin]
    G --> H[Supabase: Mark Pin\nas Completed]
    H --> I[Sleep 3 seconds\nRate Limit Buffer]
    I --> J{More pins\nin batch?}
    J -->|Yes| E
    J -->|No| K[Aggregator: Collect\nAll Results]
    K --> L[Supabase: Log\nBatch Completion]
    L --> M{Any\nfailures?}
    M -->|Yes| N[Send Alert Email]
    M -->|No| O[Done - Silent Success]

    style A fill:#4CAF50,color:#fff
    style F fill:#7C3AED,color:#fff
    style G fill:#E91E63,color:#fff
    style H fill:#FF9800,color:#fff
```

---

## Prerequisites

Before building this scenario, ensure:

- [ ] Agent 2A is built and has run at least once (so `scheduled_pins` has data)
- [ ] Make.com account (same account as Agent 2A)
- [ ] Anthropic API key (same as Agent 2A)
- [ ] Pinterest Business account with API access (same connection as Agent 2A)
- [ ] Supabase project with `scheduled_pins` and `automation_logs` tables (created during Agent 2A setup)
- [ ] The `get_due_scheduled_pins` RPC function exists in Supabase

---

## Step 0: Create the Supabase RPC Function

If not already created during Agent 2A setup, run this SQL:

```sql
CREATE OR REPLACE FUNCTION get_due_scheduled_pins(
    p_current_time TIMESTAMPTZ,
    p_limit INT DEFAULT 10
)
RETURNS SETOF scheduled_pins AS $$
    SELECT sp.*
    FROM scheduled_pins sp
    WHERE sp.pinned = false
      AND sp.scheduled_for <= p_current_time
    ORDER BY sp.scheduled_for ASC
    LIMIT p_limit;
$$ LANGUAGE sql STABLE;
```

### Verify It Works

Test the function in the Supabase SQL Editor:

```sql
SELECT * FROM get_due_scheduled_pins(NOW(), 10);
```

If Agent 2A has run, this should return scheduled pins whose `scheduled_for` timestamp has passed.

---

## Step 1: Create the Scenario

1. Log in to Make.com
2. Click **Create a new scenario**
3. Name it: `Agent 2B - Scheduled Inline Pinner`
4. Click into the blank scenario canvas

---

## Step 2: Add the Schedule Trigger

1. Click the **+** button in the center
2. Search for **Schedule** and select **Basic Scheduler**
3. Configure:
   - **Run scenario**: `At regular intervals`
   - **Minutes**: `360` (every 6 hours)
   - **Time zone**: `America/Los_Angeles`
4. Click **OK**

### Why 6 Hours?

- Agent 2A schedules inline images 6 hours apart
- Running Agent 2B every 6 hours means each check picks up 1-3 due pins
- This creates an organic posting pattern rather than bulk uploads
- Pinterest's algorithm favors consistent, spaced posting

---

## Step 3: Add Supabase RPC -- Get Due Pins

1. Add an **HTTP Make a request** module
2. Toggle **Show advanced settings** ON
3. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/rpc/get_due_scheduled_pins`
   - **Method**: `POST`
   - **Headers**:
     - `apikey` = your Supabase anon key
     - `Authorization` = `Bearer YOUR_SUPABASE_ANON_KEY`
     - `Content-Type` = `application/json`
     - `Prefer` = `return=representation`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "p_current_time": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}",
  "p_limit": 10
}
```

   - **Parse response**: Yes
   - **Timeout**: `15` seconds
4. Click **OK**

### Field Mapping Reference

After running, each item in the response array contains:

| Field | Contains | Used In |
|-------|----------|---------|
| `id` | Scheduled pin record ID | Module 7 (update) |
| `post_id` | Parent listicle post ID | Logging |
| `image_url` | Pexels image URL | Module 6 (Pinterest media) |
| `heading` | List item heading | Module 5 (Claude prompt) |
| `destination_url` | Blog post URL | Module 6 (Pinterest link) |
| `board_id` | Pinterest board ID | Module 6 (Pinterest board) |
| `brand_name` | Brand name | Module 6 (UTM params) |
| `original_post_title` | Parent post title | Module 5 (Claude prompt) |
| `image_description` | Alt text for image | Module 5 (Claude prompt) |

---

## Step 4: Add Filter -- Only Continue If Pins Due

1. Click the line connecting Module 2 to the next module
2. Click **Add a filter**
3. Configure:
   - **Label**: `Pins are due`
   - **Condition**: `{{length(2.data)}}` **Greater than** `0`
4. Click **OK**

This prevents the rest of the scenario from running when there are no pins to process, saving operations.

---

## Step 5: Add Iterator

1. Add a **Flow Control > Iterator** module
2. Configure:
   - **Array**: `{{2.data}}`
3. Click **OK**

This loops through each due pin. With a limit of 10, the iterator runs at most 10 times per execution.

---

## Step 6: Add Claude API -- Generate Unique Pin Title

Inside the iterator loop:

1. Add an **HTTP Make a request** module
2. Toggle **Show advanced settings** ON
3. Configure:
   - **URL**: `https://api.anthropic.com/v1/messages`
   - **Method**: `POST`
   - **Headers**:
     - `x-api-key` = your Anthropic API key
     - `anthropic-version` = `2023-06-01`
     - `content-type` = `application/json`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 150,
  "messages": [
    {
      "role": "user",
      "content": "Generate a unique Pinterest pin title for an inline blog image.\n\nOriginal Blog Post Title: {{4.original_post_title}}\nList Item Heading: {{4.heading}}\nImage Description: {{4.image_description}}\n\nRules:\n1. COMPLETELY different wording from the original title and heading.\n2. If original is a listicle ('7 Best...'), do NOT use listicle format.\n3. Maximum 100 characters.\n4. Include a power word: proven, essential, surprising, overlooked, underrated, honest, worth, smart, simple, tested, affordable, effective.\n5. Create a curiosity gap or promise a specific benefit.\n6. Do not give away the complete answer.\n7. Front-load attention-grabbing words.\n8. Title Case. No hashtags, emojis, or wrapping quotes.\n\nReturn ONLY the title string. Nothing else."
    }
  ]
}
```

   - **Parse response**: Yes
   - **Timeout**: `30` seconds
4. Click **OK**

### Error Handling

Right-click the module and add an error handler:

- **Type**: `Fallback`
- **Fallback output**: Set `generated_title` to `{{substring(4.heading; 0; 100)}}`
- This means if Claude fails, the original list item heading is used as the pin title

### Why max_tokens = 150?

We only need a single title string (under 100 characters). Setting max_tokens to 150 means:
- Faster response times (typically under 2 seconds)
- Lower cost per call
- Prevents Claude from outputting unnecessary explanation

---

## Step 7: Add Pinterest API -- Create Pin

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://api.pinterest.com/v5/pins`
   - **Method**: `POST`
   - **Headers**:
     - `Authorization` = `Bearer YOUR_PINTEREST_ACCESS_TOKEN`
     - `Content-Type` = `application/json`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "board_id": "{{4.board_id}}",
  "title": "{{substring(trim(5.data.content[0].text); 0; 100)}}",
  "description": "{{4.heading}}\n\nFrom our full guide: {{4.original_post_title}}\n\nRead the complete list at the link.",
  "link": "{{4.destination_url}}?utm_source=pinterest&utm_medium=inline_pin&utm_campaign={{lower(replace(4.brand_name; ' '; '_'))}}_listicle&utm_content={{formatDate(now; 'YYYYMMDD')}}",
  "media_source": {
    "source_type": "image_url",
    "url": "{{4.image_url}}"
  },
  "alt_text": "{{ifempty(4.image_description; 4.heading)}}"
}
```

   - **Parse response**: Yes
   - **Timeout**: `30` seconds
3. Click **OK**

### Pin Description Strategy

The pin description is intentionally structured to:
1. **Line 1**: Show the specific list item heading (relevant to the image)
2. **Line 3**: Reference the parent blog post title (creates curiosity about the full list)
3. **Line 5**: Explicit CTA to read the complete list

This drives clicks because the user sees ONE useful item and wants to see the rest.

### UTM Parameter Breakdown

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `utm_source` | `pinterest` | Identify traffic source |
| `utm_medium` | `inline_pin` | Distinguish from `cover_pin` |
| `utm_campaign` | `{brand}_listicle` | Group by brand and content type |
| `utm_content` | `YYYYMMDD` | Track which day the pin was created |

### Error Handling

Add a retry error handler: 3 retries, 15-second interval.

---

## Step 8: Add Supabase -- Mark Pin as Completed

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/scheduled_pins?id=eq.{{4.id}}`
   - **Method**: `PATCH`
   - **Headers**: Standard Supabase headers + `Prefer: return=representation`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "pinned": true,
  "pin_id": "{{6.data.id}}",
  "pin_url": "{{6.data.link}}",
  "generated_title": "{{trim(5.data.content[0].text)}}",
  "pinned_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
}
```

   - **Parse response**: Yes
3. Click **OK**

This update is critical -- it sets `pinned = true` so this record is not picked up again on the next run.

---

## Step 9: Add Rate Limit Delay

1. Add a **Tools > Sleep** module
2. Configure:
   - **Delay**: `3` seconds
3. Click **OK**

### Why 3 Seconds?

- Pinterest API rate limit is 1,000 requests/day
- 3-second delay between pins prevents burst patterns that trigger spam detection
- With max 10 pins per run, this adds 30 seconds maximum
- The delay also prevents Make.com from hitting Anthropic rate limits if many pins are due

---

## Step 10: Add Aggregator

After the iterator closes:

1. Add a **Flow Control > Aggregator** module
2. Configure:
   - **Source module**: Select the Iterator (Module 4)
   - **Aggregated fields**: Map the fields you want to collect:
     - `pin_record_id`: `{{4.id}}`
     - `generated_title`: `{{trim(5.data.content[0].text)}}`
     - `pinterest_pin_id`: `{{6.data.id}}`
     - `brand_name`: `{{4.brand_name}}`
     - `success`: `{{if(6.data.id; true; false)}}`
3. Click **OK**

The aggregator collects results from all iterations into a single array for the completion log.

---

## Step 11: Add Supabase -- Log Batch Completion

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/automation_logs`
   - **Method**: `POST`
   - **Headers**: Standard Supabase headers
   - **Body**:

```json
{
  "scenario": "agent_2b_scheduled_pinner",
  "status": "success",
  "total_due": {{length(2.data)}},
  "total_processed": {{length(9.array)}},
  "total_successful": {{length(filter(9.array; 'item'; item.success = true))}},
  "total_failed": {{length(filter(9.array; 'item'; item.success = false))}},
  "pins_detail": {{toJSON(9.array)}},
  "created_at": "{{formatDate(now; 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}"
}
```

3. Click **OK**

---

## Step 12: Add Error Router

1. Add a **Flow Control > Router** module
2. Create two routes:

### Route 1: Failures Detected

- **Filter label**: `Has Failures`
- **Condition**: `{{length(filter(9.array; 'item'; item.success = false))}}` **Greater than** `0`
- **Module**: Email alert

#### Email Module Configuration

- **To**: Your alert email
- **Subject**: `[Agent 2B Warning] Pin failures detected`
- **Body**:

```
Agent 2B Scheduled Pinner completed with failures.

Total due: {{length(2.data)}}
Successful: {{length(filter(9.array; 'item'; item.success = true))}}
Failed: {{length(filter(9.array; 'item'; item.success = false))}}
Time: {{formatDate(now; 'YYYY-MM-DD HH:mm:ss')}} PST

Failed pins will be retried automatically in the next 6-hour window.

Check automation_logs in Supabase for details.
```

### Route 2: All Successful

- **Filter label**: `All Successful`
- **Condition**: `{{length(filter(9.array; 'item'; item.success = false))}}` **Equal to** `0`
- **Modules**: None (silent success)

---

## Step 13: Testing Procedure

### Prerequisite: Seed Test Data

If Agent 2A has not run yet, manually insert a test scheduled pin:

```sql
INSERT INTO scheduled_pins (
    post_id, image_url, heading, image_description, destination_url,
    board_id, brand_name, original_post_title, scheduled_for
) VALUES (
    1,
    'https://images.pexels.com/photos/1431282/pexels-photo-1431282.jpeg?auto=compress&cs=tinysrgb&w=800',
    'The $12 Drawer Organizer That Fixed My Junk Drawer',
    'Neatly organized kitchen drawer with bamboo dividers',
    'https://dailydealdarling.com/kitchen-tools/',
    'YOUR_PINTEREST_BOARD_ID',
    'Daily Deal Darling',
    '7 Underrated Kitchen Tools That Actually Save Time',
    NOW() - INTERVAL '1 hour'
);
```

### Test 1: Module-by-Module

1. **Supabase RPC**: Should return the test pin (since scheduled_for is in the past)
2. **Filter**: Should pass (1 pin due)
3. **Claude API**: Should return a unique title string
4. **Pinterest API**: Should create a pin
5. **Supabase update**: Should set pinned = true

### Test 2: Full Run

1. Click **Run once**
2. Watch execution
3. Verify in Supabase:
   - `scheduled_pins` record now has `pinned = true`, `pin_id` populated
   - `automation_logs` has a success record
4. Verify on Pinterest: New pin exists with the Claude-generated title

### Test 3: Empty Run

1. Ensure no pins are due (all pinned or scheduled_for is in the future)
2. Run the scenario
3. Verify it stops at the filter (no operations wasted)

### Test 4: Retry Behavior

1. Insert a scheduled pin with an invalid `image_url`
2. Run the scenario
3. Verify the Pinterest API fails for that pin
4. Verify the pin remains with `pinned = false`
5. Fix the image URL
6. Run again -- the pin should be picked up and processed successfully

---

## Step 14: Activation Checklist

Before turning on the schedule:

- [ ] Agent 2A has run at least once and populated `scheduled_pins`
- [ ] The `get_due_scheduled_pins` RPC function exists and works
- [ ] All API connections (Anthropic, Pinterest, Supabase) are working
- [ ] Error handler sends emails to the correct address
- [ ] Full test run completed successfully
- [ ] Claude generates titles that are genuinely different from the original post titles
- [ ] Pinterest pins display correctly (title, description, image, link)
- [ ] UTM parameters are being appended to links
- [ ] Scenario is set to **ON**

---

## Operations Budget

| Component | Ops per Pin | Pins per Run (avg) | Runs per Day | Monthly Ops |
|-----------|------------|-------------------|--------------|-------------|
| Scheduler | 1 | -- | 4 | 120 |
| Supabase RPC | 1 | -- | 4 | 120 |
| Filter | 1 | -- | 4 | 120 |
| Claude API | 1 | 2 | 4 | 240 |
| Pinterest API | 1 | 2 | 4 | 240 |
| Supabase update | 1 | 2 | 4 | 240 |
| Sleep | 1 | 2 | 4 | 240 |
| Aggregator | 1 | -- | 4 | 120 |
| Log + Router | 2 | -- | 4 | 240 |
| **Total** | -- | -- | -- | **~1,680** |

Assumes an average of 2 pins due per 6-hour window (7 pins spread across ~42 hours = ~1-2 per window). Combined with Agent 2A (~1,710 ops), the total is ~3,390 ops/month -- well within the 10,000 free tier.

---

## How Agent 2A and 2B Work Together

### Timeline Example

```
Day 1, 8:00 AM  -- Agent 2A runs
                    Creates listicle post "7 Kitchen Tools That Save Time"
                    Creates cover pin on Pinterest immediately
                    Schedules 7 inline images:
                      Pin 1: Day 1 at 2:00 PM
                      Pin 2: Day 1 at 8:00 PM
                      Pin 3: Day 2 at 2:00 AM
                      Pin 4: Day 2 at 8:00 AM
                      Pin 5: Day 2 at 2:00 PM
                      Pin 6: Day 2 at 8:00 PM
                      Pin 7: Day 3 at 2:00 AM

Day 1, 12:00 PM -- Agent 2B runs
                    Finds Pin 1 is due (scheduled for 2:00 PM? Not yet)
                    No pins due -- stops

Day 1, 6:00 PM  -- Agent 2B runs
                    Finds Pin 1 (due 2:00 PM) and Pin 2 (due 8:00 PM is close)
                    Actually: Pin 1 is due (2:00 PM has passed)
                    Generates unique title via Claude
                    Creates pin on Pinterest
                    Marks as pinned

Day 2, 12:00 AM -- Agent 2B runs
                    Finds Pin 2 (due 8:00 PM yesterday) and Pin 3 (due 2:00 AM)
                    Processes both
                    ...continues every 6 hours...

Day 3, 6:00 AM  -- Agent 2B runs
                    Processes final Pin 7
                    All 7 inline images now pinned
```

### The Result

Over 2-3 days, Pinterest sees 8 total pins from one blog post:
- 1 cover pin (immediate, from Agent 2A)
- 7 inline pins (staggered over ~42 hours, from Agent 2B)

Each pin has a unique title, points to the same blog post, and uses a different image. This drives sustained traffic to the post rather than a single spike.

---

## Maintenance

### Weekly

- Check `automation_logs` for `agent_2b_scheduled_pinner` entries
- Verify `scheduled_pins` table: no old un-pinned records (indicates persistent failures)
- Spot-check 2-3 generated pin titles for quality and uniqueness

### Monthly

- Review Pinterest analytics: do inline pins drive traffic?
- Compare `cover_pin` vs `inline_pin` UTM data in Google Analytics
- Check for any `scheduled_pins` records stuck with `pinned = false` for more than 48 hours

### Monitoring Query

Run this in Supabase to check for stuck pins:

```sql
SELECT id, brand_name, heading, scheduled_for, created_at
FROM scheduled_pins
WHERE pinned = false
  AND scheduled_for < NOW() - INTERVAL '48 hours'
ORDER BY scheduled_for ASC;
```

If results appear, investigate the `automation_logs` for corresponding errors.

### Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| No pins processed | Filter blocks (no pins due) | Check `scheduled_pins` table -- are there unpinned records with past `scheduled_for`? |
| Claude returns full paragraph instead of title | Prompt not strict enough | Verify the prompt ends with "Return ONLY the title string. Nothing else." |
| Pinterest 403 | Board access issue | Verify `board_id` in scheduled_pins matches a board the Pinterest account owns |
| Same pin processed twice | Update failed silently | Check that Module 7 (PATCH) is using the correct `id` filter |
| All pins fail | API key expired | Check Anthropic and Pinterest connections in Make.com |
| Pins created but not marked | Supabase PATCH error | Verify the `scheduled_pins` table has proper grants |
