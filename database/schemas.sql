-- ============================================================
-- Social Media Empire - Consolidated Database Schema
-- Single source of truth for all tables.
-- Run in Supabase SQL Editor. Safe to re-run (uses IF NOT EXISTS).
-- ============================================================

-- ==================== Videos Table ====================
-- Used by: database/supabase_client.py, core/supabase_client.py
CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    platform VARCHAR(50),
    video_url TEXT,
    title TEXT,
    description TEXT,
    script TEXT,
    status VARCHAR(20) DEFAULT 'created',
    platform_id VARCHAR(100),
    template_id VARCHAR(100),
    render_job_id VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_brand ON videos(brand);
CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);

-- ==================== Content Bank Table ====================
-- Used by: database/supabase_client.py, core/supabase_client.py
-- Note: both 'brand' and 'brand_id' are used by different code paths.
-- brand_id mirrors brand for compatibility with core/supabase_client.py.
CREATE TABLE IF NOT EXISTS content_bank (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    brand_id VARCHAR(100),
    content_type VARCHAR(50) NOT NULL,
    topic VARCHAR(255),
    title TEXT,
    description TEXT,
    details JSONB DEFAULT '{}',
    hashtags TEXT[],
    video_script TEXT,
    image_prompt TEXT,
    source_images TEXT[],
    destination_link TEXT,
    cta_text TEXT,
    affiliate_products JSONB DEFAULT '[]',
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    performance_score DECIMAL(5,2) DEFAULT 0,
    platform_formats JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    trend_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_bank_brand ON content_bank(brand);
CREATE INDEX IF NOT EXISTS idx_content_bank_brand_id ON content_bank(brand_id);
CREATE INDEX IF NOT EXISTS idx_content_bank_type ON content_bank(content_type);
CREATE INDEX IF NOT EXISTS idx_content_bank_used ON content_bank(used);
CREATE INDEX IF NOT EXISTS idx_content_bank_status ON content_bank(status);
CREATE INDEX IF NOT EXISTS idx_content_bank_created ON content_bank(created_at DESC);

-- ==================== Agent Runs Table ====================
-- Used by: database/supabase_client.py, core/supabase_client.py, many agent modules
-- Tracks when each system component last ran (used by monitoring)
CREATE TABLE IF NOT EXISTS agent_runs (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    last_run_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'never_run',
    error_message TEXT,
    last_error TEXT,
    run_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    run_id TEXT,
    items_processed INTEGER DEFAULT 0,
    items_created INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_log TEXT[],
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_name ON agent_runs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_runs_started ON agent_runs(started_at DESC);

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

-- ==================== Subscribers Table ====================
-- Used by: database/supabase_client.py
CREATE TABLE IF NOT EXISTS subscribers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    brand VARCHAR(100) NOT NULL,
    source VARCHAR(100) DEFAULT 'website',
    lead_magnet VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscribers_brand ON subscribers(brand);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);

-- ==================== Analytics Table ====================
-- Used by: database/supabase_client.py, core/supabase_client.py, revenue_activation.py
CREATE TABLE IF NOT EXISTS analytics (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    brand VARCHAR(100),
    platform VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    data JSONB DEFAULT '{}',
    post_id BIGINT,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_brand ON analytics(brand);
CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_post ON analytics(post_id);
CREATE INDEX IF NOT EXISTS idx_analytics_recorded ON analytics(recorded_at DESC);

-- ==================== Errors Table ====================
-- Used by: database/supabase_client.py, scripts/render_video_pins.py, revenue_activation.py
CREATE TABLE IF NOT EXISTS errors (
    id BIGSERIAL PRIMARY KEY,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type);
CREATE INDEX IF NOT EXISTS idx_errors_resolved ON errors(resolved);
CREATE INDEX IF NOT EXISTS idx_errors_created_at ON errors(created_at);

-- ==================== Email Sequences Table ====================
-- Used by: email marketing system
CREATE TABLE IF NOT EXISTS email_sequences (
    id BIGSERIAL PRIMARY KEY,
    subscriber_id BIGINT REFERENCES subscribers(id),
    brand VARCHAR(100),
    sequence_name VARCHAR(100) NOT NULL,
    email_number INTEGER,
    step_number INTEGER,
    subject TEXT,
    body TEXT,
    delay_days INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_sequences_subscriber ON email_sequences(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_email_sequences_status ON email_sequences(status);

-- ==================== Posting Schedule Table ====================
CREATE TABLE IF NOT EXISTS posting_schedule (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMPTZ,
    scheduled_at TIMESTAMPTZ,
    content_id BIGINT REFERENCES content_bank(id),
    video_id BIGINT REFERENCES videos(id),
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posting_schedule_time ON posting_schedule(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_posting_schedule_status ON posting_schedule(status);

-- ==================== Content History Table ====================
-- Used by: content_brain.py, image_selector.py, trend_discovery.py, revenue_intelligence.py
-- Tracks pin uniqueness across brands
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
    pin_url TEXT,
    posting_method VARCHAR(100),
    trending_topic TEXT,
    week_calendar_id BIGINT,
    status VARCHAR(20) DEFAULT 'posted',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_history_brand ON content_history(brand);
CREATE INDEX IF NOT EXISTS idx_content_history_created ON content_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_history_brand_created ON content_history(brand, created_at DESC);

-- ==================== Daily Trending Table ====================
-- Used by: daily_trend_scout.py, content_brain.py
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

CREATE INDEX IF NOT EXISTS idx_daily_trending_brand ON daily_trending(brand);
CREATE INDEX IF NOT EXISTS idx_daily_trending_date ON daily_trending(trend_date DESC);

-- ==================== Weekly Calendar Table ====================
-- Used by: content_brain.py, trend_discovery.py, revenue_intelligence.py
CREATE TABLE IF NOT EXISTS weekly_calendar (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    week_starting DATE NOT NULL,
    week_start DATE,
    calendar_data JSONB NOT NULL DEFAULT '{}',
    trends_data JSONB,
    performance_review JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weekly_calendar_brand ON weekly_calendar(brand);
CREATE INDEX IF NOT EXISTS idx_weekly_calendar_week ON weekly_calendar(week_starting DESC);

-- ==================== Generated Articles Table ====================
-- Used by: seo_content_machine.py, pin_article_generator.py, article_generator.py, revenue_intelligence.py
CREATE TABLE IF NOT EXISTS generated_articles (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    slug TEXT NOT NULL,
    title TEXT,
    topic TEXT,
    trending_topic TEXT,
    content_preview TEXT,
    article_url TEXT,
    published_url TEXT,
    word_count INTEGER,
    has_affiliate_links BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, slug)
);

CREATE INDEX IF NOT EXISTS idx_articles_brand ON generated_articles(brand);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON generated_articles(slug);

-- ==================== Pinterest Pins Table ====================
-- Used by: scripts/render_video_pins.py, Make.com pipeline
CREATE TABLE IF NOT EXISTS pinterest_pins (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100),
    title TEXT,
    description TEXT,
    image_url TEXT,
    generated_image_url TEXT,
    background_image_url TEXT,
    board_id TEXT,
    destination_url TEXT,
    topic TEXT,
    category TEXT,
    niche TEXT,
    visual_style TEXT,
    account TEXT,
    overlay_headline TEXT,
    overlay_subtext TEXT,
    pexels_search_term TEXT,
    hashtags TEXT,
    content_json JSONB,
    tips JSONB,
    pinterest_pin_id TEXT,
    pin_id TEXT,
    pin_type TEXT DEFAULT 'image',
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    article_generated BOOLEAN DEFAULT FALSE,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pinterest_pins_brand ON pinterest_pins(brand);
CREATE INDEX IF NOT EXISTS idx_pinterest_pins_status ON pinterest_pins(status);
CREATE INDEX IF NOT EXISTS idx_pins_brand_status ON pinterest_pins(brand, status);
CREATE INDEX IF NOT EXISTS idx_pins_created_desc ON pinterest_pins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pins_retry ON pinterest_pins(status, retry_count);

-- ==================== Pinterest Analytics Table ====================
-- Used by: video_automation/pinterest_analytics.py, monitoring/daily_report_generator.py
CREATE TABLE IF NOT EXISTS pinterest_analytics (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    board_name TEXT,
    board_id TEXT,
    period_start DATE,
    period_end DATE,
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    impressions INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    pin_clicks INTEGER DEFAULT 0,
    raw_data JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_pinterest_analytics_brand ON pinterest_analytics(brand);
CREATE INDEX IF NOT EXISTS idx_pinterest_analytics_collected ON pinterest_analytics(collected_at DESC);

-- ==================== Posts Log Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS posts_log (
    id BIGSERIAL PRIMARY KEY,
    content_id BIGINT,
    blog_article_id BIGINT,
    platform VARCHAR(50) NOT NULL,
    platform_post_id TEXT,
    platform_url TEXT,
    post_type TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    scheduled_for TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_content ON posts_log(content_id);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts_log(platform);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts_log(status);
CREATE INDEX IF NOT EXISTS idx_posts_posted ON posts_log(posted_at DESC);

-- ==================== Health Checks Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS health_checks (
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    check_type TEXT DEFAULT 'scheduled_run',
    status TEXT NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    consecutive_failures INTEGER DEFAULT 0,
    last_notified_at TIMESTAMPTZ,
    auto_heal_attempted BOOLEAN DEFAULT false,
    auto_heal_success BOOLEAN DEFAULT false,
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_agent ON health_checks(agent_name);
CREATE INDEX IF NOT EXISTS idx_health_status ON health_checks(status);
CREATE INDEX IF NOT EXISTS idx_health_checked ON health_checks(checked_at DESC);

-- ==================== Winning Patterns Table ====================
-- Used by: core/supabase_client.py (Agent 5 - Self-Improvement)
CREATE TABLE IF NOT EXISTS winning_patterns (
    id BIGSERIAL PRIMARY KEY,
    brand_id VARCHAR(100),
    pattern_type TEXT NOT NULL,
    pattern_value TEXT NOT NULL,
    platform TEXT,
    avg_engagement DECIMAL(10,4) DEFAULT 0,
    avg_views INTEGER DEFAULT 0,
    avg_clicks INTEGER DEFAULT 0,
    sample_size INTEGER DEFAULT 0,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    is_active BOOLEAN DEFAULT true,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand_id, pattern_type, pattern_value, platform)
);

CREATE INDEX IF NOT EXISTS idx_patterns_brand ON winning_patterns(brand_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON winning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_active ON winning_patterns(is_active);

-- ==================== System Config Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS system_config (
    id BIGSERIAL PRIMARY KEY,
    brand_id VARCHAR(100),
    config_key TEXT NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'manual',
    UNIQUE(brand_id, config_key)
);

-- ==================== System Changes Log Table ====================
-- Used by: core/supabase_client.py (audit trail)
CREATE TABLE IF NOT EXISTS system_changes (
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    brand_id VARCHAR(100),
    change_type TEXT NOT NULL,
    config_key TEXT,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_changes_agent ON system_changes(agent_name);
CREATE INDEX IF NOT EXISTS idx_changes_created ON system_changes(created_at DESC);

-- ==================== Blog Articles Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS blog_articles (
    id BIGSERIAL PRIMARY KEY,
    brand_id VARCHAR(100),
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    meta_description TEXT,
    content_html TEXT,
    content_markdown TEXT,
    featured_image_url TEXT,
    featured_image_prompt TEXT,
    affiliate_products JSONB DEFAULT '[]',
    seo_keywords TEXT[],
    word_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft',
    published_url TEXT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blog_brand ON blog_articles(brand_id);
CREATE INDEX IF NOT EXISTS idx_blog_status ON blog_articles(status);
CREATE INDEX IF NOT EXISTS idx_blog_published ON blog_articles(published_at DESC);

-- ==================== Blog to Social Junction Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS blog_to_social (
    id BIGSERIAL PRIMARY KEY,
    blog_article_id BIGINT REFERENCES blog_articles(id) ON DELETE CASCADE,
    content_id BIGINT REFERENCES content_bank(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== Brands Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS brands (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    niche TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    website_url TEXT,
    affiliate_tag TEXT,
    pinterest_board_ids JSONB DEFAULT '{}',
    youtube_channel_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed brands
INSERT INTO brands (name, display_name, niche, target_audience) VALUES
    ('daily_deal_darling', 'Daily Deal Darling', 'beauty, home, lifestyle, self-care', 'women 25-45 looking for deals'),
    ('menopause_planner', 'The Menopause Planner', 'menopause, perimenopause, wellness', 'women in perimenopause/menopause'),
    ('fitness', 'Fit Over 35', 'mens fitness over 35', 'men over 35 seeking fitness'),
    ('deals', 'Daily Deal Darling', 'budget home and lifestyle', 'budget-conscious shoppers'),
    ('menopause', 'Menopause Planner', 'menopause wellness', 'women experiencing menopause')
ON CONFLICT (name) DO NOTHING;

-- ==================== Trending Discoveries Table ====================
-- Used by: core/supabase_client.py
CREATE TABLE IF NOT EXISTS trending_discoveries (
    id BIGSERIAL PRIMARY KEY,
    brand_id VARCHAR(100),
    discovery_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    source TEXT NOT NULL,
    source_url TEXT,
    source_data JSONB DEFAULT '{}',
    relevance_score DECIMAL(3,2) DEFAULT 0.5,
    used BOOLEAN DEFAULT false,
    used_at TIMESTAMPTZ,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX IF NOT EXISTS idx_trending_brand ON trending_discoveries(brand_id);
CREATE INDEX IF NOT EXISTS idx_trending_unused ON trending_discoveries(used, expires_at);
CREATE INDEX IF NOT EXISTS idx_trending_source ON trending_discoveries(source);

-- ==================== Affiliate Programs Table ====================
-- Used by: revenue_activation.py, revenue_intelligence.py
CREATE TABLE IF NOT EXISTS affiliate_programs (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    program_name VARCHAR(200) NOT NULL,
    network VARCHAR(100),
    signup_url TEXT,
    affiliate_url TEXT,
    commission_rate VARCHAR(50),
    status VARCHAR(20) DEFAULT 'placeholder',
    applied_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, program_name)
);

CREATE INDEX IF NOT EXISTS idx_affiliate_brand ON affiliate_programs(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_status ON affiliate_programs(status);

-- Seed affiliate_programs with known programs (idempotent)
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

-- ==================== Content Performance Table ====================
-- Used by: revenue_intelligence.py
CREATE TABLE IF NOT EXISTS content_performance (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    content_type VARCHAR(20) DEFAULT 'article',
    content_id BIGINT,
    slug TEXT,
    title TEXT,
    ga4_sessions INTEGER DEFAULT 0,
    gsc_clicks INTEGER DEFAULT 0,
    gsc_impressions INTEGER DEFAULT 0,
    gsc_position NUMERIC(5,2),
    affiliate_clicks INTEGER DEFAULT 0,
    revenue_score NUMERIC(8,4) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    data JSONB DEFAULT '{}',
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_perf_brand ON content_performance(brand);
CREATE INDEX IF NOT EXISTS idx_content_perf_score ON content_performance(revenue_score DESC);

-- ==================== Deals Table ====================
-- Used by: automation/deals/fetch_deals.py
CREATE TABLE IF NOT EXISTS deals (
    id BIGSERIAL PRIMARY KEY,
    asin TEXT NOT NULL UNIQUE,
    title TEXT,
    deal_price NUMERIC,
    original_price NUMERIC,
    discount_percentage NUMERIC,
    deal_type VARCHAR(50),
    image_url TEXT,
    end_time TIMESTAMPTZ,
    affiliate_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deals_asin ON deals(asin);
CREATE INDEX IF NOT EXISTS idx_deals_type ON deals(deal_type);

-- ==================== Affiliate Revenue Table ====================
-- Used by: revenue tracking
CREATE TABLE IF NOT EXISTS affiliate_revenue (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    program_name VARCHAR(200),
    affiliate_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    date_recorded DATE DEFAULT CURRENT_DATE,
    source VARCHAR(50) DEFAULT 'amazon',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_brand ON affiliate_revenue(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_date ON affiliate_revenue(date_recorded);

-- ==================== Email Conversions Table ====================
-- Used by: revenue tracking
CREATE TABLE IF NOT EXISTS email_conversions (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    sequence_name VARCHAR(200),
    email_number INTEGER,
    subscriber_tag VARCHAR(200),
    affiliate_url TEXT,
    product_name TEXT,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== Newsletter Sends Table ====================
-- Used by: email_marketing/menopause_newsletter.py
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    article_filename VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    broadcast_id VARCHAR(100),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, article_filename)
);

-- ==================== Analytics Events Table ====================
-- Used by: email_marketing/email_automation.py
CREATE TABLE IF NOT EXISTS analytics_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_brand ON analytics_events(brand);

-- ==================== Row Level Security ====================
-- Enable RLS on all tables (service_role bypasses RLS via BYPASSRLS=true)
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_bank ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_trending ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE pinterest_pins ENABLE ROW LEVEL SECURITY;
ALTER TABLE pinterest_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE winning_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_to_social ENABLE ROW LEVEL SECURITY;
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE trending_discoveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_revenue ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_sends ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- ==================== GRANT ALL ====================
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
GRANT ALL ON pinterest_analytics TO anon, authenticated, service_role;
GRANT ALL ON posts_log TO anon, authenticated, service_role;
GRANT ALL ON health_checks TO anon, authenticated, service_role;
GRANT ALL ON winning_patterns TO anon, authenticated, service_role;
GRANT ALL ON system_config TO anon, authenticated, service_role;
GRANT ALL ON system_changes TO anon, authenticated, service_role;
GRANT ALL ON blog_articles TO anon, authenticated, service_role;
GRANT ALL ON blog_to_social TO anon, authenticated, service_role;
GRANT ALL ON brands TO anon, authenticated, service_role;
GRANT ALL ON trending_discoveries TO anon, authenticated, service_role;
GRANT ALL ON affiliate_programs TO anon, authenticated, service_role;
GRANT ALL ON content_performance TO anon, authenticated, service_role;
GRANT ALL ON deals TO anon, authenticated, service_role;
GRANT ALL ON affiliate_revenue TO anon, authenticated, service_role;
GRANT ALL ON email_conversions TO anon, authenticated, service_role;
GRANT ALL ON newsletter_sends TO anon, authenticated, service_role;
GRANT ALL ON analytics_events TO anon, authenticated, service_role;

-- GRANT USAGE on all sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- ==================== Helper Functions ====================

-- Function to get daily video count by brand
CREATE OR REPLACE FUNCTION get_daily_video_stats(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (brand VARCHAR, platform VARCHAR, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT v.brand, v.platform, COUNT(*)::BIGINT
    FROM videos v
    WHERE v.created_at::DATE = target_date
    GROUP BY v.brand, v.platform;
END;
$$ LANGUAGE plpgsql;

-- Function to get subscriber growth
CREATE OR REPLACE FUNCTION get_subscriber_growth(days INTEGER DEFAULT 30)
RETURNS TABLE (date DATE, brand VARCHAR, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT s.created_at::DATE, s.brand, COUNT(*)::BIGINT
    FROM subscribers s
    WHERE s.created_at >= CURRENT_DATE - days
    GROUP BY s.created_at::DATE, s.brand
    ORDER BY s.created_at::DATE;
END;
$$ LANGUAGE plpgsql;

-- Upsert function for agent runs (used by fix_schema_issues migration)
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

-- Cleanup old health checks (keep last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_health_checks()
RETURNS void AS $$
BEGIN
    DELETE FROM health_checks WHERE checked_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ==================== Triggers ====================

-- updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables that have updated_at columns
DO $$
BEGIN
    -- Drop existing triggers to avoid errors on re-run, then recreate
    DROP TRIGGER IF EXISTS update_brands_updated_at ON brands;
    CREATE TRIGGER update_brands_updated_at
        BEFORE UPDATE ON brands FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    DROP TRIGGER IF EXISTS update_content_bank_updated_at ON content_bank;
    CREATE TRIGGER update_content_bank_updated_at
        BEFORE UPDATE ON content_bank FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    DROP TRIGGER IF EXISTS update_blog_articles_updated_at ON blog_articles;
    CREATE TRIGGER update_blog_articles_updated_at
        BEFORE UPDATE ON blog_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

    DROP TRIGGER IF EXISTS update_system_config_updated_at ON system_config;
    CREATE TRIGGER update_system_config_updated_at
        BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
END;
$$;

-- ==================== Reload PostgREST Schema Cache ====================
NOTIFY pgrst, 'reload schema';
