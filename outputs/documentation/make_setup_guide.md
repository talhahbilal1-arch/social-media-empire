# Make.com Setup Guide -- Pinterest Empire Automation

This guide covers the complete setup of two Make.com scenarios that power the automated Pinterest posting pipeline for Daily Deal Darling and Menopause Planner brands.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Agent 2A -- Listicle Post Creator](#agent-2a----listicle-post-creator)
3. [Agent 2B -- Scheduled Inline Pinner](#agent-2b----scheduled-inline-pinner)
4. [Testing and Validation](#testing-and-validation)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

Before building either scenario, ensure the following are in place:

### Accounts and API Keys

| Service | What You Need | Where to Get It |
|---------|--------------|-----------------|
| Make.com | Pro plan (or higher) for scheduled scenarios | make.com |
| Supabase | Project URL + service_role key | supabase.com dashboard > Settings > API |
| Claude API | API key with billing enabled | console.anthropic.com |
| Pexels | API key (free tier: 200 req/hour) | pexels.com/api |
| Pinterest | Business account + OAuth app | developers.pinterest.com |

### Supabase Tables Required

These tables must exist in the production Supabase project (`epfoxpgrpsnhlsglxvsa`):

- `subdomains` -- Active subdomain sites for destination URLs
- `pinterest_pins` -- Pin tracking and history
- `content_history` -- Content deduplication tracking
- `scheduled_inline_pins` -- Queue for delayed inline image pinning

Run the following SQL if the `scheduled_inline_pins` table does not exist:

```sql
CREATE TABLE IF NOT EXISTS scheduled_inline_pins (
    id BIGSERIAL PRIMARY KEY,
    parent_pin_id BIGINT,
    brand TEXT NOT NULL,
    image_url TEXT NOT NULL,
    image_alt_text TEXT,
    original_title TEXT,
    board_name TEXT,
    destination_url TEXT,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME DEFAULT '12:00:00',
    pinned BOOLEAN DEFAULT FALSE,
    pinned_at TIMESTAMPTZ,
    pin_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scheduled_pins_date ON scheduled_inline_pins(scheduled_date);
CREATE INDEX idx_scheduled_pins_pinned ON scheduled_inline_pins(pinned);

-- Grant access
GRANT ALL ON scheduled_inline_pins TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE scheduled_inline_pins_id_seq TO anon, authenticated, service_role;
```

Also create these RPC functions:

```sql
-- Function: schedule_inline_images
-- Distributes inline images from a listicle across future dates
CREATE OR REPLACE FUNCTION schedule_inline_images(
    p_parent_pin_id BIGINT,
    p_brand TEXT,
    p_images JSONB,
    p_board_name TEXT,
    p_destination_url TEXT
) RETURNS void AS $$
DECLARE
    img JSONB;
    day_offset INT := 1;
BEGIN
    FOR img IN SELECT * FROM jsonb_array_elements(p_images)
    LOOP
        INSERT INTO scheduled_inline_pins (
            parent_pin_id, brand, image_url, image_alt_text,
            original_title, board_name, destination_url,
            scheduled_date
        ) VALUES (
            p_parent_pin_id,
            p_brand,
            img->>'url',
            img->>'alt_text',
            img->>'title',
            p_board_name,
            p_destination_url,
            CURRENT_DATE + day_offset
        );
        day_offset := day_offset + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function: get_todays_scheduled_pins
-- Returns all pins scheduled for today that have not been posted yet
CREATE OR REPLACE FUNCTION get_todays_scheduled_pins()
RETURNS TABLE (
    id BIGINT,
    parent_pin_id BIGINT,
    brand TEXT,
    image_url TEXT,
    image_alt_text TEXT,
    original_title TEXT,
    board_name TEXT,
    destination_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sp.id, sp.parent_pin_id, sp.brand, sp.image_url,
        sp.image_alt_text, sp.original_title, sp.board_name,
        sp.destination_url
    FROM scheduled_inline_pins sp
    WHERE sp.scheduled_date = CURRENT_DATE
      AND sp.pinned = FALSE
    ORDER BY sp.scheduled_time ASC;
END;
$$ LANGUAGE plpgsql;
```

### Make.com Connections to Create

Before building scenarios, create these connections in Make.com (Connections page):

1. **Supabase** -- Use project URL and service_role key (not anon key)
2. **Pinterest** -- OAuth2 connection for each Pinterest business account
3. **HTTP (no auth needed)** -- Used for Claude and Pexels API calls

---

## Agent 2A -- Listicle Post Creator

### Overview

This scenario generates a listicle-style Pinterest post 3 times per day. It calls Claude to write the content, fetches 8 unique images from Pexels, posts the featured image immediately as a pin, and schedules the remaining 7 inline images for future posting via Agent 2B.

### Flowchart

```mermaid
flowchart TD
    A[Schedule Trigger\n8am / 12pm / 5pm PST] --> B[Supabase: Get Random\nActive Subdomain]
    B --> C[Supabase: Get Recent Pins\nfor Deduplication]
    C --> D[HTTP: Claude API\nGenerate Listicle Content]
    D --> E[JSON Parse:\nExtract Listicle Data]
    E --> F[Iterator:\nLoop Through 8 Images]
    F --> G[HTTP: Pexels API\nFetch Image per Item]
    G --> H[Aggregator:\nCollect All Images]
    H --> I[Supabase: Create Record\nStore Post in pinterest_pins]
    I --> J[Supabase RPC:\nschedule_inline_images]
    J --> K[Pinterest: Create Pin\nPost Featured Image]
    K --> L[Supabase: Update Record\nStore pin_id]
    L --> M[End]

    D -- Error --> ERR1[Error Handler:\nLog to Supabase errors table]
    K -- Error --> ERR2[Error Handler:\nLog to Supabase errors table]
```

### Step-by-Step Module Configuration

---

#### Step 1: Schedule Trigger

- **Module**: Schedule
- **Name**: `Listicle Schedule (3x Daily)`
- **Configuration**:
  - Run scenario: **At regular intervals**
  - Interval: Use **Advanced scheduling** with three specific times
  - Time 1: `08:00` (PST) = `16:00 UTC`
  - Time 2: `12:00` (PST) = `20:00 UTC`
  - Time 3: `17:00` (PST) = `01:00 UTC` (next day)
  - Days: Monday through Sunday
  - Time zone: `America/Los_Angeles`

> **Note**: Make.com free tier only allows one schedule. On the Pro plan, use the "Advanced scheduling" option under the scenario settings (gear icon) to set multiple run times.

---

#### Step 2: Supabase -- Get Random Active Subdomain

- **Module**: Supabase > Search Records
- **Name**: `Get Random Subdomain`
- **Connection**: Your Supabase connection
- **Configuration**:
  - Table: `subdomains`
  - Filter:
    - Field: `active`
    - Operator: `Equal to`
    - Value: `true`
  - Limit: `10`
  - Sort: `random()` (use the "Order By" field and type `random()`)

> **Mapping Note**: If your `subdomains` table doesn't exist yet, you can hardcode the subdomain in the next module. The table schema would be:
> ```sql
> CREATE TABLE subdomains (
>     id BIGSERIAL PRIMARY KEY,
>     brand TEXT NOT NULL,
>     subdomain TEXT NOT NULL,
>     base_url TEXT NOT NULL,
>     active BOOLEAN DEFAULT TRUE,
>     created_at TIMESTAMPTZ DEFAULT NOW()
> );
> ```

**Output used downstream**: `{{2.base_url}}`, `{{2.brand}}`, `{{2.subdomain}}`

---

#### Step 3: Supabase -- Get Recent Pins for Deduplication

- **Module**: Supabase > Search Records
- **Name**: `Get Recent Pins (Dedup)`
- **Connection**: Your Supabase connection
- **Configuration**:
  - Table: `pinterest_pins`
  - Filter:
    - Field: `brand`
    - Operator: `Equal to`
    - Value: `{{2.brand}}`
  - Limit: `30`
  - Order By: `created_at` DESC

**Output used downstream**: Array of recent titles and topics for the Claude prompt.

Map the recent titles to a variable using the `map()` function:
```
{{join(map(3.records; "title"); ", ")}}
```

---

#### Step 4: HTTP Module -- Claude API Call (Generate Listicle)

- **Module**: HTTP > Make a request
- **Name**: `Claude: Generate Listicle`
- **Configuration**:
  - URL: `https://api.anthropic.com/v1/messages`
  - Method: `POST`
  - Headers:
    ```
    x-api-key: YOUR_CLAUDE_API_KEY
    anthropic-version: 2023-06-01
    Content-Type: application/json
    ```
  - Body type: `Raw`
  - Content type: `JSON (application/json)`
  - Request content (exact JSON body):

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "You are a Pinterest content strategist creating a listicle pin post.\n\nBRAND: {{2.brand}}\nBASE URL: {{2.base_url}}\n\nRECENTLY POSTED TITLES (do NOT repeat these):\n{{join(map(3.records; \"title\"); \"\\n\")}}\n\nCreate a listicle-style pin post with:\n1. A compelling listicle title (e.g., '8 Kitchen Gadgets That Are Actually Worth Buying')\n2. A 150-300 character Pinterest description with SEO keywords\n3. A Pinterest board name to pin to\n4. 8 list items, each with:\n   - item_title: Short name of the item (3-8 words)\n   - item_description: One sentence about why it's great\n   - image_search_query: SPECIFIC Pexels search query for this item (detailed, not generic)\n   - alt_text: Accessible image description\n\nThe first item is the FEATURED image that will be pinned immediately.\nItems 2-8 are INLINE images that will be pinned individually over the next 7 days.\n\nRULES:\n- Title must create a curiosity gap\n- All 8 image queries must be DIFFERENT and SPECIFIC\n- No generic stock photo terms\n- Description must include 3-5 SEO keywords naturally\n- Board name must match an existing board on the account\n- NO generic phrases: 'must-have', 'game-changer', 'you won't believe'\n\nReturn ONLY this JSON, no markdown or backticks:\n{\n  \"title\": \"...\",\n  \"description\": \"...\",\n  \"board_name\": \"...\",\n  \"destination_url\": \"{{2.base_url}}\",\n  \"items\": [\n    {\n      \"position\": 1,\n      \"item_title\": \"...\",\n      \"item_description\": \"...\",\n      \"image_search_query\": \"...\",\n      \"alt_text\": \"...\"\n    }\n  ]\n}"
    }
  ]
}
```

- **Advanced Settings** (toggle ON):
  - Timeout: `60` seconds
  - Parse response: `Yes`
  - Disable serialization of query string: Leave unchecked

**Error Handling**: Add an Error Handler module (router) that catches 400/429/500 errors and logs them to Supabase.

**Output**: The Claude response is in `{{4.data.content[0].text}}`

---

#### Step 5: JSON Parse Module

- **Module**: JSON > Parse JSON
- **Name**: `Parse Listicle Data`
- **Configuration**:
  - JSON string: `{{4.data.content[].text}}`
  - Data structure: Create a new data structure with these fields:
    - `title` (text)
    - `description` (text)
    - `board_name` (text)
    - `destination_url` (text)
    - `items` (collection/array):
      - `position` (number)
      - `item_title` (text)
      - `item_description` (text)
      - `image_search_query` (text)
      - `alt_text` (text)

> **Tip**: You can auto-generate the data structure by pasting a sample JSON response in Make.com's data structure generator.

---

#### Step 6: Iterator -- Loop Through 8 Images

- **Module**: Flow Control > Iterator
- **Name**: `Loop Images`
- **Configuration**:
  - Array: `{{5.items}}`

This will iterate once per list item (8 times total).

---

#### Step 7: HTTP Module -- Pexels API (Per Image)

- **Module**: HTTP > Make a request
- **Name**: `Pexels: Fetch Image`
- **Configuration**:
  - URL: `https://api.pexels.com/v1/search`
  - Method: `GET`
  - Headers:
    ```
    Authorization: YOUR_PEXELS_API_KEY
    ```
  - Query String:
    - `query`: `{{6.image_search_query}}`
    - `per_page`: `5`
    - `orientation`: `portrait`
    - `size`: `large`
  - Parse response: `Yes`

