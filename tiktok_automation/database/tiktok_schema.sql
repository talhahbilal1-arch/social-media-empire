-- ==================== TikTok Queue Table ====================
-- Faceless TikTok Video Pipeline for Fitness/Beauty Niche
-- Target: U.S. women 25-44, 5-10 vertical shorts (15-60s)/day
-- Goal: TikTok Creativity Program ($0.20+/1K views) + Amazon affiliates

CREATE TABLE IF NOT EXISTS tiktok_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content Generation
    topic TEXT NOT NULL,
    script TEXT,
    voice_prompt TEXT,

    -- Audio (ElevenLabs)
    audio_url TEXT,
    voice_id TEXT DEFAULT 'EXAVITQu4vr4xnSDxMaL',  -- "Sarah" - friendly female
    audio_duration_seconds NUMERIC(5,2),

    -- Video (HeyGen)
    video_prompt TEXT,
    heygen_template_id TEXT,
    heygen_avatar_id TEXT DEFAULT 'josh_lite3_20230714',  -- Faceless background
    video_url TEXT,
    video_duration_seconds INTEGER DEFAULT 30,

    -- TikTok Posting
    caption TEXT,
    hashtags TEXT[],
    tiktok_post_id TEXT,
    tiktok_post_url TEXT,

    -- Affiliate Tracking
    affiliate_products JSONB DEFAULT '[]',
    amazon_tag TEXT DEFAULT 'fitnessquick-20',

    -- Analytics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    estimated_earnings NUMERIC(10,2) DEFAULT 0.00,

    -- Workflow Status
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending',
        'script_ready',
        'audio_ready',
        'video_ready',
        'posted',
        'failed',
        'paused'
    )),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Cross-posting
    cross_posted_youtube BOOLEAN DEFAULT FALSE,
    cross_posted_instagram BOOLEAN DEFAULT FALSE,
    cross_posted_pinterest BOOLEAN DEFAULT FALSE,
    youtube_url TEXT,
    instagram_url TEXT,
    pinterest_url TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    script_generated_at TIMESTAMPTZ,
    audio_generated_at TIMESTAMPTZ,
    video_generated_at TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Make.com Supabase triggers
CREATE INDEX idx_tiktok_queue_status ON tiktok_queue(status);
CREATE INDEX idx_tiktok_queue_created_at ON tiktok_queue(created_at);
CREATE INDEX idx_tiktok_queue_posted_at ON tiktok_queue(posted_at);
CREATE INDEX idx_tiktok_queue_status_created ON tiktok_queue(status, created_at);

-- Enable RLS
ALTER TABLE tiktok_queue ENABLE ROW LEVEL SECURITY;

-- Policy for service role (Make.com uses service_role key)
CREATE POLICY "Service role full access tiktok_queue" ON tiktok_queue
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ==================== TikTok Analytics Table ====================
CREATE TABLE IF NOT EXISTS tiktok_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tiktok_queue_id UUID REFERENCES tiktok_queue(id),
    tiktok_post_id TEXT,

    -- Performance Metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,

    -- Engagement Rates
    engagement_rate NUMERIC(5,2),
    watch_time_seconds NUMERIC(10,2),
    average_watch_percentage NUMERIC(5,2),

    -- Revenue Tracking
    creativity_program_earnings NUMERIC(10,4),
    affiliate_clicks INTEGER DEFAULT 0,
    affiliate_conversions INTEGER DEFAULT 0,
    affiliate_revenue NUMERIC(10,2),

    -- Snapshot timestamp
    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tiktok_analytics_queue_id ON tiktok_analytics(tiktok_queue_id);
CREATE INDEX idx_tiktok_analytics_snapshot ON tiktok_analytics(snapshot_at);

ALTER TABLE tiktok_analytics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access tiktok_analytics" ON tiktok_analytics
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ==================== Prompt Optimization Table ====================
CREATE TABLE IF NOT EXISTS tiktok_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_type TEXT NOT NULL CHECK (prompt_type IN ('script', 'voice', 'video', 'caption')),
    prompt_text TEXT NOT NULL,

    -- Performance tracking
    times_used INTEGER DEFAULT 0,
    average_views NUMERIC(10,2),
    average_engagement NUMERIC(5,2),

    -- A/B testing
    is_active BOOLEAN DEFAULT TRUE,
    test_group TEXT DEFAULT 'A',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE tiktok_prompts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access tiktok_prompts" ON tiktok_prompts
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ==================== Trigger for updated_at ====================
CREATE OR REPLACE FUNCTION update_tiktok_queue_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_tiktok_queue_updated_at
    BEFORE UPDATE ON tiktok_queue
    FOR EACH ROW
    EXECUTE FUNCTION update_tiktok_queue_timestamp();

