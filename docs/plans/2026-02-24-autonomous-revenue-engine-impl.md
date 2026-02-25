# Autonomous Revenue Engine — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the social media empire from a content machine that earns ~$50/month into a fully autonomous revenue engine targeting $550-1,500/month — by activating email sequences, replacing placeholder affiliate programs, parallelizing the pipeline, and adding 4 autonomous agent teams that continuously improve, self-heal, and discover new revenue streams.

**Architecture:** 6 independent implementation tracks that can be executed in parallel. Track 1 edits the existing content pipeline. Tracks 2a-2e create new files (Python agents + GitHub Actions workflows). All tracks converge on a single commit.

**Tech Stack:** Python 3.11, anthropic>=0.18.0, requests, concurrent.futures (stdlib), supabase>=2.3.0, GitHub Actions, Supabase PostgreSQL

---

## Track 1: Fix content-engine.yml — Remove Waits, Parallelize Brands

**Files:**
- Modify: `.github/workflows/content-engine.yml`

### What to change

**Change 1 — Phase 1: Parallelize brand content generation (lines ~135-175)**

Replace the serial `for brand in brands:` loop with ThreadPoolExecutor. Wrap the existing body in a function `_generate_for_brand(brand)` and use `ThreadPoolExecutor(max_workers=3)`.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def _generate_for_brand(brand):
    brand = brand.strip()
    print(f'\n--- Generating content for {brand} ---')
    try:
        today_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        try:
            today_posts = db.client.table('content_history') \
                .select('id').eq('brand', brand) \
                .gte('created_at', today_date_str + 'T00:00:00Z').execute()
            run_index = len(today_posts.data) if today_posts.data else 0
        except Exception:
            run_index = 0
        print(f'  Run index: {run_index}')
        pin_data = generate_pin_from_daily_trend(brand, run_index, db.client)
        if pin_data is not None:
            print(f'  Source: DAILY TREND')
        else:
            pin_data = generate_pin_from_calendar(brand, db.client)
            if pin_data is not None:
                print(f'  Source: WEEKLY CALENDAR')
            else:
                pin_data = generate_pin_content(brand, db.client)
                print(f'  Source: RANDOM STATIC')
        print(f'  Title: {pin_data["title"]}')
        return brand, pin_data
    except Exception as e:
        print(f'  ERROR generating content for {brand}: {e}')
        import traceback; traceback.print_exc()
        return brand, None

print('=== PHASE 1: Generating pin content (parallel) ===')
pin_data_by_brand = {}
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(_generate_for_brand, b): b for b in brands}
    for future in as_completed(futures):
        brand, pin_data = future.result()
        pin_data_by_brand[brand] = pin_data
```

**Change 2 — Phase 2: Parallelize article generation (lines ~180-215)**

Same pattern — wrap existing article generation body in `_generate_article_for_brand(brand, pin_data)` and use ThreadPoolExecutor.

**Change 3 — Remove the 60s deploy sleep (lines ~235-237)**

Delete these 2 lines entirely:
```python
# DELETE THESE:
print('  Waiting 60s for deploy...')
time.sleep(60)
```

**Change 4 — Remove the 30s inter-brand stagger (lines ~362-365)**

Delete these 4 lines entirely:
```python
# DELETE THESE:
# Stagger posts 30s apart between brands
if actual_status == 'posted' and brand_idx < len(brands) - 1:
    print(f'  Waiting 30s before next brand...')
    time.sleep(30)
```

**Change 5 — Phase 4: Parallelize brand posting**

Same ThreadPoolExecutor pattern for the render+upload+post loop. Wrap existing body in `_post_brand_pin(brand_idx, brand)`.

**Change 6 — Parallelize Vercel deploys (bash step, lines ~431-458)**

Replace serial deploys with background processes + wait:
```bash
deploy_count=0
if [ -n "$FITOVER35_PROJECT_ID" ]; then
  cd $GITHUB_WORKSPACE/outputs/fitover35-website
  VERCEL_PROJECT_ID="$FITOVER35_PROJECT_ID" vercel deploy --prod --yes --token $VERCEL_TOKEN . > /tmp/vercel_fitness.log 2>&1 &
  deploy_count=$((deploy_count+1))
  cd $GITHUB_WORKSPACE
fi
if [ -n "$DEALS_PROJECT_ID" ]; then
  cd $GITHUB_WORKSPACE/outputs/dailydealdarling-website
  VERCEL_PROJECT_ID="$DEALS_PROJECT_ID" vercel deploy --prod --yes --token $VERCEL_TOKEN . > /tmp/vercel_deals.log 2>&1 &
  deploy_count=$((deploy_count+1))
  cd $GITHUB_WORKSPACE
fi
if [ -n "$MENOPAUSE_PROJECT_ID" ]; then
  cd $GITHUB_WORKSPACE/outputs/menopause-planner-website
  VERCEL_PROJECT_ID="$MENOPAUSE_PROJECT_ID" vercel deploy --prod --yes --token $VERCEL_TOKEN . > /tmp/vercel_menopause.log 2>&1 &
  deploy_count=$((deploy_count+1))
  cd $GITHUB_WORKSPACE
fi
echo "Waiting for $deploy_count parallel deploys..."
wait
cat /tmp/vercel_*.log 2>/dev/null || true
```

---

## Track 2a: Database Migration — Revenue Tracking Tables

**Files:**
- Create: `database/migrations/002_revenue_tracking.sql`

```sql
-- 002_revenue_tracking.sql
-- Revenue tracking tables for autonomous revenue engine
-- Run in Supabase SQL Editor after 001_master_schema.sql