**Output mapping**: Use `{{7.data.photos[1].src.large2x}}` for the image URL. Using index `[1]` (the first photo) ensures you get the top result. If you want variety, use `{{7.data.photos[floor(random() * min(length(7.data.photos); 3)) + 1].src.large2x}}`.

---

#### Step 8: Aggregator -- Collect All Images

After the iterator completes, add an Array Aggregator to collect all results:

- **Module**: Tools > Array aggregator
- **Name**: `Collect Images`
- **Source Module**: Module 7 (Pexels)
- **Target structure type**: Custom
- **Aggregated fields**:
  - `position`: `{{6.position}}`
  - `item_title`: `{{6.item_title}}`
  - `item_description`: `{{6.item_description}}`
  - `image_url`: `{{7.data.photos[1].src.large2x}}`
  - `alt_text`: `{{6.alt_text}}`
  - `pexels_photo_id`: `{{7.data.photos[1].id}}`

---

#### Step 9: Supabase -- Create Record (Store Post)

- **Module**: Supabase > Create a Record
- **Name**: `Store Post in pinterest_pins`
- **Connection**: Your Supabase connection
- **Configuration**:
  - Table: `pinterest_pins`
  - Fields:
    - `brand`: `{{2.brand}}`
    - `title`: `{{5.title}}`
    - `description`: `{{5.description}}`
    - `board_name`: `{{5.board_name}}`
    - `destination_url`: `{{5.destination_url}}`
    - `featured_image_url`: `{{8.array[1].image_url}}`
    - `items_data`: `{{toString(8.array)}}` (JSON string of all items)
    - `status`: `pending`
    - `created_at`: `{{now}}`

