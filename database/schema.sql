-- ============================================
-- SOCIAL MEDIA CONTENT EMPIRE - DATABASE SCHEMA
-- ============================================
-- Run this in your Supabase SQL Editor
-- This creates all tables needed for the autonomous content system
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CORE TABLES
-- ============================================

-- Brands table - supports multiple brands
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    niche TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    website_url TEXT,
    affiliate_tag TEXT,
    pinterest_board_ids JSONB DEFAULT '{}',
    youtube_channel_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert your two brands
INSERT INTO brands (name, display_name, niche, target_audience, website_url, affiliate_tag) VALUES
('daily_deal_darling', 'Daily Deal Darling', 'beauty, home, lifestyle, self-care', 'women 25-45 looking for deals and self-care products', 'https://dailydealdarling.com', 'dailydealdarling1-20'),
('menopause_planner', 'The Menopause Planner', 'menopause, perimenopause, wellness, planning', 'women in perimenopause/menopause seeking support and organization', 'https://themenopauseplanner.com', NULL)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- TREND DISCOVERY (Agent 7)
-- ============================================

CREATE TABLE IF NOT EXISTS trending_discoveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    discovery_type TEXT NOT NULL CHECK (discovery_type IN ('product', 'topic', 'hashtag', 'news', 'search_term', 'sound')),
    title TEXT NOT NULL,
    description TEXT,
    source TEXT NOT NULL CHECK (source IN ('amazon', 'google_trends', 'pinterest', 'tiktok', 'reddit', 'news', 'manual')),
    source_url TEXT,
    source_data JSONB DEFAULT '{}', -- Store extra data like ASIN, price, ratings
    relevance_score DECIMAL(3,2) DEFAULT 0.5 CHECK (relevance_score >= 0 AND relevance_score <= 1),
    used BOOLEAN DEFAULT false,
    used_at TIMESTAMP WITH TIME ZONE,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX idx_trending_brand ON trending_discoveries(brand_id);
CREATE INDEX idx_trending_unused ON trending_discoveries(used, expires_at) WHERE used = false;
CREATE INDEX idx_trending_source ON trending_discoveries(source);

-- ============================================
-- CONTENT BANK (Agent 1 - Content Brain)
-- ============================================

CREATE TABLE IF NOT EXISTS content_bank (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    trend_id UUID REFERENCES trending_discoveries(id) ON DELETE SET NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('pin', 'video', 'reel', 'short', 'blog_promo', 'carousel')),
    title TEXT NOT NULL,
    description TEXT,
    hashtags TEXT[],
    video_script TEXT,
    image_prompt TEXT,
    source_images TEXT[], -- URLs of images to use
    destination_link TEXT,
    cta_text TEXT,
    affiliate_products JSONB DEFAULT '[]', -- Array of {asin, name, price}
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'video_ready', 'scheduled', 'posted', 'retired', 'failed')),
    performance_score DECIMAL(5,2) DEFAULT 0,
    platform_formats JSONB DEFAULT '{}', -- Platform-specific versions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_content_brand ON content_bank(brand_id);
CREATE INDEX idx_content_status ON content_bank(status);
CREATE INDEX idx_content_type ON content_bank(content_type);
CREATE INDEX idx_content_created ON content_bank(created_at DESC);

-- ============================================
-- BLOG ARTICLES (Agent 8 - Blog Factory)
-- ============================================

CREATE TABLE IF NOT EXISTS blog_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    trend_id UUID REFERENCES trending_discoveries(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    meta_description TEXT,
    content_html TEXT,
    content_markdown TEXT,
    featured_image_url TEXT,
    featured_image_prompt TEXT, -- For AI image generation
    affiliate_products JSONB DEFAULT '[]', -- Array of ASINs with product info
    internal_links UUID[] DEFAULT '{}', -- Links to other blog post IDs
    seo_keywords TEXT[],
    word_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'generating', 'ready', 'publishing', 'published', 'archived', 'failed')),
    published_url TEXT,
    netlify_deploy_id TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(brand_id, slug)
);

CREATE INDEX idx_blog_brand ON blog_articles(brand_id);
CREATE INDEX idx_blog_status ON blog_articles(status);
CREATE INDEX idx_blog_published ON blog_articles(published_at DESC);

