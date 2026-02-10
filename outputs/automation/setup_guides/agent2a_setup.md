# Agent 2A Setup Guide -- Listicle Post Creator

Step-by-step guide to build the Agent 2A Listicle Post Creator scenario in Make.com from scratch.

---

## Architecture Overview

```mermaid
flowchart TD
    A[Schedule Trigger\n3x daily: 8am, 12pm, 5pm PST] --> B[Supabase: Get Random\nActive Subdomain]
    B --> C[Supabase: Get Recent\nPosts for Deduplication]
    C --> D[Claude API: Generate\n7-Item Listicle JSON]
    D --> E[Parse JSON Response]
    E --> F[Iterator: Loop Through\n7 List Items]
    F --> G[Pexels API: Fetch\nImage per Item]
    G --> H{All Images\nFetched?}
    H -->|Yes| I[Supabase: Create\nListicle Post Record]
    I --> J[Supabase RPC:\nSchedule Inline Images]
    J --> K[Pinterest API:\nCreate Cover Pin]
    K --> L[Supabase: Update Post\nwith Pin ID]
    L --> M{Success?}
    M -->|Yes| N[Log Success]
    M -->|No| O[Log Error +\nSend Alert Email]

    style A fill:#4CAF50,color:#fff
    style D fill:#7C3AED,color:#fff
    style G fill:#2196F3,color:#fff
    style K fill:#E91E63,color:#fff
    style I fill:#FF9800,color:#fff
```

---

## Prerequisites

Before starting, ensure you have:

- [ ] Make.com account (Free tier works; Pro recommended for reliability)
- [ ] Anthropic API key with Claude access
- [ ] Pexels API key (free at pexels.com/api)
- [ ] Pinterest Business account with API access
- [ ] Supabase project with the required tables created (see Step 0)
- [ ] Alert email address for error notifications

---

## Step 0: Prepare Supabase Tables

Run the following SQL in your Supabase SQL Editor before building the scenario.

### subdomains table

```sql
CREATE TABLE IF NOT EXISTS subdomains (
    id BIGSERIAL PRIMARY KEY,
    brand_name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    target_audience TEXT,
    brand_voice TEXT,
    base_url TEXT NOT NULL,
    pinterest_board_id TEXT NOT NULL,
    next_topic TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert your subdomains
INSERT INTO subdomains (brand_name, slug, category, target_audience, brand_voice, base_url, pinterest_board_id, is_active)
VALUES
    ('Daily Deal Darling', 'ddd-kitchen', 'kitchen', 'Budget-conscious women 25-45 who love home and kitchen finds', 'Casual, excited, honest product reviewer. First person. Price-conscious.', 'https://dailydealdarling.com', 'YOUR_BOARD_ID_HERE', true),
    ('Daily Deal Darling', 'ddd-home-decor', 'home_decor', 'Women 25-45 decorating on a budget', 'Warm, relatable, specific about products and prices.', 'https://dailydealdarling.com', 'YOUR_BOARD_ID_HERE', true),
    ('Fit Over 35', 'fo35-workouts', 'workouts', 'Men 35-55 who train seriously', 'Direct, knowledgeable training partner. Specific numbers always.', 'https://fitover35.com', 'YOUR_BOARD_ID_HERE', true),
    ('Fit Over 35', 'fo35-nutrition', 'nutrition', 'Men 35-55 focused on diet for muscle and fat loss', 'Evidence-based, no bro-science, real food quantities.', 'https://fitover35.com', 'YOUR_BOARD_ID_HERE', true);

-- Grant access
GRANT ALL ON subdomains TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE subdomains_id_seq TO anon, authenticated, service_role;
```

### listicle_posts table

```sql
CREATE TABLE IF NOT EXISTS listicle_posts (
    id BIGSERIAL PRIMARY KEY,
    subdomain_id BIGINT REFERENCES subdomains(id),
    brand_name TEXT NOT NULL,
    subdomain_category TEXT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    meta_description TEXT,
    introduction TEXT,
    list_items JSONB,
    conclusion TEXT,
    tags JSONB,
    featured_image_url TEXT,
    cover_pin_id TEXT,
    cover_pin_url TEXT,
    cover_pin_created BOOLEAN DEFAULT false,
    inline_images_scheduled BOOLEAN DEFAULT false,
    scheduled_pin_count INTEGER DEFAULT 0,
    word_count INTEGER,
    status TEXT DEFAULT 'published',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_listicle_posts_subdomain ON listicle_posts(subdomain_id);
CREATE INDEX idx_listicle_posts_created ON listicle_posts(created_at DESC);

GRANT ALL ON listicle_posts TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE listicle_posts_id_seq TO anon, authenticated, service_role;
```

