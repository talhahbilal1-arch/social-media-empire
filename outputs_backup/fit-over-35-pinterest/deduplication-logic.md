# Fit Over 35 Pinterest Deduplication Logic

Technical reference for implementing content deduplication in the Pinterest automation workflow using Supabase and Make.com.

---

## Table of Contents

1. [Database Schema Requirements](#1-database-schema-requirements)
2. [Deduplication Queries](#2-deduplication-queries)
3. [Make.com Integration](#3-makecom-integration)
4. [Similarity Detection](#4-similarity-detection)
5. [Implementation Code Examples](#5-implementation-code-examples)

---

## 1. Database Schema Requirements

### Table Structure: `pinterest_posts`

This table tracks all posted pins to enable deduplication checks before posting new content.

```sql
-- Pinterest Posts Tracking Table
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS pinterest_posts (
    id BIGSERIAL PRIMARY KEY,

    -- Content identification
    brand VARCHAR(50) NOT NULL DEFAULT 'fit_over_35',
    topic VARCHAR(255) NOT NULL,
    topic_normalized VARCHAR(255) NOT NULL,  -- Lowercase, trimmed for comparison
    topic_category VARCHAR(100),              -- Grouping category (e.g., 'strength', 'nutrition', 'recovery')

    -- Image/media tracking
    image_keywords TEXT[] NOT NULL DEFAULT '{}',  -- Array of keywords used for image search
    image_keywords_normalized TEXT[] NOT NULL DEFAULT '{}',  -- Lowercase for comparison
    image_url TEXT,
    video_url TEXT,

    -- Pinterest-specific data
    board VARCHAR(100) NOT NULL,
    pin_id VARCHAR(100),                      -- Pinterest's pin ID (if available)
    pin_url TEXT,
    pin_type VARCHAR(20) DEFAULT 'idea_pin',  -- 'idea_pin', 'video_pin', 'standard'

    -- Metadata
    title VARCHAR(100) NOT NULL,
    description TEXT,
    hashtags TEXT[],

    -- Posting details
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    post_status VARCHAR(20) DEFAULT 'posted', -- 'posted', 'failed', 'pending'
    error_message TEXT,

    -- Tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments on columns for documentation
COMMENT ON COLUMN pinterest_posts.topic_normalized IS 'Lowercase topic with extra whitespace removed for reliable comparison';
COMMENT ON COLUMN pinterest_posts.topic_category IS 'Broad category for grouping similar topics (prevents posting two strength training topics same day)';
COMMENT ON COLUMN pinterest_posts.image_keywords_normalized IS 'Lowercase keywords for array overlap comparison';
```

### Required Indexes

```sql
-- Performance indexes for deduplication queries

-- Primary lookup: recent posts by brand
CREATE INDEX idx_pinterest_posts_brand_posted
ON pinterest_posts(brand, posted_at DESC);

-- Topic deduplication: find similar topics within time window
CREATE INDEX idx_pinterest_posts_topic_normalized
ON pinterest_posts(brand, topic_normalized, posted_at DESC);

-- Category deduplication: prevent same category same day
CREATE INDEX idx_pinterest_posts_category_date
ON pinterest_posts(brand, topic_category, (posted_at::DATE));

-- Image keyword deduplication: GIN index for array overlap queries
CREATE INDEX idx_pinterest_posts_image_keywords
ON pinterest_posts USING GIN(image_keywords_normalized);

-- Board-specific queries
CREATE INDEX idx_pinterest_posts_board
ON pinterest_posts(brand, board, posted_at DESC);

-- Composite index for common dedup query pattern
CREATE INDEX idx_pinterest_posts_dedup_composite
ON pinterest_posts(brand, posted_at DESC, topic_normalized, topic_category);
```

### Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE pinterest_posts ENABLE ROW LEVEL SECURITY;

-- Service role full access policy
CREATE POLICY "Service role full access"
ON pinterest_posts FOR ALL USING (true);

-- Optional: Read-only access for dashboard/analytics
CREATE POLICY "Read access for authenticated users"
ON pinterest_posts FOR SELECT
TO authenticated
USING (true);
```

### Auto-Update Trigger

```sql
-- Automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_pinterest_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pinterest_posts_updated_at
    BEFORE UPDATE ON pinterest_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_pinterest_posts_updated_at();
```

---

## 2. Deduplication Queries

### 2.1 Check Last 100 Pins for Similar Content

This comprehensive check scans recent pins for any content overlap.

```sql
-- Function: Check for duplicate content in last 100 pins
CREATE OR REPLACE FUNCTION check_recent_duplicates(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_image_keywords TEXT[],
    p_topic_category VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    is_duplicate BOOLEAN,
    duplicate_type VARCHAR,
    matching_pin_id BIGINT,
    matching_topic VARCHAR,
    matching_keywords TEXT[],
    days_since_posted INTEGER
) AS $$
DECLARE
    v_topic_normalized VARCHAR;
    v_keywords_normalized TEXT[];
BEGIN
    -- Normalize inputs
    v_topic_normalized := LOWER(TRIM(p_topic));
    v_keywords_normalized := ARRAY(
        SELECT LOWER(TRIM(kw)) FROM UNNEST(p_image_keywords) AS kw
    );

    -- Check for exact topic match in last 100 pins
    RETURN QUERY
    SELECT
        TRUE AS is_duplicate,
        'exact_topic'::VARCHAR AS duplicate_type,
        pp.id AS matching_pin_id,
        pp.topic AS matching_topic,
        pp.image_keywords AS matching_keywords,
        EXTRACT(DAY FROM NOW() - pp.posted_at)::INTEGER AS days_since_posted
    FROM pinterest_posts pp
    WHERE pp.brand = p_brand
      AND pp.topic_normalized = v_topic_normalized
    ORDER BY pp.posted_at DESC
    LIMIT 1;

    -- If no exact match, check for keyword overlap (>50% shared keywords)
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT
            TRUE AS is_duplicate,
            'keyword_overlap'::VARCHAR AS duplicate_type,
            pp.id AS matching_pin_id,
            pp.topic AS matching_topic,
            pp.image_keywords AS matching_keywords,
            EXTRACT(DAY FROM NOW() - pp.posted_at)::INTEGER AS days_since_posted
        FROM (
            SELECT * FROM pinterest_posts
            WHERE brand = p_brand
            ORDER BY posted_at DESC
            LIMIT 100
        ) pp
        WHERE CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized) >
              GREATEST(CARDINALITY(v_keywords_normalized) / 2, 1)
        ORDER BY pp.posted_at DESC
        LIMIT 1;
    END IF;

    -- If still no match, return not duplicate
    IF NOT FOUND THEN
        RETURN QUERY
        SELECT
            FALSE AS is_duplicate,
            NULL::VARCHAR AS duplicate_type,
            NULL::BIGINT AS matching_pin_id,
            NULL::VARCHAR AS matching_topic,
            NULL::TEXT[] AS matching_keywords,
            NULL::INTEGER AS days_since_posted;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Usage Example:**
```sql
SELECT * FROM check_recent_duplicates(
    'fit_over_35',
    'Best Morning Stretches for Women Over 35',
    ARRAY['morning', 'stretching', 'flexibility', 'women', 'fitness']
);
```

### 2.2 Prevent Same Topics Within 7 Days

```sql
-- Function: Check if topic was posted within N days
CREATE OR REPLACE FUNCTION is_topic_recent(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_days INTEGER DEFAULT 7
)
RETURNS TABLE (
    is_recent BOOLEAN,
    last_posted_at TIMESTAMPTZ,
    days_ago INTEGER,
    previous_pin_id BIGINT
) AS $$
DECLARE
    v_topic_normalized VARCHAR;
BEGIN
    v_topic_normalized := LOWER(TRIM(p_topic));

    RETURN QUERY
    SELECT
        TRUE AS is_recent,
        pp.posted_at AS last_posted_at,
        EXTRACT(DAY FROM NOW() - pp.posted_at)::INTEGER AS days_ago,
        pp.id AS previous_pin_id
    FROM pinterest_posts pp
    WHERE pp.brand = p_brand
      AND pp.topic_normalized = v_topic_normalized
      AND pp.posted_at > NOW() - INTERVAL '1 day' * p_days
    ORDER BY pp.posted_at DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL::TIMESTAMPTZ, NULL::INTEGER, NULL::BIGINT;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Usage Example:**
```sql
-- Check if "HIIT Workouts for Beginners" was posted in last 7 days
SELECT * FROM is_topic_recent('fit_over_35', 'HIIT Workouts for Beginners', 7);
```

**Simple Query Alternative:**
```sql
-- Direct query without function
SELECT EXISTS (
    SELECT 1 FROM pinterest_posts
    WHERE brand = 'fit_over_35'
      AND topic_normalized = LOWER(TRIM('HIIT Workouts for Beginners'))
      AND posted_at > NOW() - INTERVAL '7 days'
) AS is_duplicate;
```

### 2.3 Prevent Same Image Keywords Within 3 Days

```sql
-- Function: Check if image keywords were used within N days
CREATE OR REPLACE FUNCTION are_keywords_recent(
    p_brand VARCHAR,
    p_keywords TEXT[],
    p_days INTEGER DEFAULT 3,
    p_overlap_threshold FLOAT DEFAULT 0.6  -- 60% overlap threshold
)
RETURNS TABLE (
    is_recent BOOLEAN,
    overlap_percentage FLOAT,
    matching_keywords TEXT[],
    last_posted_at TIMESTAMPTZ,
    days_ago INTEGER,
    previous_pin_id BIGINT
) AS $$
DECLARE
    v_keywords_normalized TEXT[];
BEGIN
    -- Normalize input keywords
    v_keywords_normalized := ARRAY(
        SELECT LOWER(TRIM(kw)) FROM UNNEST(p_keywords) AS kw WHERE TRIM(kw) != ''
    );

    RETURN QUERY
    SELECT
        TRUE AS is_recent,
        (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
         GREATEST(CARDINALITY(v_keywords_normalized), 1)) AS overlap_percentage,
        pp.image_keywords_normalized & v_keywords_normalized AS matching_keywords,
        pp.posted_at AS last_posted_at,
        EXTRACT(DAY FROM NOW() - pp.posted_at)::INTEGER AS days_ago,
        pp.id AS previous_pin_id
    FROM pinterest_posts pp
    WHERE pp.brand = p_brand
      AND pp.posted_at > NOW() - INTERVAL '1 day' * p_days
      AND (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
           GREATEST(CARDINALITY(v_keywords_normalized), 1)) >= p_overlap_threshold
    ORDER BY
        CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized) DESC,
        pp.posted_at DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 0.0::FLOAT, NULL::TEXT[], NULL::TIMESTAMPTZ, NULL::INTEGER, NULL::BIGINT;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Usage Example:**
```sql
-- Check if keywords were used in last 3 days
SELECT * FROM are_keywords_recent(
    'fit_over_35',
    ARRAY['yoga', 'flexibility', 'morning', 'stretching'],
    3,    -- days
    0.6   -- 60% overlap threshold
);
```

### 2.4 Combined Deduplication Check

```sql
-- Comprehensive deduplication function for pre-post validation
CREATE OR REPLACE FUNCTION validate_pin_uniqueness(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_image_keywords TEXT[],
    p_topic_category VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    can_post BOOLEAN,
    block_reason VARCHAR,
    block_details JSONB
) AS $$
DECLARE
    v_topic_normalized VARCHAR;
    v_keywords_normalized TEXT[];
    v_topic_check RECORD;
    v_keyword_check RECORD;
    v_category_check RECORD;
BEGIN
    -- Normalize inputs
    v_topic_normalized := LOWER(TRIM(p_topic));
    v_keywords_normalized := ARRAY(
        SELECT LOWER(TRIM(kw)) FROM UNNEST(p_image_keywords) AS kw WHERE TRIM(kw) != ''
    );

    -- Check 1: Exact topic within 7 days
    SELECT * INTO v_topic_check
    FROM pinterest_posts
    WHERE brand = p_brand
      AND topic_normalized = v_topic_normalized
      AND posted_at > NOW() - INTERVAL '7 days'
    ORDER BY posted_at DESC
    LIMIT 1;

    IF FOUND THEN
        RETURN QUERY SELECT
            FALSE,
            'topic_duplicate'::VARCHAR,
            jsonb_build_object(
                'matching_pin_id', v_topic_check.id,
                'matching_topic', v_topic_check.topic,
                'posted_at', v_topic_check.posted_at,
                'days_ago', EXTRACT(DAY FROM NOW() - v_topic_check.posted_at)::INTEGER,
                'rule', 'Same topic posted within 7 days'
            );
        RETURN;
    END IF;

    -- Check 2: Image keywords within 3 days (60% overlap)
    SELECT
        pp.*,
        (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
         GREATEST(CARDINALITY(v_keywords_normalized), 1)) AS overlap_pct,
        pp.image_keywords_normalized & v_keywords_normalized AS overlap_keywords
    INTO v_keyword_check
    FROM pinterest_posts pp
    WHERE pp.brand = p_brand
      AND pp.posted_at > NOW() - INTERVAL '3 days'
      AND (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
           GREATEST(CARDINALITY(v_keywords_normalized), 1)) >= 0.6
    ORDER BY
        CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized) DESC
    LIMIT 1;

    IF FOUND THEN
        RETURN QUERY SELECT
            FALSE,
            'keyword_duplicate'::VARCHAR,
            jsonb_build_object(
                'matching_pin_id', v_keyword_check.id,
                'matching_topic', v_keyword_check.topic,
                'overlap_percentage', ROUND(v_keyword_check.overlap_pct * 100),
                'overlapping_keywords', v_keyword_check.overlap_keywords,
                'posted_at', v_keyword_check.posted_at,
                'days_ago', EXTRACT(DAY FROM NOW() - v_keyword_check.posted_at)::INTEGER,
                'rule', 'Similar image keywords used within 3 days (60%+ overlap)'
            );
        RETURN;
    END IF;

    -- Check 3: Same category same day (if category provided)
    IF p_topic_category IS NOT NULL THEN
        SELECT * INTO v_category_check
        FROM pinterest_posts
        WHERE brand = p_brand
          AND topic_category = p_topic_category
          AND posted_at::DATE = CURRENT_DATE
        ORDER BY posted_at DESC
        LIMIT 1;

        IF FOUND THEN
            RETURN QUERY SELECT
                FALSE,
                'category_duplicate'::VARCHAR,
                jsonb_build_object(
                    'matching_pin_id', v_category_check.id,
                    'matching_topic', v_category_check.topic,
                    'category', p_topic_category,
                    'posted_at', v_category_check.posted_at,
                    'rule', 'Same topic category already posted today'
                );
            RETURN;
        END IF;
    END IF;

    -- All checks passed
    RETURN QUERY SELECT
        TRUE,
        NULL::VARCHAR,
        NULL::JSONB;
END;
$$ LANGUAGE plpgsql;
```

**Usage Example:**
```sql
-- Validate before posting
SELECT * FROM validate_pin_uniqueness(
    'fit_over_35',
    'Morning Yoga Routine for Flexibility',
    ARRAY['yoga', 'morning', 'flexibility', 'stretch', 'women over 35'],
    'flexibility'  -- topic category
);
```

---

## 3. Make.com Integration

### 3.1 Architecture Overview

```
[Trigger/Scheduler]
        |
        v
[Generate Content Module]
        |
        v
[HTTP Module: Deduplication Check] --> [Supabase API]
        |
        v
[Router: Is Duplicate?]
   /          \
  YES          NO
   |            |
   v            v
[Skip/Log]  [Continue Posting]
               |
               v
        [Post to Pinterest]
               |
               v
        [HTTP Module: Log Posted Pin] --> [Supabase API]
```

### 3.2 HTTP Module Configuration for Deduplication Check

**Module: HTTP - Make a request**

**URL:**
```
https://YOUR_PROJECT_REF.supabase.co/rest/v1/rpc/validate_pin_uniqueness
```

**Method:** `POST`

**Headers:**
```json
{
    "apikey": "{{SUPABASE_ANON_KEY}}",
    "Authorization": "Bearer {{SUPABASE_ANON_KEY}}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
```

**Body:**
```json
{
    "p_brand": "fit_over_35",
    "p_topic": "{{topic}}",
    "p_image_keywords": {{toArray(image_keywords)}},
    "p_topic_category": "{{category}}"
}
```

**Note:** Replace `{{topic}}`, `{{image_keywords}}`, and `{{category}}` with data from previous modules.

### 3.3 Alternative: Direct Query via REST API

If you prefer not to use database functions, you can query the table directly.

**Check Topic Duplicate (GET request):**
```
https://YOUR_PROJECT_REF.supabase.co/rest/v1/pinterest_posts?select=id,topic,posted_at&brand=eq.fit_over_35&topic_normalized=eq.{{urlEncode(lower(trim(topic)))}}&posted_at=gte.{{formatDate(addDays(now; -7); "YYYY-MM-DD")}}T00:00:00Z&limit=1
```

**Check Keyword Overlap (POST with RPC):**
```
POST https://YOUR_PROJECT_REF.supabase.co/rest/v1/rpc/are_keywords_recent
{
    "p_brand": "fit_over_35",
    "p_keywords": ["yoga", "morning", "flexibility"],
    "p_days": 3,
    "p_overlap_threshold": 0.6
}
```

### 3.4 Response Handling Logic

**Parse Response Module Configuration:**

After the HTTP request, add a JSON parse module or use built-in Make.com data parsing.

**Router Configuration:**

Create a router with the following routes:

**Route 1: Duplicate Detected (Skip Posting)**
- Condition: `{{1.body[1].can_post}} = false`
- Action: Continue to logging module or error notification

**Route 2: Unique Content (Continue Posting)**
- Condition: `{{1.body[1].can_post}} = true`
- Action: Continue to Pinterest posting module

### 3.5 What to Do When Duplicate is Detected

**Option A: Skip and Log**

Create a module to log skipped pins for later review:

```json
// POST to pinterest_posts with status='skipped'
{
    "brand": "fit_over_35",
    "topic": "{{topic}}",
    "topic_normalized": "{{lower(trim(topic))}}",
    "image_keywords": {{toArray(image_keywords)}},
    "image_keywords_normalized": {{toArray(map(image_keywords; lower))}},
    "board": "{{board}}",
    "post_status": "skipped",
    "error_message": "Duplicate detected: {{1.body[1].block_reason}} - {{1.body[1].block_details}}"
}
```

**Option B: Generate Alternative Content**

Route back to content generation with constraints:

1. Pass the blocked topic/keywords to a "Generate Alternative" module
2. Include exclusion list: `"exclude_topics": ["{{blocked_topic}}"]`
3. Re-run deduplication check with new content
4. Limit retries to prevent infinite loops (max 3 attempts)

**Option C: Queue for Later**

Store in a separate queue table for manual review or later posting:

```sql
INSERT INTO pinterest_post_queue (brand, topic, image_keywords, scheduled_for, status)
VALUES ('fit_over_35', '{{topic}}', ARRAY[{{keywords}}], NOW() + INTERVAL '7 days', 'queued');
```

### 3.6 Logging Posted Pins

After successful Pinterest posting, log the pin:

**HTTP Module: Log Posted Pin**

**URL:**
```
https://YOUR_PROJECT_REF.supabase.co/rest/v1/pinterest_posts
```

**Method:** `POST`

**Headers:**
```json
{
    "apikey": "{{SUPABASE_ANON_KEY}}",
    "Authorization": "Bearer {{SUPABASE_ANON_KEY}}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
```

**Body:**
```json
{
    "brand": "fit_over_35",
    "topic": "{{topic}}",
    "topic_normalized": "{{lower(trim(topic))}}",
    "topic_category": "{{category}}",
    "image_keywords": {{toArray(image_keywords)}},
    "image_keywords_normalized": {{toArray(map(image_keywords; x -> lower(trim(x))))}},
    "image_url": "{{image_url}}",
    "video_url": "{{video_url}}",
    "board": "{{board}}",
    "pin_id": "{{pinterest_response.id}}",
    "pin_url": "{{pinterest_response.url}}",
    "title": "{{title}}",
    "description": "{{description}}",
    "hashtags": {{toArray(hashtags)}},
    "post_status": "posted"
}
```

---

## 4. Similarity Detection

### 4.1 Text Similarity Approaches

#### Exact Match
Simple but limited - only catches identical topics.

```sql
-- Exact match (case-insensitive)
WHERE LOWER(TRIM(topic)) = LOWER(TRIM('Your Topic Here'))
```

#### Fuzzy Matching with pg_trgm

For approximate string matching, enable the `pg_trgm` extension:

```sql
-- Enable trigram extension (run once in Supabase SQL Editor)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create trigram index
CREATE INDEX idx_pinterest_posts_topic_trgm
ON pinterest_posts USING GIN(topic_normalized gin_trgm_ops);
```

**Fuzzy Match Query:**
```sql
-- Find topics with 70%+ similarity
SELECT
    id,
    topic,
    similarity(topic_normalized, LOWER('morning yoga routine')) AS sim_score
FROM pinterest_posts
WHERE brand = 'fit_over_35'
  AND topic_normalized % LOWER('morning yoga routine')  -- Uses default threshold 0.3
  AND similarity(topic_normalized, LOWER('morning yoga routine')) > 0.7
ORDER BY sim_score DESC
LIMIT 5;
```

**Fuzzy Match Function:**
```sql
CREATE OR REPLACE FUNCTION find_similar_topics(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_similarity_threshold FLOAT DEFAULT 0.7,
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    pin_id BIGINT,
    topic VARCHAR,
    similarity_score FLOAT,
    posted_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pp.id,
        pp.topic,
        similarity(pp.topic_normalized, LOWER(TRIM(p_topic)))::FLOAT,
        pp.posted_at
    FROM pinterest_posts pp
    WHERE pp.brand = p_brand
      AND pp.posted_at > NOW() - INTERVAL '1 day' * p_days
      AND similarity(pp.topic_normalized, LOWER(TRIM(p_topic))) >= p_similarity_threshold
    ORDER BY similarity(pp.topic_normalized, LOWER(TRIM(p_topic))) DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;
```

### 4.2 Keyword Overlap Detection

#### Array Overlap Operator

PostgreSQL provides array operators for efficient overlap detection:

```sql
-- & operator: Returns elements common to both arrays
SELECT ARRAY['yoga', 'morning', 'stretch'] & ARRAY['yoga', 'flexibility', 'morning'];
-- Result: {yoga, morning}

-- && operator: Returns TRUE if arrays have any elements in common
SELECT ARRAY['yoga', 'morning'] && ARRAY['pilates', 'evening'];
-- Result: FALSE
```

**Keyword Overlap Query:**
```sql
-- Find pins with keyword overlap
SELECT
    id,
    topic,
    image_keywords,
    image_keywords_normalized & ARRAY['yoga', 'morning', 'stretch'] AS overlapping_keywords,
    CARDINALITY(image_keywords_normalized & ARRAY['yoga', 'morning', 'stretch']) AS overlap_count
FROM pinterest_posts
WHERE brand = 'fit_over_35'
  AND posted_at > NOW() - INTERVAL '3 days'
  AND image_keywords_normalized && ARRAY['yoga', 'morning', 'stretch']  -- Has any overlap
ORDER BY overlap_count DESC;
```

**Percentage-Based Overlap:**
```sql
-- Find pins where >50% of keywords overlap
WITH input AS (
    SELECT ARRAY['yoga', 'morning', 'stretch', 'flexibility', 'women'] AS keywords
)
SELECT
    pp.id,
    pp.topic,
    pp.image_keywords,
    pp.image_keywords_normalized & input.keywords AS overlapping,
    ROUND(
        (CARDINALITY(pp.image_keywords_normalized & input.keywords)::FLOAT /
         CARDINALITY(input.keywords)) * 100
    ) AS overlap_percentage
FROM pinterest_posts pp, input
WHERE pp.brand = 'fit_over_35'
  AND pp.posted_at > NOW() - INTERVAL '3 days'
  AND (CARDINALITY(pp.image_keywords_normalized & input.keywords)::FLOAT /
       CARDINALITY(input.keywords)) > 0.5
ORDER BY overlap_percentage DESC;
```

### 4.3 Topic Categorization for Grouping

#### Category Definitions

Create a reference table for topic categories:

```sql
CREATE TABLE IF NOT EXISTS topic_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    keywords TEXT[] NOT NULL,  -- Keywords that indicate this category
    max_per_day INTEGER DEFAULT 1,  -- How many of this category per day
    min_days_between INTEGER DEFAULT 1  -- Minimum days between same category
);

-- Insert category definitions
INSERT INTO topic_categories (category_name, keywords, max_per_day, min_days_between) VALUES
('strength_training', ARRAY['strength', 'weights', 'lifting', 'resistance', 'muscle', 'toning', 'dumbbell', 'barbell'], 1, 1),
('cardio', ARRAY['cardio', 'hiit', 'running', 'walking', 'aerobic', 'heart rate', 'endurance'], 1, 1),
('flexibility', ARRAY['yoga', 'stretch', 'flexibility', 'mobility', 'range of motion', 'pilates'], 1, 1),
('nutrition', ARRAY['nutrition', 'diet', 'eating', 'meal', 'protein', 'healthy food', 'recipe'], 1, 2),
('recovery', ARRAY['recovery', 'rest', 'sleep', 'foam roll', 'massage', 'relaxation'], 1, 2),
('motivation', ARRAY['motivation', 'mindset', 'goals', 'inspiration', 'habit', 'consistency'], 1, 2),
('hormones', ARRAY['hormone', 'menopause', 'perimenopause', 'metabolism', 'thyroid', 'cortisol'], 1, 3),
('injury_prevention', ARRAY['injury', 'pain', 'joint', 'back pain', 'knee', 'prevention', 'safe'], 1, 2);
```

#### Auto-Categorization Function

```sql
CREATE OR REPLACE FUNCTION categorize_topic(p_topic VARCHAR, p_keywords TEXT[])
RETURNS VARCHAR AS $$
DECLARE
    v_category RECORD;
    v_best_match VARCHAR;
    v_best_score INTEGER := 0;
    v_current_score INTEGER;
    v_combined_text TEXT;
BEGIN
    -- Combine topic and keywords for matching
    v_combined_text := LOWER(p_topic || ' ' || ARRAY_TO_STRING(p_keywords, ' '));

    FOR v_category IN SELECT * FROM topic_categories LOOP
        -- Count how many category keywords appear in the combined text
        SELECT COUNT(*) INTO v_current_score
        FROM UNNEST(v_category.keywords) AS kw
        WHERE v_combined_text LIKE '%' || LOWER(kw) || '%';

        IF v_current_score > v_best_score THEN
            v_best_score := v_current_score;
            v_best_match := v_category.category_name;
        END IF;
    END LOOP;

    -- Return 'general' if no strong match found
    RETURN COALESCE(v_best_match, 'general');
END;
$$ LANGUAGE plpgsql;
```

**Usage:**
```sql
SELECT categorize_topic(
    'Best Morning Yoga Stretches for Women Over 35',
    ARRAY['yoga', 'morning', 'stretching', 'flexibility']
);
-- Result: 'flexibility'
```

#### Category-Based Deduplication

```sql
-- Check if category limit reached for today
CREATE OR REPLACE FUNCTION is_category_limit_reached(
    p_brand VARCHAR,
    p_category VARCHAR
)
RETURNS BOOLEAN AS $$
DECLARE
    v_max_per_day INTEGER;
    v_current_count INTEGER;
BEGIN
    -- Get max allowed per day for this category
    SELECT max_per_day INTO v_max_per_day
    FROM topic_categories
    WHERE category_name = p_category;

    IF v_max_per_day IS NULL THEN
        v_max_per_day := 1;  -- Default
    END IF;

    -- Count posts in this category today
    SELECT COUNT(*) INTO v_current_count
    FROM pinterest_posts
    WHERE brand = p_brand
      AND topic_category = p_category
      AND posted_at::DATE = CURRENT_DATE
      AND post_status = 'posted';

    RETURN v_current_count >= v_max_per_day;
END;
$$ LANGUAGE plpgsql;
```

---

## 5. Implementation Code Examples

### 5.1 Complete Supabase SQL Setup Script

```sql
-- ============================================
-- Fit Over 35 Pinterest Deduplication Setup
-- Run this entire script in Supabase SQL Editor
-- ============================================

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Create main tracking table
CREATE TABLE IF NOT EXISTS pinterest_posts (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL DEFAULT 'fit_over_35',
    topic VARCHAR(255) NOT NULL,
    topic_normalized VARCHAR(255) NOT NULL,
    topic_category VARCHAR(100),
    image_keywords TEXT[] NOT NULL DEFAULT '{}',
    image_keywords_normalized TEXT[] NOT NULL DEFAULT '{}',
    image_url TEXT,
    video_url TEXT,
    board VARCHAR(100) NOT NULL,
    pin_id VARCHAR(100),
    pin_url TEXT,
    pin_type VARCHAR(20) DEFAULT 'idea_pin',
    title VARCHAR(100) NOT NULL,
    description TEXT,
    hashtags TEXT[],
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    post_status VARCHAR(20) DEFAULT 'posted',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create all indexes
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_brand_posted ON pinterest_posts(brand, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_topic_normalized ON pinterest_posts(brand, topic_normalized, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_category_date ON pinterest_posts(brand, topic_category, (posted_at::DATE));
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_image_keywords ON pinterest_posts USING GIN(image_keywords_normalized);
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_board ON pinterest_posts(brand, board, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_pinterest_posts_topic_trgm ON pinterest_posts USING GIN(topic_normalized gin_trgm_ops);

-- 4. Create topic categories table
CREATE TABLE IF NOT EXISTS topic_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    keywords TEXT[] NOT NULL,
    max_per_day INTEGER DEFAULT 1,
    min_days_between INTEGER DEFAULT 1
);

-- 5. Insert default categories
INSERT INTO topic_categories (category_name, keywords, max_per_day, min_days_between) VALUES
('strength_training', ARRAY['strength', 'weights', 'lifting', 'resistance', 'muscle', 'toning', 'dumbbell', 'barbell'], 1, 1),
('cardio', ARRAY['cardio', 'hiit', 'running', 'walking', 'aerobic', 'heart rate', 'endurance'], 1, 1),
('flexibility', ARRAY['yoga', 'stretch', 'flexibility', 'mobility', 'range of motion', 'pilates'], 1, 1),
('nutrition', ARRAY['nutrition', 'diet', 'eating', 'meal', 'protein', 'healthy food', 'recipe'], 1, 2),
('recovery', ARRAY['recovery', 'rest', 'sleep', 'foam roll', 'massage', 'relaxation'], 1, 2),
('motivation', ARRAY['motivation', 'mindset', 'goals', 'inspiration', 'habit', 'consistency'], 1, 2),
('hormones', ARRAY['hormone', 'menopause', 'perimenopause', 'metabolism', 'thyroid', 'cortisol'], 1, 3),
('injury_prevention', ARRAY['injury', 'pain', 'joint', 'back pain', 'knee', 'prevention', 'safe'], 1, 2)
ON CONFLICT (category_name) DO NOTHING;

-- 6. Enable RLS
ALTER TABLE pinterest_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_categories ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS policies
DROP POLICY IF EXISTS "Service role full access" ON pinterest_posts;
CREATE POLICY "Service role full access" ON pinterest_posts FOR ALL USING (true);
DROP POLICY IF EXISTS "Service role full access" ON topic_categories;
CREATE POLICY "Service role full access" ON topic_categories FOR ALL USING (true);

-- 8. Create update trigger
CREATE OR REPLACE FUNCTION update_pinterest_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pinterest_posts_updated_at ON pinterest_posts;
CREATE TRIGGER pinterest_posts_updated_at
    BEFORE UPDATE ON pinterest_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_pinterest_posts_updated_at();

-- 9. Create categorization function
CREATE OR REPLACE FUNCTION categorize_topic(p_topic VARCHAR, p_keywords TEXT[])
RETURNS VARCHAR AS $$
DECLARE
    v_category RECORD;
    v_best_match VARCHAR;
    v_best_score INTEGER := 0;
    v_current_score INTEGER;
    v_combined_text TEXT;
BEGIN
    v_combined_text := LOWER(p_topic || ' ' || COALESCE(ARRAY_TO_STRING(p_keywords, ' '), ''));

    FOR v_category IN SELECT * FROM topic_categories LOOP
        SELECT COUNT(*) INTO v_current_score
        FROM UNNEST(v_category.keywords) AS kw
        WHERE v_combined_text LIKE '%' || LOWER(kw) || '%';

        IF v_current_score > v_best_score THEN
            v_best_score := v_current_score;
            v_best_match := v_category.category_name;
        END IF;
    END LOOP;

    RETURN COALESCE(v_best_match, 'general');
END;
$$ LANGUAGE plpgsql;

-- 10. Create main validation function
CREATE OR REPLACE FUNCTION validate_pin_uniqueness(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_image_keywords TEXT[],
    p_topic_category VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    can_post BOOLEAN,
    block_reason VARCHAR,
    block_details JSONB
) AS $$
DECLARE
    v_topic_normalized VARCHAR;
    v_keywords_normalized TEXT[];
    v_category VARCHAR;
    v_topic_check RECORD;
    v_keyword_check RECORD;
    v_category_check RECORD;
    v_category_limit INTEGER;
BEGIN
    -- Normalize inputs
    v_topic_normalized := LOWER(TRIM(p_topic));
    v_keywords_normalized := ARRAY(
        SELECT LOWER(TRIM(kw)) FROM UNNEST(p_image_keywords) AS kw WHERE TRIM(kw) != ''
    );

    -- Auto-categorize if not provided
    v_category := COALESCE(p_topic_category, categorize_topic(p_topic, p_image_keywords));

    -- Check 1: Exact topic within 7 days
    SELECT * INTO v_topic_check
    FROM pinterest_posts
    WHERE brand = p_brand
      AND topic_normalized = v_topic_normalized
      AND posted_at > NOW() - INTERVAL '7 days'
      AND post_status = 'posted'
    ORDER BY posted_at DESC
    LIMIT 1;

    IF FOUND THEN
        RETURN QUERY SELECT
            FALSE,
            'topic_duplicate'::VARCHAR,
            jsonb_build_object(
                'matching_pin_id', v_topic_check.id,
                'matching_topic', v_topic_check.topic,
                'posted_at', v_topic_check.posted_at,
                'days_ago', EXTRACT(DAY FROM NOW() - v_topic_check.posted_at)::INTEGER,
                'rule', 'Same topic posted within 7 days'
            );
        RETURN;
    END IF;

    -- Check 2: Fuzzy topic match (>80% similarity) within 7 days
    SELECT * INTO v_topic_check
    FROM pinterest_posts
    WHERE brand = p_brand
      AND posted_at > NOW() - INTERVAL '7 days'
      AND post_status = 'posted'
      AND similarity(topic_normalized, v_topic_normalized) > 0.8
    ORDER BY similarity(topic_normalized, v_topic_normalized) DESC
    LIMIT 1;

    IF FOUND THEN
        RETURN QUERY SELECT
            FALSE,
            'similar_topic'::VARCHAR,
            jsonb_build_object(
                'matching_pin_id', v_topic_check.id,
                'matching_topic', v_topic_check.topic,
                'similarity', ROUND(similarity(v_topic_check.topic_normalized, v_topic_normalized)::NUMERIC * 100),
                'posted_at', v_topic_check.posted_at,
                'rule', 'Very similar topic posted within 7 days (>80% match)'
            );
        RETURN;
    END IF;

    -- Check 3: Image keywords within 3 days (60% overlap)
    IF CARDINALITY(v_keywords_normalized) > 0 THEN
        SELECT
            pp.*,
            (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
             CARDINALITY(v_keywords_normalized)) AS overlap_pct,
            pp.image_keywords_normalized & v_keywords_normalized AS overlap_keywords
        INTO v_keyword_check
        FROM pinterest_posts pp
        WHERE pp.brand = p_brand
          AND pp.posted_at > NOW() - INTERVAL '3 days'
          AND pp.post_status = 'posted'
          AND CARDINALITY(pp.image_keywords_normalized) > 0
          AND (CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized)::FLOAT /
               CARDINALITY(v_keywords_normalized)) >= 0.6
        ORDER BY
            CARDINALITY(pp.image_keywords_normalized & v_keywords_normalized) DESC
        LIMIT 1;

        IF FOUND THEN
            RETURN QUERY SELECT
                FALSE,
                'keyword_duplicate'::VARCHAR,
                jsonb_build_object(
                    'matching_pin_id', v_keyword_check.id,
                    'matching_topic', v_keyword_check.topic,
                    'overlap_percentage', ROUND(v_keyword_check.overlap_pct * 100),
                    'overlapping_keywords', v_keyword_check.overlap_keywords,
                    'posted_at', v_keyword_check.posted_at,
                    'rule', 'Similar image keywords used within 3 days (60%+ overlap)'
                );
            RETURN;
        END IF;
    END IF;

    -- Check 4: Category limit for today
    SELECT max_per_day INTO v_category_limit
    FROM topic_categories
    WHERE category_name = v_category;

    IF v_category_limit IS NOT NULL THEN
        SELECT * INTO v_category_check
        FROM pinterest_posts
        WHERE brand = p_brand
          AND topic_category = v_category
          AND posted_at::DATE = CURRENT_DATE
          AND post_status = 'posted'
        ORDER BY posted_at DESC
        LIMIT 1;

        IF FOUND THEN
            RETURN QUERY SELECT
                FALSE,
                'category_limit'::VARCHAR,
                jsonb_build_object(
                    'matching_pin_id', v_category_check.id,
                    'matching_topic', v_category_check.topic,
                    'category', v_category,
                    'posted_at', v_category_check.posted_at,
                    'rule', 'Category limit reached for today (' || v_category || ')'
                );
            RETURN;
        END IF;
    END IF;

    -- All checks passed
    RETURN QUERY SELECT
        TRUE,
        NULL::VARCHAR,
        jsonb_build_object('auto_category', v_category);
END;
$$ LANGUAGE plpgsql;

-- 11. Create helper function for logging new pins
CREATE OR REPLACE FUNCTION log_pinterest_post(
    p_brand VARCHAR,
    p_topic VARCHAR,
    p_image_keywords TEXT[],
    p_board VARCHAR,
    p_title VARCHAR,
    p_description TEXT DEFAULT NULL,
    p_hashtags TEXT[] DEFAULT '{}',
    p_image_url TEXT DEFAULT NULL,
    p_video_url TEXT DEFAULT NULL,
    p_pin_id VARCHAR DEFAULT NULL,
    p_pin_url TEXT DEFAULT NULL
)
RETURNS pinterest_posts AS $$
DECLARE
    v_result pinterest_posts;
    v_topic_normalized VARCHAR;
    v_keywords_normalized TEXT[];
    v_category VARCHAR;
BEGIN
    v_topic_normalized := LOWER(TRIM(p_topic));
    v_keywords_normalized := ARRAY(
        SELECT LOWER(TRIM(kw)) FROM UNNEST(p_image_keywords) AS kw WHERE TRIM(kw) != ''
    );
    v_category := categorize_topic(p_topic, p_image_keywords);

    INSERT INTO pinterest_posts (
        brand, topic, topic_normalized, topic_category,
        image_keywords, image_keywords_normalized,
        board, title, description, hashtags,
        image_url, video_url, pin_id, pin_url,
        post_status
    ) VALUES (
        p_brand, p_topic, v_topic_normalized, v_category,
        p_image_keywords, v_keywords_normalized,
        p_board, p_title, p_description, p_hashtags,
        p_image_url, p_video_url, p_pin_id, p_pin_url,
        'posted'
    )
    RETURNING * INTO v_result;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- 12. Create analytics view
CREATE OR REPLACE VIEW pinterest_post_analytics AS
SELECT
    brand,
    topic_category,
    COUNT(*) as total_posts,
    COUNT(*) FILTER (WHERE post_status = 'posted') as successful_posts,
    COUNT(*) FILTER (WHERE post_status = 'skipped') as skipped_posts,
    COUNT(*) FILTER (WHERE posted_at::DATE = CURRENT_DATE) as posts_today,
    MAX(posted_at) as last_posted,
    AVG(CARDINALITY(image_keywords)) as avg_keywords_per_post
FROM pinterest_posts
GROUP BY brand, topic_category
ORDER BY brand, total_posts DESC;

-- Done! Run: SELECT * FROM pinterest_post_analytics; to verify setup
```

### 5.2 Make.com Filter Configurations

#### Filter: Check if Can Post

In Make.com, after the HTTP deduplication check module, add a filter:

**Filter Name:** `Can Post - Not Duplicate`

**Condition:**
```
{{1.body[1].can_post}} Equal to true
```

#### Filter: Skip Duplicates

**Filter Name:** `Is Duplicate - Skip`

**Condition:**
```
{{1.body[1].can_post}} Equal to false
```

#### Router Configuration Example

```
[Deduplication Check HTTP Module]
            |
            v
        [Router]
       /        \
      /          \
Route 1:        Route 2:
can_post=true   can_post=false
     |               |
     v               v
[Post to       [Log Skipped]
Pinterest]          |
     |               v
     v          [Send Alert
[Log Posted]    (optional)]
```

### 5.3 Error Handling

#### Supabase Connection Error Handler

In Make.com, wrap HTTP modules in error handlers:

```
[HTTP Module: Dedup Check]
         |
    [Error Handler]
         |
    +---------+
    |         |
Success    Error
    |         |
    v         v
[Continue]  [Fallback: Skip Dedup, Log Warning]
```

**Error Handler Module Configuration:**
- Resume execution
- Store error in variable: `{{error.message}}`
- Continue to fallback route

#### Retry Logic

For transient errors, configure retry settings:

**HTTP Module Settings:**
- Enable "Continue making requests..."
- Number of retries: 3
- Interval between retries: 5 seconds
- Maximum retry interval: 30 seconds

### 5.4 Complete Make.com Scenario JSON Template

This is a partial scenario export showing the deduplication flow:

```json
{
  "name": "Fit Over 35 Pinterest with Deduplication",
  "flow": [
    {
      "id": 1,
      "module": "builtin:BasicTrigger",
      "version": 1,
      "parameters": {
        "time": "08:00"
      },
      "mapper": {},
      "metadata": {
        "designer": { "x": 0, "y": 0 }
      }
    },
    {
      "id": 2,
      "module": "http:ActionSendData",
      "version": 3,
      "parameters": {
        "handleErrors": true,
        "useNewZLibDeCompress": true
      },
      "mapper": {
        "url": "https://YOUR_PROJECT.supabase.co/rest/v1/rpc/validate_pin_uniqueness",
        "method": "POST",
        "headers": [
          { "name": "apikey", "value": "{{SUPABASE_ANON_KEY}}" },
          { "name": "Authorization", "value": "Bearer {{SUPABASE_ANON_KEY}}" },
          { "name": "Content-Type", "value": "application/json" }
        ],
        "body": "{\"p_brand\":\"fit_over_35\",\"p_topic\":\"{{1.topic}}\",\"p_image_keywords\":{{1.keywords}},\"p_topic_category\":null}"
      },
      "metadata": {
        "designer": { "x": 300, "y": 0 },
        "expect": [
          { "name": "body", "type": "text" }
        ]
      }
    },
    {
      "id": 3,
      "module": "builtin:BasicRouter",
      "version": 1,
      "routes": [
        {
          "flow": [
            {
              "id": 4,
              "module": "pinterest:createPin",
              "comment": "Post to Pinterest"
            },
            {
              "id": 5,
              "module": "http:ActionSendData",
              "comment": "Log posted pin to Supabase"
            }
          ],
          "filter": {
            "name": "Can Post",
            "conditions": [[{ "a": "{{2.body[1].can_post}}", "b": "true", "o": "text:equal" }]]
          }
        },
        {
          "flow": [
            {
              "id": 6,
              "module": "http:ActionSendData",
              "comment": "Log skipped pin"
            }
          ],
          "filter": {
            "name": "Is Duplicate",
            "conditions": [[{ "a": "{{2.body[1].can_post}}", "b": "false", "o": "text:equal" }]]
          }
        }
      ],
      "metadata": {
        "designer": { "x": 600, "y": 0 }
      }
    }
  ]
}
```

### 5.5 Testing the Implementation

#### Test Queries

```sql
-- Test 1: Add a test pin
SELECT * FROM log_pinterest_post(
    'fit_over_35',
    'Best Morning Yoga Stretches for Flexibility',
    ARRAY['yoga', 'morning', 'stretching', 'flexibility', 'women'],
    'fitness-tips',
    'Best Morning Yoga Stretches',
    'Start your day with these gentle stretches...',
    ARRAY['#yoga', '#fitness', '#over35']
);

-- Test 2: Try to validate a duplicate (should fail)
SELECT * FROM validate_pin_uniqueness(
    'fit_over_35',
    'Best Morning Yoga Stretches for Flexibility',  -- Same topic
    ARRAY['yoga', 'morning', 'stretching']
);
-- Expected: can_post=false, block_reason='topic_duplicate'

-- Test 3: Try a similar topic (should fail with fuzzy match)
SELECT * FROM validate_pin_uniqueness(
    'fit_over_35',
    'Morning Yoga Stretches for Better Flexibility',  -- Very similar
    ARRAY['pilates', 'core', 'strength']
);
-- Expected: can_post=false, block_reason='similar_topic'

-- Test 4: Try with overlapping keywords (should fail)
SELECT * FROM validate_pin_uniqueness(
    'fit_over_35',
    'Evening Relaxation Routine',  -- Different topic
    ARRAY['yoga', 'stretching', 'flexibility', 'morning']  -- 75% overlap
);
-- Expected: can_post=false, block_reason='keyword_duplicate'

-- Test 5: Unique content (should pass)
SELECT * FROM validate_pin_uniqueness(
    'fit_over_35',
    'HIIT Workout for Beginners Over 35',
    ARRAY['hiit', 'cardio', 'workout', 'beginners', 'fitness']
);
-- Expected: can_post=true

-- Test 6: Check analytics
SELECT * FROM pinterest_post_analytics;

-- Test 7: View recent posts
SELECT id, topic, topic_category, image_keywords, posted_at
FROM pinterest_posts
WHERE brand = 'fit_over_35'
ORDER BY posted_at DESC
LIMIT 10;
```

#### Cleanup Test Data

```sql
-- Remove test data (be careful in production!)
DELETE FROM pinterest_posts WHERE topic LIKE '%Test%' OR topic LIKE '%Yoga Stretches%';
```

---

## Appendix A: Quick Reference

### Deduplication Rules Summary

| Rule | Timeframe | Threshold | Block Reason |
|------|-----------|-----------|--------------|
| Exact topic match | 7 days | 100% | `topic_duplicate` |
| Fuzzy topic match | 7 days | >80% similarity | `similar_topic` |
| Keyword overlap | 3 days | >60% overlap | `keyword_duplicate` |
| Category limit | Same day | 1 per day (configurable) | `category_limit` |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rest/v1/rpc/validate_pin_uniqueness` | POST | Pre-post validation |
| `/rest/v1/rpc/log_pinterest_post` | POST | Log successful post |
| `/rest/v1/pinterest_posts` | GET | Query posts |
| `/rest/v1/pinterest_posts` | POST | Insert manually |

### Make.com Variables Reference

| Variable | Source | Description |
|----------|--------|-------------|
| `{{topic}}` | Content generation | Pin topic/title |
| `{{image_keywords}}` | Content generation | Array of keywords |
| `{{category}}` | Auto-detected or specified | Topic category |
| `{{board}}` | Configuration | Target Pinterest board |
| `{{1.body[1].can_post}}` | Dedup check response | Boolean result |
| `{{1.body[1].block_reason}}` | Dedup check response | Why blocked |
| `{{1.body[1].block_details}}` | Dedup check response | JSON details |

---

## Appendix B: Troubleshooting

### Common Issues

**1. Function returns empty result**
- Check that `p_brand` matches exactly (case-sensitive)
- Verify the table has data: `SELECT COUNT(*) FROM pinterest_posts`

**2. Keyword overlap not detecting duplicates**
- Ensure keywords are normalized (lowercase, trimmed)
- Check array format in the function call

**3. Fuzzy matching not working**
- Verify `pg_trgm` extension is enabled: `SELECT * FROM pg_extension WHERE extname = 'pg_trgm'`
- Check trigram index exists: `SELECT indexname FROM pg_indexes WHERE tablename = 'pinterest_posts'`

**4. Make.com HTTP module failing**
- Verify Supabase URL and API key
- Check API key has permission to execute functions
- Test endpoint directly with curl/Postman

### Debug Query

```sql
-- Debug: Check what the validation function sees
SELECT
    LOWER(TRIM('Your Topic Here')) as normalized_topic,
    ARRAY(SELECT LOWER(TRIM(kw)) FROM UNNEST(ARRAY['keyword1', 'keyword2']) AS kw) as normalized_keywords,
    categorize_topic('Your Topic Here', ARRAY['keyword1', 'keyword2']) as auto_category;
```
