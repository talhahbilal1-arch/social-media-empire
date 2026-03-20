# The Creator's AI Prompt Vault
## 10 Premium Prompts for Midjourney, DALL-E 3 & ChatGPT

---

### How to Use This Pack

**For Midjourney prompts (1, 2, 5, 6, 8, 10):**
1. Replace all [BRACKETED] text with your own details (see variable guide below each prompt)
2. Copy the filled-in prompt
3. Paste into Midjourney /imagine command
4. Pick your favorite from the 4-image grid and upscale

**For DALL-E 3 prompt (3):**
1. Replace all [BRACKETED] text
2. Paste into ChatGPT with DALL-E enabled, or the OpenAI API

**For ChatGPT/Claude prompts (4, 7, 9):**
1. Replace all [BRACKETED] text
2. Paste into ChatGPT (GPT-4 recommended) or Claude
3. The output will follow the exact structure specified in the prompt

**Pro Tips:**
- Generate 3-4 variations with different variable fills to find your favorite style
- For Midjourney: if you want more/less artistic interpretation, adjust the --s value (lower = more literal, higher = more creative)
- For text prompts: you can ask for revisions after the initial output — "make email 3 more casual" or "add more urgency to the closing section"

---

## PROMPT 1: Cinematic Fitness Portrait
**Works with:** Midjourney v6.1

```
Editorial portrait of a [AGE]-year-old [GENDER] with a [PHYSIQUE] build, [POSE], photographed inside [SETTING]. Single Rembrandt key light from upper-left at 45 degrees with a 3ft octabox, secondary hair light from behind-right for rim separation. Shot on a 85mm prime lens at f/2, shallow depth of field isolating the subject from the [BACKGROUND] background. Skin rendered with natural pores and texture, no airbrushing. Color grade: desaturated warm tones, lifted shadow detail, crushed blacks in corners. Composition follows portrait rule-of-thirds with headroom. No text, no logo, no watermark --ar 4:5 --s 200 --style raw --v 6.1
```

**Variable Guide:**
- [AGE] → 28, 35, 42, 55
- [GENDER] → male, female
- [PHYSIQUE] → lean muscular, athletic, stocky powerful, toned slim
- [POSE] → standing with arms folded across chest, gripping a barbell mid-pull, sitting on a weight bench leaning forward, holding a kettlebell at shoulder height
- [SETTING] → a raw concrete gym with hanging chains, an outdoor running track at sunset, a clean white photography studio, a dimly-lit boxing ring
- [BACKGROUND] → out-of-focus iron racks, hazy golden sky, smooth grey paper roll, dark ropes and canvas

---

## PROMPT 2: Floating Product Shot
**Works with:** Midjourney v6.1

```
Commercial studio photograph of a [PRODUCT] hovering at a 12-degree forward tilt against a seamless [GRADIENT] gradient backdrop. Main light: large rectangular softbox positioned directly above at 50 degrees casting soft even illumination across the product surface. Edge light from behind-right creating a thin bright contour along the product silhouette. [ACCENT_ELEMENTS] suspended in mid-air around the product as if frozen in time. The product material renders with accurate [MATERIAL] reflections and surface detail. A faint circular shadow sits directly beneath the product on the backdrop. Clean commercial catalog aesthetic, no text, no branding visible on product --ar 4:5 --s 150 --style raw --v 6.1
```

**Variable Guide:**
- [PRODUCT] → matte black protein powder tub, clear glass cologne bottle, white ceramic coffee mug, rose gold skincare tube, aluminum water bottle
- [GRADIENT] → charcoal fading to black, ivory fading to warm grey, deep teal fading to navy, peach fading to coral
- [ACCENT_ELEMENTS] → water droplets and small ice chips, dried lavender sprigs and pollen dust, ground coffee beans and cinnamon sticks, green tea leaves and dewdrops
- [MATERIAL] → matte plastic with slight fingerprint smudges, clear glass with internal liquid refraction, brushed metal with anodized sheen, glossy ceramic with overhead light reflection

---

## PROMPT 3: Luxury Minimalist Logo Mark
**Works with:** DALL-E 3