-- Tracks daily affiliate earnings per brand/program
CREATE TABLE IF NOT EXISTS affiliate_revenue (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    program_name VARCHAR(200),
    affiliate_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    date_recorded DATE DEFAULT CURRENT_DATE,
    source VARCHAR(50) DEFAULT 'amazon',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks email → click → purchase attribution
CREATE TABLE IF NOT EXISTS email_conversions (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    sequence_name VARCHAR(200),
    email_number INTEGER,
    subscriber_tag VARCHAR(200),
    affiliate_url TEXT,
    product_name TEXT,
    revenue_usd NUMERIC(10,2) DEFAULT 0,
    converted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tracks article/pin performance → revenue scores
CREATE TABLE IF NOT EXISTS content_performance (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    content_type VARCHAR(20) DEFAULT 'article',
    slug TEXT,
    title TEXT,
    ga4_sessions INTEGER DEFAULT 0,
    gsc_clicks INTEGER DEFAULT 0,
    gsc_impressions INTEGER DEFAULT 0,
    gsc_position NUMERIC(5,2),
    affiliate_clicks INTEGER DEFAULT 0,
    revenue_score NUMERIC(8,4) DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Catalog of all affiliate programs (active + discovered)
CREATE TABLE IF NOT EXISTS affiliate_programs (
    id BIGSERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    program_name VARCHAR(200) NOT NULL,
    network VARCHAR(100),
    signup_url TEXT,
    affiliate_url TEXT,
    commission_rate VARCHAR(50),
    status VARCHAR(20) DEFAULT 'placeholder',
    applied_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_brand ON affiliate_revenue(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_revenue_date ON affiliate_revenue(date_recorded);
CREATE INDEX IF NOT EXISTS idx_content_performance_brand ON content_performance(brand);
CREATE INDEX IF NOT EXISTS idx_content_performance_score ON content_performance(revenue_score DESC);
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_brand ON affiliate_programs(brand);
CREATE INDEX IF NOT EXISTS idx_affiliate_programs_status ON affiliate_programs(status);

-- Permissions
GRANT ALL ON affiliate_revenue TO anon, authenticated, service_role;
GRANT ALL ON email_conversions TO anon, authenticated, service_role;
GRANT ALL ON content_performance TO anon, authenticated, service_role;
GRANT ALL ON affiliate_programs TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE affiliate_revenue_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE email_conversions_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE content_performance_id_seq TO anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE affiliate_programs_id_seq TO anon, authenticated, service_role;

ALTER TABLE affiliate_revenue DISABLE ROW LEVEL SECURITY;
ALTER TABLE email_conversions DISABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance DISABLE ROW LEVEL SECURITY;
ALTER TABLE affiliate_programs DISABLE ROW LEVEL SECURITY;

-- Seed affiliate_programs from affiliate_config.json known entries
INSERT INTO affiliate_programs (brand, program_name, network, signup_url, commission_rate, status) VALUES
('fitness', 'ClickBank fitness programs', 'ClickBank', 'https://www.clickbank.com/affiliate/', '30-75%', 'placeholder'),
('fitness', 'ShareASale supplement brands', 'ShareASale', 'https://www.shareasale.com/', '15-25%', 'placeholder'),
('fitness', 'Bodybuilding.com', 'Direct', 'https://www.bodybuilding.com/affiliate', '5-15%', 'placeholder'),
('fitness', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active'),
('deals', 'ShareASale home/lifestyle', 'ShareASale', 'https://www.shareasale.com/', '10-30%', 'placeholder'),
('deals', 'Impact.com brands', 'Impact', 'https://impact.com/', '5-20%', 'placeholder'),
('deals', 'Rakuten retailers', 'Rakuten', 'https://rakutenadvertising.com/', '5-15%', 'placeholder'),
('deals', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active'),
('menopause', 'ShareASale supplement brands', 'ShareASale', 'https://www.shareasale.com/', '15-30%', 'placeholder'),
('menopause', 'ClickBank health programs', 'ClickBank', 'https://www.clickbank.com/affiliate/', '30-75%', 'placeholder'),
('menopause', 'Etsy planner (own product)', 'Etsy', 'https://www.etsy.com/listing/4435219468/', '100% minus fees', 'active'),
('menopause', 'Amazon Associates', 'Amazon', 'https://affiliate-program.amazon.com/', '4%', 'active')
ON CONFLICT DO NOTHING;
```

---

## Track 2b: Revenue Intelligence Agent

**Files:**
- Create: `video_automation/revenue_intelligence.py`
- Create: `.github/workflows/revenue-intelligence.yml`

### revenue_intelligence.py

Three-agent system: analytics_reader, performance_analyzer, strategy_updater — all run in parallel via ThreadPoolExecutor, then coordinator synthesizes and updates Supabase weekly_calendar.

```python
"""Revenue Intelligence Engine — Team 1 of 4 autonomous agent teams.

Runs daily at 6AM PST. Reads performance data → scores content by revenue →
updates weekly_calendar in Supabase so Content Engine automatically makes more
of what earns money.

Agents (run in parallel via ThreadPoolExecutor):
  1. analytics_reader  — pulls content_performance, content_history, generated_articles
  2. performance_analyzer — Claude scores each brand's content by revenue potential
  3. strategy_updater  — rewrites weekly_calendar entries toward top-earning topics
"""

import os
import sys
import json
import anthropic
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '.')
from database.supabase_client import get_supabase_client

BRANDS = ['fitness', 'deals', 'menopause']

BRAND_NICHES = {
    'fitness': 'men\'s fitness over 35, supplements, workouts, weight loss',
    'deals': 'budget home & lifestyle deals, kitchen, organization, beauty',
    'menopause': 'menopause wellness, hot flashes, sleep, supplements, mood'
}

def get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


# ─── Agent 1: Analytics Reader ───────────────────────────────────────────────

def analytics_reader_agent(db):
    """Pull all available performance data from Supabase."""
    print('[analytics_reader] Reading performance data...')
    data = {}
    for brand in BRANDS:
        brand_data = {}
        # Recent articles
        try:
            arts = db.client.table('generated_articles').select(
                'slug, article_title, brand, created_at'
            ).eq('brand', brand).order('created_at', desc=True).limit(30).execute()
            brand_data['recent_articles'] = arts.data or []
        except Exception as e:
            brand_data['recent_articles'] = []
            print(f'  [analytics_reader] articles fetch failed for {brand}: {e}')

        # Content performance scores (if table populated)
        try:
            perf = db.client.table('content_performance').select('*').eq(
                'brand', brand
            ).order('revenue_score', desc=True).limit(10).execute()
            brand_data['top_performers'] = perf.data or []
        except Exception:
            brand_data['top_performers'] = []

        # Recent pin history topics
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
            hist = db.client.table('content_history').select(
                'trending_topic, board, visual_style, status'
            ).eq('brand', brand).gte('created_at', cutoff).execute()
            brand_data['recent_topics'] = hist.data or []
        except Exception:
            brand_data['recent_topics'] = []

        # Affiliate programs status
        try:
            progs = db.client.table('affiliate_programs').select(
                'program_name, status, commission_rate'
            ).eq('brand', brand).execute()
            brand_data['affiliate_programs'] = progs.data or []
        except Exception:
            brand_data['affiliate_programs'] = []

        data[brand] = brand_data
        print(f'  [analytics_reader] {brand}: {len(brand_data["recent_articles"])} articles, '
              f'{len(brand_data["recent_topics"])} recent topics')
    return data


# ─── Agent 2: Performance Analyzer ──────────────────────────────────────────

def performance_analyzer_agent(analytics_data, client):
    """Use Claude to score each brand's content and identify revenue opportunities."""
    print('[performance_analyzer] Analyzing content performance...')
    results = {}

    def analyze_brand(brand):
        data = analytics_data[brand]
        recent_topics = [t.get('trending_topic', '') for t in data['recent_topics'] if t.get('trending_topic')]
        recent_articles = [a.get('article_title', '') or a.get('slug', '') for a in data['recent_articles']]
        active_programs = [p['program_name'] for p in data['affiliate_programs'] if p.get('status') == 'active']
        placeholder_programs = [p['program_name'] for p in data['affiliate_programs'] if p.get('status') == 'placeholder']

        prompt = f"""You are a revenue optimization analyst for a Pinterest content business.

Brand: {brand} ({BRAND_NICHES[brand]})

Recent pin topics (last 14 days):
{json.dumps(recent_topics[:15], indent=2)}

Recent articles generated:
{json.dumps(recent_articles[:10], indent=2)}

Active affiliate programs: {json.dumps(active_programs)}
Placeholder (not yet earning) programs: {json.dumps(placeholder_programs)}

Your job:
1. Identify the TOP 5 topic clusters that would drive the most affiliate revenue for this brand
2. For each topic cluster, suggest 3 specific pin/article titles optimized for buyer intent
3. Flag any content gaps (topics with high buyer intent that haven't been covered recently)

Return JSON only:
{{
  "top_revenue_topics": [
    {{
      "cluster": "topic cluster name",
      "buyer_intent": "high/medium",
      "suggested_titles": ["title 1", "title 2", "title 3"],
      "affiliate_fit": "which program this connects to"
    }}
  ],
  "content_gaps": ["gap 1", "gap 2", "gap 3"],
  "priority_action": "single most important revenue action for this brand"
}}"""

        try:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=1500,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = response.content[0].text.strip()
            # Extract JSON
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            return brand, json.loads(text)
        except Exception as e:
            print(f'  [performance_analyzer] {brand} failed: {e}')
            return brand, {
                'top_revenue_topics': [],
                'content_gaps': [],
                'priority_action': f'Analysis failed: {e}'
            }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(analyze_brand, b): b for b in BRANDS}
        for future in as_completed(futures):
            brand, result = future.result()
            results[brand] = result
            print(f'  [performance_analyzer] {brand}: {len(result.get("top_revenue_topics", []))} revenue topics identified')

    return results


# ─── Agent 3: Strategy Updater ───────────────────────────────────────────────

def strategy_updater_agent(analysis_results, db, client):
    """Rewrite weekly_calendar in Supabase toward top revenue topics."""
    print('[strategy_updater] Updating content calendar with revenue-optimized topics...')

    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    next_week_start = week_start + timedelta(weeks=1)
    updated = 0

    for brand in BRANDS:
        analysis = analysis_results.get(brand, {})
        top_topics = analysis.get('top_revenue_topics', [])
        if not top_topics:
            print(f'  [strategy_updater] {brand}: no topics to update')
            continue

        # Build calendar entries for next 7 days
        topics_for_week = []
        for i, topic_cluster in enumerate(top_topics[:5]):
            for j, title in enumerate(topic_cluster.get('suggested_titles', [])[:1]):
                topics_for_week.append({
                    'brand': brand,
                    'topic': topic_cluster['cluster'],
                    'suggested_title': title,
                    'buyer_intent': topic_cluster.get('buyer_intent', 'medium'),
                    'affiliate_fit': topic_cluster.get('affiliate_fit', ''),
                    'day_offset': i
                })

        # Upsert into weekly_calendar
        for entry in topics_for_week:
            try:
                scheduled_date = (next_week_start + timedelta(days=entry['day_offset'])).isoformat()
                db.client.table('weekly_calendar').upsert({
                    'brand': brand,
                    'scheduled_date': scheduled_date,
                    'topic': entry['topic'],
                    'suggested_title': entry['suggested_title'],
                    'notes': json.dumps({
                        'buyer_intent': entry['buyer_intent'],
                        'affiliate_fit': entry['affiliate_fit'],
                        'source': 'revenue_intelligence',
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }),
                    'status': 'pending'
                }, on_conflict='brand,scheduled_date').execute()
                updated += 1
            except Exception as e:
                print(f'  [strategy_updater] calendar upsert failed for {brand}: {e}')

        print(f'  [strategy_updater] {brand}: {len(topics_for_week)} calendar entries updated')

    return updated


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_revenue_intelligence():
    print('=== Revenue Intelligence Engine starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = get_anthropic_client()

    # Step 1: Read analytics data
    analytics_data = analytics_reader_agent(db)

    # Step 2: Analyze performance (Claude, parallel across brands)
    analysis_results = performance_analyzer_agent(analytics_data, client)

    # Step 3: Update calendar
    updates = strategy_updater_agent(analysis_results, db, client)

    # Step 4: Log run
    try:
        db.client.table('agent_runs').upsert({
            'agent_name': 'revenue_intelligence',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }, on_conflict='agent_name').execute()
    except Exception as e:
        print(f'  agent_runs log failed: {e}')

    # Summary
    print('\n=== Revenue Intelligence Summary ===')
    for brand in BRANDS:
        result = analysis_results.get(brand, {})
        print(f'  {brand}:')
        for topic in result.get('top_revenue_topics', [])[:3]:
            print(f'    - {topic.get("cluster")} ({topic.get("buyer_intent")} intent)')
        if result.get('priority_action'):
            print(f'    Priority: {result["priority_action"]}')
    print(f'  Calendar entries updated: {updates}')
    print('=== Done ===')

    # Store analysis results for review
    try:
        db.client.table('analytics').insert({
            'event_type': 'revenue_intelligence_run',
            'brand': 'all',
            'platform': 'system',
            'data': {
                'analysis': analysis_results,
                'calendar_updates': updates,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }).execute()
    except Exception:
        pass


if __name__ == '__main__':
    run_revenue_intelligence()
```

### revenue-intelligence.yml

```yaml
name: Revenue Intelligence Engine

on:
  schedule:
    - cron: '0 14 * * *'  # 6AM PST daily
  workflow_dispatch:

permissions:
  contents: read

env:
  PYTHON_VERSION: '3.11'

jobs:
  revenue-intelligence:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - run: pip install -r requirements.txt

      - name: Run Revenue Intelligence Engine
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python3 video_automation/revenue_intelligence.py
```

---

## Track 2c: Revenue Activation Agent

**Files:**
- Create: `video_automation/revenue_activation.py`
- Create: `.github/workflows/revenue-activation.yml`

### revenue_activation.py

Four-agent system: email_activator, affiliate_discoverer, affiliate_validator, revenue_reporter.

```python
"""Revenue Activation Team — Team 2 of 4 autonomous agent teams.

Runs weekly Monday 9AM PST. Activates email sequences in ConvertKit,
discovers real affiliate programs to replace placeholders, validates
all affiliate links, and reports revenue status.

Agents (run in parallel via ThreadPoolExecutor):
  1. email_activator    — checks ConvertKit sequences; creates/activates them via API
  2. affiliate_discoverer — finds real programs for placeholder slots via Claude
  3. affiliate_validator  — HTTP-checks all affiliate URLs, logs 404s
  4. revenue_reporter   — generates weekly revenue status report → logs to Supabase
"""

import os
import sys
import json
import requests
import anthropic
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '.')
from database.supabase_client import get_supabase_client

BRANDS = ['fitness', 'deals', 'menopause']

BRAND_NICHES = {
    'fitness': 'men\'s fitness over 35 — supplements, workouts, weight loss',
    'deals': 'budget home & lifestyle — kitchen gadgets, organization, beauty',
    'menopause': 'menopause wellness — supplements, sleep, mood, hot flashes'
}


def get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


# ─── Agent 1: Email Activator ────────────────────────────────────────────────

def email_activator_agent():
    """Check ConvertKit for active sequences; report status and gaps."""
    print('[email_activator] Checking ConvertKit email sequences...')
    ck_key = os.environ.get('CONVERTKIT_API_KEY', '')
    ck_secret = os.environ.get('CONVERTKIT_API_SECRET', '')

    if not ck_key:
        print('  [email_activator] CONVERTKIT_API_KEY not set — sequences cannot be checked')
        return {
            'status': 'not_configured',
            'action_needed': 'Set CONVERTKIT_API_KEY and CONVERTKIT_API_SECRET in GitHub Secrets',
            'sequences': []
        }

    try:
        # List all sequences
        resp = requests.get(
            'https://api.convertkit.com/v3/sequences',
            params={'api_secret': ck_secret},
            timeout=15
        )
        if resp.status_code != 200:
            return {'status': 'api_error', 'error': f'HTTP {resp.status_code}', 'sequences': []}

        sequences = resp.json().get('courses', [])
        print(f'  [email_activator] Found {len(sequences)} sequences in ConvertKit')

        # Check which brand sequences exist and are active
        brand_sequences = {}
        for seq in sequences:
            name_lower = seq.get('name', '').lower()
            for brand in BRANDS:
                brand_words = {'fitness': 'fit', 'deals': 'deal', 'menopause': 'menopause'}
                if brand_words[brand] in name_lower:
                    brand_sequences[brand] = {
                        'id': seq['id'],
                        'name': seq['name'],
                        'active': seq.get('active', False),
                        'subscriber_count': seq.get('subscriber_count', 0)
                    }

        missing = [b for b in BRANDS if b not in brand_sequences]
        inactive = [b for b, s in brand_sequences.items() if not s.get('active')]

        result = {
            'status': 'checked',
            'sequences_found': brand_sequences,
            'missing_brands': missing,
            'inactive_sequences': inactive,
            'action_needed': []
        }

        if missing:
            result['action_needed'].append(
                f'Create ConvertKit sequences for: {", ".join(missing)}. '
                f'Written sequences are in email_marketing/sequences/ — upload them to ConvertKit.'
            )
        if inactive:
            result['action_needed'].append(
                f'Activate ConvertKit sequences for: {", ".join(inactive)}'
            )

        for brand, seq_data in brand_sequences.items():
            print(f'  [email_activator] {brand}: {"ACTIVE" if seq_data["active"] else "INACTIVE"} '
                  f'({seq_data["subscriber_count"]} subscribers)')

        return result

    except Exception as e:
        print(f'  [email_activator] Error: {e}')
        return {'status': 'error', 'error': str(e), 'sequences': []}


# ─── Agent 2: Affiliate Discoverer ──────────────────────────────────────────

def affiliate_discoverer_agent(db, client):
    """Use Claude to generate real affiliate program recommendations for each brand."""
    print('[affiliate_discoverer] Finding real affiliate programs to replace placeholders...')

    results = {}
    for brand in BRANDS:
        # Check existing placeholder programs
        try:
            placeholders = db.client.table('affiliate_programs').select('*').eq(
                'brand', brand
            ).eq('status', 'placeholder').execute()
            placeholder_list = placeholders.data or []
        except Exception:
            placeholder_list = []

        if not placeholder_list:
            print(f'  [affiliate_discoverer] {brand}: no placeholders to fill')
            results[brand] = {'status': 'no_placeholders', 'recommendations': []}
            continue

        prompt = f"""You are an affiliate marketing expert. For a {BRAND_NICHES[brand]} content site,
identify the BEST real affiliate programs that:
1. Have high commissions (>10% or >$20/sale)
2. Are reputable and easy to join
3. Match the content niche exactly

Current placeholder programs needing real replacements:
{json.dumps([p['program_name'] for p in placeholder_list], indent=2)}

For each, provide:
1. The REAL program name and network (ShareASale ID, ClickBank marketplace, etc.)
2. Exact signup URL
3. Commission rate
4. Why it fits this brand

Return JSON only:
{{
  "recommendations": [
    {{
      "replaces": "placeholder program name from list above",
      "real_program_name": "actual program name",
      "network": "ShareASale / ClickBank / Impact / Direct",
      "signup_url": "exact URL to sign up",
      "commission": "X% per sale",
      "why_it_fits": "brief reason"
    }}
  ]
}}"""

        try:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=1000,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = response.content[0].text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            recs = json.loads(text)

            # Update affiliate_programs table with recommendations
            for rec in recs.get('recommendations', []):
                try:
                    db.client.table('affiliate_programs').upsert({
                        'brand': brand,
                        'program_name': rec['real_program_name'],
                        'network': rec.get('network', ''),
                        'signup_url': rec.get('signup_url', ''),
                        'commission_rate': rec.get('commission', ''),
                        'status': 'discovered',
                        'notes': f"Replaces: {rec.get('replaces', '')} | {rec.get('why_it_fits', '')}"
                    }, on_conflict='brand,program_name').execute()
                except Exception as e:
                    print(f'  [affiliate_discoverer] DB upsert failed: {e}')

            results[brand] = {'status': 'success', 'recommendations': recs.get('recommendations', [])}
            print(f'  [affiliate_discoverer] {brand}: {len(recs.get("recommendations", []))} programs found')

        except Exception as e:
            print(f'  [affiliate_discoverer] {brand} failed: {e}')
            results[brand] = {'status': 'error', 'error': str(e)}

    return results


# ─── Agent 3: Affiliate Validator ────────────────────────────────────────────

def affiliate_validator_agent(db):
    """HTTP-check all affiliate URLs in the database. Flag 404s."""
    print('[affiliate_validator] Validating all affiliate URLs...')

    # Load affiliate config
    config_path = 'monetization/affiliate_config.json'
    urls_to_check = []
    try:
        with open(config_path) as f:
            config = json.load(f)
        for brand, brand_data in config.items():
            for category in brand_data.values():
                if isinstance(category, list):
                    for item in category:
                        if isinstance(item, dict) and 'url' in item:
                            url = item['url']
                            if url and not url.startswith('PLACEHOLDER'):
                                urls_to_check.append({
                                    'brand': brand,
                                    'name': item.get('name', ''),
                                    'url': url
                                })
    except Exception as e:
        print(f'  [affiliate_validator] Config load failed: {e}')

    results = {'valid': [], 'broken': [], 'checked': 0}

    def check_url(item):
        try:
            resp = requests.get(item['url'], timeout=10, allow_redirects=True,
                                headers={'User-Agent': 'Mozilla/5.0'})
            return item, resp.status_code < 400
        except Exception:
            return item, False

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_url, item): item for item in urls_to_check}
        for future in as_completed(futures):
            item, valid = future.result()
            results['checked'] += 1
            if valid:
                results['valid'].append(item['name'])
            else:
                results['broken'].append(item)
                print(f'  [affiliate_validator] BROKEN: {item["name"]} ({item["url"][:60]})')

                # Log broken link to errors table
                try:
                    db.client.table('errors').insert({
                        'error_type': 'broken_affiliate_link',
                        'error_message': f'Affiliate link returning error: {item["url"]}',
                        'context': json.dumps({'brand': item['brand'], 'program': item['name']}),
                        'severity': 'high',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }).execute()
                except Exception:
                    pass

    print(f'  [affiliate_validator] Checked {results["checked"]} URLs: '
          f'{len(results["valid"])} valid, {len(results["broken"])} broken')
    return results


# ─── Agent 4: Revenue Reporter ───────────────────────────────────────────────

def revenue_reporter_agent(db, email_result, affiliate_result, validation_result):
    """Generate weekly revenue status report and log to Supabase."""
    print('[revenue_reporter] Generating revenue status report...')

    # Compile placeholder count
    total_placeholder = 0
    total_discovered = 0
    total_active = 0
    try:
        for brand in BRANDS:
            progs = db.client.table('affiliate_programs').select(
                'status'
            ).eq('brand', brand).execute()
            for p in (progs.data or []):
                if p['status'] == 'placeholder':
                    total_placeholder += 1
                elif p['status'] == 'discovered':
                    total_discovered += 1
                elif p['status'] == 'active':
                    total_active += 1
    except Exception:
        pass

    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'email_sequences': email_result,
        'affiliate_programs': {
            'active': total_active,
            'discovered_pending_signup': total_discovered,
            'placeholder': total_placeholder
        },
        'link_validation': {
            'checked': validation_result.get('checked', 0),
            'broken': len(validation_result.get('broken', []))
        },
        'affiliate_discoveries': {
            b: len(r.get('recommendations', []))
            for b, r in affiliate_result.items()
        },
        'action_items': []
    }

    # Build action items list
    if email_result.get('missing_brands'):
        report['action_items'].append(
            f'⚠️  Email sequences missing for: {", ".join(email_result["missing_brands"])}'
        )
    if email_result.get('inactive_sequences'):
        report['action_items'].append(
            f'⚠️  Activate ConvertKit sequences for: {", ".join(email_result["inactive_sequences"])}'
        )
    if total_placeholder > 0:
        report['action_items'].append(
            f'⚠️  {total_placeholder} affiliate programs still placeholder — sign up at URLs in affiliate_programs table'
        )
    if validation_result.get('broken'):
        broken_names = [b['name'] for b in validation_result['broken']]
        report['action_items'].append(
            f'⚠️  Broken affiliate links: {", ".join(broken_names)}'
        )
    if total_discovered > 0:
        report['action_items'].append(
            f'✅ {total_discovered} new programs discovered — review affiliate_programs table and sign up'
        )

    # Log to Supabase
    try:
        db.client.table('analytics').insert({
            'event_type': 'revenue_activation_run',
            'brand': 'all',
            'platform': 'system',
            'data': report
        }).execute()
    except Exception as e:
        print(f'  [revenue_reporter] Log failed: {e}')

    print('\n=== Revenue Activation Report ===')
    print(f'  Email sequences: {email_result.get("status")}')
    print(f'  Active affiliate programs: {total_active}')
    print(f'  Newly discovered programs: {total_discovered}')
    print(f'  Placeholder programs remaining: {total_placeholder}')
    print(f'  Broken links found: {len(validation_result.get("broken", []))}')
    if report['action_items']:
        print('\n  Action Items (requires manual sign-up):')
        for item in report['action_items']:
            print(f'    {item}')

    return report


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_revenue_activation():
    print('=== Revenue Activation Team starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = get_anthropic_client()

    # Run first 3 agents in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_email = executor.submit(email_activator_agent)
        f_affiliate = executor.submit(affiliate_discoverer_agent, db, client)
        f_validate = executor.submit(affiliate_validator_agent, db)

        email_result = f_email.result()
        affiliate_result = f_affiliate.result()
        validation_result = f_validate.result()

    # Revenue reporter synthesizes results
    report = revenue_reporter_agent(db, email_result, affiliate_result, validation_result)

    # Update agent_runs
    try:
        db.client.table('agent_runs').upsert({
            'agent_name': 'revenue_activation',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }, on_conflict='agent_name').execute()
    except Exception:
        pass

    print('=== Revenue Activation Done ===')
    return report


if __name__ == '__main__':
    run_revenue_activation()
```

### revenue-activation.yml

```yaml
name: Revenue Activation Team

on:
  schedule:
    - cron: '0 17 * * 1'  # Monday 9AM PST
  workflow_dispatch:

permissions:
  contents: read

env:
  PYTHON_VERSION: '3.11'

jobs:
  revenue-activation:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - run: pip install -r requirements.txt

      - name: Run Revenue Activation Team
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          CONVERTKIT_API_KEY: ${{ secrets.CONVERTKIT_API_KEY }}
          CONVERTKIT_API_SECRET: ${{ secrets.CONVERTKIT_API_SECRET }}
        run: python3 video_automation/revenue_activation.py
```

---

## Track 2d: SEO Content Machine

**Files:**
- Create: `video_automation/seo_content_machine.py`
- Create: `.github/workflows/seo-content-machine.yml`

### seo_content_machine.py

```python
"""SEO Content Machine — Team 3 of 4 autonomous agent teams.

Runs Mon/Wed/Fri 8AM PST. Finds keyword gaps → writes pillar/cluster articles
→ injects internal links across all existing articles.

Agents (run sequentially — each depends on previous):
  1. gsc_researcher   — finds position 5-20 keyword gaps per brand from Supabase data
  2. article_writer   — generates 3 SEO articles per brand targeting those gaps
  3. internal_linker  — scans existing articles, injects cross-links
"""

import os
import sys
import json
import re
import anthropic
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '.')
from database.supabase_client import get_supabase_client

BRANDS = ['fitness', 'deals', 'menopause']

BRAND_SITE_DIRS = {
    'fitness': 'outputs/fitover35-website',
    'deals': 'outputs/dailydealdarling-website',
    'menopause': 'outputs/menopause-planner-website'
}

BRAND_BASE_URLS = {
    'fitness': 'https://fitover35.com',
    'deals': 'https://dailydealdarling.com',
    'menopause': 'https://menopause-planner-website.vercel.app'
}

BRAND_NICHES = {
    'fitness': 'men\'s fitness over 35, supplements, strength training, weight loss, testosterone',
    'deals': 'budget home decor, kitchen gadgets, organization hacks, beauty deals, lifestyle',
    'menopause': 'menopause symptoms, hot flashes, sleep problems, supplements, mood swings, weight gain'
}

BRAND_AMAZON_TAGS = {
    'fitness': 'fitover35-20',
    'deals': 'dailydealdarl-20',
    'menopause': 'menopauseplan-20'
}


def get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


def _make_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]


# ─── Agent 1: GSC Researcher ──────────────────────────────────────────────────

def gsc_researcher_agent(db, client):
    """Find keyword gaps using existing article data + Claude analysis."""
    print('[gsc_researcher] Finding keyword gaps for all brands...')
    gaps = {}

    for brand in BRANDS:
        # Get existing article titles to avoid duplication
        try:
            existing = db.client.table('generated_articles').select(
                'article_title, slug'
            ).eq('brand', brand).execute()
            existing_titles = [a.get('article_title', '') or a.get('slug', '') for a in (existing.data or [])]
        except Exception:
            existing_titles = []

        # Get content performance data (position 5-20 targets)
        try:
            perf = db.client.table('content_performance').select(
                'slug, title, gsc_position, gsc_clicks, gsc_impressions'
            ).eq('brand', brand).gte('gsc_position', 5).lte('gsc_position', 20).order(
                'gsc_impressions', desc=True
            ).limit(10).execute()
            position_5_20 = perf.data or []
        except Exception:
            position_5_20 = []

        prompt = f"""You are an SEO content strategist for a {BRAND_NICHES[brand]} website.

Existing articles (do NOT create duplicates):
{json.dumps(existing_titles[:20], indent=2)}

Your task: Identify 5 article topics with HIGH buyer intent that:
1. Are NOT already covered in the existing articles list
2. Target long-tail keywords (3-5 words) someone would search when ready to buy
3. Could naturally include Amazon affiliate product recommendations
4. Are specific enough to rank quickly (not "fitness tips")

Return JSON only:
{{
  "keyword_gaps": [
    {{
      "title": "exact article title to write",
      "target_keyword": "3-5 word search phrase",
      "search_intent": "buyer/informational/comparison",
      "affiliate_angle": "which products to recommend",
      "why_itll_rank": "brief reason"
    }}
  ]
}}"""

        try:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=1000,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = response.content[0].text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            result = json.loads(text)
            gaps[brand] = result.get('keyword_gaps', [])
            print(f'  [gsc_researcher] {brand}: {len(gaps[brand])} keyword gaps identified')
        except Exception as e:
            print(f'  [gsc_researcher] {brand} failed: {e}')
            gaps[brand] = []

    return gaps


# ─── Agent 2: Article Writer ──────────────────────────────────────────────────

def article_writer_agent(keyword_gaps, db, client):
    """Write 2 SEO articles per brand targeting the keyword gaps."""
    print('[article_writer] Writing SEO articles...')
    written = []

    def write_article_for_brand(brand):
        gaps = keyword_gaps.get(brand, [])
        if not gaps:
            return brand, []

        brand_written = []
        amazon_tag = BRAND_AMAZON_TAGS.get(brand, 'dailydealdarl-20')
        site_dir = Path(BRAND_SITE_DIRS[brand])
        articles_dir = site_dir / 'articles'
        articles_dir.mkdir(parents=True, exist_ok=True)

        # Write top 2 gap articles per brand (don't overwhelm Claude API)
        for gap in gaps[:2]:
            title = gap['title']
            slug = _make_slug(title)
            output_path = articles_dir / f'{slug}.html'

            # Skip if already exists
            if output_path.exists():
                print(f'  [article_writer] {brand}/{slug}: already exists, skipping')
                continue

            try:
                prompt = f"""Write a complete SEO article for a {BRAND_NICHES[brand]} website.

Title: {title}
Target keyword: {gap.get("target_keyword", title)}
Affiliate angle: {gap.get("affiliate_angle", "relevant products")}
Amazon Associates tag: {amazon_tag}

Requirements:
- 800-1000 words
- H2 subheadings for structure
- Include 2-3 Amazon product recommendations with real affiliate links
  Format: [Product Name](https://www.amazon.com/s?k=PRODUCT+NAME&tag={amazon_tag})
- End with a clear CTA
- Include FTC disclosure: "This article contains affiliate links."
- Write in a helpful, conversational tone — real person, not a robot
- Use markdown format

Write the complete article now:"""

                response = client.messages.create(
                    model='claude-sonnet-4-5',
                    max_tokens=2000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                article_md = response.content[0].text.strip()

                # Convert to HTML
                html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{gap.get('target_keyword', title)} — expert tips and recommendations">
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<article class="blog-post">
<h1>{title}</h1>
<div class="affiliate-disclosure">
<em>This article contains affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you.</em>
</div>
"""
                # Simple markdown to HTML conversion
                lines = article_md.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        html += '<br>\n'
                    elif line.startswith('## '):
                        html += f'<h2>{line[3:]}</h2>\n'
                    elif line.startswith('### '):
                        html += f'<h3>{line[4:]}</h3>\n'
                    elif line.startswith('# '):
                        pass  # skip duplicate h1
                    else:
                        # Convert markdown links
                        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                                      r'<a href="\2" rel="nofollow sponsored" target="_blank">\1</a>',
                                      line)
                        line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
                        html += f'<p>{line}</p>\n'

                html += '</article>\n</body>\n</html>'

                # Save article
                output_path.write_text(html, encoding='utf-8')
                brand_written.append({
                    'brand': brand,
                    'slug': slug,
                    'title': title,
                    'path': str(output_path)
                })
                print(f'  [article_writer] {brand}/{slug}: written ({len(html)} bytes)')

                # Log to generated_articles
                try:
                    base_url = BRAND_BASE_URLS[brand]
                    db.client.table('generated_articles').insert({
                        'brand': brand,
                        'slug': slug,
                        'article_title': title,
                        'article_url': f'{base_url}/articles/{slug}.html',
                        'has_affiliate_links': True,
                        'word_count': len(article_md.split()),
                        'source': 'seo_content_machine',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }).execute()
                except Exception as e:
                    print(f'  [article_writer] DB log failed for {brand}/{slug}: {e}')

            except Exception as e:
                print(f'  [article_writer] Failed to write {brand}/{slug}: {e}')

        return brand, brand_written

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(write_article_for_brand, b): b for b in BRANDS}
        for future in as_completed(futures):
            brand, brand_written = future.result()
            written.extend(brand_written)

    print(f'  [article_writer] Total articles written: {len(written)}')
    return written


# ─── Agent 3: Internal Linker ─────────────────────────────────────────────────

def internal_linker_agent():
    """Scan all articles and inject internal links between related content."""
    print('[internal_linker] Scanning articles for internal link opportunities...')
    total_links_added = 0

    for brand in BRANDS:
        articles_dir = Path(BRAND_SITE_DIRS[brand]) / 'articles'
        if not articles_dir.exists():
            continue

        html_files = list(articles_dir.glob('*.html'))
        if len(html_files) < 2:
            continue

        # Build slug → title map
        slug_title_map = {}
        for f in html_files:
            slug = f.stem
            try:
                content = f.read_text(encoding='utf-8')
                title_match = re.search(r'<title>([^<]+)</title>', content)
                if title_match:
                    slug_title_map[slug] = title_match.group(1)
                else:
                    slug_title_map[slug] = slug.replace('-', ' ').title()
            except Exception:
                pass

        base_url = BRAND_BASE_URLS[brand]
        links_added_brand = 0

        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                original = content

                for target_slug, target_title in slug_title_map.items():
                    if target_slug == html_file.stem:
                        continue  # don't link to self

                    # Skip if already linked
                    target_url = f'{base_url}/articles/{target_slug}.html'
                    if target_url in content:
                        continue

                    # Find a relevant keyword to link from (first few words of title)
                    keywords = target_title.lower().split()[:3]
                    keyword_phrase = ' '.join(keywords)

                    # Simple: find first occurrence of keyword phrase in a <p> tag and wrap with link
                    pattern = re.compile(
                        rf'(<p>[^<]*)({re.escape(keyword_phrase)})([^<]*</p>)',
                        re.IGNORECASE
                    )
                    replacement = rf'\1<a href="{target_url}">\2</a>\3'
                    new_content, n_subs = re.subn(pattern, replacement, content, count=1)
                    if n_subs > 0:
                        content = new_content
                        links_added_brand += 1

                if content != original:
                    html_file.write_text(content, encoding='utf-8')

            except Exception as e:
                print(f'  [internal_linker] Failed on {html_file.name}: {e}')

        print(f'  [internal_linker] {brand}: added {links_added_brand} internal links across {len(html_files)} articles')
        total_links_added += links_added_brand

    return total_links_added


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_seo_content_machine():
    print('=== SEO Content Machine starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = get_anthropic_client()

    # Step 1: Find keyword gaps
    keyword_gaps = gsc_researcher_agent(db, client)

    # Step 2: Write articles (parallel by brand)
    written_articles = article_writer_agent(keyword_gaps, db, client)

    # Step 3: Inject internal links
    links_added = internal_linker_agent()

    # Update agent_runs
    try:
        db.client.table('agent_runs').upsert({
            'agent_name': 'seo_content_machine',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }, on_conflict='agent_name').execute()
    except Exception:
        pass

    print('\n=== SEO Content Machine Summary ===')
    print(f'  Articles written: {len(written_articles)}')
    for a in written_articles:
        print(f'    {a["brand"]}: {a["title"]}')
    print(f'  Internal links added: {links_added}')
    print('=== Done ===')

    return written_articles


if __name__ == '__main__':
    run_seo_content_machine()
```

### seo-content-machine.yml

```yaml
name: SEO Content Machine

on:
  schedule:
    - cron: '0 16 * * 1,3,5'  # Mon/Wed/Fri 8AM PST
  workflow_dispatch:

permissions:
  contents: write

env:
  PYTHON_VERSION: '3.11'

jobs:
  seo-content-machine:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - run: pip install -r requirements.txt

      - name: Run SEO Content Machine
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python3 video_automation/seo_content_machine.py

      - name: Commit and push new articles
        run: |
          git config user.name "SEO Content Machine"
          git config user.email "bot@fitover35.com"
          git add outputs/
          git diff --staged --quiet && echo "No new articles" || (
            git commit -m "content: SEO content machine — new articles + internal links $(date -u +%Y-%m-%d)"
            git push
          )
```

---

## Track 2e: Enhance system-health.yml — Revenue Watchdog

**Files:**
- Modify: `.github/workflows/system-health.yml`

### What to add to the self-heal job

After Phase 7b (Storage Cleanup), add 3 new phases to the inline Python:

**Phase 9: Affiliate Link Validation**
```python
# ── Phase 9: Affiliate Link Validation ──
print('\n=== Phase 9: Affiliate Link Validation ===')
try:
    import json as _json
    with open('monetization/affiliate_config.json') as f:
        aff_config = _json.load(f)
    broken_links = []
    for brand, brand_data in aff_config.items():
        for category in brand_data.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict) and 'url' in item:
                        url = item['url']
                        if url and not url.startswith('PLACEHOLDER'):
                            try:
                                resp = requests.get(url, timeout=8, allow_redirects=True,
                                                    headers={'User-Agent': 'Mozilla/5.0'})
                                if resp.status_code >= 400:
                                    broken_links.append(f'{brand}/{item.get("name","")}: HTTP {resp.status_code}')
                            except Exception as link_e:
                                broken_links.append(f'{brand}/{item.get("name","")}: {link_e}')
    if broken_links:
        print(f'  BROKEN affiliate links ({len(broken_links)}):')
        for b in broken_links:
            print(f'    - {b}')
        unresolvable.extend([f'Broken affiliate link: {b}' for b in broken_links])
    else:
        print(f'  All affiliate links valid')
        healed += 1
except Exception as e:
    print(f'  Affiliate validation: {e}')
```

**Phase 10: Revenue Zero Alert**
```python
# ── Phase 10: Revenue Zero Alert ──
print('\n=== Phase 10: Revenue Zero Alert ===')
try:
    from datetime import timedelta as _td
    cutoff_48h = (datetime.now(timezone.utc) - _td(hours=48)).isoformat()
    recent_pins = db.client.table('pinterest_pins').select('id').gte(
        'created_at', cutoff_48h
    ).execute()
    pin_count = len(recent_pins.data) if recent_pins.data else 0
    if pin_count == 0:
        msg = 'No pins posted in last 48 hours — content engine may be failing'
        print(f'  WARNING: {msg}')
        unresolvable.append(msg)
    else:
        print(f'  {pin_count} pins posted in last 48h — pipeline active')
        healed += 1
except Exception as e:
    print(f'  Revenue zero check: {e}')
```

**Phase 11: Make.com Scenario Health**
```python
# ── Phase 11: Make.com Scenario Health ──
print('\n=== Phase 11: Make.com Scenario Health ===')
webhook_brands = {
    'fitness': os.environ.get('MAKE_WEBHOOK_FITNESS', ''),
    'deals': os.environ.get('MAKE_WEBHOOK_DEALS', ''),
    'menopause': os.environ.get('MAKE_WEBHOOK_MENOPAUSE', ''),
}
for brand_name, webhook_url in webhook_brands.items():
    if not webhook_url:
        print(f'  {brand_name}: webhook not configured')
        continue
    try:
        # Ping with empty payload to verify webhook is alive (Make.com returns 200 even for invalid payloads)
        resp = requests.post(webhook_url, json={'_health_check': True}, timeout=10)
        if resp.status_code < 400:
            print(f'  {brand_name}: webhook OK ({resp.status_code})')
            healed += 1
        else:
            msg = f'Make.com webhook for {brand_name} returned HTTP {resp.status_code}'
            print(f'  WARNING: {msg}')
            unresolvable.append(msg)
    except Exception as e:
        print(f'  {brand_name} webhook check failed: {e}')
```

Also add these env vars to the self-heal step in the YAML:
```yaml
MAKE_WEBHOOK_FITNESS: ${{ secrets.MAKE_WEBHOOK_FITNESS }}
MAKE_WEBHOOK_DEALS: ${{ secrets.MAKE_WEBHOOK_DEALS }}
MAKE_WEBHOOK_MENOPAUSE: ${{ secrets.MAKE_WEBHOOK_MENOPAUSE }}
CONVERTKIT_API_KEY: ${{ secrets.CONVERTKIT_API_KEY }}
```
