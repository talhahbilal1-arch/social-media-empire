-- 005_fix_security_rls.sql
-- Fix: Enable RLS on all tables to block anonymous access
-- Safe to run multiple times (ENABLE RLS is idempotent).
--
-- WHY: Supabase flagged all tables as security vulnerabilities because
-- RLS was disabled + GRANT ALL TO anon — anyone with the public anon key
-- could read/write all business data.
--
-- HOW: service_role (used by all Python scripts via SUPABASE_KEY) has
-- BYPASSRLS=true in Supabase, so it always has full access regardless of RLS.
-- Enabling RLS with no policies blocks anon/authenticated while keeping
-- service_role working. No code changes needed.
--
-- Run in Supabase SQL Editor. No restart required.
-- ============================================================

-- ── Drop existing permissive USING(true) policies that expose data to anon ──
-- These were created in fix_schema_issues.sql and are too broad
DROP POLICY IF EXISTS "Service role full access errors" ON errors;
DROP POLICY IF EXISTS "Service role full access" ON agent_runs;

-- ── Enable RLS on all tables (blocks anon + authenticated, service_role bypasses) ──

-- From 001_master_schema
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

-- From 002_revenue_tracking
ALTER TABLE affiliate_revenue ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_programs ENABLE ROW LEVEL SECURITY;

-- From 004_newsletter_sends
ALTER TABLE newsletter_sends ENABLE ROW LEVEL SECURITY;

-- ── Verify: list all tables and their RLS status ──
SELECT
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