```
A single luxury brand logo mark for a [BUSINESS_TYPE], designed as a [DESIGN_APPROACH] rendered in [COLOR_PALETTE] on a solid [BACKGROUND_COLOR] background. The mark is a standalone symbol with no text or letters. It uses clean geometric lines with consistent 2px stroke weight throughout. The overall shape fits within a perfect square boundary. Presented centered in the frame with equal negative space on all four sides. The design is flat with no gradients, no shadows, no 3D effects — purely two-dimensional line work suitable for both 16px favicon rendering and 300dpi print reproduction.
```

**Variable Guide:**
- [BUSINESS_TYPE] → organic skincare brand, boutique fitness studio, artisan bakery, luxury candle company, minimalist architecture firm, premium tea house
- [DESIGN_APPROACH] → interlocking geometric shapes forming an abstract leaf, continuous single-line drawing of a flame, negative-space optical illusion between two forms, symmetrical botanical illustration with mathematical precision, overlapping circles creating a flower-of-life pattern
- [COLOR_PALETTE] → solid black only, dark forest green on light, warm copper metallic tone, deep navy blue, muted terracotta
- [BACKGROUND_COLOR] → pure white, off-white cream, jet black, light warm grey

---

## PROMPT 4: 7-Email Client Onboarding Sequence
**Works with:** ChatGPT (GPT-4) or Claude

```
ROLE: You are an email marketing strategist who has written onboarding sequences for 200+ service businesses. You specialize in [INDUSTRY] businesses.

TASK: Write a complete 7-email welcome sequence for a [BUSINESS_DESCRIPTION] that converts new subscribers into paying clients.

STRUCTURE — For every email, output in this exact format:

---
EMAIL [NUMBER] — Send: [DAY AFTER SIGNUP]
SUBJECT: [subject line, max 45 characters, starts with lowercase]
PREVIEW: [preview text, max 80 characters]

[Email body: 120-180 words. Paragraphs of 2 sentences max. Address the reader as "you" throughout. End with a single clear action.]

CTA BUTTON: [button text, 3-5 words]
---

SEQUENCE ARC:
1. (Day 0) — Deliver the promised lead magnet or welcome gift. Tell them exactly what to expect from you and when. One sentence about who you are.
2. (Day 1) — Share one specific tactic they can use in [QUICK_WIN_TIMEFRAME]. No theory, just a step-by-step they can act on right now.
3. (Day 3) — Tell a client success story. Use this framework: "Before working with us, [CLIENT_TYPE] was struggling with [PROBLEM]. After [TIMEFRAME], they achieved [RESULT]."
4. (Day 5) — Bust the #1 myth in [EXPERTISE_AREA]. Open with the myth stated as fact, then dismantle it with evidence.
5. (Day 7) — Share a personal story about why you started this business. Be specific — one pivotal moment, not your full biography.
6. (Day 10) — Present your [PAID_OFFER] as the logical next step. Frame it around what they've learned in emails 1-5, not as a cold pitch.
7. (Day 14) — Simple check-in. Ask how they're doing with the tip from Email 2. Include a one-question survey or reply prompt.

CONSTRAINTS:
- No exclamation marks in subject lines
- No words: "synergy", "leverage", "utilize", "empower", "journey"
- Every email opens with a direct statement or question, never "I hope this finds you well"
- Subject lines must create curiosity without clickbait
- Tone: [TONE_STYLE]
```

**Variable Guide:**
- [INDUSTRY] → fitness coaching, financial planning, wedding photography, home renovation, life coaching
- [BUSINESS_DESCRIPTION] → online personal training for men over 35, bookkeeping service for freelancers, meal prep delivery for busy families
- [QUICK_WIN_TIMEFRAME] → 10 minutes today, by this weekend, within 24 hours
- [CLIENT_TYPE] → a 38-year-old software developer, a freelance graphic designer, a working mother of two
- [EXPERTISE_AREA] → fat loss nutrition, personal finance, social media marketing
- [PAID_OFFER] → 12-week coaching program ($497), monthly retainer package, group training membership
- [TONE_STYLE] → direct and motivational like a trusted coach, warm and professional, casual like texting a smart friend

---

## PROMPT 5: Isometric 3D App Icon
**Works with:** Midjourney v6.1

