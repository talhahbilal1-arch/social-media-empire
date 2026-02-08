-- ============================================================================
-- Fit Over 35 -- Content Deduplication SQL
-- ============================================================================
-- Run these in Supabase SQL Editor in order.
-- Depends on: content_history table (from content_history_schema.sql)
--
-- What this file provides:
--   1. pg_trgm extension for fuzzy text similarity
--   2. Query to get recent pins for deduplication (last 14 days by subdomain)
--   3. Function: is_content_too_similar() -- checks new title against recent pins
--   4. Function: get_content_gaps() -- finds underused topic angles
--   5. Function: get_posting_stats() -- per-subdomain posting frequency
--   6. View: v_recent_content_by_category -- gap analysis dashboard
-- ============================================================================


-- ============================================================================
-- 1. Enable pg_trgm extension
-- ============================================================================
-- pg_trgm provides trigram-based similarity functions: similarity(), word_similarity(),
-- and the % operator. This is the foundation for fuzzy title matching.
-- On Supabase, this extension is available but must be explicitly enabled.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create a GIN trigram index on content_history.title for fast similarity lookups.
-- This index accelerates similarity() and % operator queries significantly.
CREATE INDEX IF NOT EXISTS idx_content_history_title_trgm
ON content_history USING GIN (title gin_trgm_ops);

-- Create a trigram index on the description column as well for broader dedup checks.
CREATE INDEX IF NOT EXISTS idx_content_history_description_trgm
ON content_history USING GIN (description gin_trgm_ops);

-- Add a topic_angle column to content_history if it does not already exist.
-- This tracks which of the 7 angles (WHY, HOW, MISTAKE, SCIENCE, IDENTITY, SYSTEM, CONTRAST)
-- was used for each pin, enabling gap analysis.
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS topic_angle TEXT;

-- Add a subdomain column for multi-brand filtering within the same brand key.
-- For FO35 this maps to board categories; for other brands it maps to content verticals.
-- If your content_history already uses 'board' for this purpose, this column provides
-- a normalized alternative that is decoupled from Pinterest board naming.
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS subdomain TEXT;

-- Index for subdomain-based queries (used by all functions below).
CREATE INDEX IF NOT EXISTS idx_content_history_subdomain
ON content_history(subdomain, created_at DESC);

-- Composite index for the most common dedup query pattern.
CREATE INDEX IF NOT EXISTS idx_content_history_dedup_composite
ON content_history(brand, subdomain, created_at DESC);

-- Index for topic_angle gap analysis.
CREATE INDEX IF NOT EXISTS idx_content_history_topic_angle
ON content_history(brand, subdomain, topic_angle, created_at DESC);


-- ============================================================================
-- 2. Query: Get recent pins for deduplication (last 14 days by subdomain)
-- ============================================================================
-- Use this query (or wrap it in an RPC) to fetch the recent pin titles and
-- metadata that get injected into the Claude prompt as {recent_pins_list}.
--
-- Parameters:
--   $1 = subdomain (e.g., 'workout_tips', 'nutrition', 'recovery', 'identity', 'home_gym')
--   $2 = number of days to look back (default 14)
--
-- Example usage from Python/PostgREST:
--   supabase.rpc('get_recent_pins_for_dedup', {
--       'p_subdomain': 'workout_tips',
--       'p_days_back': 14
--   })

