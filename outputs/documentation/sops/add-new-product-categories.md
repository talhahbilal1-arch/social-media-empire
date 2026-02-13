# Add New Product Categories

## Overview

This Standard Operating Procedure guides you through adding new product categories to the Social Media Empire automation system. New categories expand the range of content your brands can produce, target new audience segments, and create additional revenue opportunities through affiliate marketing. Adding categories requires updates across multiple system components including content banks, Make.com scenarios, AI prompts, Pinterest boards, and database tracking.

## Prerequisites

- Repository write access to update configuration files
- Access to Make.com for scenario configuration
- Pinterest Business account access for the relevant brand(s)
- Access to Supabase database for tracking setup
- Understanding of the brand's target audience and content strategy
- Market research on the new category's potential
- Affiliate program access for the new category (if monetizing)

---

## When to Add New Categories

Consider adding a new product category when:

1. **Market Opportunity**: Analytics show audience interest in related topics not currently covered
2. **Audience Request**: Comments, emails, or surveys indicate demand for new content areas
3. **Seasonal Alignment**: New seasonal opportunities (e.g., "Back to School" in August)
4. **Monetization**: New affiliate programs become available in adjacent niches
5. **Competitive Gap**: Competitors aren't covering a valuable sub-niche
6. **Content Diversification**: Current categories are becoming saturated or repetitive

### Category Viability Criteria

Before proceeding, evaluate the category against these criteria:

| Criteria | Minimum Threshold | Ideal |
|----------|------------------|-------|
| Audience Alignment | 60% overlap with existing audience | 80%+ overlap |
| Content Ideas | 10+ unique video topics | 25+ topics |
| Affiliate Potential | At least 1 program | 3+ programs |
| Search Volume | 1,000+ monthly searches | 10,000+ |
| Competition | Low to moderate | Low |
| Evergreen Potential | 50% evergreen content | 70%+ evergreen |

---

## Step 1: Market Research and Validation

### 1.1 Identify Potential Categories

Start by brainstorming categories adjacent to your brand's niche:

**Daily Deal Darling Examples:**
- Current: General deals, beauty, home
- Potential: Kitchen gadgets, office supplies, pet products, tech accessories

**Menopause Planner Examples:**
- Current: Wellness, symptoms management
- Potential: Fashion for hot flashes, travel tips, fitness modifications

**Nurse Planner Examples:**
- Current: Shift life, self-care
- Potential: Career development, continuing education, specialty nursing

**ADHD Planner Examples:**
- Current: Productivity, focus
- Potential: ADHD-friendly recipes, exercise routines, relationship tips

### 1.2 Validate Category Demand

