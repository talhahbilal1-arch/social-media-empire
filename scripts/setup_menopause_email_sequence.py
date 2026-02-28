#!/usr/bin/env python3
"""
Set up ConvertKit email sequence for Menopause Planner lead magnet.

Sequence: "Menopause Symptom Tracker Welcome"
  Email 1 (Day 0): Welcome + PDF download link
  Email 2 (Day 1): How to use your tracker + sugar trigger tip
  Email 3 (Day 3): The sleep-sugar connection
  Email 4 (Day 5): When to see your doctor + prep worksheet
  Email 5 (Day 7): Full planner bundle offer (Etsy upsell)

After sequence: subscriber stays on newsletter for weekly tips.

Requires: CONVERTKIT_API_KEY and CONVERTKIT_API_SECRET env vars.
"""
import os
import sys
import json
import requests

API_KEY = os.environ.get('CONVERTKIT_API_KEY', '')
API_SECRET = os.environ.get('CONVERTKIT_API_SECRET', '')
BASE_URL = 'https://api.convertkit.com/v3'
FORM_ID = '9144859'

PDF_URL = 'https://menopause-planner-website.vercel.app/menopause-symptom-tracker.pdf'
ETSY_URL = 'https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle'
SITE_URL = 'https://menopause-planner-website.vercel.app'