CREATE OR REPLACE FUNCTION get_recent_pins_for_dedup(
    p_subdomain TEXT,
    p_days_back INTEGER DEFAULT 14
)
RETURNS TABLE (
    id BIGINT,
    title TEXT,
    description TEXT,
    topic TEXT,
    topic_angle TEXT,
    board TEXT,
    image_query TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ch.id,
        ch.title,
        ch.description,
        ch.topic,
        ch.topic_angle,
        ch.board,
        ch.image_query,
        ch.created_at
    FROM content_history ch
    WHERE ch.subdomain = p_subdomain
      AND ch.created_at >= (NOW() - (p_days_back || ' days')::INTERVAL)
    ORDER BY ch.created_at DESC
    LIMIT 50;
END;
$$;

-- Alternate plain SQL query for direct use (not wrapped in a function):
-- SELECT id, title, description, topic, topic_angle, board, image_query, created_at
-- FROM content_history
-- WHERE subdomain = 'workout_tips'
--   AND created_at >= NOW() - INTERVAL '14 days'
-- ORDER BY created_at DESC
-- LIMIT 50;


-- ============================================================================
-- 3. Function: is_content_too_similar()
-- ============================================================================
-- Checks whether a proposed new pin title is too similar to any recent pin
-- in the same subdomain. Uses pg_trgm similarity() which returns a float
-- between 0.0 (completely different) and 1.0 (identical).
--
-- Parameters:
--   p_new_title   TEXT    -- The proposed title to check
--   p_subdomain   TEXT    -- The subdomain/board category to check against
--   p_threshold   FLOAT  -- Similarity threshold (default 0.4; titles above this are "too similar")
--
-- Returns a single row with:
--   is_too_similar   BOOLEAN  -- TRUE if the max similarity exceeds threshold
--   max_similarity   FLOAT    -- The highest similarity score found
--   most_similar_id  BIGINT   -- ID of the most similar existing pin
--   most_similar_title TEXT   -- Title of the most similar existing pin
--
-- A threshold of 0.4 is intentionally aggressive. Trigram similarity of 0.4
-- catches titles that share significant phrasing even if worded differently.
-- Tune this up (e.g., 0.5) if you get too many false positives, or down (e.g., 0.35)
-- if near-duplicates are slipping through.

CREATE OR REPLACE FUNCTION is_content_too_similar(
    p_new_title TEXT,
    p_subdomain TEXT,
    p_threshold FLOAT DEFAULT 0.4
)
RETURNS TABLE (
    is_too_similar BOOLEAN,
    max_similarity FLOAT,
    most_similar_id BIGINT,
    most_similar_title TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_max_sim FLOAT := 0.0;
    v_similar_id BIGINT;
    v_similar_title TEXT;
BEGIN
    -- Find the most similar title from the last 30 days in this subdomain.
    -- We look at 30 days (not 14) for similarity to cast a wider net against
    -- repetition, even though the prompt only shows the last 14 days.
    SELECT
        similarity(ch.title, p_new_title),
        ch.id,
        ch.title
    INTO
        v_max_sim,
        v_similar_id,
        v_similar_title
    FROM content_history ch
    WHERE ch.subdomain = p_subdomain
      AND ch.created_at >= NOW() - INTERVAL '30 days'
      AND ch.title IS NOT NULL
      AND ch.title != ''
    ORDER BY similarity(ch.title, p_new_title) DESC
    LIMIT 1;

    -- Handle case where no recent pins exist
    IF v_max_sim IS NULL THEN
        v_max_sim := 0.0;
    END IF;

    RETURN QUERY
    SELECT
        (v_max_sim >= p_threshold) AS is_too_similar,
        v_max_sim AS max_similarity,
        v_similar_id AS most_similar_id,
        v_similar_title AS most_similar_title;
END;
$$;

-- Also provide a broader check that examines BOTH title and description similarity.
-- This catches cases where the title is reworded but the description is nearly identical.

CREATE OR REPLACE FUNCTION is_content_too_similar_full(
    p_new_title TEXT,
    p_new_description TEXT,
    p_subdomain TEXT,
    p_title_threshold FLOAT DEFAULT 0.4,
    p_description_threshold FLOAT DEFAULT 0.35
)
RETURNS TABLE (
    is_too_similar BOOLEAN,
    title_max_similarity FLOAT,
    description_max_similarity FLOAT,
    most_similar_id BIGINT,
    most_similar_title TEXT,
    rejection_reason TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_title_sim FLOAT := 0.0;
    v_desc_sim FLOAT := 0.0;
    v_similar_id BIGINT;
    v_similar_title TEXT;
    v_reason TEXT := NULL;
BEGIN
    -- Check title similarity
    SELECT
        similarity(ch.title, p_new_title),
        ch.id,
        ch.title
    INTO
        v_title_sim,
        v_similar_id,
        v_similar_title
    FROM content_history ch
    WHERE ch.subdomain = p_subdomain
      AND ch.created_at >= NOW() - INTERVAL '30 days'
      AND ch.title IS NOT NULL
      AND ch.title != ''
    ORDER BY similarity(ch.title, p_new_title) DESC
    LIMIT 1;

    -- Check description similarity (separate pass)
    SELECT
        GREATEST(v_desc_sim, similarity(ch.description, p_new_description))
    INTO v_desc_sim
    FROM content_history ch
    WHERE ch.subdomain = p_subdomain
      AND ch.created_at >= NOW() - INTERVAL '30 days'
      AND ch.description IS NOT NULL
      AND ch.description != ''
    ORDER BY similarity(ch.description, p_new_description) DESC
    LIMIT 1;

    -- Handle NULLs
    IF v_title_sim IS NULL THEN v_title_sim := 0.0; END IF;
    IF v_desc_sim IS NULL THEN v_desc_sim := 0.0; END IF;

    -- Determine rejection reason
    IF v_title_sim >= p_title_threshold AND v_desc_sim >= p_description_threshold THEN
        v_reason := 'Both title and description too similar to pin #' || v_similar_id;
    ELSIF v_title_sim >= p_title_threshold THEN
        v_reason := 'Title too similar to pin #' || v_similar_id || ': "' || LEFT(v_similar_title, 60) || '"';
    ELSIF v_desc_sim >= p_description_threshold THEN
        v_reason := 'Description too similar to a recent pin';
    END IF;

    RETURN QUERY
    SELECT
        (v_title_sim >= p_title_threshold OR v_desc_sim >= p_description_threshold) AS is_too_similar,
        v_title_sim AS title_max_similarity,
        v_desc_sim AS description_max_similarity,
        v_similar_id AS most_similar_id,
        v_similar_title AS most_similar_title,
        v_reason AS rejection_reason;
END;
$$;


-- ============================================================================
-- 4. Function: get_content_gaps()
-- ============================================================================
-- Identifies which topic angles have NOT been used recently for a given subdomain.
-- This drives the {random_angle} selection in the prompt, ensuring all 7 angles
-- get rotated through before any angle repeats.
--
-- Parameters:
--   p_subdomain TEXT -- The subdomain/board category to analyze
--
-- Returns one row per topic angle showing:
--   - angle name
--   - number of times used in the last 14 days
--   - number of times used in the last 30 days
--   - days since last use (NULL if never used)
--   - gap_priority: 'high' (never used or 7+ days), 'medium' (3-6 days), 'low' (0-2 days)

CREATE OR REPLACE FUNCTION get_content_gaps(
    p_subdomain TEXT
)
RETURNS TABLE (
    angle TEXT,
    uses_last_14_days BIGINT,
    uses_last_30_days BIGINT,
    days_since_last_use INTEGER,
    last_used_at TIMESTAMPTZ,
    gap_priority TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH all_angles AS (
        -- The 7 canonical topic angles for Fit Over 35
        SELECT unnest(ARRAY[
            'WHY', 'HOW', 'MISTAKE', 'SCIENCE', 'IDENTITY', 'SYSTEM', 'CONTRAST'
        ]) AS angle_name
    ),
    usage_14d AS (
        SELECT
            ch.topic_angle AS angle_name,
            COUNT(*) AS cnt
        FROM content_history ch
        WHERE ch.subdomain = p_subdomain
          AND ch.created_at >= NOW() - INTERVAL '14 days'
          AND ch.topic_angle IS NOT NULL
        GROUP BY ch.topic_angle
    ),
    usage_30d AS (
        SELECT
            ch.topic_angle AS angle_name,
            COUNT(*) AS cnt
        FROM content_history ch
        WHERE ch.subdomain = p_subdomain
          AND ch.created_at >= NOW() - INTERVAL '30 days'
          AND ch.topic_angle IS NOT NULL
        GROUP BY ch.topic_angle
    ),
    last_used AS (
        SELECT DISTINCT ON (ch.topic_angle)
            ch.topic_angle AS angle_name,
            ch.created_at AS last_at
        FROM content_history ch
        WHERE ch.subdomain = p_subdomain
          AND ch.topic_angle IS NOT NULL
        ORDER BY ch.topic_angle, ch.created_at DESC
    )
    SELECT
        a.angle_name AS angle,
        COALESCE(u14.cnt, 0) AS uses_last_14_days,
        COALESCE(u30.cnt, 0) AS uses_last_30_days,
        CASE
            WHEN lu.last_at IS NOT NULL
            THEN EXTRACT(DAY FROM (NOW() - lu.last_at))::INTEGER
            ELSE NULL
        END AS days_since_last_use,
        lu.last_at AS last_used_at,
        CASE
            WHEN lu.last_at IS NULL THEN 'high'
            WHEN EXTRACT(DAY FROM (NOW() - lu.last_at)) >= 7 THEN 'high'
            WHEN EXTRACT(DAY FROM (NOW() - lu.last_at)) >= 3 THEN 'medium'
            ELSE 'low'
        END AS gap_priority
    FROM all_angles a
    LEFT JOIN usage_14d u14 ON u14.angle_name = a.angle_name
    LEFT JOIN usage_30d u30 ON u30.angle_name = a.angle_name
    LEFT JOIN last_used lu ON lu.angle_name = a.angle_name
    ORDER BY
        -- high priority first, then medium, then low
        CASE
            WHEN lu.last_at IS NULL THEN 0
            WHEN EXTRACT(DAY FROM (NOW() - lu.last_at)) >= 7 THEN 1
            WHEN EXTRACT(DAY FROM (NOW() - lu.last_at)) >= 3 THEN 2
            ELSE 3
        END,
        -- Within same priority, least recently used first
        COALESCE(lu.last_at, '1970-01-01'::TIMESTAMPTZ) ASC;
END;
$$;


-- ============================================================================
-- 5. Function: get_posting_stats()
-- ============================================================================
-- Returns per-subdomain posting frequency statistics for a given brand.
-- Useful for monitoring whether content distribution is balanced across
-- all subdomains/boards.
--
-- Parameters:
--   p_brand TEXT -- The brand key (e.g., 'fitness', 'deals', 'menopause')
--
-- Returns one row per subdomain with:
--   - total pin count
--   - pins in last 7 days
--   - pins in last 14 days
--   - pins in last 30 days
--   - average pins per day (last 30 days)
--   - most common topic angle used
--   - most recent pin date
--   - unique topic angles used in last 14 days

CREATE OR REPLACE FUNCTION get_posting_stats(
    p_brand TEXT
)
RETURNS TABLE (
    subdomain TEXT,
    total_pins BIGINT,
    pins_last_7_days BIGINT,
    pins_last_14_days BIGINT,
    pins_last_30_days BIGINT,
    avg_pins_per_day NUMERIC,
    most_common_angle TEXT,
    most_recent_pin TIMESTAMPTZ,
    unique_angles_last_14d BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH base AS (
        SELECT
            ch.subdomain AS sd,
            ch.topic_angle,
            ch.created_at
        FROM content_history ch
        WHERE ch.brand = p_brand
          AND ch.subdomain IS NOT NULL
    ),
    totals AS (
        SELECT
            sd,
            COUNT(*) AS total_cnt,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') AS cnt_7d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '14 days') AS cnt_14d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS cnt_30d,
            MAX(created_at) AS latest_pin
        FROM base
        GROUP BY sd
    ),
    angle_counts AS (
        SELECT
            sd,
            topic_angle,
            COUNT(*) AS angle_cnt,
            ROW_NUMBER() OVER (PARTITION BY sd ORDER BY COUNT(*) DESC) AS rn
        FROM base
        WHERE created_at >= NOW() - INTERVAL '30 days'
          AND topic_angle IS NOT NULL
        GROUP BY sd, topic_angle
    ),
    unique_angles AS (
        SELECT
            sd,
            COUNT(DISTINCT topic_angle) AS uniq_angles
        FROM base
        WHERE created_at >= NOW() - INTERVAL '14 days'
          AND topic_angle IS NOT NULL
        GROUP BY sd
    )
    SELECT
        t.sd AS subdomain,
        t.total_cnt AS total_pins,
        t.cnt_7d AS pins_last_7_days,
        t.cnt_14d AS pins_last_14_days,
        t.cnt_30d AS pins_last_30_days,
        ROUND(t.cnt_30d::NUMERIC / 30.0, 2) AS avg_pins_per_day,
        ac.topic_angle AS most_common_angle,
        t.latest_pin AS most_recent_pin,
        COALESCE(ua.uniq_angles, 0) AS unique_angles_last_14d
    FROM totals t
    LEFT JOIN angle_counts ac ON ac.sd = t.sd AND ac.rn = 1
    LEFT JOIN unique_angles ua ON ua.sd = t.sd
    ORDER BY t.cnt_30d DESC, t.sd;
END;
$$;


-- ============================================================================
-- 6. View: v_recent_content_by_category
-- ============================================================================
-- Dashboard view showing recent content grouped by subdomain and topic angle.
-- Use this to visually identify gaps in angle rotation and spot content clustering.
--
-- Each row represents one subdomain + topic_angle combination, showing the count
-- of pins using that combination in the last 14 days and the most recent title.

CREATE OR REPLACE VIEW v_recent_content_by_category AS
WITH recent AS (
    SELECT
        ch.brand,
        ch.subdomain,
        ch.topic_angle,
        ch.title,
        ch.board,
        ch.created_at,
        ROW_NUMBER() OVER (
            PARTITION BY ch.subdomain, ch.topic_angle
            ORDER BY ch.created_at DESC
        ) AS rn
    FROM content_history ch
    WHERE ch.created_at >= NOW() - INTERVAL '14 days'
      AND ch.subdomain IS NOT NULL
),
angle_stats AS (
    SELECT
        brand,
        subdomain,
        topic_angle,
        COUNT(*) AS pin_count,
        MAX(created_at) AS latest_pin_at,
        MIN(created_at) AS earliest_pin_at
    FROM recent
    GROUP BY brand, subdomain, topic_angle
)
SELECT
    a.brand,
    a.subdomain,
    a.topic_angle,
    a.pin_count,
    a.latest_pin_at,
    a.earliest_pin_at,
    EXTRACT(DAY FROM (NOW() - a.latest_pin_at))::INTEGER AS days_since_latest,
    r.title AS most_recent_title,
    r.board AS most_recent_board,
    -- Flag subdomains where one angle is overrepresented
    CASE
        WHEN a.pin_count >= 4 THEN 'OVERUSED'
        WHEN a.pin_count >= 2 THEN 'moderate'
        WHEN a.pin_count = 1 THEN 'ok'
        ELSE 'gap'
    END AS usage_status
FROM angle_stats a
LEFT JOIN recent r ON r.subdomain = a.subdomain
                   AND r.topic_angle = a.topic_angle
                   AND r.rn = 1
ORDER BY a.subdomain, a.pin_count DESC, a.latest_pin_at DESC;

-- Add a comment on the view for documentation.
COMMENT ON VIEW v_recent_content_by_category IS
    'Dashboard view for FO35 content gap analysis. Shows pin count by subdomain + topic_angle for the last 14 days. Rows marked OVERUSED indicate angles that need to be rested.';


-- ============================================================================
-- GRANTS -- Required for Supabase service_role / anon access
-- ============================================================================
-- On Supabase free tier, new functions and views need explicit grants.

GRANT EXECUTE ON FUNCTION get_recent_pins_for_dedup(TEXT, INTEGER) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION is_content_too_similar(TEXT, TEXT, FLOAT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION is_content_too_similar_full(TEXT, TEXT, TEXT, FLOAT, FLOAT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_content_gaps(TEXT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_posting_stats(TEXT) TO anon, authenticated, service_role;
GRANT SELECT ON v_recent_content_by_category TO anon, authenticated, service_role;


-- ============================================================================
-- USAGE EXAMPLES (for reference, do not run as-is)
-- ============================================================================

-- Example 1: Check if a proposed title is too similar to recent content
--
-- SELECT * FROM is_content_too_similar(
--     'Why Compound Lifts Matter More After 35',
--     'workout_tips',
--     0.4
-- );
-- Returns: is_too_similar=true, max_similarity=0.52, most_similar_title='Why Compound Movements Beat Isolation After 35'

-- Example 2: Full similarity check (title + description)
--
-- SELECT * FROM is_content_too_similar_full(
--     'The Protein Timing Myth That Won''t Die',
--     'Research shows the anabolic window is actually 24-48 hours, not 30 minutes. Stop chugging shakes in the locker room.',
--     'nutrition',
--     0.4,
--     0.35
-- );

-- Example 3: Find which topic angles need attention for workout_tips
--
-- SELECT * FROM get_content_gaps('workout_tips');
-- Returns rows like:
--   angle=IDENTITY, uses_last_14_days=0, days_since_last_use=NULL, gap_priority='high'
--   angle=CONTRAST, uses_last_14_days=0, days_since_last_use=12, gap_priority='high'
--   angle=HOW, uses_last_14_days=3, days_since_last_use=1, gap_priority='low'

-- Example 4: Get posting stats across all subdomains for the fitness brand
--
-- SELECT * FROM get_posting_stats('fitness');
-- Returns rows like:
--   subdomain=workout_tips, total_pins=45, pins_last_7_days=6, avg_pins_per_day=0.87, unique_angles_last_14d=5
--   subdomain=nutrition, total_pins=38, pins_last_7_days=4, avg_pins_per_day=0.60, unique_angles_last_14d=4

-- Example 5: View the gap analysis dashboard
--
-- SELECT * FROM v_recent_content_by_category WHERE brand = 'fitness' ORDER BY subdomain, usage_status;

-- Example 6: Python integration in content_brain.py
--
-- # Before generating a pin:
-- gaps = supabase.rpc('get_content_gaps', {'p_subdomain': 'workout_tips'}).execute()
-- high_priority_angles = [g['angle'] for g in gaps.data if g['gap_priority'] == 'high']
-- random_angle = random.choice(high_priority_angles) if high_priority_angles else random.choice(ALL_ANGLES)
--
-- # After Claude generates the title, before posting:
-- similarity = supabase.rpc('is_content_too_similar', {
--     'p_new_title': pin_data['title'],
--     'p_subdomain': 'workout_tips',
--     'p_threshold': 0.4
-- }).execute()
--
-- if similarity.data[0]['is_too_similar']:
--     # Regenerate with a note to avoid the similar title
--     ...