-- ==================== 20 Starter Content Ideas ====================
-- Target: Quick fitness/beauty/lifestyle for women 25-44

INSERT INTO tiktok_queue (topic, hashtags, affiliate_products) VALUES
-- Quick Workout Series (5)
('5-min abs for busy moms - no equipment needed',
 ARRAY['quickworkout', 'momfitness', 'absworkout', 'noequipment', 'fitnesshacks', 'workout', 'fyp'],
 '[{"name": "Yoga Mat", "asin": "B01LP0U5X0", "price": 19.99}]'),

('3 arm exercises you can do at your desk',
 ARRAY['deskworkout', 'armtoning', 'officefitness', 'quickfitness', 'tonedarms', 'workout', 'fyp'],
 '[{"name": "Resistance Bands", "asin": "B07GJJSTX6", "price": 12.99}]'),

('Morning stretch routine for better posture in 60 seconds',
 ARRAY['morningroutine', 'stretching', 'posture', 'flexibility', 'wellness', 'selfcare', 'fyp'],
 '[{"name": "Foam Roller", "asin": "B00XM2MRGI", "price": 24.99}]'),

('Booty burn workout you can do anywhere - 5 mins',
 ARRAY['bootyworkout', 'gluteexercises', 'homeworkout', 'fitness', 'fitnessmotivation', 'fyp'],
 '[{"name": "Booty Bands Set", "asin": "B07Q5LRQVJ", "price": 14.99}]'),

('The only 4 exercises you need for flat stomach',
 ARRAY['flatstomach', 'corestrength', 'absexercises', 'fitnessjourney', 'motivation', 'fyp'],
 '[{"name": "Ab Roller", "asin": "B07LBQF6SZ", "price": 16.99}]'),

-- Beauty Hacks (5)
('Ice roller trick that depuffs your face instantly',
 ARRAY['beautyhacks', 'skincare', 'morningroutine', 'depuff', 'glowup', 'beauty', 'fyp'],
 '[{"name": "Ice Roller", "asin": "B07RGQW3HD", "price": 9.99}]'),

('5-minute makeup look for school runs and zoom calls',
 ARRAY['quickmakeup', 'momlife', 'makeuptutorial', 'naturalmakeup', 'easymakeup', 'fyp'],
 '[{"name": "BB Cream", "asin": "B002JBJ3IM", "price": 11.99}]'),

('Gua sha technique for instant face lift effect',
 ARRAY['guasha', 'facemassage', 'skincareroutine', 'antiaging', 'naturalbeauty', 'fyp'],
 '[{"name": "Gua Sha Set", "asin": "B07NQKZ6J2", "price": 15.99}]'),

('Hair growth serum application most people get wrong',
 ARRAY['hairgrowth', 'haircare', 'thinhair', 'beautytips', 'hairtok', 'fyp'],
 '[{"name": "Hair Growth Serum", "asin": "B07PXZQWVB", "price": 29.99}]'),

('Lip plumping trick without injections',
 ARRAY['lipplumping', 'beautyhack', 'makeuptips', 'naturallips', 'beautysecrets', 'fyp'],
 '[{"name": "Lip Plumper", "asin": "B07H2ZDNK6", "price": 8.99}]'),

-- Lifestyle/Wellness (5)
('30-second breathing technique for instant calm',
 ARRAY['anxiety', 'breathingexercises', 'mentalhealth', 'stressrelief', 'wellness', 'fyp'],
 '[{"name": "Meditation App Subscription", "asin": "B08TLRXQR3", "price": 12.99}]'),

('Morning water routine that changed my energy levels',
 ARRAY['morningroutine', 'hydration', 'wellness', 'healthyhabits', 'selfcare', 'fyp'],
 '[{"name": "Water Bottle with Timer", "asin": "B07P7K4XMX", "price": 22.99}]'),