# ── Email Content ─────────────────────────────────
SEQUENCE_EMAILS = [
    {
        "subject": "Your Free Menopause Symptom Tracker is here! 📋",
        "delay_days": 0,
        "content": f"""
<p>Hi {{{{ subscriber.first_name | default: "there" }}}},</p>

<p>Welcome to The Menopause Planner community! You've just joined over 2,400 women who are taking control of their menopause journey.</p>

<p><strong>Here's your free tracker:</strong></p>

<p style="text-align:center;margin:24px 0;">
  <a href="{PDF_URL}" style="display:inline-block;padding:14px 32px;background-color:#7c9a82;color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;font-size:16px;">
    Download Your Symptom Tracker (PDF)
  </a>
</p>

<p><strong>What's inside your 27-page tracker:</strong></p>
<ul>
  <li>Baseline symptom assessment checklist</li>
  <li>4 weeks of daily symptom tracking sheets</li>
  <li>Food &amp; sugar trigger logs</li>
  <li>Sleep quality tracker</li>
  <li>Doctor visit prep worksheet</li>
  <li>Monthly patterns summary</li>
</ul>

<p><strong>Quick start tip:</strong> Print the tracker tonight and fill in your baseline assessment before bed. This gives you a starting snapshot to compare against in 30 days.</p>

<p>Over the next week, I'll send you some specific tips on how to get the most from your tracker -- including the surprising connection between sugar and hot flashes.</p>

<p>You've got this.<br>
The Menopause Planner Team</p>

<p style="font-size:12px;color:#6b7280;">P.S. Save this email -- you can re-download your tracker anytime from the link above.</p>
"""
    },
    {
        "subject": "Day 1: The #1 thing to track first (it's not what you think)",
        "delay_days": 1,
        "content": f"""
<p>Hi {{{{ subscriber.first_name | default: "there" }}}},</p>

<p>You downloaded your Menopause Symptom Tracker yesterday -- nice work! Now let me share the most valuable insight from our community of 2,400+ women:</p>

<p><strong>The #1 thing to track first isn't your hot flashes. It's your sugar intake.</strong></p>

<p>Here's why: Research shows that blood sugar spikes can trigger hot flashes within 2-4 hours. That means your 3pm cookie could be causing your 7pm hot flash.</p>

<p><strong>Today's action step:</strong></p>
<ol>
  <li>Open your tracker to the <em>Food &amp; Sugar Trigger Log</em> page</li>
  <li>Write down everything you eat today -- especially anything sweet</li>
  <li>In the "Symptom After" column, note any symptoms within 4-8 hours</li>
</ol>

<p>Most women discover a clear pattern within just 3-5 days. Some women cut their hot flash frequency in half simply by changing <em>when</em> they eat sugar (mornings are less disruptive than afternoons).</p>

<p><strong>Hidden sugar sources to watch for:</strong> Flavored yogurt, granola bars, pasta sauce, salad dressing, "healthy" cereals, oat milk, and that afternoon coffee with syrup.</p>

<p>Tomorrow we'll dig deeper into why this happens -- and what you can do about it.</p>

<p>Keep tracking!<br>
The Menopause Planner Team</p>
"""
    },
    {
        "subject": "Why you wake up at 2am (and what sugar has to do with it)",
        "delay_days": 3,
        "content": f"""
<p>Hi {{{{ subscriber.first_name | default: "there" }}}},</p>

<p>If you've been tracking for a few days, you might already be seeing patterns. One of the most common revelations:</p>

<p><strong>The sugar-sleep connection.</strong></p>

<p>Here's the science in plain English:</p>

<ol>
  <li><strong>Evening sugar spike</strong> -- You eat something sweet after dinner</li>
  <li><strong>Insulin surge</strong> -- Your body floods with insulin to process it</li>
  <li><strong>Blood sugar crash</strong> -- Around 2-3am, your blood sugar drops too low</li>
  <li><strong>Cortisol spike</strong> -- Your body releases cortisol (stress hormone) to compensate</li>
  <li><strong>Wide awake at 2am</strong> -- That cortisol jolt wakes you up, heart racing</li>
</ol>

<p>During menopause, your insulin sensitivity is already declining. Sugar amplifies this cascade dramatically.</p>

<p><strong>This week's tracker challenge:</strong></p>
<p>Compare your <em>Sleep Quality Tracker</em> scores against your <em>Food Log</em>. Do your worst sleep nights correspond with higher sugar days?</p>

<p><strong>3 quick wins for better sleep:</strong></p>
<ul>
  <li>No sugar or refined carbs within 4 hours of bedtime</li>
  <li>A small protein snack at 8pm (a few almonds, cheese) stabilizes blood sugar overnight</li>
  <li>Magnesium glycinate before bed (400mg) -- it helps both sleep AND blood sugar regulation</li>
</ul>

<p>Check out our article on <a href="{SITE_URL}/articles/magnesium-glycinate-sleep-protocol-for-menopause">magnesium glycinate for menopause sleep</a> for the full protocol.</p>

<p>Sweet dreams (no pun intended),<br>
The Menopause Planner Team</p>
"""
    },
    {
        "subject": "Bring this to your doctor (they'll be impressed)",
        "delay_days": 5,
        "content": f"""
<p>Hi {{{{ subscriber.first_name | default: "there" }}}},</p>

<p>By now you've been tracking for almost a week. You might have data on 5-7 days of symptoms, food triggers, and sleep patterns. Here's something powerful you can do with that data:</p>

<p><strong>Bring your tracker to your next doctor's appointment.</strong></p>

<p>Most women walk into their doctor's office and say something like "I've been having hot flashes and not sleeping well." That's vague and hard for a doctor to act on.</p>

<p>But imagine saying: "I tracked my symptoms for 4 weeks. My hot flashes average 3.5/5 severity, spike on days I eat sugar after 2pm, and my worst sleep nights correlate with evening carbs. Here's the data."</p>

<p><strong>That changes the entire conversation.</strong></p>

<p>Your tracker includes a <em>Doctor Visit Prep Worksheet</em> with:</p>
<ul>
  <li>Space for your top 3 concerns</li>
  <li>Current medications and supplements list</li>
  <li>Questions to ask (including ones you might not think of)</li>
  <li>A symptom summary section to fill from your tracking data</li>
</ul>

<p><strong>Questions you might not think to ask:</strong></p>
<ul>
  <li>"Could my symptoms be thyroid-related, not just menopause?"</li>
  <li>"Should I get hormone levels tested? Which ones and when?"</li>
  <li>"Is HRT appropriate given my health history?"</li>
</ul>

<p>You deserve a doctor who listens -- and data makes them listen harder.</p>

<p>Keep tracking,<br>
The Menopause Planner Team</p>
"""
    },
    {
        "subject": "Your first week of tracking (what did you discover?)",
        "delay_days": 7,
        "content": f"""
<p>Hi {{{{ subscriber.first_name | default: "there" }}}},</p>

<p>It's been one week since you started tracking. Let's pause and look at the big picture.</p>

<p><strong>Open your tracker and fill in the Week 1 "Pattern Check" box:</strong></p>
<ul>
  <li>What was your worst symptom day?</li>
  <li>What was your best day?</li>
  <li>Can you identify one possible trigger?</li>
</ul>

<p>If you've spotted even one pattern -- congratulations. Most women don't discover these connections for <em>years</em> without structured tracking.</p>

<p><strong>Ready for the complete toolkit?</strong></p>

<p>Your free tracker covers the essentials. But if you want to go deeper, the full <strong>Menopause Wellness Planner Bundle</strong> gives you 34 pages including:</p>

<ul>
  <li>Everything in the free tracker, plus...</li>
  <li>HRT tracking &amp; medication schedules</li>
  <li>Comprehensive nutrition planner</li>
  <li>Exercise &amp; movement tracker</li>
  <li>Mood journal with guided prompts</li>
  <li>Monthly &amp; quarterly review templates</li>
  <li>Digital version for GoodNotes &amp; Notability</li>
</ul>

<p style="text-align:center;margin:24px 0;">
  <a href="{ETSY_URL}" style="display:inline-block;padding:14px 32px;background-color:#c9918f;color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;font-size:16px;">
    Get the Full 34-Page Planner Bundle -- $19.99
  </a>
</p>

<p style="text-align:center;font-size:13px;color:#6b7280;">
  <s>Regular price: $47</s> &nbsp; Save 57% during our launch period
</p>

<p>Whether you stick with the free tracker or upgrade, you're already ahead of most women who suffer in silence. Keep tracking, keep learning, and know you're not alone.</p>

<p>From here, you'll get our weekly newsletter with evidence-based menopause tips, new research, and community insights every Wednesday.</p>

<p>To your health,<br>
The Menopause Planner Team</p>
"""
    },
]


