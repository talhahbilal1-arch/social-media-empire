-- ============================================================
-- 002_fix_pinterest_pins_schema.sql
-- CRITICAL FIX: Add missing columns to pinterest_pins table
-- that the content-engine.yml pipeline requires.
--
-- Without these columns, Phase 0 INSERT fails silently and
-- NO pins are generated, rendered, or posted.
--
-- Run in Supabase SQL Editor immediately.
-- Safe to re-run (uses IF NOT EXISTS).
-- ============================================================

-- Phase 0 (content generation) columns
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS overlay_headline TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS overlay_subtext TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS tips JSONB DEFAULT '[]';
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS pexels_search_term TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS niche VARCHAR(100);
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS topic TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS visual_style VARCHAR(100);

-- Phase 1 (rendering) columns
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS generated_image_url TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS image_hash TEXT;

-- Phase 2 (article generation) columns
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS article_generated BOOLEAN DEFAULT FALSE;

-- Phase 1b (posting) columns
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS posted_at TIMESTAMPTZ;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Reload PostgREST schema cache so new columns are immediately available
NOTIFY pgrst, 'reload schema';

-- Verify columns exist
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'pinterest_pins'
ORDER BY ordinal_position;