```
A single 3D rendered app icon viewed from a standard isometric perspective, depicting a [ICON_SUBJECT] centered within a rounded-square iOS icon shape. The icon is made of [MATERIAL] with a subtle top-surface specular highlight. Lit by soft ambient light from all directions with a stronger warm directional light from the upper-left casting a short drop shadow beneath the icon onto a [SURFACE] surface. The icon uses a [COLOR_SCHEME] color palette. The rounded-square has a smooth continuous radius matching Apple's squircle proportion. One icon only, centered in frame, clean [BACKGROUND_COLOR] background, no additional objects --ar 1:1 --s 100 --style raw --v 6.1
```

**Variable Guide:**
- [ICON_SUBJECT] → a minimalist dumbbell, a glowing envelope, a bar chart with upward arrow, a music note with sound waves, a shield with checkmark, a camera lens
- [MATERIAL] → frosted semi-transparent glass, smooth matte clay, brushed stainless steel, soft-touch silicone rubber, polished ceramic
- [SURFACE] → matte white desk, light grey seamless paper, natural maple wood, frosted glass shelf
- [COLOR_SCHEME] → electric blue and white, sunset orange gradient into pink, forest green and cream, dark purple and gold, coral and charcoal
- [BACKGROUND_COLOR] → pure white, very light grey, soft warm cream, faint blue-grey

---

## PROMPT 6: Architectural Interior Visualization
**Works with:** Midjourney v6.1

```
Interior photograph of a [ROOM_TYPE] designed in a [STYLE] aesthetic. The room has [CEILING_TYPE] ceilings and [FLOORING] flooring. Primary furniture: [MAIN_FURNITURE]. Daylight enters through [WINDOW_TYPE] on the left wall, casting long directional shadows across the floor. Material palette: [MATERIALS]. One [PLANT_TYPE] in the right third of the frame adds organic contrast. Photographed from the doorway threshold looking inward at standing eye level with a 24mm rectilinear lens keeping vertical lines straight. Warm late-afternoon light temperature around 4200K. The space feels lived-in with [LIVED_IN_DETAIL]. No people. Editorial style matching Kinfolk or Cereal magazine interior spreads --ar 16:9 --s 250 --style raw --v 6.1
```

**Variable Guide:**
- [ROOM_TYPE] → open-plan living and dining area, master bedroom, home office study, compact kitchen, luxury bathroom
- [STYLE] → Japandi with warm minimalism, mid-century modern, Mediterranean farmhouse, industrial converted loft, Scandinavian coastal
- [CEILING_TYPE] → 10ft flat white, exposed timber beam, vaulted with skylights, coffered with recessed lighting
- [FLOORING] → wide-plank white oak in herringbone pattern, honed concrete with area rug, dark walnut planks, pale limestone tiles
- [MAIN_FURNITURE] → a low-profile linen sofa with rounded arms and timber legs, a walnut desk with brass legs and a leather task chair, a king platform bed with an upholstered headboard
- [WINDOW_TYPE] → tall floor-to-ceiling sliding glass panels, three arched casement windows, a single large picture window, industrial steel-frame grid windows
- [MATERIALS] → warm oak and white plaster with matte brass hardware, raw concrete and black steel with saddle leather, travertine and beige linen with brushed nickel
- [PLANT_TYPE] → a tall fiddle leaf fig in a woven basket, a trailing pothos on a floating shelf, an olive tree in a terracotta pot, a cluster of dried pampas grass in a ceramic vase
- [LIVED_IN_DETAIL] → an open book face-down on the sofa arm, a half-finished coffee on the side table, a folded throw blanket draped over a chair, reading glasses resting on a stack of magazines

---

## PROMPT 7: 90-Day Content Strategy System
**Works with:** ChatGPT (GPT-4) or Claude