**Output**: `{{9.id}}` -- the new record ID, used to link inline pins.

---

#### Step 10: Supabase RPC -- Schedule Inline Images

- **Module**: HTTP > Make a request (calling Supabase RPC)
- **Name**: `Schedule Inline Images`
- **Configuration**:
  - URL: `https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/rpc/schedule_inline_images`
  - Method: `POST`
  - Headers:
    ```
    apikey: YOUR_SUPABASE_SERVICE_ROLE_KEY
    Authorization: Bearer YOUR_SUPABASE_SERVICE_ROLE_KEY
    Content-Type: application/json
    Prefer: return=minimal
    ```
  - Body (JSON):

```json
{
  "p_parent_pin_id": {{9.id}},
  "p_brand": "{{2.brand}}",
  "p_images": {{toString(slice(8.array; 1; 8))}},
  "p_board_name": "{{5.board_name}}",
  "p_destination_url": "{{5.destination_url}}"
}
```

> **Note**: `slice(8.array; 1; 8)` gets items 2-8 (skipping the featured image at position 0).

---

#### Step 11: Pinterest -- Create Pin (Featured Image)

- **Module**: Pinterest > Create a Pin
- **Name**: `Pin Featured Image`
- **Connection**: Your Pinterest OAuth connection
- **Configuration**:
  - Board: Use a Router or lookup to match `{{5.board_name}}` to a board ID. Alternatively, use the Pinterest API HTTP module:
    - URL: `https://api.pinterest.com/v5/pins`
    - Method: `POST`
    - Headers:
      ```
      Authorization: Bearer YOUR_PINTEREST_ACCESS_TOKEN
      Content-Type: application/json
      ```
    - Body:
    ```json
    {
      "title": "{{5.title}}",
      "description": "{{5.description}}",
      "board_id": "YOUR_BOARD_ID",
      "media_source": {
        "source_type": "image_url",
        "url": "{{8.array[1].image_url}}"
      },
      "link": "{{5.destination_url}}?utm_source=pinterest&utm_medium=make_s1&utm_campaign={{2.brand}}_listicle"
    }
    ```

