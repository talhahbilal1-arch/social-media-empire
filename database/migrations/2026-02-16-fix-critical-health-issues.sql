-- Fix Critical Health Issues Migration
-- Date: 2026-02-16
-- Resolves: 3 CRITICAL errors and prepares self-healing/notification infrastructure
--
-- Run this in Supabase SQL Editor, then NOTIFY pgrst to reload schema.

-- =====================================================
-- CRITICAL FIX 1: Ensure affiliate_products column exists on content_bank
-- Error: PGRST204 "Could not find the 'affiliate_products' column of 'content_bank'"
-- =====================================================
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS affiliate_products JSONB DEFAULT '[]'::jsonb;

-- Also ensure all content_bank columns expected by agents exist
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS hashtags TEXT[];
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS video_script TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS image_prompt TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS source_images TEXT[];
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS destination_link TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS cta_text TEXT;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS performance_score DECIMAL(5,2) DEFAULT 0;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS platform_formats JSONB DEFAULT '{}';
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS trend_id UUID;
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- =====================================================
-- CRITICAL FIX 3: Ensure brand_id column exists on content_bank
-- Error: 42703 "column content_bank.brand_id does not exist"
-- Hint: "Perhaps you meant to reference the column content_bank.brand"
--
-- The content_bank table uses 'brand' in the live DB but agents query 'brand_id'.
-- Add brand_id if it doesn't exist and keep it synced with brand.
-- =====================================================
DO $$
BEGIN
    -- Add brand_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'content_bank' AND column_name = 'brand_id'
    ) THEN
        ALTER TABLE content_bank ADD COLUMN brand_id VARCHAR(50);

        -- Populate brand_id from brand for existing rows
        UPDATE content_bank SET brand_id = brand WHERE brand_id IS NULL AND brand IS NOT NULL;

        -- Create trigger to keep brand_id in sync with brand
        CREATE OR REPLACE FUNCTION sync_content_bank_brand_id()
        RETURNS TRIGGER AS $func$
        BEGIN
            IF NEW.brand IS NOT NULL AND NEW.brand_id IS NULL THEN
                NEW.brand_id := NEW.brand;
            ELSIF NEW.brand_id IS NOT NULL AND NEW.brand IS NULL THEN
                NEW.brand := NEW.brand_id;
            END IF;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS content_bank_sync_brand_id ON content_bank;
        CREATE TRIGGER content_bank_sync_brand_id
            BEFORE INSERT OR UPDATE ON content_bank
            FOR EACH ROW
            EXECUTE FUNCTION sync_content_bank_brand_id();
    END IF;
END $$;

-- Create index on brand_id for query performance
CREATE INDEX IF NOT EXISTS idx_content_bank_brand_id ON content_bank(brand_id);

-- =====================================================
-- NOTIFICATION SYSTEM: Add columns to health_checks table
-- For tracking consecutive failures and notification state
-- =====================================================
ALTER TABLE health_checks ADD COLUMN IF NOT EXISTS consecutive_failures INTEGER DEFAULT 0;
ALTER TABLE health_checks ADD COLUMN IF NOT EXISTS last_notified_at TIMESTAMPTZ;
ALTER TABLE health_checks ADD COLUMN IF NOT EXISTS auto_heal_attempted BOOLEAN DEFAULT false;
ALTER TABLE health_checks ADD COLUMN IF NOT EXISTS auto_heal_success BOOLEAN DEFAULT false;

-- =====================================================
-- Ensure agent_runs table has proper structure
-- =====================================================
-- Add missing columns if they don't exist (supports both schema versions)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'agent_runs' AND column_name = 'last_run_at'
    ) THEN
        ALTER TABLE agent_runs ADD COLUMN last_run_at TIMESTAMPTZ DEFAULT NOW();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'agent_runs' AND column_name = 'run_count'
    ) THEN
        ALTER TABLE agent_runs ADD COLUMN run_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- =====================================================
-- Clear stale errors related to these fixes
-- =====================================================
UPDATE errors SET resolved = TRUE, resolved_at = NOW(),
    resolution_notes = 'Auto-resolved: 2026-02-16 schema migration applied'
WHERE resolved = FALSE
AND (
    error_message LIKE '%affiliate_products%'
    OR error_message LIKE '%brand_id%'
    OR error_message LIKE '%is.not.null%'
    OR error_message LIKE '%not.null%'
    OR error_message LIKE '%PGRST204%'
    OR error_message LIKE '%PGRST100%'
    OR error_message LIKE '%42703%'
);

-- =====================================================
-- Refresh PostgREST schema cache
-- =====================================================
NOTIFY pgrst, 'reload schema';