```
ROLE: You are a content strategist who has scaled 50+ brand accounts past 10K followers on [PLATFORM]. You think in systems, not random post ideas.

TASK: Build a complete 90-day content system for a [BUSINESS_TYPE] targeting [AUDIENCE]. The goal is to generate [MONTHLY_LEADS] inbound leads per month through organic content.

OUTPUT SECTION 1 — CONTENT PILLARS (define 4):
For each pillar, state:
- Pillar name and percentage of total posts
- Why this pillar matters for this specific audience
- 3 example post topics under this pillar

Pillar distribution must follow: 40% educational, 25% proof/results, 20% personal/relatable, 15% promotional.

OUTPUT SECTION 2 — 12-WEEK CALENDAR:
Format as a markdown table with columns: Week | Mon | Tue | Wed | Thu | Fri
For each cell, write: "[Pillar initial] — [Specific post title/hook]"

Each week must include:
- Exactly [POSTS_PER_WEEK] posts
- At least 1 contrarian or myth-busting post (label these with *)
- At least 1 post with a direct CTA to [CTA_DESTINATION]
- A mix of formats: specify (C) for carousel, (R) for reel/video, (T) for text-only, (I) for single image

OUTPUT SECTION 3 — REUSABLE TEMPLATES:
A) Carousel template: Hook slide, Problem slide, 3 solution slides, CTA slide
B) Reel script template: 3-second hook, 15-second value, 5-second CTA
C) Caption formula: Opening question, Bridge, Value bullet points, Engagement question, CTA

OUTPUT SECTION 4 — WEEKLY TRACKER:
Posts published | Reach | Engagement rate | Profile visits | Link clicks | DMs received

CONSTRAINTS:
- No generic filler posts like "share a motivational quote"
- Every post title must be specific enough to write the post from the title alone
- Use numbers in at least 40% of post titles
```

**Variable Guide:**
- [PLATFORM] → Instagram, LinkedIn, TikTok, Twitter/X
- [BUSINESS_TYPE] → personal training studio, digital marketing agency, financial advisor practice, online course creator
- [AUDIENCE] → men 30-50 wanting to lose weight, B2B SaaS founders, first-time homebuyers under 35, freelance designers
- [MONTHLY_LEADS] → 10, 20, 50
- [POSTS_PER_WEEK] → 3, 4, 5
- [CTA_DESTINATION] → free consultation booking page, lead magnet download, DM for details

---

## PROMPT 8: Editorial Food Photography
**Works with:** Midjourney v6.1

```
Overhead editorial food photograph of [DISH], plated on [PLATE] placed on a [TABLE_SURFACE] table. The dish is garnished with [GARNISH]. Key light: diffused natural daylight from a large window on the left side of frame, creating soft directional shadows falling to the right. Fill light: reflected off a white card on the right side at half intensity. Thin wisps of steam rise from the dish, backlit by the window. Props: [PROPS] positioned off-center using rule-of-thirds placement. Color mood: [MOOD_PALETTE]. Shot with a 90mm macro lens at f/4 from directly overhead. The image has lifted shadow tones, slightly pulled-back saturation, and a fine analog grain texture. No text, no hands, no faces, no utensils in use --ar 4:5 --s 200 --style raw --v 6.1
```

**Variable Guide:**
- [DISH] → pan-seared salmon fillet with crispy skin on a bed of asparagus, a thick-crust margherita pizza with torn fresh mozzarella, a layered chocolate cake slice showing interior layers, a colorful poke bowl with organized toppings
- [PLATE] → handmade matte charcoal stoneware bowl, round white porcelain dinner plate, rustic olive wood board, speckled grey ceramic shallow dish
- [TABLE_SURFACE] → dark slate stone, weathered reclaimed oak, white Carrara marble, black linen tablecloth
- [GARNISH] → microgreens and a lemon wedge, torn fresh basil leaves and a dusting of parmesan, gold leaf and reduced balsamic drizzle, flaky Maldon sea salt and cracked black pepper
- [PROPS] → a folded linen napkin and small bowl of salt, scattered fresh herbs and a pepper mill, a wine glass and torn bread piece, a small ramekin of sauce and wooden spoon
- [MOOD_PALETTE] → warm golden tones with deep shadows, bright and airy with pastel accents, moody dark and dramatic with rich contrast, earthy autumn tones with warm highlights

---

## PROMPT 9: Sales Objection Playbook
**Works with:** ChatGPT (GPT-4) or Claude

