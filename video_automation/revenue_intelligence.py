"""Revenue Intelligence Engine — Team 1 of 4 autonomous agent teams.

Runs daily at 6AM PST via revenue-intelligence.yml GitHub Action.
Reads content + affiliate performance data → scores content by revenue potential
→ updates weekly_calendar in Supabase so Content Engine automatically pivots
toward topics that earn money.

Self-improving loop:
  Content Engine reads weekly_calendar (5x/day)
  → makes pins about top-earning topics
  → revenue intelligence reads performance next day
  → updates calendar again
  → system continuously optimizes toward revenue

Agents (run in parallel via ThreadPoolExecutor):
  1. analytics_reader   — pulls content_performance, content_history, generated_articles
  2. performance_analyzer — Claude scores each brand's content by revenue potential
  3. strategy_updater   — rewrites weekly_calendar toward top-earning topics
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
    'fitness': "men's fitness over 35 — supplements, strength training, weight loss, testosterone",
    'deals': "budget home & lifestyle — kitchen gadgets, organization, beauty deals",
    'menopause': "menopause wellness — hot flashes, sleep, supplements, mood, weight gain",
}


def _get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


# ─── Agent 1: Analytics Reader ───────────────────────────────────────────────

def analytics_reader_agent(db):
    """Pull all available performance data from Supabase for all brands."""
    print('[analytics_reader] Reading performance data...')
    data = {}

    for brand in BRANDS:
        brand_data = {}

        # Recent generated articles (last 30)
        try:
            arts = db.client.table('generated_articles').select(
                'slug, article_title, brand, created_at'
            ).eq('brand', brand).order('created_at', desc=True).limit(30).execute()
            brand_data['recent_articles'] = arts.data or []
        except Exception as e:
            brand_data['recent_articles'] = []
            print(f'  [analytics_reader] articles error for {brand}: {e}')

        # Revenue-scored content (if table populated)
        try:
            perf = db.client.table('content_performance').select('*').eq(
                'brand', brand
            ).order('revenue_score', desc=True).limit(10).execute()
            brand_data['top_performers'] = perf.data or []
        except Exception:
            brand_data['top_performers'] = []

        # Recent pin topics (last 14 days)
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
        print(
            f'  [analytics_reader] {brand}: '
            f'{len(brand_data["recent_articles"])} articles, '
            f'{len(brand_data["recent_topics"])} recent topics, '
            f'{len(brand_data["affiliate_programs"])} affiliate programs'
        )

    return data


# ─── Agent 2: Performance Analyzer ──────────────────────────────────────────

def performance_analyzer_agent(analytics_data, client):
    """Use Claude to identify top revenue opportunities per brand."""
    print('[performance_analyzer] Analyzing revenue opportunities (parallel across brands)...')
    results = {}

    def _analyze_brand(brand):
        data = analytics_data[brand]
        recent_topics = [
            t.get('trending_topic', '')
            for t in data['recent_topics']
            if t.get('trending_topic')
        ]
        recent_articles = [
            a.get('article_title', '') or a.get('slug', '')
            for a in data['recent_articles']
        ]
        active_programs = [
            p['program_name']
            for p in data['affiliate_programs']
            if p.get('status') == 'active'
        ]
        placeholder_programs = [
            p['program_name']
            for p in data['affiliate_programs']
            if p.get('status') == 'placeholder'
        ]

        prompt = f"""You are a revenue optimization analyst for a Pinterest content business.

Brand: {brand} ({BRAND_NICHES[brand]})

Recent pin topics (last 14 days) — avoid repeating these:
{json.dumps(recent_topics[:15], indent=2)}

Recent articles — avoid duplicating:
{json.dumps(recent_articles[:10], indent=2)}

Active affiliate programs (these earn money): {json.dumps(active_programs)}
Placeholder programs (not yet earning): {json.dumps(placeholder_programs)}

Identify the TOP 5 content clusters that would drive the most affiliate revenue.
For each, suggest specific pin titles with strong buyer intent.
Focus on topics where the audience is ready to buy, not just browse.

