-- Content history table for tracking pin uniqueness across brands.
-- Run this in Supabase SQL Editor.

CREATE TABLE IF NOT EXISTS content_history (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    title TEXT,
    description TEXT,
    topic TEXT,
    category TEXT,
    angle_framework TEXT,
    visual_style TEXT,
    board TEXT,
    description_opener TEXT,
    image_query TEXT,
    pexels_image_id TEXT,
    destination_url TEXT,
    pin_url TEXT,
    posting_method TEXT,  -- 'late_api', 'make_s1', 'make_s2'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_history_brand ON content_history(brand);
CREATE INDEX IF NOT EXISTS idx_content_history_created ON content_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_history_brand_created ON content_history(brand, created_at DESC);
