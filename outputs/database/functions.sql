-- =============================================================================
-- Pinterest Empire V2 — Database Functions
-- =============================================================================
-- Target project: epfoxpgrpsnhlsglxvsa (production)
-- Run this in Supabase SQL Editor AFTER supabase_migration_v2.sql
--
-- Prerequisites:
--   - pg_trgm extension enabled
--   - inline_images table created
--   - pinterest_pins table with subdomain column
--   - subdomains table created
-- =============================================================================


-- =============================================================================
-- 1. get_todays_scheduled_pins()
-- =============================================================================
-- Returns all inline images scheduled for today that haven't been pinned yet.
-- Joins with pinterest_pins to get the parent post's subdomain and metadata.
--
-- Usage:
--   SELECT * FROM get_todays_scheduled_pins();
--
-- Returns: image details + parent post context for the Pinterest API call.

CREATE OR REPLACE FUNCTION get_todays_scheduled_pins()
RETURNS TABLE (
    image_id UUID,
    post_id UUID,
    image_index INTEGER,
    image_url TEXT,
    pexels_photo_id TEXT,
    pin_title TEXT,
    pin_description TEXT,
    board_id TEXT,
    scheduled_date DATE,
    -- Parent post context
    post_subdomain TEXT,
    post_type TEXT,
    post_url TEXT,
    post_brand TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ii.id AS image_id,
        ii.post_id,
        ii.image_index,
        ii.image_url,
        ii.pexels_photo_id,
        ii.pin_title,
        ii.pin_description,
        ii.board_id,
        ii.scheduled_date,
        -- Parent post fields
        pp.subdomain AS post_subdomain,
        pp.post_type,
        pp.post_url,
        pp.brand AS post_brand
    FROM inline_images ii
    LEFT JOIN pinterest_pins pp ON ii.post_id = pp.id::UUID
    WHERE ii.scheduled_date = CURRENT_DATE
      AND ii.pinned = FALSE
    ORDER BY ii.image_index ASC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_todays_scheduled_pins IS 'Get all unpinned inline images scheduled for today, with parent post context';


-- =============================================================================
-- 2. schedule_inline_images(post_id, images, board_id, start_date)
-- =============================================================================
-- Takes a JSONB array of image objects and inserts them into inline_images,
-- spacing each one 7 days apart starting from start_date.
--
-- Usage:
--   SELECT schedule_inline_images(
--     '550e8400-e29b-41d4-a716-446655440000'::UUID,
--     '[
--       {"image_url": "https://...", "pexels_photo_id": "123", "pin_title": "Tip 1", "pin_description": "..."},
--       {"image_url": "https://...", "pexels_photo_id": "456", "pin_title": "Tip 2", "pin_description": "..."}
--     ]'::JSONB,
--     'BOARD_ID_HERE',
--     '2026-02-10'::DATE
--   );
--
-- Each image is scheduled 7 days after the previous one:
--   Image 0 -> start_date
--   Image 1 -> start_date + 7
--   Image 2 -> start_date + 14
--   ...

CREATE OR REPLACE FUNCTION schedule_inline_images(
    p_post_id UUID,
    p_images JSONB,
    p_board_id TEXT,
    p_start_date DATE DEFAULT CURRENT_DATE
)
RETURNS INTEGER AS $$
DECLARE
    v_image JSONB;
    v_index INTEGER := 0;
    v_inserted INTEGER := 0;
BEGIN
    -- Validate input
    IF p_images IS NULL OR jsonb_array_length(p_images) = 0 THEN
        RAISE NOTICE 'No images provided, nothing to schedule';
        RETURN 0;
    END IF;

    -- Loop through each image in the JSONB array
    FOR v_image IN SELECT jsonb_array_elements(p_images)
    LOOP
        INSERT INTO inline_images (
            post_id,
            image_index,
            image_url,
            pexels_photo_id,
            pin_title,
            pin_description,
            board_id,
            scheduled_date
        ) VALUES (
            p_post_id,
            v_index,
            v_image ->> 'image_url',
            v_image ->> 'pexels_photo_id',
            COALESCE(v_image ->> 'pin_title', 'Untitled Pin'),
            v_image ->> 'pin_description',
            p_board_id,
            p_start_date + (v_index * 7)  -- 7-day spacing
        );

        v_index := v_index + 1;
        v_inserted := v_inserted + 1;
    END LOOP;

    RETURN v_inserted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION schedule_inline_images IS 'Insert inline images with 7-day staggered scheduling from start_date';


