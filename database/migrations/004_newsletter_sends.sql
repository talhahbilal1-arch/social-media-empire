-- Newsletter sends tracking table
-- Tracks which articles have been sent as newsletter broadcasts per brand
CREATE TABLE IF NOT EXISTS newsletter_sends (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    article_filename VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    broadcast_id VARCHAR(100),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand, article_filename)
);

-- Grant access
GRANT ALL ON newsletter_sends TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE newsletter_sends_id_seq TO anon, authenticated, service_role;

-- Disable RLS (free tier pattern)
ALTER TABLE newsletter_sends DISABLE ROW LEVEL SECURITY;
