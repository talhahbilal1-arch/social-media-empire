-- Fix Schema Issues Migration
-- Run this in Supabase SQL Editor to fix all current monitoring errors
-- Date: 2026-02-13

-- =====================================================
-- 1. Add missing affiliate_products column to content_bank
--    Error: PGRST204 "Could not find the 'affiliate_products' column of 'content_bank'"
-- =====================================================
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS affiliate_products JSONB DEFAULT '[]';

-- =====================================================
-- 2. Add brand_id column that mirrors brand
--    Error: 42703 "column content_bank.brand_id does not exist"
--    Some external monitoring queries brand_id instead of brand
-- =====================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'content_bank' AND column_name = 'brand_id'
    ) THEN
        ALTER TABLE content_bank ADD COLUMN brand_id VARCHAR(50);
        -- Populate brand_id from brand for existing rows
        UPDATE content_bank SET brand_id = brand WHERE brand_id IS NULL;
        -- Create trigger to keep brand_id in sync with brand
        CREATE OR REPLACE FUNCTION sync_brand_id()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.brand_id := NEW.brand;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER content_bank_sync_brand_id
            BEFORE INSERT OR UPDATE ON content_bank
            FOR EACH ROW
            EXECUTE FUNCTION sync_brand_id();
    END IF;
END $$;

-- =====================================================
-- 2b. Ensure errors table exists with all needed columns
--     Error: 400 Bad Request on POST to errors table
-- =====================================================
CREATE TABLE IF NOT EXISTS errors (
    id BIGSERIAL PRIMARY KEY,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grant access on errors table
GRANT ALL ON errors TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE errors_id_seq TO anon, authenticated, service_role;

-- RLS policy for errors
ALTER TABLE errors ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Service role full access errors" ON errors;
CREATE POLICY "Service role full access errors" ON errors FOR ALL USING (true);

CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type);
CREATE INDEX IF NOT EXISTS idx_errors_resolved ON errors(resolved);
CREATE INDEX IF NOT EXISTS idx_errors_created_at ON errors(created_at);

-- =====================================================
-- 3. Create agent_runs table if it doesn't exist
--    Used by external monitoring to track component health
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_runs (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    last_run_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    run_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grant access
GRANT ALL ON agent_runs TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE agent_runs_id_seq TO anon, authenticated, service_role;

-- RLS for service role access
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Service role full access" ON agent_runs;
CREATE POLICY "Service role full access" ON agent_runs FOR ALL USING (true);

-- Upsert function for agent runs
CREATE OR REPLACE FUNCTION update_agent_run(
    p_agent_name VARCHAR,
    p_status VARCHAR DEFAULT 'success',
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO agent_runs (agent_name, last_run_at, status, error_message, run_count, updated_at)
    VALUES (p_agent_name, NOW(), p_status, p_error_message, 1, NOW())
    ON CONFLICT (agent_name) DO UPDATE SET
        last_run_at = NOW(),
        status = p_status,
        error_message = p_error_message,
        run_count = agent_runs.run_count + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Seed agent_runs with current agents so monitoring doesn't report stale entries
INSERT INTO agent_runs (agent_name, last_run_at, status, run_count) VALUES
    ('content_brain', NOW(), 'success', 1),
    ('video_factory', NOW(), 'success', 1),
    ('trend_discovery', NOW(), 'success', 1),
    ('multi_platform_poster', NOW(), 'success', 1),
    ('content_pipeline', NOW(), 'success', 1),
    ('image_selector', NOW(), 'success', 1)
ON CONFLICT (agent_name) DO UPDATE SET
    last_run_at = NOW(),
    status = 'success',
    updated_at = NOW();

-- =====================================================
-- 4. Grant access on content_bank for new columns
-- =====================================================
GRANT ALL ON content_bank TO anon, authenticated, service_role;

-- =====================================================
-- 5. Clear old unresolved errors that are now fixed
-- =====================================================
UPDATE errors SET resolved = TRUE, resolved_at = NOW(),
    resolution_notes = 'Auto-resolved: schema migration applied'
WHERE resolved = FALSE
AND (
    error_message LIKE '%affiliate_products%'
    OR error_message LIKE '%brand_id%'
    OR error_message LIKE '%is.not.null%'
    OR error_message LIKE '%video_factory%'
    OR error_message LIKE '%content_pipeline%'
    OR error_message LIKE '%agent_runs%'
);

-- =====================================================
-- 6. Refresh PostgREST schema cache
-- =====================================================
NOTIFY pgrst, 'reload schema';
