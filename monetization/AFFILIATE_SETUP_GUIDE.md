# Affiliate Marketing Setup Guide

## Overview
This guide will help you set up affiliate marketing for all 4 brands to start generating passive income from your social media content.

## Step 1: Amazon Associates Setup

### Sign Up for Amazon Associates
1. Go to https://affiliate-program.amazon.com/
2. Sign in with your Amazon account
3. Complete the application for each brand website:

| Brand | Associate Tag | Website |
|-------|---------------|---------|
| Daily Deal Darling | dailydealdarl-20 | dailydealdarling.com |
| Menopause Planner | menopauseplan-20 | themenopauseplanner.com |
| Nurse Planner | nurseplanner-20 | thenurseplanner.com |
| ADHD Planner | adhdplanner-20 | theadhdplanner.com |

### Amazon Commission Rates (2024)
- Home & Kitchen: 4%
- Beauty: 4-6%
- Health & Personal Care: 1-4.5%
- Office Products: 4%
- Clothing: 4%

## Step 2: ShareASale Setup

### Sign Up
1. Go to https://www.shareasale.com/info/affiliates/
2. Create an account
3. Apply to relevant merchants:

**For Daily Deal Darling:**
- Wayfair (Home goods)
- Target (General deals)
- Bed Bath & Beyond
- Kohl's

**For Menopause Planner:**
- Vitacost (Supplements)
- Life Extension
- Garden of Life

**For Nurse Planner:**
- Uniform Advantage (Scrubs)
- Shoes For Crews
- Scrubs & Beyond

**For ADHD Planner:**
- Clever Fox Planners
- Erin Condren

## Step 3: Impact Radius Setup

Impact hosts many premium brands:
1. Go to https://impact.com/
2. Sign up as a publisher
3. Apply to brands like:
   - Canva (for digital products)
   - Skillshare (for educational content)
   - Audible (for book recommendations)

## Step 4: Integrate Affiliates into Content

### Video Descriptions
Every video should include:
```
Shop my favorites: [AFFILIATE LINK]

#ad As an Amazon Associate I earn from qualifying purchases.
```

### Link in Bio
Use our link-in-bio pages (created separately) to:
- Feature top product recommendations
- Organize by category
- Track clicks

### Pinterest Pins
- Add affiliate links to pin descriptions
- Include FTC disclosure
- Use "Shop" or "Get it here" CTAs

## Step 5: FTC Compliance

**REQUIRED DISCLOSURES:**

For YouTube:
```
DISCLOSURE: This video contains affiliate links. If you purchase through these links, I may earn a small commission at no extra cost to you.
```

For Instagram/TikTok:
```
#ad #affiliate
```

For Pinterest:
```
This pin contains affiliate links.
```

## Step 6: Track Performance

### Key Metrics to Monitor
1. Click-through rate (CTR)
2. Conversion rate
3. Earnings per click (EPC)
4. Top-performing products
5. Best-performing content types

### Monthly Revenue Goals

| Month | Target | Strategy |
|-------|--------|----------|
| 1 | $50-100 | Build content library |
| 2 | $100-250 | Optimize top performers |
| 3 | $250-500 | Scale winning content |
| 6 | $500-1000 | Diversify affiliate programs |
| 12 | $2000+ | Multiple income streams |

## Brand-Specific Product Recommendations

### Daily Deal Darling
1. **Organization bins** - High volume, good commission
2. **Kitchen gadgets** - Viral potential
3. **Cleaning supplies** - Repeat purchases
4. **Home decor** - Higher price point

### Menopause Planner
1. **Cooling pillows/sheets** - High demand
2. **Supplements** - Recurring purchases
3. **Self-care products** - Premium pricing
4. **Sleep aids** - Problem-solving

### Nurse Planner
1. **Compression socks** - Essential item
2. **Comfortable shoes** - Higher commission
3. **Badge reels/accessories** - Fun purchases
4. **Self-care items** - Emotional purchases

### ADHD Planner
1. **Visual timers** - Problem-solving
2. **Planners** - Core product
3. **Fidget tools** - Impulse buys
4. **Noise-canceling headphones** - High ticket

## Automation Integration

The `affiliate_setup.py` module automatically:
1. Generates affiliate links for video descriptions
2. Matches products to content topics
3. Includes proper FTC disclosures
4. Tracks performance metrics

### Usage in Video Generation
```python
from monetization import AffiliateManager, generate_affiliate_description

manager = AffiliateManager()

# Get affiliate link for content
link = manager.get_link_for_content("menopause_planner", "hot flash relief")

# Generate description with affiliate
description = generate_affiliate_description("menopause_planner", "hot flash relief")
```

## Next Steps
1. [ ] Sign up for Amazon Associates (all 4 brands)
2. [ ] Apply to ShareASale merchants
3. [ ] Set up Impact Radius account
4. [ ] Configure affiliate links in video automation
5. [ ] Create product recommendation lists
6. [ ] Set up tracking dashboard