def check_credentials():
    """Verify API credentials work."""
    if not API_KEY or not API_SECRET:
        print("ERROR: Set CONVERTKIT_API_KEY and CONVERTKIT_API_SECRET env vars")
        print("  export CONVERTKIT_API_KEY='your_key'")
        print("  export CONVERTKIT_API_SECRET='your_secret'")
        sys.exit(1)

    resp = requests.get(f"{BASE_URL}/forms", params={"api_key": API_KEY})
    if resp.status_code != 200:
        print(f"ERROR: ConvertKit API returned {resp.status_code}")
        sys.exit(1)

    forms = resp.json().get("forms", [])
    form_ids = [str(f["id"]) for f in forms]
    if FORM_ID not in form_ids:
        print(f"WARNING: Form {FORM_ID} not found in your account.")
        print(f"Available forms: {json.dumps(forms, indent=2)}")
    else:
        print(f"  Form {FORM_ID} found")


def list_existing_sequences():
    """List existing sequences."""
    resp = requests.get(f"{BASE_URL}/sequences", params={"api_key": API_KEY})
    resp.raise_for_status()
    return resp.json().get("courses", [])


def create_sequence():
    """Create the welcome email sequence."""
    # Check if sequence already exists
    sequences = list_existing_sequences()
    for seq in sequences:
        if 'symptom tracker' in seq.get('name', '').lower() or \
           'menopause' in seq.get('name', '').lower():
            print(f"  Existing sequence found: '{seq['name']}' (ID: {seq['id']})")
            return seq['id']

    # Create new sequence
    resp = requests.post(
        f"{BASE_URL}/sequences",
        json={
            "api_secret": API_SECRET,
            "name": "Menopause Symptom Tracker Welcome",
        }
    )
    resp.raise_for_status()
    seq_id = resp.json().get("course", {}).get("id") or resp.json().get("id")
    print(f"  Created sequence: 'Menopause Symptom Tracker Welcome' (ID: {seq_id})")
    return seq_id


def create_tag(name):
    """Create a tag, return its ID."""
    resp = requests.post(
        f"{BASE_URL}/tags",
        json={"api_key": API_KEY, "tag": {"name": name}}
    )
    if resp.status_code == 200:
        return resp.json().get("id")
    # Tag might already exist
    tags_resp = requests.get(f"{BASE_URL}/tags", params={"api_key": API_KEY})
    for tag in tags_resp.json().get("tags", []):
        if tag["name"] == name:
            return tag["id"]
    return None


def setup_form_automation(sequence_id):
    """
    Print instructions for connecting form 5641382 to the sequence.
    (ConvertKit's v3 API doesn't support automation rules programmatically.)
    """
    print("\n" + "=" * 60)
    print("MANUAL STEPS REQUIRED IN CONVERTKIT DASHBOARD")
    print("=" * 60)
    print(f"""
1. GO TO: https://app.convertkit.com/forms/{FORM_ID}/edit
   - Under "Settings" > "After subscribing" > select "Redirect to URL"
   - Enter: https://menopause-planner-website.vercel.app/thank-you
   - Click Save

2. GO TO: https://app.convertkit.com/automations
   - Click "New Automation" > "Visual Automation"
   - Trigger: "Subscribes to form" > select form {FORM_ID}
   - Add Action: "Email sequence" > select "Menopause Symptom Tracker Welcome"
   - Add Action: "Tag subscriber" > select "menopause-tracker-subscriber"
   - Click "Go Live"

3. GO TO: https://app.convertkit.com/sequences
   - Open "Menopause Symptom Tracker Welcome" (ID: {sequence_id})
   - Add 5 emails with the content shown below
   - Set the delay between emails as indicated

4. WEEKLY NEWSLETTER:
   - After the sequence completes (Day 7), subscribers stay on your list
   - Use ConvertKit Broadcasts to send weekly tips every Wednesday
   - OR create a recurring automation that sends a new broadcast weekly
""")


def print_email_content():
    """Print email content for manual entry into ConvertKit."""
    print("\n" + "=" * 60)
    print("EMAIL SEQUENCE CONTENT")
    print("=" * 60)

    for i, email in enumerate(SEQUENCE_EMAILS, 1):
        print(f"\n{'─' * 50}")
        print(f"EMAIL {i} — Send on Day {email['delay_days']}")
        print(f"Subject: {email['subject']}")
        print(f"{'─' * 50}")
        # Strip leading whitespace but preserve HTML
        content = email['content'].strip()
        print(content)
        print()


def main():
    print("Menopause Planner — ConvertKit Email Sequence Setup")
    print("=" * 50)

    print("\n[1/4] Checking credentials...")
    check_credentials()

    print("\n[2/4] Creating/finding sequence...")
    sequence_id = create_sequence()

    print("\n[3/4] Creating subscriber tag...")
    tag_id = create_tag("menopause-tracker-subscriber")
    if tag_id:
        print(f"  Tag 'menopause-tracker-subscriber' ready (ID: {tag_id})")

    print("\n[4/4] Setup instructions...")
    setup_form_automation(sequence_id)
    print_email_content()

    print("\n" + "=" * 50)
    print("DONE! Follow the manual steps above in ConvertKit.")
    print("=" * 50)


if __name__ == '__main__':
    main()