**Output**: `{{11.data.id}}` -- the Pinterest pin ID.

---

#### Step 12: Supabase -- Update Record (Store Pin ID)

- **Module**: Supabase > Update a Record
- **Name**: `Store Pin ID`
- **Connection**: Your Supabase connection
- **Configuration**:
  - Table: `pinterest_pins`
  - Record ID: `{{9.id}}`
  - Fields:
    - `pin_id`: `{{11.data.id}}`
    - `status`: `posted`
    - `pinned_at`: `{{now}}`

---

#### Step 13: Error Handler Router

Add an error handler route at the scenario level:

- **Module**: Router (Error Handler)
- **Route 1**: On HTTP 429 (Rate Limit)
  - Filter: `{{error.statusCode}}` equals `429`
  - Action: Tools > Sleep for `60` seconds, then retry (use the "Retry" directive)
- **Route 2**: On HTTP 400/500
  - Filter: `{{error.statusCode}}` is in `400, 500, 502, 503`
  - Action: Supabase > Create Record in `errors` table:
    - `error_type`: `make_agent_2a`
    - `error_message`: `{{error.message}}`
    - `context`: `{"brand": "{{2.brand}}", "step": "{{error.moduleName}}", "status_code": "{{error.statusCode}}"}`
    - `created_at`: `{{now}}`

