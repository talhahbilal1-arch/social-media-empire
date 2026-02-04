-- YouTube Shorts Automation - Supabase Schema
-- Run this in Supabase SQL Editor to create the required tables

-- ===========================================
-- SCRIPTS TABLE (replaces Google Sheets)
-- ===========================================
CREATE TABLE IF NOT EXISTS youtube_scripts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    script_text TEXT NOT NULL,
    description TEXT,
    hashtags TEXT,
    thumbnail_text VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'published', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,

    -- Generated content
    audio_url TEXT,
    video_url TEXT,

    -- Platform IDs
    youtube_post_id VARCHAR(100),
    late_post_id VARCHAR(100),
    did_talk_id VARCHAR(100),

    -- Metadata
    voice_id VARCHAR(100),
    avatar_id VARCHAR(100),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

-- Index for finding pending scripts
CREATE INDEX IF NOT EXISTS idx_youtube_scripts_status ON youtube_scripts(status);
CREATE INDEX IF NOT EXISTS idx_youtube_scripts_created ON youtube_scripts(created_at);

-- ===========================================
-- ERRORS TABLE (for logging)
-- ===========================================
CREATE TABLE IF NOT EXISTS youtube_automation_errors (
    id SERIAL PRIMARY KEY,
    script_id INTEGER REFERENCES youtube_scripts(id),
    error_type VARCHAR(50),
    error_message TEXT,
    error_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- DAILY STATS TABLE (for monitoring)
-- ===========================================
CREATE TABLE IF NOT EXISTS youtube_automation_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE DEFAULT CURRENT_DATE,
    scripts_processed INTEGER DEFAULT 0,
    videos_created INTEGER DEFAULT 0,
    videos_published INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    elevenlabs_chars_used INTEGER DEFAULT 0,
    did_credits_used DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================
-- INSERT SAMPLE SCRIPT
-- ===========================================
INSERT INTO youtube_scripts (title, script_text, description, hashtags, thumbnail_text, status)
VALUES (
    'Stop Taking Zinc for Testosterone',
    'Stop taking zinc for testosterone unless you''re actually deficient.

A 2023 study found that zinc supplementation only raised testosterone in men who were already low to begin with.

If your zinc levels are normal, you''re wasting your money.

Here''s what to do instead:

First, get a blood test. Check your zinc AND testosterone levels.

Second, if you''re deficient, 15 to 30 milligrams daily is enough. More isn''t better.

Third, focus on what actually works: sleep, strength training, and managing stress.

Follow for more evidence-based fitness tips.',
    'Learn why zinc supplementation might not boost your testosterone, and what actually works. Based on 2023 research.

Subscribe for daily fitness tips for men 35+',
    '#testosterone #fitness #menover40 #health #workout #supplements',
    'ZINC MYTH',
    'pending'
) ON CONFLICT DO NOTHING;

-- ===========================================
-- ROW LEVEL SECURITY (Optional but recommended)
-- ===========================================
-- ALTER TABLE youtube_scripts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE youtube_automation_errors ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE youtube_automation_stats ENABLE ROW LEVEL SECURITY;

-- Grant service role full access
-- CREATE POLICY "Service role has full access to scripts" ON youtube_scripts
--     FOR ALL USING (true) WITH CHECK (true);
