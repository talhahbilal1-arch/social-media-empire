"""7-email welcome sequence for FitOver35 subscribers.

Sequence schedule:
  Email 1: Immediate — Lead magnet delivery + welcome
  Email 2: Day 2 — Quick win workout
  Email 3: Day 4 — Nutrition fundamentals
  Email 4: Day 7 — Recovery protocols (affiliate: foam roller, bands)
  Email 5: Day 9 — Mindset / identity shift
  Email 6: Day 12 — Product pitch (7-Day Fat Burn Challenge)
  Email 7: Day 14 — Final value + community invite

Each email includes:
- Plain text and HTML versions
- Affiliate product recommendations where natural
- Links back to website articles
- Clear single CTA
"""

WELCOME_SEQUENCE = [
    {
        "email_number": 1,
        "delay_days": 0,
        "subject": "Your free guide is inside (+ what to expect)",
        "preview_text": "Here's your 7-Day Fat Loss Kickstart Guide",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p style="font-size: 18px; font-weight: 600;">Welcome to FitOver35.</p>

  <p>Here's your <strong>7-Day Fat Loss Kickstart Guide</strong> as promised:</p>

  <p style="text-align: center; margin: 24px 0;">
    <a href="https://fitover35.com/downloads/7-day-kickstart.pdf" style="background: #5c7cfa; color: white; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; display: inline-block;">Download Your Free Guide</a>
  </p>

  <p>Quick summary of what's inside:</p>
  <ul style="line-height: 1.8;">
    <li>7 daily workouts (30-40 min, no gym needed)</li>
    <li>Simple nutrition framework (no calorie counting)</li>
    <li>Recovery tips between sessions</li>
    <li>Progress tracking sheet</li>
  </ul>

  <p><strong>What to expect from me:</strong></p>
  <p>One email per week with actionable training and nutrition advice. No fluff, no spam, no bro-science. Everything is evidence-based and built for men over 35 whose bodies don't respond like they used to.</p>

  <p>Hit reply if you have any questions. I read every email.</p>

  <p>Let's build something that lasts.</p>
  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;">You're receiving this because you signed up at fitover35.com. <a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Welcome to FitOver35.

Here's your 7-Day Fat Loss Kickstart Guide: https://fitover35.com/downloads/7-day-kickstart.pdf

What's inside:
- 7 daily workouts (30-40 min, no gym needed)
- Simple nutrition framework (no calorie counting)
- Recovery tips between sessions
- Progress tracking sheet

What to expect from me:
One email per week with actionable training and nutrition advice. No fluff, no spam, no bro-science.

Hit reply if you have questions. I read every email.

— FitOver35
"""
    },
    {
        "email_number": 2,
        "delay_days": 2,
        "subject": "Try this 20-minute workout today",
        "preview_text": "No gym needed. Just you and 20 minutes.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>Most guys overcomplicate fitness.</p>

  <p>They think they need an hour in the gym, a perfect diet, and a stack of supplements to see results.</p>

  <p>They don't. Especially not at the start.</p>

  <p><strong>Here's a 20-minute workout you can do right now:</strong></p>

  <div style="background: #f7f7f7; padding: 20px; border-radius: 8px; margin: 16px 0;">
    <p style="font-weight: 600; margin-bottom: 12px;">4 rounds, minimal rest between exercises:</p>
    <ul style="line-height: 2;">
      <li>Goblet Squats x 12</li>
      <li>Push-ups x 15</li>
      <li>Dumbbell Rows x 10/side</li>
      <li>Plank x 30 seconds</li>
    </ul>
    <p style="font-size: 14px; color: #718096;">Rest 60 seconds between rounds. Done in 20 minutes.</p>
  </div>

  <p>This hits every major muscle group. It builds strength and burns calories. And it proves that you don't need hours to make progress.</p>

  <p>Want the complete system? I wrote a full article on time-efficient training:</p>

  <p><a href="https://fitover35.com/articles/time-efficient-training.html" style="color: #5c7cfa; font-weight: 600;">Read: The Time-Efficient Training System for Men Over 35</a></p>

  <p>Tomorrow: consistency. Not motivation.</p>
  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Most guys overcomplicate fitness.

Here's a 20-minute workout you can do right now:

4 rounds, minimal rest:
- Goblet Squats x 12
- Push-ups x 15
- Dumbbell Rows x 10/side
- Plank x 30 seconds
Rest 60 seconds between rounds.

Full article: https://fitover35.com/articles/time-efficient-training.html

— FitOver35
"""
    },
    {
        "email_number": 3,
        "delay_days": 4,
        "subject": "The nutrition rule that changed everything for me",
        "preview_text": "Forget calorie counting. Do this instead.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>I used to overthink nutrition. Tracking macros, weighing food, stressing about meal timing.</p>

  <p>Then I simplified it to one rule:</p>

  <p style="font-size: 20px; font-weight: 700; text-align: center; padding: 20px; background: #f7f7f7; border-radius: 8px; margin: 20px 0;">Protein at every meal. Vegetables at every meal. That's it.</p>

  <p>For men over 35, protein is non-negotiable. Your body needs more of it to maintain and build muscle as testosterone naturally declines. Aim for 0.8-1g per pound of bodyweight.</p>

  <p><strong>Practical application:</strong></p>
  <ul style="line-height: 1.8;">
    <li>Breakfast: Eggs + spinach (30g protein)</li>
    <li>Lunch: Chicken + mixed greens (40g protein)</li>
    <li>Dinner: Salmon + broccoli (35g protein)</li>
    <li>Snack: Protein shake (25g protein)</li>
  </ul>

  <p>That's 130g without trying. Add a quality protein powder and you're at your target.</p>

  <p>Speaking of which — <a href="https://www.amazon.com/dp/B000QSNYGI?tag=fitover35-20" style="color: #5c7cfa; font-weight: 600;">this is the protein powder I use daily</a>. Clean ingredients, good taste, reasonable price.</p>

  <p>Full nutrition deep-dive here: <a href="https://fitover35.com/articles/nutrition-fundamentals.html" style="color: #5c7cfa;">Nutrition Fundamentals for Slowing Metabolisms</a></p>

  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """The nutrition rule that changed everything:

Protein at every meal. Vegetables at every meal. That's it.

Aim for 0.8-1g protein per pound of bodyweight.

Protein powder I use: https://www.amazon.com/dp/B000QSNYGI?tag=fitover35-20

Full article: https://fitover35.com/articles/nutrition-fundamentals.html

— FitOver35
"""
    },
    {
        "email_number": 4,
        "delay_days": 7,
        "subject": "Why recovery matters more after 35 (and what to do about it)",
        "preview_text": "Your 25-year-old self could skip this. You can't.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>At 25, you could train 6 days a week, sleep 5 hours, and eat garbage.</p>
  <p>At 35+, recovery is the thing that separates progress from injury.</p>

  <p><strong>Three non-negotiable recovery habits:</strong></p>

  <div style="background: #f7f7f7; padding: 20px; border-radius: 8px; margin: 16px 0;">
    <p><strong>1. Foam rolling (10 min/day)</strong></p>
    <p style="color: #718096;">Reduces muscle tension, improves mobility, speeds recovery between sessions. I use <a href="https://www.amazon.com/dp/B0040EKZDY?tag=fitover35-20" style="color: #5c7cfa;">this foam roller</a> every single day.</p>

    <p style="margin-top: 16px;"><strong>2. Sleep 7+ hours</strong></p>
    <p style="color: #718096;">Growth hormone peaks during deep sleep. Less than 7 hours = compromised recovery, higher cortisol, more belly fat.</p>

    <p style="margin-top: 16px;"><strong>3. Active recovery days</strong></p>
    <p style="color: #718096;">Walking, light stretching, or band work on off days. <a href="https://www.amazon.com/dp/B08N5J924L?tag=fitover35-20" style="color: #5c7cfa;">A basic resistance band set</a> is all you need.</p>
  </div>

  <p>Recovery isn't laziness. It's where the adaptation happens.</p>

  <p>Deep dive: <a href="https://fitover35.com/articles/recovery-stretching.html" style="color: #5c7cfa; font-weight: 600;">Recovery and Stretching: The Missing Piece for Men 35+</a></p>

  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Recovery matters more after 35.

3 non-negotiable habits:
1. Foam rolling 10 min/day — https://www.amazon.com/dp/B0040EKZDY?tag=fitover35-20
2. Sleep 7+ hours
3. Active recovery days — https://www.amazon.com/dp/B08N5J924L?tag=fitover35-20

Full article: https://fitover35.com/articles/recovery-stretching.html

— FitOver35
"""
    },
    {
        "email_number": 5,
        "delay_days": 9,
        "subject": "The identity shift that makes fitness permanent",
        "preview_text": "Stop trying to get fit. Become someone who trains.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>Most fitness advice focuses on what to do.</p>
  <p>That's not where the real change happens.</p>

  <p>The men who build lasting physiques don't just follow a program. They <strong>become someone who trains.</strong></p>

  <p>There's a difference between:</p>
  <ul style="line-height: 1.8;">
    <li>"I'm trying to get in shape" (behavior)</li>
    <li>"I'm someone who trains" (identity)</li>
  </ul>

  <p>When fitness is part of your identity, you don't need motivation. You train because that's who you are. Just like you brush your teeth — not because you're motivated, but because you're someone who takes care of themselves.</p>

  <p><strong>How to make the shift:</strong></p>
  <ol style="line-height: 2;">
    <li>Show up consistently (even for 20 minutes)</li>
    <li>Track your workouts (proof builds identity)</li>
    <li>Surround yourself with people who train</li>
    <li>Say "I don't skip training" instead of "I should work out"</li>
  </ol>

  <p>This is the most important email in this sequence. Everything else — the workouts, the nutrition, the supplements — only works if you show up.</p>

  <p>Full article: <a href="https://fitover35.com/articles/training-identity.html" style="color: #5c7cfa; font-weight: 600;">Building a Training Identity</a></p>

  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Most fitness advice focuses on what to do. That's not where real change happens.

The shift: Stop "trying to get in shape." Become someone who trains.

How:
1. Show up consistently (even 20 min)
2. Track workouts (proof builds identity)
3. Surround yourself with people who train
4. Say "I don't skip training" instead of "I should work out"

Full article: https://fitover35.com/articles/training-identity.html

— FitOver35
"""
    },
    {
        "email_number": 6,
        "delay_days": 12,
        "subject": "I built something for you",
        "preview_text": "A complete 7-day program. Everything included.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>Over the past couple weeks, I've shared workouts, nutrition advice, recovery protocols, and mindset strategies.</p>

  <p>But I know that piecing it all together yourself takes time you don't have.</p>

  <p>So I put everything into one complete program:</p>

  <div style="background: #f7f7f7; padding: 24px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #5c7cfa;">
    <h3 style="margin-top: 0;">The 7-Day Fat Burn Challenge</h3>
    <p style="color: #718096;">A complete done-for-you program:</p>
    <ul style="line-height: 1.8;">
      <li>7 progressive daily workouts (30-40 min)</li>
      <li>Complete nutrition framework with meal ideas</li>
      <li>Exercise demonstrations for every movement</li>
      <li>Recovery protocols between sessions</li>
      <li>Progress tracking sheet</li>
    </ul>
    <p style="margin-top: 16px;">
      <span style="font-size: 24px; font-weight: 700;">$17</span>
      <span style="color: #a0a0a0; text-decoration: line-through; margin-left: 8px;">$29</span>
      <span style="background: #5c7cfa; color: white; padding: 2px 8px; border-radius: 4px; font-size: 13px; margin-left: 8px;">Launch Price</span>
    </p>
  </div>

  <p style="text-align: center; margin: 24px 0;">
    <a href="https://fitover35.com/products.html" style="background: #5c7cfa; color: white; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; display: inline-block;">Get the 7-Day Challenge</a>
  </p>

  <p>This isn't a 200-page ebook you'll never read. It's a focused, actionable plan you can start tomorrow.</p>

  <p>30-day money-back guarantee. No questions asked.</p>

  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Over the past couple weeks, I've shared workouts, nutrition, recovery, and mindset strategies.

I put it all together into one program: The 7-Day Fat Burn Challenge.

What's included:
- 7 progressive daily workouts (30-40 min)
- Complete nutrition framework
- Exercise demonstrations
- Recovery protocols
- Progress tracking

$17 (launch price, normally $29)

Get it here: https://fitover35.com/products.html

30-day money-back guarantee.

— FitOver35
"""
    },
    {
        "email_number": 7,
        "delay_days": 14,
        "subject": "What comes next",
        "preview_text": "You've got the foundation. Here's how to keep building.",
        "html": """
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; color: #1a1a1a;">
  <p>You've been getting these emails for two weeks now. Here's what you have:</p>

  <ul style="line-height: 2;">
    <li>A complete kickstart guide</li>
    <li>A time-efficient training system</li>
    <li>A simple nutrition framework</li>
    <li>Recovery protocols</li>
    <li>The mindset shift that makes it stick</li>
  </ul>

  <p>That's more than most guys ever get. The question is: <strong>are you going to use it?</strong></p>

  <p><strong>Here's what I recommend:</strong></p>
  <ol style="line-height: 2;">
    <li>Start the kickstart guide this week</li>
    <li>Read one article per week from <a href="https://fitover35.com/blog.html" style="color: #5c7cfa;">the blog</a></li>
    <li>Follow @fitnessmadeasy on Pinterest for daily tips</li>
    <li>Reply to any email with questions — I answer everything</li>
  </ol>

  <p>From here, you'll get my weekly newsletter with new workouts, nutrition strategies, and training insights. Same format: actionable, no fluff.</p>

  <p>If you want the complete done-for-you program, <a href="https://fitover35.com/products.html" style="color: #5c7cfa; font-weight: 600;">check out the 7-Day Fat Burn Challenge</a> ($17).</p>

  <p>Whatever you do — start. The compound interest of consistent training is real, and the best time to start was 10 years ago. The second best time is today.</p>

  <p style="font-weight: 600;">— FitOver35</p>

  <hr style="border: none; border-top: 1px solid #e2e2e2; margin: 32px 0;">
  <p style="font-size: 13px; color: #a0a0a0;"><a href="{{unsubscribe_url}}" style="color: #a0a0a0;">Unsubscribe</a></p>
</div>
""",
        "text": """Two weeks in. Here's what you have:
- Complete kickstart guide
- Time-efficient training system
- Simple nutrition framework
- Recovery protocols
- The mindset shift

What comes next:
1. Start the kickstart guide this week
2. Read one article/week: https://fitover35.com/blog.html
3. Follow @fitnessmadeasy on Pinterest
4. Reply with questions — I answer everything

Weekly newsletter starts next week.

Want the done-for-you program? https://fitover35.com/products.html ($17)

— FitOver35
"""
    },
]


def get_sequence_email(email_number: int) -> dict:
    """Get a specific email from the welcome sequence.

    Args:
        email_number: 1-indexed email number (1-7)

    Returns:
        Email dict with subject, html, text, delay_days
    """
    for email in WELCOME_SEQUENCE:
        if email["email_number"] == email_number:
            return email
    return None


def get_next_email_for_subscriber(current_email: int) -> dict:
    """Get the next email in the sequence.

    Args:
        current_email: The last email number sent (0 if none sent yet)

    Returns:
        Next email dict, or None if sequence is complete
    """
    next_number = current_email + 1
    return get_sequence_email(next_number)