---

## Agent 2B -- Scheduled Inline Pinner

### Overview

This scenario runs every 6 hours, checks for inline images scheduled for today, generates a unique pin title for each (different from the original listicle title), posts them to Pinterest, and marks them as completed.

### Flowchart

```mermaid
flowchart TD
    A[Schedule Trigger\nEvery 6 Hours] --> B[Supabase RPC:\nget_todays_scheduled_pins]
    B --> C{Any Pins\nScheduled?}
    C -- No --> END1[End: Nothing to Post]
    C -- Yes --> D[Iterator:\nFor Each Scheduled Pin]
    D --> E[HTTP: Claude API\nGenerate Unique Pin Title]
    E --> F[Pinterest: Create Pin\nPost Inline Image]
    F --> G[Supabase: Update Record\nSet pinned=true + pin_id]
    G --> D
    D -- Done --> H[Aggregator:\nCount Completed Pins]
    H --> END2[End: Log Summary]

    E -- Error --> ERR[Error Handler:\nSkip Pin + Log Error]
    F -- Error --> ERR
```

### Step-by-Step Module Configuration

---

#### Step 1: Schedule Trigger

- **Module**: Schedule
- **Name**: `Inline Pinner Schedule (Every 6h)`
- **Configuration**:
  - Run scenario: **At regular intervals**
  - Interval: `6` hours
  - Time zone: `America/Los_Angeles`

---

#### Step 2: Supabase RPC -- Get Today's Scheduled Pins

- **Module**: HTTP > Make a request
- **Name**: `Get Scheduled Pins`
- **Configuration**:
  - URL: `https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/rpc/get_todays_scheduled_pins`
  - Method: `POST`
  - Headers:
    ```
    apikey: YOUR_SUPABASE_SERVICE_ROLE_KEY
    Authorization: Bearer YOUR_SUPABASE_SERVICE_ROLE_KEY
    Content-Type: application/json
    ```
  - Body: `{}` (empty JSON object -- the function takes no parameters)
  - Parse response: `Yes`

**Output**: Array of scheduled pin objects with `id`, `image_url`, `original_title`, `board_name`, `destination_url`, `brand`.

---

#### Step 3: Router -- Check if Any Pins Exist

- **Module**: Router
- **Route 1 Filter**: `{{length(2.data)}}` greater than `0`
  - Continues to Iterator
- **Route 2 Filter**: `{{length(2.data)}}` equals `0`
  - Connects to an empty end module (nothing to do)

---

