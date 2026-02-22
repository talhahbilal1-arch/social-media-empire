-- ============================================================
-- 001_master_schema.sql — Consolidated idempotent master schema
-- Safe to re-run at any time. All DDL uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS.
-- Run in Supabase SQL Editor (Settings > SQL Editor).
-- ============================================================

-- ── videos ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    platform VARCHAR(50),
    title TEXT,
    script TEXT,
    video_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS template_id VARCHAR(100);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS render_job_id VARCHAR(100);

-- ── content_bank ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_bank (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    brand_id VARCHAR(100),
    content_type VARCHAR(50),
    title TEXT,
    content TEXT,
    tags JSONB DEFAULT '[]',
    affiliate_products JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS brand_id VARCHAR(100);
ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS affiliate_products JSONB DEFAULT '[]';

-- ── agent_runs ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_runs (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(100) UNIQUE NOT NULL,
    last_run_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'never_run',
    run_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed agent_runs with known agents (idempotent)
INSERT INTO agent_runs (agent_name, status) VALUES
    ('content_brain', 'never_run'),
    ('video_factory', 'never_run'),
    ('trend_discovery', 'never_run'),
    ('multi_platform_poster', 'never_run'),
    ('content_pipeline', 'never_run'),
    ('image_selector', 'never_run'),
    ('pin_article_generator', 'never_run')
ON CONFLICT (agent_name) DO NOTHING;

-- ── subscribers ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscribers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    brand VARCHAR(100),
    source VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── analytics ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analytics (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    platform VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── errors ────────────────────────────────────────────────────
-- severity column was missing — added here and via ALTER
CREATE TABLE IF NOT EXISTS errors (
    id BIGSERIAL PRIMARY KEY,
    error_type VARCHAR(100),
    error_message TEXT,
    context JSONB,
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE errors ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'medium';
ALTER TABLE errors ADD COLUMN IF NOT EXISTS resolved BOOLEAN DEFAULT FALSE;

-- Clear stale error entries from known failure patterns so they don't pile up
DELETE FROM errors
WHERE created_at < NOW() - INTERVAL '7 days'
   OR error_message LIKE '%column "severity" of relation "errors" does not exist%'
   OR error_message LIKE '%null value in column "severity"%';

-- ── email_sequences ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS email_sequences (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    sequence_name VARCHAR(100),
    step_number INTEGER,
    subject TEXT,
    body TEXT,
    delay_days INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── posting_schedule ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posting_schedule (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    platform VARCHAR(50),
    scheduled_at TIMESTAMPTZ,
    content_id BIGINT REFERENCES content_bank(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── content_history ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_history (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    title TEXT,
    description TEXT,
    topic TEXT,
    category VARCHAR(100),
    angle_framework TEXT,
    visual_style VARCHAR(100),
    board VARCHAR(200),
    description_opener VARCHAR(50),
    image_query TEXT,
    image_url TEXT,
    pexels_image_id TEXT,
    destination_url TEXT,
    posting_method VARCHAR(100),
    trending_topic TEXT,
    week_calendar_id BIGINT,
    status VARCHAR(20) DEFAULT 'posted',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS trending_topic TEXT;
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS week_calendar_id BIGINT;
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'posted';

-- ── daily_trending ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_trending (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    trend_date DATE NOT NULL,
    topics JSONB NOT NULL DEFAULT '[]',
    raw_data JSONB,
    sources_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, trend_date)
);

-- ── weekly_calendar ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weekly_calendar (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    week_start DATE,
    calendar_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── generated_articles ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS generated_articles (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    slug TEXT NOT NULL,
    title TEXT,
    topic TEXT,
    article_url TEXT,
    word_count INTEGER,
    has_affiliate_links BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, slug)
);

-- ── pinterest_pins ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pinterest_pins (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    title TEXT,
    description TEXT,
    image_url TEXT,
    board_id TEXT,
    destination_url TEXT,
    pinterest_pin_id TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── RLS: disable on all tables (service_role bypasses anyway, but explicit for safety) ──
ALTER TABLE videos DISABLE ROW LEVEL SECURITY;
ALTER TABLE content_bank DISABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs DISABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;
ALTER TABLE errors DISABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences DISABLE ROW LEVEL SECURITY;
ALTER TABLE posting_schedule DISABLE ROW LEVEL SECURITY;
ALTER TABLE content_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE daily_trending DISABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_calendar DISABLE ROW LEVEL SECURITY;
ALTER TABLE generated_articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE pinterest_pins DISABLE ROW LEVEL SECURITY;

-- ── GRANT ALL to anon + authenticated + service_role on all tables ──
GRANT ALL ON videos TO anon, authenticated, service_role;
GRANT ALL ON content_bank TO anon, authenticated, service_role;
GRANT ALL ON agent_runs TO anon, authenticated, service_role;
GRANT ALL ON subscribers TO anon, authenticated, service_role;
GRANT ALL ON analytics TO anon, authenticated, service_role;
GRANT ALL ON errors TO anon, authenticated, service_role;
GRANT ALL ON email_sequences TO anon, authenticated, service_role;
GRANT ALL ON posting_schedule TO anon, authenticated, service_role;
GRANT ALL ON content_history TO anon, authenticated, service_role;
GRANT ALL ON daily_trending TO anon, authenticated, service_role;
GRANT ALL ON weekly_calendar TO anon, authenticated, service_role;
GRANT ALL ON generated_articles TO anon, authenticated, service_role;
GRANT ALL ON pinterest_pins TO anon, authenticated, service_role;

-- GRANT USAGE on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- ── Reload PostgREST schema cache ──
NOTIFY pgrst, 'reload schema';
