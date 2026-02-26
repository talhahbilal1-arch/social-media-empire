-- Migration 003: Pinterest Rebuild — Extend pinterest_pins for schedule-based Make.com pipeline
-- Safe to run multiple times (all ADD COLUMN IF NOT EXISTS)
-- Run in Supabase SQL Editor, then restart project (Settings > General, 5-8 min)

-- Add columns needed for Make.com-driven pipeline
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS account TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS pin_type TEXT DEFAULT 'image';
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS generated_image_url TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS overlay_headline TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS overlay_subtext TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS background_image_url TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS niche TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS content_json JSONB;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS hashtags TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS posted_at TIMESTAMPTZ;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS pin_id TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS article_generated BOOLEAN DEFAULT FALSE;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS topic TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS visual_style TEXT;
ALTER TABLE pinterest_pins ADD COLUMN IF NOT EXISTS tips JSONB;

-- Normalize status values for existing rows (anything not in the new set → 'posted')
UPDATE pinterest_pins
SET status = 'posted'
WHERE status NOT IN ('content_ready', 'ready', 'rendering', 'posting', 'posted', 'failed', 'dead');

-- Performance indexes for Make.com PostgREST queries
CREATE INDEX IF NOT EXISTS idx_pins_status ON pinterest_pins(status);
CREATE INDEX IF NOT EXISTS idx_pins_brand_status ON pinterest_pins(brand, status);
CREATE INDEX IF NOT EXISTS idx_pins_created_desc ON pinterest_pins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pins_retry ON pinterest_pins(status, retry_count);

-- Ensure access (RLS already disabled for this table)
GRANT ALL ON pinterest_pins TO anon, authenticated, service_role;
ALTER TABLE pinterest_pins DISABLE ROW LEVEL SECURITY;

-- Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify: run this after migration to confirm all new columns exist
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'pinterest_pins'
-- ORDER BY ordinal_position;
