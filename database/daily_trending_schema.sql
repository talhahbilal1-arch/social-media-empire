-- Daily Trending Topics table
-- Stores 3 trending topics per brand per day, discovered by daily_trend_scout.py
-- Must be run in Supabase SQL Editor, then restart the project to clear PostgREST cache

CREATE TABLE IF NOT EXISTS daily_trending (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    trend_date DATE NOT NULL DEFAULT CURRENT_DATE,
    topics JSONB NOT NULL,
    raw_data JSONB,
    sources_summary JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure one row per brand per day (safe reruns via upsert)
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_trending_unique
    ON daily_trending(brand, trend_date);

-- Fast lookups by brand + date
CREATE INDEX IF NOT EXISTS idx_daily_trending_brand_date
    ON daily_trending(brand, trend_date DESC);

-- Grant access to all Supabase roles
GRANT ALL ON daily_trending TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE daily_trending_id_seq TO anon, authenticated, service_role;