#### Step 4: Iterator -- For Each Scheduled Pin

- **Module**: Flow Control > Iterator
- **Name**: `Loop Scheduled Pins`
- **Configuration**:
  - Array: `{{2.data}}`

---

#### Step 5: HTTP Module -- Claude API (Generate Unique Title)

- **Module**: HTTP > Make a request
- **Name**: `Claude: Generate Pin Title`
- **Configuration**:
  - URL: `https://api.anthropic.com/v1/messages`
  - Method: `POST`
  - Headers:
    ```
    x-api-key: YOUR_CLAUDE_API_KEY
    anthropic-version: 2023-06-01
    Content-Type: application/json
    ```
  - Body (JSON):

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 300,
  "messages": [
    {
      "role": "user",
      "content": "Generate a unique Pinterest pin title and description for this image.\n\nBRAND: {{4.brand}}\nORIGINAL LISTICLE TITLE: {{4.original_title}}\nIMAGE DESCRIPTION: {{4.image_alt_text}}\n\nThe new title must be COMPLETELY DIFFERENT from the original. Use a different angle, different hook, different framing. It should stand alone as its own pin.\n\nRULES:\n- Title under 100 characters\n- Creates curiosity gap\n- No generic phrases\n- Description 100-200 characters with 2-3 SEO keywords\n\nReturn ONLY this JSON:\n{\"title\": \"...\", \"description\": \"...\"}"
    }
  ]
}
```

  - Advanced Settings: Toggle ON
  - Timeout: `30` seconds
  - Parse response: `Yes`

**Error Handling**: Attach a Break error handler that skips this pin on failure and continues to the next.

---

#### Step 6: JSON Parse (Title Response)

- **Module**: JSON > Parse JSON
- **Name**: `Parse Title`
- **Configuration**:
  - JSON string: `{{5.data.content[].text}}`

---

#### Step 7: Pinterest -- Create Pin (Inline Image)

- **Module**: HTTP > Make a request (Pinterest API)
- **Name**: `Pin Inline Image`
- **Configuration**:
  - URL: `https://api.pinterest.com/v5/pins`
  - Method: `POST`
  - Headers:
    ```
    Authorization: Bearer YOUR_PINTEREST_ACCESS_TOKEN
    Content-Type: application/json
    ```
  - Body:

```json
{
  "title": "{{6.title}}",
  "description": "{{6.description}}",
  "board_id": "YOUR_BOARD_ID",
  "media_source": {
    "source_type": "image_url",
    "url": "{{4.image_url}}"
  },
  "link": "{{4.destination_url}}?utm_source=pinterest&utm_medium=make_inline&utm_campaign={{4.brand}}_inline"
}
```

  - Parse response: `Yes`

> **Board ID Mapping**: If you have multiple boards, use a lookup table or a Switch module to map `{{4.board_name}}` to the correct board ID.

---

#### Step 8: Supabase -- Update Record (Mark as Pinned)

- **Module**: HTTP > Make a request (Supabase REST API)
- **Name**: `Mark Pin Complete`
- **Configuration**:
  - URL: `https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/scheduled_inline_pins?id=eq.{{4.id}}`
  - Method: `PATCH`
  - Headers:
    ```
    apikey: YOUR_SUPABASE_SERVICE_ROLE_KEY
    Authorization: Bearer YOUR_SUPABASE_SERVICE_ROLE_KEY
    Content-Type: application/json
    Prefer: return=minimal
    ```
  - Body:

```json
{
  "pinned": true,
  "pinned_at": "{{now}}",
  "pin_id": "{{7.data.id}}"
}
```

---

#### Step 9: Aggregator -- Count Completed Pins

- **Module**: Tools > Numeric aggregator
- **Name**: `Count Posted`
- **Source Module**: Module 8 (Supabase Update)
- **Aggregated value**: `1` (counts each successful update)

---

#### Step 10: Error Handler

