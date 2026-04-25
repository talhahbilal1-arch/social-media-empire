-- Migration 004: Local video pipeline states
-- Adds a dedicated column to track the local Short Video Maker render pipeline
-- without overloading pinterest_pins.status (which is owned by the Make.com
-- posting flow). Safe to run multiple times.
--
-- State values (enforced in application code, not the schema, so new states
-- can be added without migrations):
--   NULL            — image pin or legacy row (ignore in local pipeline)
--   video_pending   — content-engine wrote content; awaiting local render
--   video_ready     — MP4 + cover uploaded to Supabase Storage (posted OR staged)
--   video_posted    — Zernio confirmed Pinterest post (fitness only today)
--   video_failed    — render or upload failed; eligible for manual requeue

ALTER TABLE pinterest_pins
  ADD COLUMN IF NOT EXISTS video_state TEXT DEFAULT NULL;

CREATE INDEX IF NOT EXISTS idx_pinterest_pins_video_state
  ON pinterest_pins(video_state)
  WHERE video_state IS NOT NULL;

-- Reload PostgREST schema cache so the column is immediately queryable
NOTIFY pgrst, 'reload schema';

-- Verify: list rows waiting for local render
-- SELECT id, brand, created_at
-- FROM pinterest_pins
-- WHERE video_state = 'video_pending'
-- ORDER BY created_at DESC;
