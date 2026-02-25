-- 002_revenue_tracking.sql
-- Revenue tracking tables for autonomous revenue engine
-- Run in Supabase SQL Editor after 001_master_schema.sql
-- Then restart Supabase project (Settings > General) — takes 5-8 min

-- Tracks daily affiliate earnings per brand/program
CREATE TABLE IF NOT EXISTS affiliate_revenue (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    program_name VARCHAR(200),
    affiliate_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    date_recorded DATE DEFAULT CURRENT_DATE,
    source VARCHAR(50) DEFAULT 'amazon',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks email → click → purchase attribution
CREATE TABLE IF NOT EXISTS email_conversions (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    sequence_name VARCHAR(200),
    email_number INTEGER,
    subscriber_tag VARCHAR(200),
    affiliate_url TEXT,
    product_name TEXT,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks article/pin performance → revenue scores
-- Updated by revenue_intelligence.py daily
CREATE TABLE IF NOT EXISTS content_performance (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    content_type VARCHAR(20) DEFAULT 'article',
    slug TEXT,
    title TEXT,
    ga4_sessions INTEGER DEFAULT 0,
    gsc_clicks INTEGER DEFAULT 0,
    gsc_impressions INTEGER DEFAULT 0,
    gsc_position NUMERIC(5,2),
    affiliate_clicks INTEGER DEFAULT 0,
    revenue_score NUMERIC(8,4) DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Catalog of all affiliate programs (active + discovered + placeholder)
-- Seeded with known programs; revenue_activation.py discovers new ones
CREATE TABLE IF NOT EXISTS affiliate_programs (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    program_name VARCHAR(200) NOT NULL,
    network VARCHAR(100),
    signup_url TEXT,
    affiliate_url TEXT,
    commission_rate VARCHAR(50),
    status VARCHAR(20) DEFAULT 'placeholder',  -- placeholder | discovered | applied | active
    applied_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, program_name)
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_brand ON affiliate_revenue(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_date ON affiliate_revenue(date_recorded);
CREATE INDEX IF NOT EXISTS idx_content_performance_brand ON content_performance(brand);
CREATE INDEX IF NOT EXISTS idx_content_performance_score ON content_performance(revenue_score DESC);
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_brand ON affiliate_programs(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_status ON affiliate_programs(status);

-- Permissions (required for Supabase free tier)
GRANT ALL ON affiliate_revenue TO anon, authenticated, service_role;
GRANT ALL ON email_conversions TO anon, authenticated, service_role;
GRANT ALL ON content_performance TO anon, authenticated, service_role;
GRANT ALL ON affiliate_programs TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE affiliate_revenue_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE email_conversions_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE content_performance_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE affiliate_programs_id_seq TO anon, authenticated, service_role;

ALTER TABLE affiliate_revenue DISABLE ROW LEVEL SECURITY;
ALTER TABLE email_conversions DISABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance DISABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_programs DISABLE ROW LEVEL SECURITY;

-- Seed affiliate_programs with all known programs from affiliate_config.json
INSERT INTO affiliate_programs (brand, program_name, network, signup_url, commission_rate, status) VALUES
('fitness', 'ClickBank fitness programs', 'ClickBank', 'https://www.clickbank.com/affiliate/', '30-75%', 'placeholder'),
('fitness', 'ShareASale supplement brands', 'ShareASale', 'https://www.shareasale.com/', '15-25%', 'placeholder'),
('fitness', 'Bodybuilding.com', 'Direct', 'https://www.bodybuilding.com/affiliate', '5-15%', 'placeholder'),
('fitness', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active'),
('deals', 'ShareASale home/lifestyle', 'ShareASale', 'https://www.shareasale.com/', '10-30%', 'placeholder'),
('deals', 'Impact.com brands', 'Impact', 'https://impact.com/', '5-20%', 'placeholder'),
('deals', 'Rakuten retailers', 'Rakuten', 'https://rakutenadvertising.com/', '5-15%', 'placeholder'),
('deals', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active'),
('menopause', 'ShareASale supplement brands', 'ShareASale', 'https://www.shareasale.com/', '15-30%', 'placeholder'),
('menopause', 'ClickBank health programs', 'ClickBank', 'https://www.clickbank.com/affiliate/', '30-75%', 'placeholder'),
('menopause', 'Etsy planner (own product)', 'Etsy', 'https://www.etsy.com/listing/4435219468/', '100% minus fees', 'active'),
('menopause', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active')
ON CONFLICT (brand, program_name) DO NOTHING;
