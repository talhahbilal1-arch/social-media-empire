"""Revenue Activation Team — Team 2 of 4 autonomous agent teams.

Runs weekly Monday 9AM PST via revenue-activation.yml GitHub Action.
Activates email sequences in ConvertKit, discovers real affiliate programs
to replace placeholders, validates all affiliate links, and generates a
weekly revenue status report.

Revenue lever priority:
  1. Email sequences — written but NOT live (biggest immediate revenue unlock)
  2. Affiliate program discovery — 70% are placeholders earning $0
  3. Link validation — broken links = lost commissions every day

Agents (run in parallel via ThreadPoolExecutor):
  1. email_activator     — checks ConvertKit sequences; reports which need activation
  2. affiliate_discoverer — finds real programs via Claude to replace placeholders
  3. affiliate_validator  — HTTP-checks all affiliate URLs, logs broken ones
  4. revenue_reporter    — synthesizes results → weekly report → Supabase
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
    'fitness': "men's fitness over 35 — supplements, workouts, weight loss",
    'deals': "budget home & lifestyle — kitchen gadgets, organization, beauty",
    'menopause': "menopause wellness — supplements, sleep, mood, hot flashes",
}


def _get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


# ─── Agent 1: Email Activator ────────────────────────────────────────────────

def email_activator_agent():
    """Check ConvertKit for active email sequences; report what needs action."""
    print('[email_activator] Checking ConvertKit email sequences...')

    ck_key = os.environ.get('CONVERTKIT_API_KEY', '')
    ck_secret = os.environ.get('CONVERTKIT_API_SECRET', '')

    if not ck_key:
        print('  [email_activator] CONVERTKIT_API_KEY not configured')
        return {
            'status': 'not_configured',
            'action_needed': [
                'Set CONVERTKIT_API_KEY and CONVERTKIT_API_SECRET in GitHub Secrets',
                'Written sequences are in email_marketing/sequences/ — upload to ConvertKit'
            ],
            'sequences': {}
        }

    try:
        resp = requests.get(
            'https://api.convertkit.com/v3/sequences',
            params={'api_secret': ck_secret},
            timeout=15
        )
        if resp.status_code != 200:
            return {
                'status': 'api_error',
                'error': f'HTTP {resp.status_code}: {resp.text[:200]}',
                'sequences': {}
            }

        sequences = resp.json().get('courses', [])
        print(f'  [email_activator] Found {len(sequences)} sequences in ConvertKit')

        # Match sequences to brands
        brand_sequences = {}
        brand_keywords = {'fitness': 'fit', 'deals': 'deal', 'menopause': 'menopause'}
        for seq in sequences:
            name_lower = seq.get('name', '').lower()
            for brand, keyword in brand_keywords.items():
                if keyword in name_lower:
                    brand_sequences[brand] = {
                        'id': seq['id'],
                        'name': seq['name'],
                        'active': seq.get('active', False),
                        'subscriber_count': seq.get('subscriber_count', 0)
                    }

        missing = [b for b in BRANDS if b not in brand_sequences]
        inactive = [b for b, s in brand_sequences.items() if not s.get('active')]

        action_needed = []
        if missing:
            action_needed.append(
                f'Create sequences for brands: {", ".join(missing)}. '
                f'Content is ready in email_marketing/sequences/'
            )
        if inactive:
            action_needed.append(
                f'Activate sequences for: {", ".join(inactive)} in ConvertKit dashboard'
            )

        for brand, seq_data in brand_sequences.items():
            status_str = 'ACTIVE' if seq_data['active'] else 'INACTIVE'
            print(
                f'  [email_activator] {brand}: {status_str} '
                f'({seq_data["subscriber_count"]} subscribers)'
            )

        return {
            'status': 'checked',
            'sequences': brand_sequences,
            'missing_brands': missing,
            'inactive_sequences': inactive,
            'action_needed': action_needed
        }

    except Exception as e:
        print(f'  [email_activator] Error: {e}')
        return {'status': 'error', 'error': str(e), 'sequences': {}}


# ─── Agent 2: Affiliate Discoverer ──────────────────────────────────────────

def affiliate_discoverer_agent(db, client):
    """Use Claude to find real affiliate programs to replace placeholders."""
    print('[affiliate_discoverer] Discovering real affiliate programs...')
    results = {}

    for brand in BRANDS:
        # Get current placeholder programs
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

        placeholder_names = [p['program_name'] for p in placeholder_list]

        prompt = f"""You are an affiliate marketing expert. For a content site in the {BRAND_NICHES[brand]} niche,
