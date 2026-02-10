-- =============================================================================
-- Pinterest Empire V2 — Supabase Migration
-- =============================================================================
-- Target project: epfoxpgrpsnhlsglxvsa (production)
-- Run this in Supabase SQL Editor
--
-- This migration:
--   1. Adds new columns to the existing pinterest_pins table
--   2. Creates inline_images table for per-image pin scheduling
--   3. Creates subdomains table for brand subdomain management
--   4. Creates posting_schedule_v2 table for recurring schedules
--   5. Creates pin_performance table for analytics tracking
--   6. Enables pg_trgm extension for content similarity checks
--   7. Grants permissions for Supabase free tier compatibility
--
-- IMPORTANT: Run this ONCE. All statements use IF NOT EXISTS / IF EXISTS
-- guards so re-running is safe (idempotent).
-- =============================================================================


-- =============================================================================
-- 0. Extensions
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- =============================================================================
-- 1. ALTER existing pinterest_pins table
-- =============================================================================
-- Add new columns to support the subdomain-based content system.
-- The pinterest_pins table already exists in production; we only ADD columns.

ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS subdomain TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS post_type TEXT DEFAULT 'single';
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS listicle_items JSONB;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS featured_image_url TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS featured_image_pinned BOOLEAN DEFAULT FALSE;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS featured_pin_id TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS post_url TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS brand TEXT;

-- Add a comment explaining post_type values
COMMENT ON COLUMN pinterest_pins.post_type IS 'single = one image pin, listicle = multi-image blog post with inline pins';
COMMENT ON COLUMN pinterest_pins.listicle_items IS 'JSONB array of {heading, body, image_url, tip} for listicle posts';

-- Indexes for new query patterns
CREATE INDEX IF NOT EXISTS idx_pinterest_pins_subdomain ON pinterest_pins(subdomain);
CREATE INDEX IF NOT EXISTS idx_pinterest_pins_brand ON pinterest_pins(brand);
CREATE INDEX IF NOT EXISTS idx_pinterest_pins_post_type ON pinterest_pins(post_type);


-- =============================================================================
-- 2. Create inline_images table
-- =============================================================================
-- Each blog post (listicle) generates multiple inline images. Each image
-- becomes its own Pinterest pin, scheduled on different days for drip content.

CREATE TABLE IF NOT EXISTS inline_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Link to parent post
    post_id UUID NOT NULL,

    -- Image metadata
    image_index INTEGER NOT NULL,          -- Position within the post (0-based)
    image_url TEXT NOT NULL,               -- Pexels/generated image URL
    pexels_photo_id TEXT,                  -- Pexels photo ID for attribution

    -- Pin content (each image gets its own pin title/description)
    pin_title TEXT NOT NULL,
    pin_description TEXT,

    -- Scheduling
    scheduled_date DATE,                   -- When this image should be pinned
    pinned BOOLEAN DEFAULT FALSE,          -- Has it been pinned yet?
    pinned_at TIMESTAMPTZ,                 -- When it was actually pinned

    -- Pinterest result
    pin_id TEXT,                           -- Pinterest pin ID after posting
    board_id TEXT,                         -- Pinterest board it was posted to

    -- Performance tracking (denormalized for quick access)
    impressions INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0
);

-- Primary query: "get all unpinned images scheduled for today"
CREATE INDEX IF NOT EXISTS idx_inline_images_schedule
    ON inline_images(scheduled_date, pinned)
    WHERE pinned = FALSE;

-- Lookup all images for a given post
CREATE INDEX IF NOT EXISTS idx_inline_images_post_id
    ON inline_images(post_id);

-- Find images by pin status for reporting
CREATE INDEX IF NOT EXISTS idx_inline_images_pinned
    ON inline_images(pinned, pinned_at);

COMMENT ON TABLE inline_images IS 'Individual images extracted from listicle blog posts, each scheduled as a separate Pinterest pin';


-- =============================================================================
-- 3. Create subdomains table
-- =============================================================================
-- Each brand has multiple content subdomains (e.g., home.dailydealdarling.com).
-- This table drives content generation, scheduling, and board routing.

CREATE TABLE IF NOT EXISTS subdomains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Identity
    brand TEXT NOT NULL,                   -- 'ddd', 'fo35', etc.
    subdomain TEXT NOT NULL UNIQUE,        -- 'home', 'beauty', 'kitchen'
    full_url TEXT NOT NULL,                -- 'home.dailydealdarling.com'

    -- Pinterest routing
    pinterest_board_id TEXT,               -- Board ID for this subdomain's pins
    pinterest_board_name TEXT,             -- Human-readable board name

    -- Content config
    category TEXT NOT NULL,                -- Content category/niche
    description TEXT,                      -- What kind of content this produces

    -- Brand styling
    color_primary TEXT,                    -- Primary hex color (e.g., '#E3F2FD')
    color_secondary TEXT,                  -- Secondary hex color (e.g., '#1976D2')

    -- Scheduling
    posts_per_week INTEGER DEFAULT 3,      -- How many posts to generate per week
    is_active BOOLEAN DEFAULT TRUE         -- Can be deactivated without deleting
);

