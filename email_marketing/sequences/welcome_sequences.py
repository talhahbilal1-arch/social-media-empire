"""Email welcome sequences for all brands."""

from dataclasses import dataclass
from typing import Optional

# Email sequence configurations for all brands
EMAIL_SEQUENCES = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "from_name": "Sarah from Daily Deal Darling",
        "from_email": "sarah@dailydealdarling.com",
        "lead_magnet": "The Ultimate Deal Tracker",
        "sequence": [
            {
                "day": 0,
                "subject": "Your Deal Tracker is here! 🎉",
                "preview": "Plus my #1 secret for never paying full price",
                "template": "welcome_delivery",
                "content": """
Hey there, deal hunter! 👋

I'm SO excited you're here! Your Ultimate Deal Tracker is attached to this email - download it now and start saving immediately.

But first, let me share my #1 money-saving secret that most people don't know:

**The 30-Day Price Rule**

Before buying ANYTHING over $30, I add it to my tracker and wait. 90% of the time, it goes on sale within 30 days. This simple habit has saved me over $3,000 this year alone!

Here's how to use your tracker:
1. Download and print (or use digitally)
2. Add items you're eyeing
3. Track prices weekly
4. Buy when it hits your target price

Tomorrow, I'll share my favorite price-tracking tools that do the work FOR you.

Happy saving!
Sarah 💕

P.S. Hit reply and tell me - what's your biggest money-saving goal right now?
""",
                "cta_text": "Download Your Tracker",
                "cta_url": "{{lead_magnet_url}}"
            },
            {
                "day": 1,
                "subject": "The free tools I use to save $500+/month",
                "preview": "These browser extensions changed everything",
                "template": "value_email",
                "content": """
Hey friend!

Yesterday I mentioned price-tracking tools - today I'm spilling ALL my secrets.

**My Must-Have Free Tools:**

1. **Honey** - Automatically applies coupon codes at checkout
2. **CamelCamelCamel** - Tracks Amazon price history
3. **Rakuten** - Cash back on almost everything
4. **RetailMeNot** - Coupon codes for any store

**Pro tip:** Set up price drop alerts on CamelCamelCamel for items on your tracker. You'll get an email the SECOND the price drops!

I use these every single day and they've literally paid for themselves 100x over.

Tomorrow: My secret shopping schedule (hint: there's a BEST day to buy almost everything).

Saving together,
Sarah 💕

P.S. Already use any of these? Reply and let me know your favorite!
""",
                "cta_text": "Follow Me for Daily Deals",
                "cta_url": "{{instagram_url}}"
            },
            {
                "day": 3,
                "subject": "The BEST days to shop (insider secrets)",
                "preview": "Tuesday is for...",
                "template": "value_email",
                "content": """
Okay, this is the email I'm most excited to send you! 🙌

**The Secret Shopping Calendar:**

- **Monday:** Electronics deals (retailers compete with Amazon)
- **Tuesday:** Grocery deals drop (use your tracker!)
- **Wednesday:** Best day for airline tickets
- **Thursday:** Target circle deals refresh
- **Friday:** Avoid shopping (prices often higher)
- **Saturday:** Clearance restocks
- **Sunday:** Meal prep = less impulse food buying

**The BEST times of year:**
- January: White sales (bedding, towels)
- March: Frozen foods
- May: Mattresses
- July: Summer clothes clearance
- November: Everything (but be strategic!)

I've been tracking prices for 5+ years and these patterns are CONSISTENT.

Coming up: How I organize my deals to never miss a sale...

Your deal-finding bestie,
Sarah 💕
""",
                "cta_text": "Get Daily Deal Alerts",
                "cta_url": "{{tiktok_url}}"
            },
            {
                "day": 5,
                "subject": "My simple system for organized savings",
                "preview": "The folder hack that saves me hours",
                "template": "value_email",
                "content": """
Happy [DAY]!

Let's talk organization - because the best deal means nothing if you can't find it when you need it!

**My Deal Organization System:**

📁 **Email Folders:**
- "Active Deals" - Current sales I'm tracking
- "Coupons to Use" - Codes expiring soon
- "Wish List" - Items I'm watching

📱 **Phone Setup:**
- Screenshot folder for deal finds
- Notes app with running wish list
- Browser bookmarks by store

🗓️ **Calendar Alerts:**
- Sale end dates
- Price check reminders
- Coupon expiration dates

The KEY is spending 5 minutes on Sunday setting up your week. I review my tracker, check upcoming sales, and plan my shopping.

This system means I NEVER miss a deal I've been waiting for!

Tomorrow: The psychology of why we overspend (and how to stop) 🧠

Stay organized!
Sarah 💕
""",
                "cta_text": "Watch My Organization Video",
                "cta_url": "{{youtube_url}}"
            },
            {
                "day": 7,
                "subject": "Why we overspend (it's not what you think)",
                "preview": "The psychology stores use against you",
                "template": "value_email",
                "content": """
Time for some real talk... 💭

Stores spend MILLIONS studying how to make us buy more. Here's what they don't want you to know:

**Tricks They Use:**

1. **Anchoring** - Show high price first, then "sale" price looks amazing
2. **Scarcity** - "Only 3 left!" (often fake)
3. **Social proof** - "1,000 people bought this today"
4. **The Gruen Effect** - Store layouts designed to disorient you

**How I Fight Back:**

✓ Always check price history (is it REALLY a deal?)
✓ Sleep on purchases over $50
✓ Shop with a LIST and stick to it
✓ Unsubscribe from tempting emails

The tracker I gave you? It's your DEFENSE against these tricks. When you see the price history, you can't be fooled.

Knowledge is power, friend!

Your savings advocate,
Sarah 💕

P.S. Coming up - my FAVORITE current deals you don't want to miss!
""",
                "cta_text": "Join Our Deal-Finding Community",
                "cta_url": "{{facebook_group_url}}"
            },
            {
                "day": 10,
                "subject": "🔥 This week's deals I'm obsessed with",
                "preview": "I bought 3 of these already...",
                "template": "product_email",
                "content": """
OKAY I had to share these with you immediately! 🏃‍♀️

**This Week's Best Finds:**

1. **[PRODUCT 1]** - Usually $XX, now $XX (XX% off!)
   Perfect for: [use case]
   My take: [personal recommendation]

2. **[PRODUCT 2]** - Price just dropped!
   I've been tracking this for weeks

3. **[PRODUCT 3]** - Back in stock!
   This sells out constantly

**Links to everything:** [LINK]

I personally use/own all of these - I never recommend anything I wouldn't buy myself!

More deals dropping this week on my socials 👀

Happy shopping!
Sarah 💕

P.S. These deals won't last - some expire in 24 hours!
""",
                "cta_text": "Shop These Deals",
                "cta_url": "https://www.amazon.com/shop/dailydealdarling?tag=dailydealdarl-20"
            },
            {
                "day": 14,
                "subject": "What's next on your savings journey?",
                "preview": "Let's make this year YOUR year",
                "template": "conversion_email",
                "content": """
Hey friend!

It's been two weeks since you joined the Daily Deal Darling family, and I hope you've already started saving!

Quick check-in: Have you...
☐ Downloaded and used your Deal Tracker?
☐ Set up at least one price tracking tool?
☐ Followed me for daily deals?

If not, no judgment! Start with ONE thing today.

**Ready for the next level?**

I created something special for serious savers - my complete Deal Mastery System that includes:

✓ Advanced deal-stacking strategies
✓ Store-specific hacks (Target, Amazon, Costco)
✓ Seasonal buying guide
✓ Private community access
✓ Weekly live deal alerts

Check it out here: https://dailydealdarling.com/deal-tracker-pro

Whether you go deeper or just use the free tracker, I'm cheering you on!

Here's to smart shopping,
Sarah 💕

P.S. Reply anytime - I read every email and love hearing your wins!
""",
                "cta_text": "Level Up Your Savings",
                "cta_url": "{{product_url}}"
            }
        ]
    },
    "menopause_planner": {
        "name": "The Menopause Planner",
        "from_name": "Dr. Lisa from The Menopause Planner",
        "from_email": "lisa@themenopauseplanner.com",
        "lead_magnet": "Menopause Symptom Tracker",
        "sequence": [
            {
                "day": 0,
                "subject": "Your Symptom Tracker + a message of hope 💜",
                "preview": "You're not alone in this journey",
                "template": "welcome_delivery",
                "content": """
Dear friend,

First, take a deep breath. You're in the right place. 💜

Your Menopause Symptom Tracker is attached - this simple tool helped me finally understand my body during the most confusing time of my life.

**Why tracking matters:**

When I started perimenopause at 45, I thought I was losing my mind. The brain fog, the mood swings, the 3am wake-ups... sound familiar?

Tracking changed everything. Within 2 weeks, I discovered:
- My worst hot flashes happened after wine (goodbye, nightly glass 😢)
- My anxiety spiked the week before my period
- Exercise in the morning = better sleep that night

Your patterns will be different. But finding them? That's powerful.

**How to use your tracker:**
1. Print it or save to your tablet
2. Track for at least 2 weeks
3. Look for patterns
4. Share with your doctor if needed

Tomorrow, I'll send you my top 5 immediate relief strategies.

You've got this,
Lisa 💜

P.S. You are not crazy. You are not alone. This is temporary. 🤗
""",
                "cta_text": "Download Your Tracker",
                "cta_url": "{{lead_magnet_url}}"
            },
            {
                "day": 1,
                "subject": "5 things that help RIGHT NOW",
                "preview": "#3 works in 60 seconds",
                "template": "value_email",
                "content": """
Hey there,

Hot flash hitting? Anxiety creeping in? Here are my go-to instant relief strategies:

**1. The Cold Water Trick**
Keep ice water by your bed. First sign of a hot flash? Drink it and put the cold glass on your wrists. Works in under a minute.

**2. 4-7-8 Breathing**
Breathe in for 4 counts, hold for 7, out for 8. This activates your parasympathetic nervous system. I do this for anxiety AND to fall back asleep.

**3. Peppermint Oil**
Dab on your temples and neck. The cooling sensation helps with hot flashes AND headaches.

**4. The 5-Minute Walk**
When brain fog hits, a quick walk (even around your house) gets blood flowing to your brain.

**5. Cold Pillowcase**
Keep an extra pillowcase in the freezer. Middle-of-the-night hot flash? Swap it out. Game changer.

None of these are cures, but they make the hard moments easier.

More strategies coming your way!
Lisa 💜

P.S. Which one are you going to try first? Hit reply!
""",
                "cta_text": "More Tips on Instagram",
                "cta_url": "{{instagram_url}}"
            },
            {
                "day": 3,
                "subject": "The foods that made my symptoms WORSE",
                "preview": "I wish someone had told me sooner",
                "template": "value_email",
                "content": """
Can we talk about food? 🍽️

I spent months wondering why some days were SO much worse than others. Then I started tracking what I ate alongside my symptoms.

**My Personal Trigger Foods:**
- Red wine (hot flashes within 2 hours)
- Spicy food (night sweats)
- Too much sugar (mood crashes)
- Caffeine after noon (sleep problems)

**Foods That Actually Help:**
- Flaxseed (natural phytoestrogens)
- Fatty fish (omega-3s for brain fog)
- Leafy greens (magnesium for sleep)
- Fermented foods (gut health = hormone health)

**The Game-Changer:**
I started having a "hormone smoothie" every morning:
- 1 tbsp ground flaxseed
- Handful of spinach
- Berries
- Almond milk
- Scoop of collagen

Within 3 weeks, my hot flashes reduced by about 40%.

Your body is different - that's why tracking is so important!

Nourishing you,
Lisa 💜
""",
                "cta_text": "Get My Hormone Food Guide",
                "cta_url": "{{lead_magnet_2_url}}"
            },
            {
                "day": 5,
                "subject": "What your doctor might not tell you",
                "preview": "Questions to ask at your next appointment",
                "template": "value_email",
                "content": """
Real talk time... 💬

Many women tell me their doctors dismissed their symptoms or didn't take them seriously. This is unfortunately common.

**You deserve to be heard.**

Here's what to bring to your next appointment:

**1. Your completed symptom tracker**
Data is powerful. Doctors respond to specifics.

**2. A list of questions:**
- "What are ALL my treatment options?"
- "What are the risks AND benefits of HRT for someone like me?"
- "Can we test my hormone levels?"
- "Are there specialists you'd recommend?"

**3. Know your options:**
- Hormone Replacement Therapy (HRT)
- Low-dose antidepressants
- Gabapentin for hot flashes
- Lifestyle modifications
- Supplements

**4. Advocate for yourself:**
If you feel dismissed, it's okay to say "I need you to take this seriously" or to find another doctor.

You know your body. Trust yourself.

In your corner,
Lisa 💜

P.S. The North American Menopause Society has a provider directory of menopause specialists.
""",
                "cta_text": "Find a Menopause Specialist",
                "cta_url": "{{nams_url}}"
            },
            {
                "day": 7,
                "subject": "The sleep strategies that finally worked",
                "preview": "From 3am wake-ups to 7 hours straight",
                "template": "value_email",
                "content": """
Sleep. Let's talk about it. 😴

If you're waking up at 3am drenched in sweat, unable to fall back asleep... I've been there. For months.

**What Finally Worked for Me:**

**The Bedroom Setup:**
- Temperature at 65°F (I know, it's cold!)
- Cooling mattress pad
- Moisture-wicking pajamas
- Blackout curtains
- Fan for white noise AND air circulation

**The Evening Routine:**
- No screens 1 hour before bed
- Magnesium glycinate supplement
- Lavender on my pillow
- Light stretching or yoga
- Same bedtime every night (even weekends)

**When I Wake Up:**
- I DON'T check my phone
- 4-7-8 breathing
- Body scan meditation
- If not asleep in 20 min, I read (boring book, dim light)

**Game changers:**
- No caffeine after noon
- No alcohol (this was hard but made the biggest difference)
- Exercise, but not after 4pm

It took about 3 weeks of consistency to see real improvement. Be patient with yourself.

Sweet dreams,
Lisa 💜
""",
                "cta_text": "Watch My Sleep Routine",
                "cta_url": "{{youtube_url}}"
            },
            {
                "day": 10,
                "subject": "Let's talk about the mental side...",
                "preview": "Anxiety, rage, tears - you're not alone",
                "template": "value_email",
                "content": """
Can I be vulnerable with you? 💜

The physical symptoms get all the attention. But the mental and emotional changes? Those blindsided me.

**What I experienced:**
- Anxiety that came out of nowhere
- Rage over small things (then guilt)
- Crying at commercials
- Feeling like I'd lost myself
- Brain fog so bad I forgot words

**What helped:**

1. **Understanding it's hormonal** - Estrogen affects serotonin and dopamine. This isn't a character flaw.

2. **Therapy** - Having someone to talk to who understood was invaluable.

3. **Telling my family** - "I'm going through hormonal changes. I might seem different. I still love you."

4. **Movement** - Even when I didn't want to. Walking, yoga, anything.

5. **Community** - Finding other women going through this. The isolation made everything worse.

**Please hear this:**
You are not going crazy. Your brain is adapting to major hormonal shifts. It gets better.

If you're struggling with depression or anxiety, please talk to someone. There are effective treatments.

With so much compassion,
Lisa 💜

P.S. My DMs are always open if you need to vent. I mean it.
""",
                "cta_text": "Join Our Support Community",
                "cta_url": "{{facebook_group_url}}"
            },
            {
                "day": 14,
                "subject": "What's next for you?",
                "preview": "Taking control of your menopause journey",
                "template": "conversion_email",
                "content": """
Hey friend,

Two weeks ago, you took a brave step by downloading that symptom tracker. How's it going?

**Check-in time:**
- Have you noticed any patterns?
- Tried any of the strategies I shared?
- Talked to your doctor?

Whatever your answer, you're making progress just by paying attention.

**If you're ready for more support...**

I created The Complete Menopause Planner specifically for women who want to take control of this transition:

📔 **What's Inside:**
- 12-month symptom tracking system
- Meal planning for hormone balance
- Sleep optimization protocols
- Doctor appointment prep guides
- Self-care practices
- Monthly reflection pages
- Private community access

This isn't just a planner - it's a companion through this journey.

Check it out here: https://menopauseplanner.com/planner

Whether you continue with the free resources or go deeper, I'm here for you.

This phase of life can actually be empowering. I promise.

With love,
Lisa 💜

P.S. Questions? Just reply to this email. I'm a real person and I read everything!
""",
                "cta_text": "Get The Complete Planner",
                "cta_url": "{{product_url}}"
            }
        ]
    },
    "nurse_planner": {
        "name": "The Nurse Planner",
        "from_name": "Jessica from The Nurse Planner",
        "from_email": "jessica@thenurseplanner.com",
        "lead_magnet": "Ultimate Shift Planner",
        "sequence": [
            {
                "day": 0,
                "subject": "Your Shift Planner is here! 🏥",
                "preview": "From one nurse to another...",
                "template": "welcome_delivery",
                "content": """
Hey nurse friend! 👋

Your Ultimate Shift Planner is attached and ready to help you conquer those crazy schedules!

**A little about me:**
I'm Jessica - 12 years as an ER nurse, now helping fellow nurses thrive (not just survive). I've worked nights, days, rotating shifts... I get it.

**Why I created this planner:**

After my third burnout episode, I realized: no one teaches us how to actually MANAGE this career. We learn to save lives, not protect our own.

This planner includes:
✓ Weekly shift overview
✓ Self-care check-ins (non-negotiable!)
✓ Meal prep planning
✓ Sleep schedule tracker
✓ Wins & gratitude section

**How to use it:**
1. Print your week's pages on Sunday
2. Fill in your shifts first
3. Block self-care BEFORE anything else
4. Prep meals around your schedule
5. Celebrate small wins daily

Tomorrow: My pre-shift ritual that keeps me energized for 12+ hours.

Taking care of those who take care of others,
Jessica 💙

P.S. What unit are you on? Hit reply - I love meeting fellow nurses!
""",
                "cta_text": "Download Your Planner",
                "cta_url": "{{lead_magnet_url}}"
            },
            {
                "day": 1,
                "subject": "My 12-hour shift survival kit",
                "preview": "What's actually in my bag",
                "template": "value_email",
                "content": """
Okay let's talk about what gets me through those brutal shifts! 🎒

**My Non-Negotiable Bag Contents:**

Food & Hydration:
- 64oz water bottle (I aim to finish it)
- Protein-heavy snacks (nuts, cheese, protein bars)
- Real meal in a container (not just snacks!)
- Electrolyte packets

Comfort:
- Extra compression socks (game changer at hour 8)
- Comfortable shoes (I rotate between 2 pairs)
- Lip balm & lotion (hospital air is BRUTAL)
- Small essential oil roller (peppermint for energy)

Sanity:
- Headphones for commute decompression
- Gum/mints
- Hair ties (always losing these)
- Mini notebook for brain dumps

**Pre-Shift Ritual (30 min before leaving):**
1. Eat a real meal with protein
2. 5 minutes of stretching
3. Set my intention for the shift
4. Quick review of my patients (if available)

**Post-Shift Ritual (before bed):**
1. Shower immediately (wash the shift off)
2. Dim lights, no screens
3. Journal 3 good things that happened
4. Legs up the wall for 5 minutes

These small things add up to sustainable shifts.

What's in YOUR bag? Reply and share!
Jessica 💙
""",
                "cta_text": "My Amazon Nurse Essentials",
                "cta_url": "https://www.amazon.com/dp/B07D3N8C8M?tag=dailydealdarl-20"
            },
            {
                "day": 3,
                "subject": "The meal prep that saved my health",
                "preview": "15 minutes on Sunday = a week of real food",
                "template": "value_email",
                "content": """
Let's talk about what we're EATING on shift... 🍱

Hospital cafeteria at 3am? Vending machine dinner? Been there. My body paid for it.

**My Simple Meal Prep System:**

Sunday (15-20 minutes):
- Cook a big batch of protein (chicken, ground turkey, etc.)
- Roast a sheet pan of veggies
- Make a pot of rice or quinoa
- Hard boil eggs

That's it. Then I mix and match all week.

**My Go-To Shift Meals:**
- Protein + veggies + grain in a container
- Mason jar salads (dressing on bottom!)
- Overnight oats for early mornings
- Pre-portioned snack bags

**What I avoid on shift:**
- Super heavy/greasy food (hello, afternoon crash)
- Too much sugar (energy spike then crash)
- Anything I need to heat for more than 2 min
- Food that smells strong (coworker courtesy!)

**Game changer:**
I prep in my scrubs, right before I meal prep for the week. It's my "Sunday reset" ritual now.

The energy difference when I eat real food vs. grab-and-go is REAL.

Nourishing our healers,
Jessica 💙
""",
                "cta_text": "Watch My Meal Prep Routine",
                "cta_url": "{{youtube_url}}"
            },
            {
                "day": 5,
                "subject": "Night shift survival (from someone who's been there)",
                "preview": "The sleep schedule that actually works",
                "template": "value_email",
                "content": """
Night shift nurses... this one's for you. 🌙

I worked nights for 4 years. The sleep deprivation nearly broke me. Here's what finally worked:

**The Sleep Schedule:**

After a night shift:
- NO sunlight on drive home (sunglasses, even if cloudy)
- Shower immediately
- Bedroom: blackout curtains, 65°F, white noise
- Sleep 7-8 hours (not "just a few hours")

Before a night shift:
- Wake up, don't nap again
- Light exercise
- Big meal before shift
- Caffeine only in first half of shift

**Between Stretches:**
- Try to maintain somewhat consistent sleep times
- Don't flip completely to day schedule for days off
- "Anchor sleep" - keep 4 hours the same every day

**Supplements that helped me:**
- Magnesium before sleep
- Vitamin D (we don't see the sun!)
- Melatonin ONLY occasionally

**The mental game:**
Night shift can feel isolating. Build your community with other night nurses. We get it in a way day shift never will.

Surviving and thriving,
Jessica 💙

P.S. Day/night rotators - you have it hardest. Be extra gentle with yourself.
""",
                "cta_text": "Join Our Night Shift Community",
                "cta_url": "{{facebook_group_url}}"
            },
            {
                "day": 7,
                "subject": "When nursing breaks your heart...",
                "preview": "Processing the hard days",
                "template": "value_email",
                "content": """
Can we talk about the hard stuff? 💙

This week I want to acknowledge something we don't talk about enough: nursing is emotionally brutal sometimes.

**The patients we lose.**
**The families who blame us.**
**The impossible situations.**
**The feeling that we're never doing enough.**

I've cried in supply closets. I've driven home in silence. I've questioned everything.

**What helps me:**

1. **Debriefing** - Talking to someone who gets it (not just "at least you have a job" people)

2. **The drive home ritual** - Music that matches my mood, then shifts to something lighter

3. **Separating work and home** - Changing out of scrubs immediately, physical signal that shift is over

4. **Allowing the feelings** - Not pushing them down

5. **Professional help** - Therapy isn't weakness. Many hospitals offer free EAP sessions.

6. **Remembering WHY** - Keeping cards from patients, remembering the saves, the connections

**Please know:**
- Compassion fatigue is real
- Moral injury is real
- It's okay to not be okay
- Asking for help is strength

You carry so much. You're allowed to set it down sometimes.

Here for you,
Jessica 💙
""",
                "cta_text": "Nurse Mental Health Resources",
                "cta_url": "{{resources_url}}"
            },
            {
                "day": 10,
                "subject": "Building a career you love (yes, it's possible)",
                "preview": "Nursing doesn't have to mean burnout",
                "template": "value_email",
                "content": """
Okay, some hope today! 🌟

Nursing has SO many paths. If bedside is breaking you, know that your skills transfer to:

**Alternative Nursing Careers:**
- Case management
- Utilization review
- Nurse educator
- Informatics
- Legal nurse consultant
- Research nursing
- School nursing
- Corporate wellness
- Telehealth
- Travel nursing (for adventure!)

**Side Hustles for Nurses:**
- Per diem for extra income
- IV hydration clinics
- Health writing/blogging
- Tutoring nursing students
- Medical sales

**Questions to ask yourself:**
- What parts of nursing do I actually enjoy?
- What are my boundaries now?
- What would I do if money weren't an issue?
- What skills do I have that I'm not using?

Nursing doesn't have to mean 12-hour bedside shifts until retirement. You have options.

Your career can evolve. You can evolve.

Cheering you on,
Jessica 💙
""",
                "cta_text": "Explore Nursing Career Paths",
                "cta_url": "{{career_guide_url}}"
            },
            {
                "day": 14,
                "subject": "What's next for you, nurse friend?",
                "preview": "Taking control of your nursing career",
                "template": "conversion_email",
                "content": """
Hey there!

It's been two weeks since you joined The Nurse Planner family. How are you feeling?

**Quick check:**
- Using your shift planner?
- Prioritizing any self-care?
- Feeling a tiny bit more in control?

Progress isn't linear, especially in nursing. Be proud of ANY step forward.

**If you're ready for more...**

I created The Complete Nurse Planner for nurses who are serious about thriving:

📔 **What's Inside:**
- Full year planning system
- Shift swap tracking
- CEU/certification tracker
- Financial planning for nurses
- Career development sections
- Self-care accountability
- Private community of nurses
- Monthly live Q&As with me

This is the planner I wish existed when I was drowning.

Check it out here: https://www.amazon.com/dp/B0CPQZ7TFS?tag=dailydealdarl-20

Whether you use the free resources or go deeper, please know: you matter. Your health matters. Your career matters.

Take care of yourself like you take care of your patients.

With so much respect,
Jessica 💙

P.S. Use code NURSELIFE for 15% off this week!
""",
                "cta_text": "Get The Complete Nurse Planner",
                "cta_url": "{{product_url}}"
            }
        ]
    },
    "fitover35": {
        "name": "Fit Over 35",
        "from_name": "Fit Over 35",
        "from_email": "hello@fitover35.com",
        "lead_magnet": "Free 12-Week Workout Program",
        "form_id": "8946984",
        "tags": {
            "subscriber": 15064074,
            "lead_magnet": 15064075,
            "blog_reader": 15064076
        },
        "sequence": [
            {
                "day": 0,
                "subject": "Your Free 12-Week Workout Program is Here!",
                "preview": "3 phases, 12 weeks, designed for men 35+ -- let's get started",
                "template": "welcome_delivery",
                "content": """
Hey there,

Thanks for joining the Fit Over 35 community. You just made a decision that your future self will thank you for.

Your free 12-Week Workout Program is ready. This is the same structured approach that has helped hundreds of men over 35 build real, sustainable strength -- without destroying their joints or spending hours in the gym.

**What's Inside Your 12-Week Program:**

**Phase 1: Foundation (Weeks 1-4)**
Build your base with compound movements, proper form, and progressive overload. This phase focuses on re-establishing movement patterns and building the habit of consistent training.

**Phase 2: Strength Building (Weeks 5-8)**
Increase intensity with structured strength work. You'll train 3-4 days per week with proven exercises that build functional muscle while protecting your joints.

**Phase 3: Performance (Weeks 9-12)**
Push your limits with advanced programming. This is where the transformation happens -- increased strength, better body composition, and the confidence that comes with consistent progress.

**Why This Program Works for Men 35+:**
- Joint-friendly progression with smart warm-ups
- Time-efficient sessions (45-60 minutes, 3-4 days/week)
- Recovery-focused with built-in deload weeks
- Works with a standard gym setup
- Evidence-based, not social media trends

One piece of advice before you start: trust the process. The first two weeks might feel easy. That's by design. Building a strong foundation prevents injuries and ensures you're still progressing at Week 12.

Welcome to the community. Let's build something that lasts.

Stay strong,
The Fit Over 35 Team
""",
                "cta_text": "Access Your 12-Week Program",
                "cta_url": "https://fitover35.com/12-week-program.html"
            }
        ]
    },
    "adhd_planner": {
        "name": "The ADHD Planner",
        "from_name": "Mike from The ADHD Planner",
        "from_email": "mike@theadhdplanner.com",
        "lead_magnet": "ADHD Brain Dump Sheets",
        "sequence": [
            {
                "day": 0,
                "subject": "Your Brain Dump Sheets! 🧠",
                "preview": "Let's get that chaos out of your head",
                "template": "welcome_delivery",
                "content": """
Hey there, fellow ADHD brain! 👋

Your Brain Dump Sheets are attached - and trust me, these are about to become your new best friend.

**Quick story:**

I was diagnosed at 32. Before that, I just thought I was lazy, scattered, and "not living up to my potential." Sound familiar?

Turns out my brain just works differently. And once I stopped fighting it and started WORKING with it? Everything changed.

**Why brain dumps work for ADHD:**

Our brains hold onto EVERYTHING. Tasks, ideas, worries, random facts about octopi... it's exhausting.

Brain dumps:
- Free up mental RAM
- Reduce anxiety
- Make the invisible visible
- Help prioritize (finally!)

**How to use these sheets:**
1. Set a timer for 10 minutes
2. Write EVERYTHING in your head (no organizing!)
3. Walk away for 5 minutes
4. Come back and circle the 3 most important things
5. Do ONE of them

That's it. No complex system. Just chaos → clarity.

Tomorrow: Why traditional planners fail us (and what works instead).

You've got this,
Mike 🧠

P.S. I still brain dump almost daily. It's not a "fix" - it's a tool. And that's okay!
""",
                "cta_text": "Download Your Sheets",
                "cta_url": "{{lead_magnet_url}}"
            },
            {
                "day": 1,
                "subject": "Why normal planners don't work for us",
                "preview": "It's not you. It's the planner.",
                "template": "value_email",
                "content": """
Let me guess...

You've bought planners. Multiple planners. Fancy planners. Simple planners. Digital planners. And they all ended up abandoned by February. 📓

**It's not a character flaw. Those planners weren't designed for brains like ours.**

**Why traditional planners fail ADHD:**

1. **Too many boxes** - Our brains rebel against rigid structures
2. **Daily pages** - We forget to check them (oops)
3. **No flexibility** - Life doesn't fit in neat boxes
4. **Shame-inducing** - Blank pages feel like failure
5. **Boring** - Our brains need stimulation

**What actually works:**

✓ **Visual systems** - See everything at once
✓ **Flexibility** - Adapt to how you feel that day
✓ **Low barrier** - Quick to use, not elaborate
✓ **Forgiveness built in** - Miss a day? No guilt spiral
✓ **Dopamine hits** - Checking things off feels GOOD

The planner isn't the problem. The fit is.

Tomorrow: The time management trick that finally worked for me.

Working WITH your brain,
Mike 🧠
""",
                "cta_text": "Follow for ADHD Tips",
                "cta_url": "{{tiktok_url}}"
            },
            {
                "day": 3,
                "subject": "The time trick that changed everything",
                "preview": "Time blindness is real. Here's my hack.",
                "template": "value_email",
                "content": """
Time blindness. Let's talk about it. ⏰

You know that thing where:
- 5 minutes feels like 30
- 30 minutes feels like 5
- You're ALWAYS late despite trying
- "I'll just do this quick thing" → 2 hours gone

**My game-changing system:**

1. **Visual timers everywhere**
   - Time Timer on my desk
   - Phone timer always visible
   - Kitchen timer for tasks

2. **The 2x Rule**
   However long I think something takes? I double it. Now I'm early instead of late.

3. **Transition alarms**
   10 minutes before I need to leave/switch tasks, alarm goes off. Non-negotiable.

4. **Body doubling**
   Working alongside someone (even virtually) keeps me time-aware.

5. **Time blocking (loosely)**
   Not hour-by-hour, but "morning = deep work" "afternoon = meetings" "evening = rest"

**The mindset shift:**

I stopped beating myself up for being "bad at time." I just accepted I need more support and built systems around it.

It's not cheating. It's adapting.

Your time-challenged friend,
Mike 🧠
""",
                "cta_text": "My Favorite Visual Timer",
                "cta_url": "https://www.amazon.com/dp/B07K2KYDXJ?tag=dailydealdarl-20"
            },
            {
                "day": 5,
                "subject": "Focus hacks that actually work",
                "preview": "From someone who also has 47 browser tabs open",
                "template": "value_email",
                "content": """
Focus. The eternal struggle. 🎯

First, let's normalize something: ADHD isn't a focus problem. It's a focus REGULATION problem. We can hyperfocus for 8 hours... just maybe not on the right things.

**What helps me focus on demand:**

**Environment:**
- Noise-canceling headphones (non-negotiable)
- One browser tab at a time (I use website blockers)
- Phone in another room
- Clear desk (chaos = distraction)

**Techniques:**
- Pomodoro (but flexible - 25 min, 15 min, whatever works that day)
- Body doubling (Focusmate is great)
- "Just 5 minutes" - usually turns into more
- Matching music to task (lo-fi for writing, upbeat for boring tasks)

**Hacks:**
- Eat the frog... or don't (some days I need a win first)
- Gamify boring tasks
- Change locations for novelty
- Use a fidget toy

**The truth:**

Some days, focus happens. Some days, it doesn't. I've learned to:
- Plan important tasks for my best focus times
- Accept that some days are "low tide" days
- Not catastrophize when focus won't come

You're not broken. You're neurospicy. 🌶️

Focusing alongside you,
Mike 🧠
""",
                "cta_text": "Watch My Focus Setup Tour",
                "cta_url": "{{youtube_url}}"
            },
            {
                "day": 7,
                "subject": "The emotional side of ADHD",
                "preview": "Nobody talks about this part...",
                "template": "value_email",
                "content": """
Can we get real for a minute? 💚

ADHD isn't just about focus and organization. It's deeply emotional.

**What I've experienced:**
- Rejection Sensitive Dysphoria (RSD) - Criticism feels like physical pain
- Emotional flooding - Going from 0 to 100 instantly
- Shame spirals - "Why can't I just be normal?"
- Imposter syndrome - "Eventually they'll figure out I'm a mess"
- Grief - For the "neurotypical" life I thought I should have

**What helps:**

1. **Naming it** - "This is RSD, not reality"

2. **ADHD-informed therapy** - Not all therapists understand

3. **Community** - Other ADHD people GET IT

4. **Self-compassion** - Talking to myself like I'd talk to a friend

5. **Medication** (for me) - Helped regulate emotions too, not just focus

6. **Boundaries** - It's okay to need accommodations

**Please remember:**

- Your struggles are real, not excuses
- Late diagnosis doesn't mean less valid
- "Everyone is a little ADHD" is NOT TRUE
- You've been playing life on hard mode. You're amazing for getting this far.

You're not alone in this.

With so much understanding,
Mike 🧠
""",
                "cta_text": "Join Our ADHD Community",
                "cta_url": "{{facebook_group_url}}"
            },
            {
                "day": 10,
                "subject": "Building systems that STICK",
                "preview": "The habit hack for ADHD brains",
                "template": "value_email",
                "content": """
Habits. They're supposed to be automatic, right? 😅

For ADHD brains, habits are HARD. We need novelty, not routine. But we also desperately need some structure.

**The ADHD Habit Formula:**

1. **Anchor to existing behaviors**
   - Already make coffee? That's when you take meds
   - Already brush teeth? That's when you floss
   - Already sit at desk? That's when you brain dump

2. **Make it visible**
   - Meds next to coffee maker
   - Habit tracker on the wall (not in an app)
   - Sticky notes everywhere (no shame)

3. **Reduce friction to zero**
   - Gym clothes laid out
   - Water bottle always full
   - Brain dump sheet on desk

4. **Build in novelty**
   - Rotate between 3 workout types
   - Different brain dump prompts
   - New planner every few months? FINE.

5. **Celebrate immediately**
   - Dopamine rewards matter
   - Checkbox? Check!
   - Small treat? Yes!

**The key:** Stop fighting your need for novelty. ROTATE systems instead of abandoning them. Come back to what worked.

Building better systems,
Mike 🧠
""",
                "cta_text": "My Habit Tracker System",
                "cta_url": "{{habit_tracker_url}}"
            },
            {
                "day": 14,
                "subject": "What's next for your ADHD journey?",
                "preview": "You deserve to thrive, not just survive",
                "template": "conversion_email",
                "content": """
Hey friend!

It's been two weeks. How are those brain dumps treating you?

**Quick reflection:**
- Have you dumped your brain at least once?
- Tried any of the focus hacks?
- Been a little kinder to yourself?

Any progress counts. ADHD isn't cured, it's managed. Daily.

**If you're ready for a full system...**

I created The Complete ADHD Planner specifically for brains like ours:

🧠 **What's Inside:**
- Flexible daily/weekly layouts
- Brain dump sections everywhere
- Time blocking (the ADHD way)
- Habit tracking that doesn't shame
- Project breakdown systems
- Emotion regulation tools
- "Low tide day" protocols
- Private community of ADHD adults
- Monthly live coworking sessions

This isn't another planner that'll guilt you. It's designed FOR your brain.

Check it out here: https://www.amazon.com/dp/B0D61V1YLM?tag=dailydealdarl-20

Whether you stick with the free brain dumps or go deeper, you're on the right path.

Your brain is different, not defective. Let's build a life that works FOR you.

Rooting for you,
Mike 🧠

P.S. Use code BRAINDUMP for 20% off this week!
""",
                "cta_text": "Get The ADHD Planner",
                "cta_url": "{{product_url}}"
            }
        ]
    }
}


def get_sequence(brand: str) -> dict:
    """Get the email sequence for a brand."""
    return EMAIL_SEQUENCES.get(brand, EMAIL_SEQUENCES["daily_deal_darling"])


def get_email(brand: str, day: int) -> Optional[dict]:
    """Get a specific email from a sequence."""
    sequence = get_sequence(brand)
    for email in sequence.get("sequence", []):
        if email["day"] == day:
            return email
    return None


def preview_sequence(brand: str) -> None:
    """Print a preview of the email sequence."""
    sequence = get_sequence(brand)
    print(f"\n{'='*60}")
    print(f"Email Sequence: {sequence['name']}")
    print(f"From: {sequence['from_name']} <{sequence['from_email']}>")
    print(f"Lead Magnet: {sequence['lead_magnet']}")
    print(f"{'='*60}\n")

    for email in sequence["sequence"]:
        print(f"Day {email['day']}: {email['subject']}")
        print(f"  Preview: {email['preview']}")
        print(f"  CTA: {email['cta_text']}")
        print()


if __name__ == "__main__":
    for brand in EMAIL_SEQUENCES.keys():
        preview_sequence(brand)