Return JSON only — no commentary:
{{
  "top_revenue_topics": [
    {{
      "cluster": "topic cluster name (specific, not generic)",
      "buyer_intent": "high",
      "suggested_titles": ["title 1", "title 2", "title 3"],
      "affiliate_fit": "which active program this monetizes"
    }}
  ],
  "content_gaps": ["3 specific topics with buyer intent not yet covered"],
  "priority_action": "single most impactful revenue action for this brand right now"
}}"""

        try:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=1500,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = response.content[0].text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            result = json.loads(text)
            return brand, result
        except Exception as e:
            print(f'  [performance_analyzer] {brand} failed: {e}')
            return brand, {
                'top_revenue_topics': [],
                'content_gaps': [],
                'priority_action': f'Analysis failed: {e}'
            }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_analyze_brand, b): b for b in BRANDS}
        for future in as_completed(futures):
            brand, result = future.result()
            results[brand] = result
            n_topics = len(result.get('top_revenue_topics', []))
            print(f'  [performance_analyzer] {brand}: {n_topics} revenue topics identified')

    return results


# ─── Agent 3: Strategy Updater ───────────────────────────────────────────────

def strategy_updater_agent(analysis_results, db):
    """Rewrite next week's content calendar toward top-revenue topics."""
    print('[strategy_updater] Updating content calendar with revenue-optimized topics...')

    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=today.weekday())
    next_week_start = week_start + timedelta(weeks=1)
    total_updated = 0

    for brand in BRANDS:
        analysis = analysis_results.get(brand, {})
        top_topics = analysis.get('top_revenue_topics', [])
        if not top_topics:
            print(f'  [strategy_updater] {brand}: no topics to update')
            continue

        # Map top topics to next 5 weekdays
        for day_offset, topic_cluster in enumerate(top_topics[:5]):
            titles = topic_cluster.get('suggested_titles', [])
            if not titles:
                continue
            scheduled_date = (next_week_start + timedelta(days=day_offset)).isoformat()
            try:
                db.client.table('weekly_calendar').upsert({
                    'brand': brand,
                    'scheduled_date': scheduled_date,
                    'topic': topic_cluster['cluster'],
                    'suggested_title': titles[0],
                    'notes': json.dumps({
                        'buyer_intent': topic_cluster.get('buyer_intent', 'medium'),
                        'affiliate_fit': topic_cluster.get('affiliate_fit', ''),
                        'all_titles': titles,
                        'source': 'revenue_intelligence',
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }),
                    'status': 'pending'
                }, on_conflict='brand,scheduled_date').execute()
                total_updated += 1
            except Exception as e:
                print(f'  [strategy_updater] upsert failed {brand}/{scheduled_date}: {e}')

        print(f'  [strategy_updater] {brand}: {min(len(top_topics), 5)} calendar entries updated for next week')

    return total_updated


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_revenue_intelligence():
    print('=== Revenue Intelligence Engine starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = _get_anthropic_client()

    # Step 1: Read analytics (sequential — must complete before analysis)
    analytics_data = analytics_reader_agent(db)

    # Step 2: Analyze all brands in parallel via Claude
    analysis_results = performance_analyzer_agent(analytics_data, client)

    # Step 3: Update calendar with revenue-optimized topics
    updates = strategy_updater_agent(analysis_results, db)

    # Step 4: Log the run
    try:
        db.client.table('agent_runs').upsert({
            'agent_name': 'revenue_intelligence',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }, on_conflict='agent_name').execute()
    except Exception as e:
        print(f'  [agent_runs] log failed: {e}')

    # Step 5: Store full analysis for review/debugging
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

    # Summary
    print('\n=== Revenue Intelligence Summary ===')
    for brand in BRANDS:
        result = analysis_results.get(brand, {})
        print(f'  {brand}:')
        for topic in result.get('top_revenue_topics', [])[:3]:
            print(f'    - {topic.get("cluster")} [{topic.get("buyer_intent")} intent]')
        priority = result.get('priority_action', '')
        if priority:
            print(f'    Priority: {priority}')
    print(f'\n  Calendar entries updated: {updates}')
    print('=== Done ===')


if __name__ == '__main__':
    run_revenue_intelligence()