-- Fast lookup by brand
CREATE INDEX IF NOT EXISTS idx_subdomains_brand
    ON subdomains(brand);

-- Active subdomains only (common filter)
CREATE INDEX IF NOT EXISTS idx_subdomains_active
    ON subdomains(is_active)
    WHERE is_active = TRUE;

COMMENT ON TABLE subdomains IS 'Brand subdomain configuration: content categories, Pinterest board routing, and styling';


-- =============================================================================
-- 4. Create posting_schedule table (v2)
-- =============================================================================
-- Defines recurring posting times per subdomain.
-- Note: The original posting_schedule table (from schemas.sql) used BIGSERIAL
-- and was tied to the video pipeline. This v2 version is UUID-based and
-- subdomain-oriented for the Pinterest content system.

CREATE TABLE IF NOT EXISTS posting_schedule_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Which subdomain this schedule applies to
    subdomain_id UUID NOT NULL REFERENCES subdomains(id) ON DELETE CASCADE,

    -- Recurring schedule
    day_of_week INTEGER NOT NULL           -- 0=Sunday, 1=Monday, ..., 6=Saturday
        CHECK (day_of_week >= 0 AND day_of_week <= 6),
    post_time TIME NOT NULL,               -- Time of day to post (PST assumed)

    is_active BOOLEAN DEFAULT TRUE
);

-- Lookup schedule for a given subdomain
CREATE INDEX IF NOT EXISTS idx_posting_schedule_v2_subdomain
    ON posting_schedule_v2(subdomain_id);

-- Find all active schedules for a given day
CREATE INDEX IF NOT EXISTS idx_posting_schedule_v2_day
    ON posting_schedule_v2(day_of_week, is_active)
    WHERE is_active = TRUE;

COMMENT ON TABLE posting_schedule_v2 IS 'Recurring posting schedule per subdomain (day of week + time)';


-- =============================================================================
-- 5. Create pin_performance table
-- =============================================================================
-- Periodic snapshots of pin analytics. Supports both pinterest_pins (featured)
-- and inline_images (drip) sources.

CREATE TABLE IF NOT EXISTS pin_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),

    -- Which pin this tracks
    pin_id TEXT NOT NULL,                  -- Pinterest pin ID
    source_table TEXT NOT NULL             -- 'pinterest_pins' or 'inline_images'
        CHECK (source_table IN ('pinterest_pins', 'inline_images')),
    source_id UUID NOT NULL,               -- UUID of the row in source_table

    -- Metrics snapshot
    impressions INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    closeups INTEGER DEFAULT 0
);

-- Time-series query: performance over time for a pin
CREATE INDEX IF NOT EXISTS idx_pin_performance_pin_id
    ON pin_performance(pin_id, recorded_at);

-- Lookup by source for batch analytics
CREATE INDEX IF NOT EXISTS idx_pin_performance_source
    ON pin_performance(source_table, source_id);

-- Recent performance window
CREATE INDEX IF NOT EXISTS idx_pin_performance_recent
    ON pin_performance(recorded_at DESC);

COMMENT ON TABLE pin_performance IS 'Time-series analytics snapshots for Pinterest pins from any source table';


-- =============================================================================
-- 6. Permissions (CRITICAL for Supabase free tier)
-- =============================================================================
-- Supabase requires explicit grants on new tables for the API to work.
-- Without these, PostgREST returns 401/403 errors.

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- Grant usage on the pg_trgm extension functions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;


-- =============================================================================
-- 7. Disable RLS on new tables (match existing pattern)
-- =============================================================================
-- The existing tables use RLS with permissive policies. For the new tables,
-- we disable RLS entirely since all access is via service_role key.
-- If you want RLS, enable it and add policies per table.

ALTER TABLE inline_images DISABLE ROW LEVEL SECURITY;
ALTER TABLE subdomains DISABLE ROW LEVEL SECURITY;
ALTER TABLE posting_schedule_v2 DISABLE ROW LEVEL SECURITY;
ALTER TABLE pin_performance DISABLE ROW LEVEL SECURITY;


-- =============================================================================
-- ROLLBACK (uncomment to undo this migration)
-- =============================================================================
-- WARNING: This will DROP tables and columns permanently!
--
-- -- Remove new tables
-- DROP TABLE IF EXISTS pin_performance CASCADE;
-- DROP TABLE IF EXISTS posting_schedule_v2 CASCADE;
-- DROP TABLE IF EXISTS inline_images CASCADE;
-- DROP TABLE IF EXISTS subdomains CASCADE;
--
-- -- Remove columns added to pinterest_pins
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS subdomain;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS post_type;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS listicle_items;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS featured_image_url;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS featured_image_pinned;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS featured_pin_id;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS post_url;
-- ALTER TABLE pinterest_pins DROP COLUMN IF EXISTS brand;
--
-- -- Remove indexes on pinterest_pins
-- DROP INDEX IF EXISTS idx_pinterest_pins_subdomain;
-- DROP INDEX IF EXISTS idx_pinterest_pins_brand;
-- DROP INDEX IF EXISTS idx_pinterest_pins_post_type;
--
-- -- Remove extension (only if no other usage)
-- DROP EXTENSION IF EXISTS pg_trgm;