### scheduled_pins table

```sql
CREATE TABLE IF NOT EXISTS scheduled_pins (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT REFERENCES listicle_posts(id),
    image_url TEXT NOT NULL,
    heading TEXT NOT NULL,
    image_description TEXT,
    image_keyword TEXT,
    amazon_product TEXT,
    destination_url TEXT NOT NULL,
    board_id TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    original_post_title TEXT,
    scheduled_for TIMESTAMPTZ NOT NULL,
    pinned BOOLEAN DEFAULT false,
    pin_id TEXT,
    pin_url TEXT,
    generated_title TEXT,
    pinned_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scheduled_pins_due ON scheduled_pins(pinned, scheduled_for);
CREATE INDEX idx_scheduled_pins_post ON scheduled_pins(post_id);

GRANT ALL ON scheduled_pins TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE scheduled_pins_id_seq TO anon, authenticated, service_role;
```

### schedule_inline_images RPC function

```sql
CREATE OR REPLACE FUNCTION schedule_inline_images(
    p_post_id BIGINT,
    p_list_items JSONB,
    p_base_url TEXT,
    p_post_slug TEXT,
    p_brand_name TEXT,
    p_board_id TEXT,
    p_schedule_start TIMESTAMPTZ,
    p_schedule_interval_hours INT DEFAULT 6
)
RETURNS JSONB AS $$
DECLARE
    item JSONB;
    i INT := 0;
    scheduled_time TIMESTAMPTZ;
    total_scheduled INT := 0;
    first_time TIMESTAMPTZ;
    last_time TIMESTAMPTZ;
BEGIN
    FOR item IN SELECT * FROM jsonb_array_elements(p_list_items)
    LOOP
        scheduled_time := p_schedule_start + (i * (p_schedule_interval_hours || ' hours')::INTERVAL);

        INSERT INTO scheduled_pins (
            post_id, image_url, heading, image_description, image_keyword,
            amazon_product, destination_url, board_id, brand_name,
            original_post_title, scheduled_for
        ) VALUES (
            p_post_id,
            item->>'image_url',
            item->>'heading',
            item->>'heading',
            item->>'image_keyword',
            item->>'amazon_product',
            p_base_url || '/' || p_post_slug || '/',
            p_board_id,
            p_brand_name,
            (SELECT title FROM listicle_posts WHERE id = p_post_id),
            scheduled_time
        );

        IF i = 0 THEN first_time := scheduled_time; END IF;
        last_time := scheduled_time;
        i := i + 1;
        total_scheduled := total_scheduled + 1;
    END LOOP;

    -- Update the post record
    UPDATE listicle_posts
    SET inline_images_scheduled = true, scheduled_pin_count = total_scheduled
    WHERE id = p_post_id;

    RETURN jsonb_build_object(
        'scheduled_count', total_scheduled,
        'first_pin_at', first_time,
        'last_pin_at', last_time
    );
END;
$$ LANGUAGE plpgsql;
```

### automation_logs table

```sql
CREATE TABLE IF NOT EXISTS automation_logs (
    id BIGSERIAL PRIMARY KEY,
    scenario TEXT NOT NULL,
    status TEXT NOT NULL,
    brand TEXT,
    subdomain_category TEXT,
    post_title TEXT,
    post_id BIGINT,
    cover_pin_id TEXT,
    scheduled_inline_pins INT,
    images_fetched INT,
    total_due INT,
    total_processed INT,
    total_successful INT,
    total_failed INT,
    pins_detail JSONB,
    error_module TEXT,
    error_message TEXT,
    error_type TEXT,
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_automation_logs_scenario ON automation_logs(scenario, created_at DESC);

GRANT ALL ON automation_logs TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE automation_logs_id_seq TO anon, authenticated, service_role;
```

---

## Step 1: Create the Scenario

1. Log in to Make.com
2. Click **Create a new scenario** (top right, purple button)
3. Name it: `Agent 2A - Listicle Post Creator`
4. Click into the blank scenario canvas

---

## Step 2: Add the Schedule Trigger

1. Click the **+** button in the center of the canvas
2. Search for **Schedule** and select **Basic Scheduler**
3. Configure:
   - **Run scenario**: `At specific days and times`
   - **Days**: Select all 7 days
   - **Times**: Add three entries: `08:00`, `12:00`, `17:00`
   - **Time zone**: `America/Los_Angeles`
4. Click **OK** to save

---

## Step 3: Add Supabase -- Get Random Subdomain