-- Junction table: Blog to Social Content
CREATE TABLE IF NOT EXISTS blog_to_social (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_article_id UUID REFERENCES blog_articles(id) ON DELETE CASCADE,
    content_id UUID REFERENCES content_bank(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- VIDEOS (Agent 2 - Video Factory)
-- ============================================

CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_bank(id) ON DELETE CASCADE,
    creatomate_render_id TEXT,
    video_url TEXT,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    width INTEGER DEFAULT 1080,
    height INTEGER DEFAULT 1920,
    platform_format TEXT DEFAULT '9:16',
    file_size_bytes BIGINT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'rendering', 'ready', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_videos_content ON videos(content_id);
CREATE INDEX idx_videos_status ON videos(status);

-- ============================================
-- POSTS LOG (Agent 3 - Multi-Platform Poster)
-- ============================================

CREATE TABLE IF NOT EXISTS posts_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content_bank(id) ON DELETE CASCADE,
    blog_article_id UUID REFERENCES blog_articles(id) ON DELETE SET NULL,
    platform TEXT NOT NULL CHECK (platform IN ('pinterest', 'tiktok', 'instagram', 'youtube', 'twitter', 'facebook')),
    platform_post_id TEXT,
    platform_url TEXT,
    post_type TEXT, -- pin, video, reel, short, tweet
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'posted', 'failed', 'deleted')),
    error_message TEXT,
    scheduled_for TIMESTAMP WITH TIME ZONE,
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_posts_content ON posts_log(content_id);
CREATE INDEX idx_posts_platform ON posts_log(platform);
CREATE INDEX idx_posts_status ON posts_log(status);
CREATE INDEX idx_posts_posted ON posts_log(posted_at DESC);

-- ============================================
-- ANALYTICS (Agent 4 - Analytics Collector)
-- ============================================

CREATE TABLE IF NOT EXISTS analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES posts_log(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4) DEFAULT 0,
    reach INTEGER DEFAULT 0,
    video_watch_time_seconds INTEGER DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analytics_post ON analytics(post_id);
CREATE INDEX idx_analytics_platform ON analytics(platform);
CREATE INDEX idx_analytics_recorded ON analytics(recorded_at DESC);

-- Daily aggregated analytics for faster queries
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    date DATE NOT NULL,
    total_posts INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    avg_engagement_rate DECIMAL(5,4) DEFAULT 0,
    top_performing_content_id UUID REFERENCES content_bank(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(brand_id, platform, date)
);

-- ============================================
-- WINNING PATTERNS (Agent 5 - Self-Improvement)
-- ============================================

CREATE TABLE IF NOT EXISTS winning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    pattern_type TEXT NOT NULL CHECK (pattern_type IN ('topic', 'hashtag', 'posting_time', 'format', 'cta', 'hook', 'product_category', 'title_style')),
    pattern_value TEXT NOT NULL,
    platform TEXT, -- NULL means all platforms
    avg_engagement DECIMAL(10,4) DEFAULT 0,
    avg_views INTEGER DEFAULT 0,
    avg_clicks INTEGER DEFAULT 0,
    sample_size INTEGER DEFAULT 0,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    is_active BOOLEAN DEFAULT true,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(brand_id, pattern_type, pattern_value, platform)
);

CREATE INDEX idx_patterns_brand ON winning_patterns(brand_id);
CREATE INDEX idx_patterns_type ON winning_patterns(pattern_type);
CREATE INDEX idx_patterns_active ON winning_patterns(is_active) WHERE is_active = true;

-- ============================================
-- SYSTEM CONFIGURATION
-- ============================================

CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    config_key TEXT NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by TEXT DEFAULT 'manual',
    UNIQUE(brand_id, config_key)
);

-- Insert default configurations
INSERT INTO system_config (brand_id, config_key, config_value, description)
SELECT
    b.id,
    'posting_schedule',
    '{"pinterest": {"times": ["09:00", "13:00", "21:00"], "max_per_day": 3}, "youtube": {"times": ["12:00"], "max_per_day": 1}}'::jsonb,
    'Posting schedule per platform'
FROM brands b
ON CONFLICT (brand_id, config_key) DO NOTHING;

INSERT INTO system_config (brand_id, config_key, config_value, description)
SELECT
    b.id,
    'content_generation',
    '{"daily_pieces": 10, "video_ratio": 0.3, "blog_articles_per_week": 3}'::jsonb,
    'Content generation settings'
FROM brands b
ON CONFLICT (brand_id, config_key) DO NOTHING;

-- ============================================
-- SYSTEM CHANGES LOG (Audit Trail)
-- ============================================

CREATE TABLE IF NOT EXISTS system_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    brand_id UUID REFERENCES brands(id) ON DELETE SET NULL,
    change_type TEXT NOT NULL,
    config_key TEXT,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_changes_agent ON system_changes(agent_name);
CREATE INDEX idx_changes_created ON system_changes(created_at DESC);

-- ============================================
-- HEALTH CHECKS (Agent 6)
-- ============================================

CREATE TABLE IF NOT EXISTS health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    check_type TEXT DEFAULT 'scheduled_run',
    status TEXT NOT NULL CHECK (status IN ('success', 'failure', 'warning', 'skipped')),
    duration_ms INTEGER,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_health_agent ON health_checks(agent_name);
CREATE INDEX idx_health_status ON health_checks(status);
CREATE INDEX idx_health_checked ON health_checks(checked_at DESC);

