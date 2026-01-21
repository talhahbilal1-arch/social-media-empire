-- Social Media Empire Database Schema
-- Run this in Supabase SQL Editor to create all required tables

-- ==================== Videos Table ====================
CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    video_url TEXT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'created',
    platform_id VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_videos_brand ON videos(brand);
CREATE INDEX idx_videos_platform ON videos(platform);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at);

-- ==================== Content Bank Table ====================
CREATE TABLE IF NOT EXISTS content_bank (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    details JSONB DEFAULT '{}',
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_content_bank_brand ON content_bank(brand);
CREATE INDEX idx_content_bank_type ON content_bank(content_type);
CREATE INDEX idx_content_bank_used ON content_bank(used);

-- ==================== Subscribers Table ====================
CREATE TABLE IF NOT EXISTS subscribers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    brand VARCHAR(50) NOT NULL,
    source VARCHAR(50) DEFAULT 'website',
    lead_magnet VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscribers_brand ON subscribers(brand);
CREATE INDEX idx_subscribers_status ON subscribers(status);
CREATE INDEX idx_subscribers_email ON subscribers(email);

-- ==================== Analytics Table ====================
CREATE TABLE IF NOT EXISTS analytics (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    platform VARCHAR(50),
    data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analytics_event_type ON analytics(event_type);
CREATE INDEX idx_analytics_brand ON analytics(brand);
CREATE INDEX idx_analytics_created_at ON analytics(created_at);

-- ==================== Errors Table ====================
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

CREATE INDEX idx_errors_type ON errors(error_type);
CREATE INDEX idx_errors_resolved ON errors(resolved);
CREATE INDEX idx_errors_created_at ON errors(created_at);

-- ==================== Email Sequences Table ====================
CREATE TABLE IF NOT EXISTS email_sequences (
    id BIGSERIAL PRIMARY KEY,
    subscriber_id BIGINT REFERENCES subscribers(id),
    sequence_name VARCHAR(100) NOT NULL,
    email_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_sequences_subscriber ON email_sequences(subscriber_id);
CREATE INDEX idx_email_sequences_status ON email_sequences(status);

-- ==================== Posting Schedule Table ====================
CREATE TABLE IF NOT EXISTS posting_schedule (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    content_id BIGINT REFERENCES content_bank(id),
    video_id BIGINT REFERENCES videos(id),
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_posting_schedule_time ON posting_schedule(scheduled_time);
CREATE INDEX idx_posting_schedule_status ON posting_schedule(status);

-- ==================== Row Level Security ====================
-- Enable RLS on all tables
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_bank ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_schedule ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated access (service role)
CREATE POLICY "Service role full access" ON videos FOR ALL USING (true);
CREATE POLICY "Service role full access" ON content_bank FOR ALL USING (true);
CREATE POLICY "Service role full access" ON subscribers FOR ALL USING (true);
CREATE POLICY "Service role full access" ON analytics FOR ALL USING (true);
CREATE POLICY "Service role full access" ON errors FOR ALL USING (true);
CREATE POLICY "Service role full access" ON email_sequences FOR ALL USING (true);
CREATE POLICY "Service role full access" ON posting_schedule FOR ALL USING (true);

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