1. Click the **+** after the scheduler to add a new module
2. Search for **HTTP** and select **Make a request**
3. Toggle **Show advanced settings** ON
4. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/subdomains?select=*&is_active=eq.true&order=random()&limit=1`
   - **Method**: `GET`
   - **Headers**:
     - `apikey` = your Supabase anon key
     - `Authorization` = `Bearer YOUR_SUPABASE_ANON_KEY`
     - `Content-Type` = `application/json`
   - **Parse response**: Yes
5. Click **OK**
6. **Test this module**: Click "Run this module only" to verify you get a subdomain back

### Field Mapping Reference

After running, you will see the output structure. The key fields to reference later:

| Field Path | Contains | Used In |
|-----------|----------|---------|
| `data[0].id` | Subdomain ID | Module 3 filter, Module 8 post record |
| `data[0].brand_name` | Brand name | Module 4 prompt, Module 8, Module 10 |
| `data[0].category` | Category slug | Module 4 prompt, Module 8 |
| `data[0].target_audience` | Audience description | Module 4 prompt |
| `data[0].brand_voice` | Voice guidelines | Module 4 prompt |
| `data[0].base_url` | Website base URL | Module 9 RPC, Module 10 pin link |
| `data[0].pinterest_board_id` | Board ID | Module 9 RPC, Module 10 pin |

---

## Step 4: Add Supabase -- Get Recent Posts

1. Add another **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/listicle_posts?select=id,title,topic,subdomain_category,created_at&subdomain_id=eq.{{2.data[0].id}}&order=created_at.desc&limit=15`
   - **Method**: `GET`
   - **Headers**: Same Supabase headers as Step 3
   - **Parse response**: Yes
3. Click **OK**

### Mapping the Recent Posts for Claude

After this module, add a **Set Variable** module (optional but recommended):

- Variable name: `recent_posts_formatted`
- Value: Use Make.com's `join()` and `map()` functions to format the array into a readable string for the Claude prompt

Alternatively, you can format this directly in the Claude prompt body using Make.com string concatenation.

---

## Step 5: Add Claude API -- Generate Listicle

This is the core content generation step.

1. Add an **HTTP Make a request** module
2. Toggle **Show advanced settings** ON
3. Configure:
   - **URL**: `https://api.anthropic.com/v1/messages`
   - **Method**: `POST`
   - **Headers**:
     - `x-api-key` = your Anthropic API key
     - `anthropic-version` = `2023-06-01`
     - `content-type` = `application/json`
   - **Body type**: `Raw`
   - **Content type**: `JSON (application/json)`
   - **Request content**: See the full request body below
   - **Parse response**: Yes
   - **Timeout**: `120` seconds (important -- content generation takes 30-60s)

### Request Body

Paste this into the Request content field (replacing the Make.com variables with mapped values):

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "You are the content engine for a lifestyle brand's blog. Generate a 7-item listicle.\n\nBrand: {{2.data[0].brand_name}}\nAudience: {{2.data[0].target_audience}}\nCategory: {{2.data[0].category}}\nTopic: {{2.data[0].next_topic}}\n\nBrand Voice:\n{{2.data[0].brand_voice}}\n\nRecent posts (do not duplicate):\n{{3.recent_posts_formatted}}\n\nReturn ONLY JSON with: title (50-65 chars), meta_description (155 chars max), introduction (120-180 words), list_items (array of 7, each with heading, content (150-200 words, 2-3 paragraphs), image_keyword (5-8 words for Pexels), amazon_product (real product: Name | $price | ASIN or N/A)), conclusion (80-120 words), tags (array of 5).\n\nRules: Each heading starts with a different word. Every item has a specific number. At least 2 items have caveats. No banned phrases. Real Amazon products only.\n\nReturn ONLY the JSON. No markdown fences."
    }
  ]
}
```

**Important**: The full prompt from `claude_prompts/listicle_generator.md` should be used in production. The above is a condensed version for readability. Copy the complete prompt template and replace the `{placeholders}` with Make.com `{{module.field}}` references.

4. Click **OK**

### Error Handling

Right-click the module and select **Add error handler**:

- **Error handler type**: `Retry`
- **Number of retries**: `2`
- **Interval between retries**: `10` seconds

---

## Step 6: Add JSON Parse Module

1. Add a **JSON > Parse JSON** module
2. Configure:
   - **JSON string**: `{{4.data.content[0].text}}`
3. Click **OK**

### Handling Markdown Fences

Claude sometimes wraps JSON in markdown fences. Add a **Text parser > Replace** module before the JSON parse as a safety measure:

- **Pattern**: `` ^```json\n?|\n?```$ ``
- **Replacement**: (empty)
- **Global**: Yes
- **Input**: `{{4.data.content[0].text}}`

Then feed the cleaned output into the JSON parse module.

---

## Step 7: Add Iterator for List Items

1. Add a **Flow Control > Iterator** module
2. Configure:
   - **Array**: `{{5.list_items}}` (the parsed list_items array)
3. Click **OK**

This will loop through each of the 7 list items, executing the next module once per item.

---

## Step 8: Add Pexels API -- Fetch Images

Inside the iterator loop:

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://api.pexels.com/v1/search?query={{encodeURL(6.image_keyword)}}&orientation=landscape&per_page=5&size=large`
   - **Method**: `GET`
   - **Headers**:
     - `Authorization` = your Pexels API key
   - **Parse response**: Yes
