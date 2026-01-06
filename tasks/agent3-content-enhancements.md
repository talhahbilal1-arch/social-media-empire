# Agent 3: Content Enhancements

**Date:** January 6, 2026
**Author:** Agent 3 (Automated)

---

## Overview

This document covers two major enhancements to the content pipeline:
1. Pinterest Idea Pins in Video Factory
2. Higher Commission Affiliate Programs in Content Brain

---

## Task 1: Pinterest Idea Pins

### What are Idea Pins?
Pinterest Idea Pins are multi-page video/image posts that get **9x more reach** than standard pins. They're Pinterest's answer to Stories/Reels.

### Specifications
| Property | Value |
|----------|-------|
| Aspect Ratio | 9:16 (1080x1920) |
| Pages | 2-20 clips |
| Clip Duration | 1-60 seconds each |
| Total Duration | Max 5 minutes |

### Implementation Details

#### Database Changes (`database/schema.sql`)
Added fields to `videos` table:
```sql
idea_pin_url TEXT,
idea_pin_render_id TEXT,
idea_pin_pages INTEGER DEFAULT 0,
```

#### Video Factory Changes (`agents/video_factory.py`)

1. **New Configuration:**
```python
IDEA_PIN_CONFIG = {
    'width': 1080,
    'height': 1920,
    'min_pages': 2,
    'max_pages': 5,
    'page_duration': 5,  # seconds
    'format': '9:16'
}
```

2. **New Methods:**
- `_create_idea_pin(content, template)` - Creates Idea Pin render via Creatomate
- `_build_idea_pin_pages(content)` - Structures content into multi-page format

3. **Page Structure:**
- Page 1: Title/Hook
- Pages 2-4: Content chunks from script/description
- Final Page: Call-to-action

### How to Test
1. Run Video Factory manually: `python agents/video_factory.py`
2. Check Supabase `videos` table for new `idea_pin_render_id` entries
3. Verify Creatomate dashboard shows multi-page renders

---

## Task 2: Higher Commission Affiliate Programs

### Problem
Amazon Associates only pays 3-4% commission. We're leaving money on the table.

### Solution
Added support for higher-commission affiliate networks with automatic priority:

| Program | Commission | Priority |
|---------|------------|----------|
| ShareASale | 10-30% | 100 (highest) |
| Impact | 10-25% | 90 |
| CJ Affiliate | 5-20% | 80 |
| Amazon | 3-4% | 10 (fallback) |

### Database Changes (`database/schema.sql`)

**New Table: `affiliate_programs`**
```sql
CREATE TABLE affiliate_programs (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    commission_rate DECIMAL(5,2) NOT NULL,
    min_commission DECIMAL(5,2),
    max_commission DECIMAL(5,2),
    signup_url TEXT,
    api_endpoint TEXT,
    api_key_secret_name TEXT,
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP
);
```

**New Table: `product_affiliates`**
```sql
CREATE TABLE product_affiliates (
    id UUID PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_category TEXT,
    amazon_asin TEXT,
    amazon_link TEXT,
    shareasale_link TEXT,
    impact_link TEXT,
    cj_link TEXT,
    best_program TEXT,
    best_commission DECIMAL(5,2),
    last_verified_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Content Brain Changes (`agents/content_brain.py`)

**New Configuration:**
```python
AFFILIATE_PRIORITY = {
    'shareasale': {'priority': 100, 'avg_commission': 20.0, 'secret_name': 'SHAREASALE_API_KEY'},
    'impact': {'priority': 90, 'avg_commission': 17.5, 'secret_name': 'IMPACT_API_KEY'},
    'cj': {'priority': 80, 'avg_commission': 12.5, 'secret_name': 'CJ_API_KEY'},
    'amazon': {'priority': 10, 'avg_commission': 3.5, 'secret_name': None}
}
```

**New Methods:**
- `get_best_affiliate_link(product, brand)` - Returns best affiliate link by priority
- `_get_available_affiliate_programs()` - Checks which API keys are configured
- `_lookup_affiliate_link(program, product_name)` - Looks up product in network
- `_build_amazon_link(asin, tag)` - Builds Amazon fallback link
- `_save_product_affiliate(product, program, link, commission)` - Caches affiliate data
- `enhance_affiliate_products(products, brand)` - Enhances product list with best links

### Blog Factory Changes (`agents/blog_factory.py`)

**Updated `_add_affiliate_links()` method:**
1. First checks `product_affiliates` table for higher-commission links
2. Replaces Amazon links with better affiliate links when available
3. Falls back to Amazon affiliate tag for remaining links

**New Methods:**
- `_upgrade_to_best_affiliate(content, affiliate_tag)` - Swaps to higher commission links
- `_add_amazon_tags(content, affiliate_tag)` - Adds tags to remaining Amazon URLs

### Required GitHub Secrets (Placeholder)
```
SHAREASALE_API_KEY - Sign up at https://www.shareasale.com/join/
IMPACT_API_KEY - Sign up at https://impact.com/
CJ_API_KEY - Sign up at https://www.cj.com/
```

**Note:** These are placeholders. Fill in after signing up for each program.

### How to Test

1. **Without API Keys (Amazon fallback):**
   - Run Content Brain or Blog Factory
   - All links should use Amazon with affiliate tag
   - No errors should occur

2. **With API Keys:**
   - Add secrets to GitHub repository
   - Run Content Brain
   - Check `product_affiliates` table for cached data
   - Blog articles should use higher-commission links when available

3. **Manual Product Test:**
   ```python
   from agents.content_brain import ContentBrain
   brain = ContentBrain()
   result = brain.get_best_affiliate_link(
       {'name': 'Test Product', 'asin': 'B0123456789'},
       {'affiliate_tag': 'dailydealdarling1-20'}
   )
   print(result)  # Should show best_program and commission
   ```

---

## Files Changed

| File | Changes |
|------|---------|
| `database/schema.sql` | Added `idea_pin_*` fields to videos, new affiliate tables |
| `agents/video_factory.py` | Added Idea Pin creation with multi-page support |
| `agents/content_brain.py` | Added affiliate matching with priority system |
| `agents/blog_factory.py` | Updated to use best affiliate links |
| `tasks/todo.md` | Added Agent 3 task section |

---

## Next Steps

1. **Sign up for affiliate programs:**
   - ShareASale: https://www.shareasale.com/join/
   - Impact: https://impact.com/
   - CJ Affiliate: https://www.cj.com/

2. **Add API keys to GitHub Secrets**

3. **Run schema migrations in Supabase:**
   - Execute the new table creation SQL in Supabase SQL Editor

4. **Populate product_affiliates table:**
   - Add products with links from each network
   - System will automatically use best available link

5. **Monitor commission earnings:**
   - Track which programs generate most revenue
   - Adjust priority based on actual earnings