**Pinterest Trends Research:**
1. Go to [Pinterest Trends](https://trends.pinterest.com/)
2. Search for category-related keywords
3. Check for upward trend indicators
4. Note seasonal patterns
5. Document related trending searches

**Google Trends Validation:**
1. Go to [Google Trends](https://trends.google.com/)
2. Compare new category to existing successful categories
3. Check for stable or growing interest
4. Identify regional variations

**Competitor Analysis:**
1. Search Pinterest for similar content creators
2. Check pin engagement (saves, comments)
3. Identify content gaps they're not covering
4. Note successful content formats

### 1.3 Document Research Findings

Create a category validation document:

```markdown
# Category Validation: [Category Name]

## Brand: [brand_name]
## Date: [date]

### Search Volume
- Pinterest: [number] monthly searches
- Google: [number] monthly searches
- Trend: [Growing/Stable/Declining]

### Audience Fit
- Overlap Score: [percentage]
- Relevance Notes: [description]

### Competition Analysis
- Number of Competitors: [number]
- Content Gap Opportunities: [list]

### Monetization
- Affiliate Programs: [list]
- Commission Rates: [ranges]

### Content Potential
- Evergreen Topics: [count]
- Seasonal Topics: [count]
- Total Topic Ideas: [count]

### Decision: [APPROVED / NOT APPROVED]
### Reasoning: [explanation]
```

---

## Step 2: Add Category to Content Bank JSON Files

### 2.1 Identify the Correct Content Bank File

Content bank files are located in `/video_automation/content_bank/`:

| Brand | Primary File | Additional Files |
|-------|--------------|------------------|
| daily_deal_darling | deal_topics.json | wellness_ideas.json |
| menopause_planner | menopause_topics.json | wellness_ideas.json |
| nurse_planner | nurse_topics.json | wellness_ideas.json |
| adhd_planner | adhd_topics.json | wellness_ideas.json |

### 2.2 Add Category Structure

Edit the appropriate JSON file to add the new category:

```json
{
  "categories": {
    "existing_category": {
      "...existing content..."
    },
    "new_category_name": {
      "display_name": "Kitchen Gadgets",
      "description": "Must-have kitchen tools and gadgets under $30",
      "target_board": "kitchen-gadgets-daily-deal-darling",
      "affiliate_tags": ["amazon_kitchen", "target_home"],
      "hashtags": [
        "#kitchengadgets",
        "#amazonkitchen",
        "#kitchenfinds",
        "#cookinghacks",
        "#kitchenorganization"
      ],
      "topics": [
        "5 Kitchen gadgets under $20 that changed my life",
        "This $15 gadget replaced 3 kitchen tools",
        "Amazon kitchen finds you didn't know you needed",
        "Viral kitchen gadgets that actually work",
        "Best kitchen organization products under $25",
        "Kitchen essentials for small spaces",
        "Time-saving kitchen tools for busy moms",
        "TikTok famous kitchen gadgets - worth it?",
        "Meal prep gadgets that save hours",
        "Kitchen gadgets for beginners",
        "Aesthetic kitchen finds that are also functional",
        "Kitchen products I regret not buying sooner"
      ],
      "hooks": [
        "Stop scrolling - you NEED this kitchen gadget",
        "This $12 find changed my entire cooking routine",
        "POV: You just discovered the best kitchen hack",
        "Kitchen gadgets I use EVERY single day",
        "My most-used kitchen finds under $20"
      ],
      "search_terms": [
        "kitchen gadgets",
        "cooking tools",
        "kitchen organization",
        "meal prep",
        "kitchen aesthetic"
      ],
      "enabled": true,
      "weight": 1.0,
      "min_posts_per_week": 2,
      "max_posts_per_week": 5
    }
  }
}
```

### 2.3 Validate JSON Syntax

After editing, validate the JSON:

```bash
python -c "
import json
with open('video_automation/content_bank/deal_topics.json', 'r') as f:
    data = json.load(f)
    print('JSON valid!')
    print(f'Categories: {list(data[\"categories\"].keys())}')
"
```

---

## Step 3: Update Make.com Scenarios

### 3.1 Assess Scenario Requirements

Determine if the new category needs:
- **Dedicated scenario**: For categories with unique posting requirements
- **Router addition**: For categories using existing scenario with filtering
- **No changes**: If using default posting flow

### 3.2 Add Router Filter (Recommended Approach)

1. Log into Make.com
2. Open the relevant Pinterest posting scenario
3. Add a Router module after the webhook (if not present)
4. Add a new route with filter:

**Filter Configuration:**
```
Condition: content_category equals "new_category_name"
```

5. Connect to Pinterest module configured for the new board

### 3.3 Create Dedicated Scenario (If Needed)

If the category requires special handling:

1. Clone existing Pinterest scenario
2. Rename to identify the category (e.g., "Pinterest - Kitchen Gadgets")
3. Update Pinterest module with new board ID
4. Configure any category-specific transformations
5. Save and activate the scenario
6. Copy the webhook URL

### 3.4 Update Environment Variables (If New Webhook)

If you created a new scenario with a new webhook:

```bash
# Add to .env file
MAKE_COM_PINTEREST_KITCHEN_WEBHOOK=https://hook.us1.make.com/xxxxx
```

Update `/utils/config.py`:

```python
@property
def make_com_pinterest_kitchen_webhook(self) -> str:
    return os.getenv("MAKE_COM_PINTEREST_KITCHEN_WEBHOOK", "")
```

Add to GitHub Secrets:
1. Repository > Settings > Secrets and variables > Actions
2. Add new secret with the webhook URL

Update workflow files in `.github/workflows/`:

```yaml
env:
  MAKE_COM_PINTEREST_KITCHEN_WEBHOOK: ${{ secrets.MAKE_COM_PINTEREST_KITCHEN_WEBHOOK }}
```

---

## Step 4: Update Claude/Gemini Prompts

### 4.1 Update Brand Configuration

Edit `/video_automation/video_content_generator.py`:

```python
BRAND_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "niche": "lifestyle deals, beauty finds, home organization, kitchen gadgets",  # Add new category
        "tone": "friendly, excited, relatable",
        "audience": "budget-conscious women 25-45",
        "content_categories": [
            "general_deals",
            "beauty",
            "home",
            "kitchen_gadgets"  # Add new category
        ],
        "category_prompts": {
            "kitchen_gadgets": {
                "focus": "affordable kitchen tools, gadgets, and organization products",
                "price_range": "under $30",
                "tone_modifier": "excited about cooking and kitchen organization",
                "avoid": ["expensive appliances", "professional chef equipment"]
            }
        }
    }
}
```

### 4.2 Update Content Generation Prompt

If using custom prompts per category, add category-specific instructions:

```python
def _get_category_prompt(self, brand: str, category: str) -> str:
    """Get category-specific prompt additions."""
    prompts = {
        "daily_deal_darling": {
            "kitchen_gadgets": """
            Focus on:
            - Practical kitchen tools under $30
            - Space-saving gadgets
            - Tools that simplify meal prep
            - Aesthetic but functional items
            - Products available on Amazon or Target

            Avoid:
            - Professional-grade equipment
            - Items over $30
            - Complex appliances
            - Brand-specific items without alternatives
            """
        }
    }
    return prompts.get(brand, {}).get(category, "")
```

### 4.3 Test Prompt Updates

```bash
python -c "
from video_automation.video_content_generator import VideoContentGenerator

generator = VideoContentGenerator()
content = generator.generate_video_content(
    brand='daily_deal_darling',
    content_type='tips',
    category='kitchen_gadgets'
)
print('Generated topic:', content['topic'])
print('Hook:', content['hook'])
"
```

---

## Step 5: Create Pinterest Board for New Category

### 5.1 Create the Board

Follow the detailed steps in [Add New Pinterest Boards](add-new-pinterest-boards.md).

Quick summary:
1. Log into Pinterest Business account
2. Create new board with SEO-optimized name
3. Write keyword-rich description
4. Set to Public visibility
5. Document the board ID/slug

**Example for Kitchen Gadgets:**
```
Board Name: Kitchen Gadgets & Finds | Daily Deal Darling
Board Slug: kitchen-gadgets-finds-daily-deal-darling
Description: Discover the best kitchen gadgets, tools, and organization
products under $30. Amazon kitchen finds, meal prep essentials, and
space-saving solutions for every home cook.
Category: Home Decor (or Food & Drink)
```

### 5.2 Add Initial Pins (Recommended)

Before automation starts, add 5-10 manual pins to:
- Establish board topic for Pinterest algorithm
- Provide content for new followers
- Test board visibility

---

## Step 6: Set Up Tracking in Supabase

### 6.1 Add Category to Analytics Schema

If not already present, add category tracking:

```sql
-- Run in Supabase SQL Editor

-- Add category column to videos table if not exists
ALTER TABLE videos
ADD COLUMN IF NOT EXISTS content_category VARCHAR(100);

-- Create index for category queries
CREATE INDEX IF NOT EXISTS idx_videos_content_category
ON videos(content_category);

-- Add category to analytics table if tracking separately
ALTER TABLE analytics
ADD COLUMN IF NOT EXISTS content_category VARCHAR(100);
```

### 6.2 Create Category Performance View

```sql
-- Create view for category performance tracking
CREATE OR REPLACE VIEW category_performance AS
SELECT
    brand,
    content_category,
    COUNT(*) as total_videos,
    COUNT(CASE WHEN status = 'posted' THEN 1 END) as successful_posts,
    AVG(CASE WHEN status = 'posted' THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
    MIN(created_at) as first_post,
    MAX(created_at) as last_post
FROM videos
WHERE content_category IS NOT NULL
GROUP BY brand, content_category
ORDER BY brand, total_videos DESC;
```

### 6.3 Verify Tracking Setup

```bash
python -c "
from database.supabase_client import get_supabase_client

db = get_supabase_client()
# Test category tracking
result = db.log_video_creation(
    brand='daily_deal_darling',
    platform='pinterest',
    content_category='kitchen_gadgets',
    topic='Test kitchen topic',
    status='test'
)
print('Category tracking working:', result is not None)

# Clean up test
db.delete_test_records()
"
```

---

## Step 7: Test New Category Content Generation

### 7.1 Dry Run Test

```bash
# Test content generation for new category
python -m video_automation.daily_video_generator \
    --brand daily_deal_darling \
    --category kitchen_gadgets \
    --dry-run

# Expected output:
# - Content topic related to kitchen gadgets
# - Appropriate hashtags
# - Correct target board
```

### 7.2 Full Integration Test

```bash
# Test full pipeline (will post to platform)
python -c "
from video_automation.daily_video_generator import DailyVideoGenerator

generator = DailyVideoGenerator()
result = generator.generate_and_post(
    brand='daily_deal_darling',
    content_type='tips',
    category='kitchen_gadgets',
    test_mode=True  # Posts to test board if configured
)
print('Result:', result)
"
```

### 7.3 Verify Post on Pinterest

1. Log into Pinterest
2. Navigate to the new category board
3. Verify the test pin appears correctly
4. Check title, description, and hashtags
5. Delete test pin after verification

---

## Step 8: Monitor Initial Performance

### 8.1 First Week Monitoring

Track these metrics daily for the first week:

| Metric | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | Day 6 | Day 7 |
|--------|-------|-------|-------|-------|-------|-------|-------|
| Posts Created | | | | | | | |
| Posting Success % | | | | | | | |
| Impressions | | | | | | | |
| Saves | | | | | | | |
| Errors | | | | | | | |

### 8.2 Performance Thresholds

Evaluate category viability after 2 weeks:

| Metric | Minimum Threshold | Action if Below |
|--------|-------------------|-----------------|
| Posting Success Rate | 90% | Fix technical issues |
| Impressions per Pin | 100 | Adjust keywords/hashtags |
| Save Rate | 1% | Improve content quality |
| Error Rate | <10% | Debug and fix issues |

### 8.3 Adjustment Period

If performance is below thresholds after 2 weeks:

1. **Review content topics** - Are they relevant to the audience?
2. **Check hashtags** - Are they discoverable but not too competitive?
3. **Evaluate board setup** - Is the board properly optimized?
4. **Test different hooks** - Try new hook styles
5. **Adjust posting frequency** - May need more or fewer posts

---

## Troubleshooting Common Issues

### Category Content Not Generating

**Symptom:** Content generator skips the new category.

**Fixes:**
1. Verify category is in the correct JSON file
2. Check `enabled` flag is `true`
3. Verify JSON syntax is valid
4. Check category weight is > 0

```bash
python -c "
import json
with open('video_automation/content_bank/deal_topics.json') as f:
    data = json.load(f)
    cat = data['categories'].get('kitchen_gadgets')
    if cat:
        print('Enabled:', cat.get('enabled'))
        print('Weight:', cat.get('weight'))
        print('Topics count:', len(cat.get('topics', [])))
    else:
        print('Category not found!')
"
```

### Posts Going to Wrong Board

**Symptom:** Category content posted to default board instead of category board.

**Fixes:**
1. Verify `target_board` is set correctly in JSON
2. Check Make.com router filter conditions
3. Verify category is being passed through the webhook payload
4. Check board ID/slug matches Pinterest exactly

### Low Engagement on New Category

**Symptom:** New category posts have significantly lower engagement than existing content.

**Fixes:**
1. Analyze successful competitors' content in this category
2. A/B test different hook styles
3. Adjust posting time for this category
4. Review and improve hashtag selection
5. Consider if category truly fits audience

### Make.com Scenario Errors

**Symptom:** Webhook calls fail or scenario shows errors.

**Fixes:**
1. Test webhook manually with curl
2. Check scenario execution history for error details
3. Verify Pinterest connection is still valid
4. Check board exists and is accessible
5. Verify video URL is accessible

---

## Rollback Procedure

If the new category causes issues:

### Immediate Disable

1. Set `enabled: false` in the category JSON:
   ```json
   "new_category": {
       "enabled": false,
       ...
   }
   ```

2. Disable Make.com route (if dedicated):
   - Open scenario
   - Toggle route OFF

### Full Rollback

1. Revert code changes:
   ```bash
   git checkout HEAD~1 -- video_automation/content_bank/deal_topics.json
   git checkout HEAD~1 -- video_automation/video_content_generator.py
   ```

2. Remove environment variables from GitHub Secrets

3. Delete or archive Pinterest board (optional)

4. Document rollback reason for future reference

---

## Documentation Updates

After successfully adding a new category, update:

1. **CLAUDE.md** - Add category to brand documentation
2. **Content Bank README** - Document new category structure
3. **This SOP** - Add any lessons learned
4. **Performance Monitoring SOP** - Add category-specific metrics to track

---

## Related Procedures

- [Add New Pinterest Boards](add-new-pinterest-boards.md)
- [Performance Monitoring](performance-monitoring.md)
- [Troubleshooting Guide](troubleshooting-guide.md)
- [Weekly Maintenance Checklist](weekly-maintenance-checklist.md)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-28 | 1.0 | Initial creation |