3. Click **OK**

### Image Selection Logic

Map the image URL with a fallback:

- **Primary**: `{{7.data.photos[0].src.large}}`
- **Fallback**: `https://images.pexels.com/photos/1431282/pexels-photo-1431282.jpeg?auto=compress&cs=tinysrgb&w=800`

Use Make.com's `ifempty()` function: `{{ifempty(7.data.photos[0].src.large; 'FALLBACK_URL')}}`

---

## Step 9: Add Supabase -- Create Post Record

After the iterator completes (place this module AFTER the iterator closes):

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/listicle_posts`
   - **Method**: `POST`
   - **Headers**: Standard Supabase headers + `Prefer: return=representation`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "subdomain_id": "{{2.data[0].id}}",
  "brand_name": "{{2.data[0].brand_name}}",
  "subdomain_category": "{{2.data[0].category}}",
  "title": "{{5.title}}",
  "slug": "YOUR_SLUG_GENERATION_LOGIC",
  "meta_description": "{{5.meta_description}}",
  "introduction": "{{5.introduction}}",
  "list_items": {{toJSON(5.list_items)}},
  "conclusion": "{{5.conclusion}}",
  "tags": {{toJSON(5.tags)}},
  "featured_image_url": "{{7.image_url}}",
  "status": "published"
}
```

   - **Parse response**: Yes
3. Click **OK**

### Slug Generation

In Make.com, generate the slug using chained `replace()` functions:

```
{{replace(replace(replace(lower(5.title); '/[^a-z0-9\\s-]/g'; ''); '/\\s+/g'; '-'); '/-+/g'; '-')}}
```

Or use a **Set Variable** module before this step to pre-compute the slug.

---

## Step 10: Add Supabase RPC -- Schedule Inline Images

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/rpc/schedule_inline_images`
   - **Method**: `POST`
   - **Headers**: Standard Supabase headers + `Prefer: return=representation`
   - **Body type**: `Raw` / `JSON`
   - **Request content**:

```json
{
  "p_post_id": {{8.data[0].id}},
  "p_list_items": {{toJSON(5.list_items)}},
  "p_base_url": "{{2.data[0].base_url}}",
  "p_post_slug": "{{8.data[0].slug}}",
  "p_brand_name": "{{2.data[0].brand_name}}",
  "p_board_id": "{{2.data[0].pinterest_board_id}}",
  "p_schedule_start": "{{formatDate(addHours(now; 6); 'YYYY-MM-DDTHH:mm:ss.SSSZ')}}",
  "p_schedule_interval_hours": 6
}
```

   - **Parse response**: Yes
3. Click **OK**

---

## Step 11: Add Pinterest API -- Create Cover Pin

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
  "board_id": "{{2.data[0].pinterest_board_id}}",
  "title": "{{substring(5.title; 0; 100)}}",
  "description": "{{5.meta_description}}\n\nIn this guide:\n- {{5.list_items[0].heading}}\n- {{5.list_items[1].heading}}\n- {{5.list_items[2].heading}}\n... and 4 more.\n\nFull list at the link.",
  "link": "{{2.data[0].base_url}}/{{8.data[0].slug}}/?utm_source=pinterest&utm_medium=cover_pin&utm_campaign=listicle",
  "media_source": {
    "source_type": "image_url",
    "url": "{{7.image_url}}"
  },
  "alt_text": "{{5.title}}"
}
```

   - **Parse response**: Yes
   - **Timeout**: `30` seconds
3. Click **OK**

### Error Handling

Add a retry error handler: 3 retries, 15-second interval. Pinterest occasionally returns transient errors.

---

## Step 12: Add Supabase -- Update Post Record

1. Add an **HTTP Make a request** module
2. Configure:
   - **URL**: `https://YOUR_SUPABASE_URL.supabase.co/rest/v1/listicle_posts?id=eq.{{8.data[0].id}}`
   - **Method**: `PATCH`
   - **Headers**: Standard Supabase headers + `Prefer: return=representation`
   - **Body**:

