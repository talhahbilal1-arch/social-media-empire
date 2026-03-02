# Content Strategy — Niche Setup and Topic Architecture

## The Topic Rotation System

The core principle: **never repeat a topic within 25 pins per brand.**

This means you need at least 25 unique topics per brand to run the system forever.
The live system has 60-80 topics per brand, organized into 4-5 categories.

---

## How to Structure Topics for Your Niche

### Step 1: Identify 4-6 Content Categories

These are the main pillars of your niche. For a men's fitness brand:
- Workouts
- Nutrition
- Supplements
- Fat Loss
- Lifestyle/Recovery

For a home deals brand:
- Kitchen
- Home Decor
- Organization
- Self Care
- Seasonal

**Rule:** Each category should map to one or more Pinterest boards.
This ensures every pin lands in the right board automatically.

### Step 2: Create 10-15 Topics Per Category

Each topic is specific enough to write a full pin + article about.

**Too broad:** "nutrition"
**Just right:** "protein timing and the anabolic window myth"
**Too specific:** "exact grams of leucine in a post-workout shake"

Sample topic format:
```python
"nutrition": [
    "protein timing and the anabolic window myth",
    "creatine monohydrate — the most studied supplement in history",
    "Mediterranean diet modified for muscle building goals",
    "intermittent fasting real pros and cons for men over 35",
    "micronutrients most men over 35 are deficient in",
    ...
]
```

### Step 3: Map Categories to Pinterest Boards

```python
TOPIC_TO_BOARD_MAP = {
    "your_brand": {
        "workouts": "Your Workouts Board",
        "nutrition": "Your Nutrition Board",
        "supplements": "Your Supplements Board",
        "fat_loss": "Your Fat Loss Board",
        "lifestyle": "Your Lifestyle Board",
        "_default": "Your Main Board"
    }
}
```

---

## Pinterest Board Strategy

### Minimum Board Setup (3-4 boards to start)
- 1 broad "hero" board (your main content)
- 2-3 niche-specific boards (one per content category)

### Optimal Board Setup (6-8 boards)
- 1 hero board
- 4-5 category boards
- 1 "best of" curated board (repin your best performers here)

### Board Naming for SEO

Pinterest SEO works like Google. Board names and descriptions are indexed.

**Bad board names:**
- "My Fitness Tips"
- "Health Stuff"
- "Random Finds"

**Good board names (keyword-first):**
- "Fat Loss After 35 — Men's Fitness"
- "Workouts for Men Over 35"
- "Meal Prep & Nutrition for Men"
- "Supplement Reviews — What Actually Works"

### Board Description Template
```
[Primary keyword phrase] — [secondary description 1-2 sentences].
Pinning [frequency] about [specific topics].
Follow for [value proposition].
```

Example:
```
Fat Loss After 35 — Men's Fitness. Real strategies for losing belly fat and building
muscle after your metabolism slows down. Pinning daily about nutrition, training,
and the habits that actually move the needle. Follow for no-nonsense fitness content.
```

---

## Scheduling Logic (5x Daily)

The live system runs at these times (PST):
- 7:00 AM — morning commuters
- 10:30 AM — late morning browse
- 2:00 PM — lunch break
- 6:00 PM — evening wind-down
- 9:00 PM — peak Pinterest time

**Why these times matter:**
Pinterest's Smart Feed surfaces recent, engaging pins to users browsing at similar times.
Posting across 5 time windows maximizes the chance of landing in someone's active session.

**Time zone note:** Pinterest's audience skews heavily US-based.
All scheduling should be optimized for US Eastern time (add 3 hours to PST times above).

---

## Content Variety Rotation

The system tracks and rotates these dimensions:

| Dimension | What Rotates | Why |
|-----------|-------------|-----|
| Topic | 60+ topics, none repeated in last 25 | Prevents feed fatigue |
| Visual style | 7 overlay styles, none repeated in last 4 | Keeps feed visually varied |
| Board | Matches category, highest-follower boards prioritized | Maximizes distribution |
| Description opener | 10 styles, none repeated in last 5 | Voice variety |
| Image query | Logged, none repeated in last 25 | Visual uniqueness |
| Hook framework | 45 frameworks, rotated | Prevents same patterns |

---

## Seasonal Content Injection

The system supports seasonal topics that override the standard rotation.

**Inject these in January:**
- New Year fitness reset
- Setting realistic goals
- Reversing holiday weight gain

**Inject these in May-June:**
- Summer body prep
- Outdoor training
- BBQ nutrition

**Inject these in September:**
- Fall fitness routines
- Back to schedule after summer
- Supplement for immunity going into winter

**How to inject:** Add a "seasonal" category to your topics_by_category dict
with 5-10 current seasonal topics. The system will naturally mix them in.

---

## Tracking What Works

Even in a fully automated system, you should review performance monthly.

**What to check in Pinterest Analytics:**
1. Top performing pins by outbound clicks (these drive actual traffic)
2. Top performing pins by saves (these are most likely to go viral)
3. Which boards get the most impressions
4. Which visual style performs best (your data will differ from defaults)

**What to do with the data:**
- Double down on topic categories that generate the most clicks
- Update hook frameworks with what's working in your niche
- Remove or deprioritize boards with consistently low performance
- Adjust posting frequency for each category based on performance

---

## Minimum Viable Setup (Start Posting in 24 Hours)

If you want to start posting immediately without the full automated system:

1. **Pick one brand/niche**
2. **Write 10 topics** (enough for 2 weeks)
3. **Set up Make.com** (webhook + Pinterest connection)
4. **Run the Claude prompts manually** — generate 1 pin at a time
5. **Get Pexels image** — manual or via the API
6. **Use Canva** — create the text overlay instead of PIL
7. **Post manually** — or via Make.com webhook call from terminal

This gets you posting with zero coding while you build the automation.
The full pipeline just automates what you'd do manually.