-- Keep only last 30 days of health checks (cleanup function)
CREATE OR REPLACE FUNCTION cleanup_old_health_checks()
RETURNS void AS $$
BEGIN
    DELETE FROM health_checks WHERE checked_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PLATFORM CREDENTIALS (Encrypted storage)
-- ============================================

CREATE TABLE IF NOT EXISTS platform_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    credential_type TEXT NOT NULL, -- oauth_token, refresh_token, api_key
    encrypted_value TEXT NOT NULL, -- Store encrypted, decrypt in application
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(brand_id, platform, credential_type)
);

-- ============================================
-- VIDEO TEMPLATES (Creatomate)
-- ============================================

CREATE TABLE IF NOT EXISTS video_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    template_name TEXT NOT NULL,
    creatomate_template_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    description TEXT,
    variables JSONB DEFAULT '{}', -- Template variables schema
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- AGENT RUNS LOG (For debugging)
-- ============================================

CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    run_id TEXT, -- GitHub Actions run ID
    status TEXT NOT NULL CHECK (status IN ('started', 'running', 'completed', 'failed')),
    items_processed INTEGER DEFAULT 0,
    items_created INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    error_log TEXT[],
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER
);

CREATE INDEX idx_agent_runs_name ON agent_runs(agent_name);
CREATE INDEX idx_agent_runs_started ON agent_runs(started_at DESC);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get unused trends for a brand
CREATE OR REPLACE FUNCTION get_fresh_trends(p_brand_id UUID, p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    id UUID,
    discovery_type TEXT,
    title TEXT,
    description TEXT,
    source TEXT,
    source_data JSONB,
    relevance_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        td.id,
        td.discovery_type,
        td.title,
        td.description,
        td.source,
        td.source_data,
        td.relevance_score
    FROM trending_discoveries td
    WHERE td.brand_id = p_brand_id
        AND td.used = false
        AND td.expires_at > NOW()
    ORDER BY td.relevance_score DESC, td.discovered_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get pending content for posting
CREATE OR REPLACE FUNCTION get_ready_content(p_brand_id UUID, p_platform TEXT, p_limit INTEGER DEFAULT 5)
RETURNS TABLE (
    id UUID,
    content_type TEXT,
    title TEXT,
    description TEXT,
    hashtags TEXT[],
    destination_link TEXT,
    video_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cb.id,
        cb.content_type,
        cb.title,
        cb.description,
        cb.hashtags,
        cb.destination_link,
        v.video_url
    FROM content_bank cb
    LEFT JOIN videos v ON v.content_id = cb.id AND v.status = 'ready'
    WHERE cb.brand_id = p_brand_id
        AND cb.status IN ('pending', 'video_ready')
        AND NOT EXISTS (
            SELECT 1 FROM posts_log pl
            WHERE pl.content_id = cb.id
            AND pl.platform = p_platform
            AND pl.status = 'posted'
        )
    ORDER BY cb.performance_score DESC, cb.created_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate engagement rate
CREATE OR REPLACE FUNCTION calculate_engagement_rate(
    p_views INTEGER,
    p_likes INTEGER,
    p_comments INTEGER,
    p_shares INTEGER,
    p_saves INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    IF p_views = 0 THEN
        RETURN 0;
    END IF;
    RETURN ROUND(
        ((p_likes + p_comments * 2 + p_shares * 3 + p_saves * 2)::DECIMAL / p_views) * 100,
        4
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (Optional but recommended)
-- ============================================

-- Enable RLS on sensitive tables
ALTER TABLE platform_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_brands_updated_at
    BEFORE UPDATE ON brands
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_bank_updated_at
    BEFORE UPDATE ON content_bank
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_articles_updated_at
    BEFORE UPDATE ON blog_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at
    BEFORE UPDATE ON system_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE brands IS 'Stores brand configurations for multi-brand support';
COMMENT ON TABLE trending_discoveries IS 'Agent 7: Stores trending topics, products, and ideas discovered daily';
COMMENT ON TABLE content_bank IS 'Agent 1: Main content storage generated by Content Brain';
COMMENT ON TABLE blog_articles IS 'Agent 8: Full blog articles for SEO and affiliate marketing';
COMMENT ON TABLE videos IS 'Agent 2: Video renders from Creatomate';
COMMENT ON TABLE posts_log IS 'Agent 3: Tracks all social media posts';
COMMENT ON TABLE analytics IS 'Agent 4: Engagement metrics per post';
COMMENT ON TABLE winning_patterns IS 'Agent 5: Patterns that drive engagement, updated by Self-Improvement';
COMMENT ON TABLE health_checks IS 'Agent 6: System health monitoring logs';
COMMENT ON TABLE system_changes IS 'Audit trail for all automated system changes';

-- ============================================
-- DONE! Your database schema is ready.
-- ============================================