```json
{
  "cover_pin_id": "{{10.data.id}}",
  "cover_pin_url": "{{10.data.link}}",
  "cover_pin_created": true,
  "inline_images_scheduled": true,
  "scheduled_pin_count": {{9.data.scheduled_count}}
}
```

3. Click **OK**

---

## Step 13: Add Error Handling Router

1. Add a **Flow Control > Router** module at the end
2. Create two routes:

### Route 1: Success

- **Filter label**: `Success`
- **Condition**: The previous modules completed without error
- **Module**: HTTP request to Supabase `automation_logs` table with status `success`

### Route 2: Error

- **Filter label**: `Error`
- **Condition**: Error occurred
- **Modules**:
  1. HTTP request to Supabase `automation_logs` with status `error` and error details
  2. Email module to send alert to your alert email address

---

## Step 14: Testing Procedure

### Test 1: Module-by-Module

Run each module individually using Make.com's "Run this module only" feature:

1. **Scheduler**: Skip (just triggers)
2. **Supabase subdomain**: Should return 1 active subdomain
3. **Supabase recent posts**: Should return 0-15 posts (empty is fine for first run)
4. **Claude API**: Should return valid JSON with 7 list items
5. **JSON parse**: Should parse without errors
6. **Iterator + Pexels**: Should return images for each item
7. **Supabase create post**: Should create a record and return its ID
8. **Supabase RPC**: Should create 7 scheduled_pins records
9. **Pinterest**: Should create a pin and return its ID
10. **Supabase update**: Should update the post record

### Test 2: Full Run

1. Click **Run once** on the scenario
2. Watch each module execute in sequence
3. Verify in Supabase:
   - New record in `listicle_posts`
   - 7 new records in `scheduled_pins`
   - New record in `automation_logs`
4. Verify on Pinterest: New cover pin exists on the correct board

### Test 3: Error Path

1. Temporarily use an invalid API key for Claude
2. Run the scenario
3. Verify the error handler catches the failure
4. Check that `automation_logs` has an error record
5. Check your email for the alert
6. Restore the valid API key

---

## Step 15: Activation Checklist

Before turning on the schedule:

- [ ] All API connections verified and working
- [ ] At least 2 subdomains in the `subdomains` table with `is_active = true`
- [ ] Pinterest board IDs are correct and the account has write access
- [ ] Supabase tables exist with proper grants
- [ ] Supabase RPC function `schedule_inline_images` is created
- [ ] Error handler sends emails to the correct address
- [ ] Full test run completed successfully
- [ ] Claude prompt produces good quality content (review 2-3 outputs)
- [ ] Pexels images are relevant (review the search queries Claude generates)
- [ ] Pinterest pin looks correct (title, description, image, link)
- [ ] Scenario is set to **ON** (toggle in top-left of scenario editor)

---

## Operations Budget

| Component | Ops per Run | Runs per Day | Monthly Ops |
|-----------|-------------|--------------|-------------|
| Scheduler | 1 | 3 | 90 |
| Supabase reads | 2 | 3 | 180 |
| Claude API | 1 | 3 | 90 |
| JSON parse | 1 | 3 | 90 |
| Iterator | 1 | 3 | 90 |
| Pexels API (x7) | 7 | 3 | 630 |
| Supabase writes | 3 | 3 | 270 |
| Pinterest API | 1 | 3 | 90 |
| Logging/Router | 2 | 3 | 180 |
| **Total** | **~19** | **3** | **~1,710** |

Make.com free tier allows 10,000 operations/month. This scenario uses approximately 1,710 operations, well within limits.

---

## Maintenance

### Weekly

- Review `automation_logs` for any errors or degraded performance
- Spot-check 2-3 listicle posts for content quality
- Verify scheduled_pins are being picked up by Agent 2B

### Monthly

- Review Pinterest analytics to see which listicle topics drive the most clicks
- Update `subdomains` table with new categories or deactivate underperformers
- Rotate or expand the topic pool in the `next_topic` field
- Export the scenario blueprint for version control

### Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Claude returns markdown fences | Prompt does not explicitly forbid them | Add text parser module to strip fences before JSON parse |
| Pexels returns no images | Search query too specific | Broaden the image_keyword guidance in the Claude prompt |
| Pinterest 401 error | Token expired | Refresh the OAuth token in Make.com connections |
| Supabase 404 | Table does not exist | Run the SQL from Step 0 |
| Supabase RLS error | Grants not applied | Run the GRANT statements from Step 0 |
| Duplicate topics | recent_posts query not working | Verify the subdomain_id filter in Module 3 |