```
ROLE: You are a sales trainer who has coached 500+ service-based business owners on consultative selling. Your approach is empathy-first — you never use pressure tactics or artificial urgency.

TASK: Create a complete objection-handling playbook for a [BUSINESS_TYPE] selling [OFFER] at [PRICE_POINT] to [BUYER_TYPE].

For EACH of these 10 objections, provide all 5 parts in this exact format:

---
OBJECTION [NUMBER]: "[exact words the prospect says]"

HIDDEN MEANING: [1 sentence]

REFRAME: [1 sentence]

RESPONSE SCRIPT:
"[3-4 sentences. Include a pause point marked with (pause). End with a question.]"

BRIDGE QUESTION: [One question that moves the conversation forward]
---

THE 10 OBJECTIONS:
1. "That's more than I was expecting to spend"
2. "I need to think about it for a few days"
3. "I need to run this by my partner/spouse/business partner"
4. "I tried something similar before and it didn't work for me"
5. "I can probably figure this out myself with free resources"
6. "This sounds great but the timing isn't right"
7. "Can you just email me the details?"
8. "I'm already working with someone on this"
9. "How do I know this will actually work for my specific situation?"
10. "What happens if I'm not happy with the results?"

CLOSING SECTION — 5-Step Warm Close:
Step 1: Summarize the 3 things they said they wanted
Step 2: Directly address their one remaining concern
Step 3: Present two options (not yes/no — Option A or Option B)
Step 4: State the simple next step in one sentence
Step 5: Be silent and wait (explain why)

CONSTRAINTS:
- Never use: "honestly", "trust me", "no-brainer", "once in a lifetime", "act now"
- Every response must reference the prospect's stated goal
- Tone: [TONE]
```

**Variable Guide:**
- [BUSINESS_TYPE] → online fitness coaching business, boutique marketing agency, personal training studio, freelance web design service
- [OFFER] → 12-week body transformation program, 6-month growth retainer, 1-on-1 private training package, website redesign project
- [PRICE_POINT] → $497 one-time, $2,500/month, $197/month, $3,500 project fee
- [BUYER_TYPE] → busy professionals aged 35-50, small business owners with 5-20 employees, solopreneurs making under $100K
- [TONE] → confident and warm like a trusted advisor, calm and direct like a doctor giving a recommendation, enthusiastic but grounded like a supportive coach

---

## PROMPT 10: Styled Product Flat Lay
**Works with:** Midjourney v6.1

```
Directly overhead flat-lay photograph of [PRODUCTS] arranged in a balanced asymmetric composition on a [SURFACE] surface. Styling props: [PROPS] placed at natural-looking angles rather than perfectly aligned. Soft diffused daylight from above with no harsh shadows — overcast outdoor lighting quality. A [TEXTURE_ACCENT] adds visual depth between the products. The overall color story follows a [COLOR_PALETTE] palette. Intentional empty space in the [EMPTY_AREA] of the frame for adding text or a logo later. Shot at exactly 90 degrees overhead with a 50mm lens at f/5.6 for even sharpness across the entire flat surface. No hands, no people, no text overlays, no reflections --ar 1:1 --s 150 --style raw --v 6.1
```

**Variable Guide:**
- [PRODUCTS] → three skincare bottles of different heights, a protein powder tub next to a shaker and resistance band, a notebook and pen set with washi tape rolls, a coffee bag with a ceramic mug and pour-over dripper
- [SURFACE] → white marble slab with faint grey veins, raw unbleached linen cloth, light blonde wood grain, smooth grey concrete
- [PROPS] → a sprig of dried eucalyptus and two cotton bolls, scattered whole coffee beans and a cinnamon stick, pressed dried flowers and a wax seal, small succulent in a ceramic pot and a stone
- [TEXTURE_ACCENT] → a crumpled sheet of kraft paper tucked under one product, a small pile of loose leaf tea, a few scattered salt crystals, a dusting of cocoa powder
- [COLOR_PALETTE] → muted sage green and warm cream with brass accents, earthy terracotta and off-white, soft blush pink and ivory, monochrome white and grey with one gold detail
- [EMPTY_AREA] → upper-left quadrant, entire right third, bottom half, center of the arrangement

---

*Created by PilotTools — pilottools.ai*
*For support or questions: hello@pilottools.ai*
