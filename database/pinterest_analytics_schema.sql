-- Pinterest Analytics Table Schema
-- Run this in Supabase SQL Editor to create the pinterest_analytics table
-- Stores board-level analytics collected from Pinterest API v5

CREATE TABLE IF NOT EXISTS pinterest_analytics (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    board_name VARCHAR(255) NOT NULL,
    board_id VARCHAR(100) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    impressions BIGINT DEFAULT 0,
    saves BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    pin_clicks BIGINT DEFAULT 0,
    raw_data JSONB DEFAULT '{}',
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_pinterest_analytics_brand ON pinterest_analytics(brand);
CREATE INDEX idx_pinterest_analytics_board_id ON pinterest_analytics(board_id);
CREATE INDEX idx_pinterest_analytics_collected_at ON pinterest_analytics(collected_at);
CREATE INDEX idx_pinterest_analytics_period ON pinterest_analytics(period_start, period_end);

-- Row Level Security
ALTER TABLE pinterest_analytics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access" ON pinterest_analytics FOR ALL USING (true);

-- Helper function to get latest analytics for a board
CREATE OR REPLACE FUNCTION get_latest_board_analytics(p_brand VARCHAR DEFAULT NULL)
RETURNS TABLE (
    brand VARCHAR,
    board_name VARCHAR,
    board_id VARCHAR,
    period_start DATE,
    period_end DATE,
    impressions BIGINT,
    saves BIGINT,
    clicks BIGINT,
    pin_clicks BIGINT,
    collected_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (pa.board_id)
        pa.brand,
        pa.board_name,
        pa.board_id,
        pa.period_start,
        pa.period_end,
        pa.impressions,
        pa.saves,
        pa.clicks,
        pa.pin_clicks,
        pa.collected_at
    FROM pinterest_analytics pa
    WHERE (p_brand IS NULL OR pa.brand = p_brand)
    ORDER BY pa.board_id, pa.collected_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Helper function to get analytics trend (weekly/monthly aggregates)
CREATE OR REPLACE FUNCTION get_analytics_trend(p_brand VARCHAR, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    date DATE,
    total_impressions BIGINT,
    total_saves BIGINT,
    total_clicks BIGINT,
    total_pin_clicks BIGINT,
    board_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pa.collected_at::DATE,
        SUM(pa.impressions)::BIGINT,
        SUM(pa.saves)::BIGINT,
        SUM(pa.clicks)::BIGINT,
        SUM(pa.pin_clicks)::BIGINT,
        COUNT(DISTINCT pa.board_id)::INTEGER
    FROM pinterest_analytics pa
    WHERE pa.brand = p_brand
        AND pa.collected_at >= CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL
    GROUP BY pa.collected_at::DATE
    ORDER BY pa.collected_at::DATE DESC;
END;
$$ LANGUAGE plpgsql;