-- =============================================================================
-- 3. check_content_duplicate(subdomain, title, days_back)
-- =============================================================================
-- Checks if a proposed title is too similar to recent content in the same
-- subdomain. Uses pg_trgm similarity() with a threshold of 0.6.
--
-- Usage:
--   SELECT * FROM check_content_duplicate('home', 'Best Kitchen Organization Tips', 30);
--
-- Returns matching rows with their similarity scores. If the result set is
-- empty, the content is unique enough to publish.

CREATE OR REPLACE FUNCTION check_content_duplicate(
    p_subdomain TEXT,
    p_title TEXT,
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    pin_id UUID,
    existing_title TEXT,
    similarity_score REAL,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pp.id::UUID AS pin_id,
        pp.title::TEXT AS existing_title,
        similarity(pp.title, p_title) AS similarity_score,
        pp.created_at
    FROM pinterest_pins pp
    WHERE pp.subdomain = p_subdomain
      AND pp.created_at >= NOW() - (p_days_back || ' days')::INTERVAL
      AND similarity(pp.title, p_title) >= 0.6
    ORDER BY similarity_score DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION check_content_duplicate IS 'Find recent pins with similar titles (similarity >= 0.6) in same subdomain';


-- =============================================================================
-- 4. is_content_too_similar(new_title, subdomain, threshold)
-- =============================================================================
-- Quick boolean-like check: returns the maximum similarity score against
-- pins from the last 14 days. If max_similarity >= threshold, content is
-- too similar and should be regenerated.
--
-- Usage:
--   SELECT * FROM is_content_too_similar('5 Easy Meal Prep Ideas', 'kitchen', 0.4);
--
-- Returns:
--   max_similarity | is_duplicate | closest_title
--   0.72           | TRUE         | "5 Quick Meal Prep Recipes"
--
-- In application code:
--   if result.is_duplicate: regenerate_content()

CREATE OR REPLACE FUNCTION is_content_too_similar(
    p_new_title TEXT,
    p_subdomain TEXT,
    p_threshold FLOAT DEFAULT 0.4
)
RETURNS TABLE (
    max_similarity FLOAT,
    is_duplicate BOOLEAN,
    closest_title TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(MAX(similarity(pp.title, p_new_title))::FLOAT, 0.0) AS max_similarity,
        COALESCE(MAX(similarity(pp.title, p_new_title))::FLOAT, 0.0) >= p_threshold AS is_duplicate,
        (
            SELECT pp2.title::TEXT
            FROM pinterest_pins pp2
            WHERE pp2.subdomain = p_subdomain
              AND pp2.created_at >= NOW() - INTERVAL '14 days'
            ORDER BY similarity(pp2.title, p_new_title) DESC
            LIMIT 1
        ) AS closest_title
    FROM pinterest_pins pp
    WHERE pp.subdomain = p_subdomain
      AND pp.created_at >= NOW() - INTERVAL '14 days';
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION is_content_too_similar IS 'Check if title exceeds similarity threshold against last 14 days of pins in subdomain';


-- =============================================================================
-- Permissions for functions
-- =============================================================================
-- Ensure all roles can execute these functions via the Supabase API.

GRANT EXECUTE ON FUNCTION get_todays_scheduled_pins() TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION schedule_inline_images(UUID, JSONB, TEXT, DATE) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION check_content_duplicate(TEXT, TEXT, INTEGER) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION is_content_too_similar(TEXT, TEXT, FLOAT) TO anon, authenticated, service_role;
