-- Weekly calendar and article tracking tables.
-- Run this in Supabase SQL Editor AFTER content_history_schema.sql.

-- Weekly content calendars built from trend discovery
CREATE TABLE IF NOT EXISTS weekly_calendar (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    week_starting DATE NOT NULL,
    calendar_data JSONB NOT NULL,
    trends_data JSONB,
    performance_review JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weekly_calendar_brand ON weekly_calendar(brand);
CREATE INDEX IF NOT EXISTS idx_weekly_calendar_week ON weekly_calendar(week_starting DESC);

-- Generated articles for trending topics
CREATE TABLE IF NOT EXISTS generated_articles (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    slug TEXT NOT NULL,
    trending_topic TEXT,
    content_preview TEXT,
    word_count INTEGER,
    published_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_brand ON generated_articles(brand);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON generated_articles(slug);

-- Add trending topic tracking to content_history
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS trending_topic TEXT;
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS week_calendar_id BIGINT;