identify the BEST real affiliate programs to replace these placeholders:

{json.dumps(placeholder_names, indent=2)}

Requirements:
- Programs must actually exist and accept publishers
- Prefer programs with >10% commission or >$20/sale
- Must be relevant to the niche
- Provide exact signup URLs

Return JSON only:
{{
  "recommendations": [
    {{
      "replaces": "exact placeholder name from the list",
      "real_program_name": "actual program name",
      "network": "ShareASale / ClickBank / Impact / Direct",
      "signup_url": "exact URL to sign up as affiliate",
      "commission": "X% per sale or $X per lead",
      "why_it_fits": "one sentence reason"
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
            recommendations = recs.get('recommendations', [])

            # Save discoveries to DB
            for rec in recommendations:
                try:
                    db.client.table('affiliate_programs').upsert({
                        'brand': brand,
                        'program_name': rec['real_program_name'],
                        'network': rec.get('network', ''),
                        'signup_url': rec.get('signup_url', ''),
                        'commission_rate': rec.get('commission', ''),
                        'status': 'discovered',
                        'notes': (
                            f"Replaces: {rec.get('replaces', '')} | "
                            f"{rec.get('why_it_fits', '')}"
                        )
                    }, on_conflict='brand,program_name').execute()
                except Exception as e:
                    print(f'  [affiliate_discoverer] DB upsert failed: {e}')

            results[brand] = {'status': 'success', 'recommendations': recommendations}
            print(
                f'  [affiliate_discoverer] {brand}: '
                f'{len(recommendations)} programs discovered and saved to DB'
            )

        except Exception as e:
            print(f'  [affiliate_discoverer] {brand} failed: {e}')
            results[brand] = {'status': 'error', 'error': str(e)}

    return results


# ─── Agent 3: Affiliate Validator ────────────────────────────────────────────

def affiliate_validator_agent(db):
    """HTTP-check all non-placeholder affiliate URLs. Log broken ones."""
    print('[affiliate_validator] Validating affiliate URLs...')

    config_path = 'monetization/affiliate_config.json'
    urls_to_check = []

    try:
        with open(config_path) as f:
            config = json.load(f)
        for brand, brand_data in config.items():
            for category_key, category_val in brand_data.items():
                if not isinstance(category_val, list):
                    continue
                for item in category_val:
                    if not isinstance(item, dict):
                        continue
                    url = item.get('url', '')
                    if url and not url.startswith('PLACEHOLDER'):
                        urls_to_check.append({
                            'brand': brand,
                            'name': item.get('name', category_key),
                            'url': url
                        })
    except Exception as e:
        print(f'  [affiliate_validator] Config load failed: {e}')

    results = {'valid': [], 'broken': [], 'checked': 0}

    def _check(item):
        try:
            r = requests.get(
                item['url'], timeout=10, allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return item, r.status_code < 400
        except Exception:
            return item, False

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_check, item): item for item in urls_to_check}
        for future in as_completed(futures):
            item, valid = future.result()
            results['checked'] += 1
            if valid:
                results['valid'].append(item['name'])
            else:
                results['broken'].append(item)
                print(f'  [affiliate_validator] BROKEN: {item["name"]}')
                try:
                    db.client.table('errors').insert({
                        'error_type': 'broken_affiliate_link',
                        'error_message': f'Affiliate link not reachable: {item["url"]}',
                        'context': json.dumps({'brand': item['brand'], 'program': item['name']}),
                        'severity': 'high',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }).execute()
                except Exception:
                    pass

    print(
        f'  [affiliate_validator] Checked {results["checked"]} URLs: '
        f'{len(results["valid"])} valid, {len(results["broken"])} broken'
    )
    return results


# ─── Agent 4: Revenue Reporter ───────────────────────────────────────────────

def revenue_reporter_agent(db, email_result, affiliate_result, validation_result):
    """Generate weekly revenue status report and log to Supabase."""
    print('[revenue_reporter] Generating weekly revenue report...')

    # Tally program statuses
    totals = {'placeholder': 0, 'discovered': 0, 'applied': 0, 'active': 0}
    try:
        all_progs = db.client.table('affiliate_programs').select('status').execute()
        for p in (all_progs.data or []):
            s = p.get('status', 'placeholder')
            if s in totals:
                totals[s] += 1
    except Exception:
        pass

    # Build action items
    action_items = []
    if email_result.get('missing_brands'):
        action_items.append(
            f'EMAIL: Create ConvertKit sequences for {", ".join(email_result["missing_brands"])} '
            f'(content ready in email_marketing/sequences/)'
        )
    if email_result.get('inactive_sequences'):
        action_items.append(
            f'EMAIL: Activate sequences for {", ".join(email_result["inactive_sequences"])} in ConvertKit'
        )
    if totals['placeholder'] > 0:
        action_items.append(
            f'AFFILIATES: {totals["placeholder"]} placeholder programs need sign-up '
            f'(check affiliate_programs table for signup_url)'
        )
    if totals['discovered'] > 0:
        action_items.append(
            f'AFFILIATES: {totals["discovered"]} newly discovered programs — '
            f'review in affiliate_programs table and sign up'
        )
    if validation_result.get('broken'):
        broken_names = [b['name'] for b in validation_result['broken']]
        action_items.append(
            f'LINKS: {len(broken_names)} broken affiliate links: {", ".join(broken_names)}'
        )

    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'email_sequences': {
            'status': email_result.get('status'),
            'sequences_found': len(email_result.get('sequences', {})),
            'missing_brands': email_result.get('missing_brands', []),
            'inactive': email_result.get('inactive_sequences', [])
        },
        'affiliate_programs': totals,
        'newly_discovered': {
            b: len(r.get('recommendations', []))
            for b, r in affiliate_result.items()
        },
        'link_validation': {
            'checked': validation_result.get('checked', 0),
            'broken_count': len(validation_result.get('broken', []))
        },
        'action_items': action_items
    }

    # Persist report
    try:
        db.client.table('analytics').insert({
            'event_type': 'revenue_activation_run',
            'brand': 'all',
            'platform': 'system',
            'data': report
        }).execute()
    except Exception as e:
        print(f'  [revenue_reporter] Log failed: {e}')

    # Print summary
    print('\n=== Weekly Revenue Report ===')
    print(f'  Email sequences: {email_result.get("status", "unknown")}')
    print(f'  Active affiliate programs: {totals["active"]}')
    print(f'  Discovered (pending sign-up): {totals["discovered"]}')
    print(f'  Still placeholder: {totals["placeholder"]}')
    print(f'  Broken links: {len(validation_result.get("broken", []))}')
    if action_items:
        print('\n  Action Items (manual sign-ups required):')
        for item in action_items:
            print(f'    → {item}')

    return report


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_revenue_activation():
    print('=== Revenue Activation Team starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = _get_anthropic_client()

    # Run first 3 agents in parallel — they're independent
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_email = executor.submit(email_activator_agent)
        f_affiliate = executor.submit(affiliate_discoverer_agent, db, client)
        f_validate = executor.submit(affiliate_validator_agent, db)

        email_result = f_email.result()
        affiliate_result = f_affiliate.result()
        validation_result = f_validate.result()

    # Revenue reporter synthesizes all results
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