- **Module**: Error Handler (attached to modules 5, 6, 7)
- **Type**: `Break` (skip current item, continue iteration)
- **Action**: Supabase > Create Record in `errors` table:
  - `error_type`: `make_agent_2b`
  - `error_message`: `{{error.message}}`
  - `context`: `{"scheduled_pin_id": "{{4.id}}", "brand": "{{4.brand}}", "step": "{{error.moduleName}}"}`
  - `created_at`: `{{now}}`

---

## Testing and Validation

### Agent 2A Testing Checklist

- [ ] Run scenario manually once with a single brand
- [ ] Verify Claude returns valid JSON (check module 5 output)
- [ ] Verify all 8 Pexels images return successfully (check module 7 outputs)
- [ ] Verify the `pinterest_pins` record was created in Supabase
- [ ] Verify 7 rows were inserted into `scheduled_inline_pins`
- [ ] Verify the Pinterest pin was created (check Pinterest board)
- [ ] Verify `pin_id` was stored back in the `pinterest_pins` record
- [ ] Run 3 times to test deduplication (titles should differ)

### Agent 2B Testing Checklist

- [ ] Insert a test row into `scheduled_inline_pins` with `scheduled_date = today` and `pinned = false`
- [ ] Run the scenario manually
- [ ] Verify Claude generated a different title than the `original_title`
- [ ] Verify the pin was created on Pinterest
- [ ] Verify the `scheduled_inline_pins` row was updated (`pinned = true`, `pin_id` populated)
- [ ] Test with zero scheduled pins (should exit gracefully)

### Validation Queries

```sql
-- Check recent pinterest_pins entries
SELECT id, brand, title, pin_id, status, created_at
FROM pinterest_pins
ORDER BY created_at DESC
LIMIT 10;

-- Check today's scheduled inline pins
SELECT * FROM scheduled_inline_pins
WHERE scheduled_date = CURRENT_DATE
ORDER BY id;

-- Check for errors from Make.com
SELECT * FROM errors
WHERE error_type IN ('make_agent_2a', 'make_agent_2b')
ORDER BY created_at DESC
LIMIT 20;
```

---

## Monitoring and Maintenance

### Scenario Settings (Both Agents)

| Setting | Value |
|---------|-------|
| Max errors before stop | 3 (prevents runaway spending on Claude API) |
| Sequential processing | ON (prevents duplicate pins) |
| Data is confidential | ON |
| Incomplete executions | Store for 15 days |

### Monthly Operations Budget

| Component | Monthly Usage | Estimated Cost |
|-----------|--------------|----------------|
| Make.com operations (2A) | ~90 runs x ~15 ops = 1,350 ops | Included in Pro plan |
| Make.com operations (2B) | ~120 runs x ~8 ops = 960 ops | Included in Pro plan |
| Claude API (2A) | ~90 calls x ~4K tokens = 360K tokens | ~$1.50 |
| Claude API (2B) | ~210 calls x ~500 tokens = 105K tokens | ~$0.40 |
| Pexels API | ~720 calls | Free |
| **Total** | | **~$2/month + Make.com plan** |

### Export Scenarios (Weekly Backup)

1. Open each scenario in Make.com
2. Click the three-dot menu (bottom-left)
3. Select **Export Blueprint**
4. Save the JSON file to `outputs/documentation/make_backups/`

---

## Appendix: Make.com Module Quick Reference

| Module Type | Use Case | Notes |
|-------------|----------|-------|
| HTTP > Make a request | Claude API, Pexels API, Supabase RPC | Toggle "Advanced settings" ON for timeout control |
| Supabase > Search Records | Read from tables | Use service_role key |
| Supabase > Create a Record | Insert rows | Use service_role key |
| Supabase > Update a Record | Update rows | Requires record ID |
| JSON > Parse JSON | Parse Claude responses | Define data structure first |
| Flow Control > Iterator | Loop through arrays | Connect aggregator after |
| Tools > Array aggregator | Collect iterator results | Must specify source module |
| Router | Conditional branching | Set filters on each route |
| Error Handler | Catch and handle errors | Break = skip, Retry = retry |