('Meal prep hack that saves 3 hours every week',
 ARRAY['mealprep', 'mealprepideas', 'timesaving', 'healthyeating', 'momhacks', 'fyp'],
 '[{"name": "Meal Prep Containers", "asin": "B076QBRG6C", "price": 19.99}]'),

('Sleep posture fix that eliminated my back pain',
 ARRAY['sleeptips', 'backpain', 'wellness', 'sleephacks', 'health', 'fyp'],
 '[{"name": "Memory Foam Pillow", "asin": "B00V9J3QHW", "price": 39.99}]'),

('Walking workout that burns more calories than running',
 ARRAY['walkingworkout', 'weightloss', 'lowimpact', 'fitness', 'healthylifestyle', 'fyp'],
 '[{"name": "Walking Shoes", "asin": "B08R8KZNTP", "price": 59.99}]'),

-- Impulse Buy/Product Reviews (5)
('Amazon finds under $20 that actually work',
 ARRAY['amazonfinds', 'amazonmusthaves', 'budgetfinds', 'tiktokmademebuyit', 'fyp'],
 '[{"name": "LED Strip Lights", "asin": "B07JPK8NQ1", "price": 15.99}, {"name": "Portable Blender", "asin": "B07QF8P9WX", "price": 18.99}]'),

('Gym bag essentials every woman needs',
 ARRAY['gymbag', 'gymessentials', 'workoutgear', 'fitness', 'musthaves', 'fyp'],
 '[{"name": "Gym Bag", "asin": "B07QGML5GJ", "price": 34.99}]'),

('Self-care products I can''t live without',
 ARRAY['selfcare', 'selfcareroutine', 'relaxation', 'treatyourself', 'wellness', 'fyp'],
 '[{"name": "Bath Bombs Set", "asin": "B07DGXG4PN", "price": 24.99}]'),

('Kitchen gadget that makes healthy eating easy',
 ARRAY['kitchengadgets', 'healthyeating', 'mealprep', 'amazonfinds', 'cooking', 'fyp'],
 '[{"name": "Vegetable Chopper", "asin": "B0764HS4SL", "price": 26.99}]'),

('Desk setup items for work from home productivity',
 ARRAY['wfh', 'desksetup', 'productivity', 'homeoffice', 'amazonfinds', 'fyp'],
 '[{"name": "Laptop Stand", "asin": "B07P7BTJBZ", "price": 28.99}]');

-- ==================== Helper Functions ====================

-- Function to get next pending content for rendering
CREATE OR REPLACE FUNCTION get_next_pending_tiktok()
RETURNS TABLE (
    id UUID,
    topic TEXT,
    script TEXT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT tq.id, tq.topic, tq.script, tq.status
    FROM tiktok_queue tq
    WHERE tq.status = 'script_ready'
    ORDER BY tq.created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;
END;
$$ LANGUAGE plpgsql;

-- Function to get daily posting stats
CREATE OR REPLACE FUNCTION get_tiktok_daily_stats(target_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    total_posted BIGINT,
    total_views BIGINT,
    total_earnings NUMERIC,
    avg_engagement NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COALESCE(SUM(tq.views), 0)::BIGINT,
        COALESCE(SUM(tq.estimated_earnings), 0)::NUMERIC,
        COALESCE(AVG(
            CASE WHEN tq.views > 0
            THEN ((tq.likes + tq.comments + tq.shares)::NUMERIC / tq.views::NUMERIC) * 100
            ELSE 0 END
        ), 0)::NUMERIC
    FROM tiktok_queue tq
    WHERE tq.posted_at::DATE = target_date
    AND tq.status = 'posted';
END;
$$ LANGUAGE plpgsql;

-- Function to calculate estimated earnings from views
CREATE OR REPLACE FUNCTION calculate_tiktok_earnings(view_count INTEGER)
RETURNS NUMERIC AS $$
BEGIN
    -- TikTok Creativity Program: $0.20-$1.00 per 1K views
    -- Using conservative estimate of $0.25 per 1K views
    RETURN ROUND((view_count::NUMERIC / 1000) * 0.25, 2);
END;
$$ LANGUAGE plpgsql;
