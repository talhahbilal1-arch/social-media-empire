# Add New Pinterest Boards

## Overview

This procedure guides you through adding new Pinterest boards to the Social Media Empire automation system. New boards may be needed when expanding a brand's content categories, targeting new audience segments, or optimizing content distribution based on Pinterest analytics.

## Prerequisites

- Pinterest Business account access for the relevant brand
- Access to Make.com for webhook configuration
- Repository write access to update configuration files
- Understanding of the brand's content strategy
- Pinterest board naming conventions

---

## When to Add New Boards

Consider adding new Pinterest boards when:

1. **New Content Category**: Launching a new content type (e.g., "Holiday Gift Guides" for Daily Deal Darling)
2. **Audience Segmentation**: Targeting a specific sub-audience (e.g., "Night Shift Tips" for Nurse Planner)
3. **Seasonal Content**: Creating seasonal collections (e.g., "Summer Wellness" for Menopause Planner)
4. **Performance Optimization**: Pinterest analytics show certain topics perform better separately
5. **SEO Strategy**: Creating boards optimized for Pinterest search keywords

### Board Strategy Guidelines

| Brand | Current Boards | Potential New Boards |
|-------|---------------|---------------------|
| daily_deal_darling | daily-deal-darling-tips | beauty-finds, home-organization, seasonal-deals |
| menopause_planner | menopause-wellness-tips | hot-flash-relief, sleep-tips, hormone-health |
| nurse_planner | nurse-life-tips | shift-survival, self-care-for-nurses, scrub-style |
| adhd_planner | adhd-productivity-tips | focus-hacks, time-management, adhd-friendly-spaces |

---

## Step 1: Create Board in Pinterest

### 1.1 Log into Pinterest Business Account

1. Go to pinterest.com and log in with the brand's business account
2. Verify you're in the correct account by checking the profile name

### 1.2 Create the New Board

1. Click the "+" button or "Create Board"
2. Enter board details:
   - **Name**: Use a descriptive, keyword-rich name (50-100 characters)
   - **Description**: Write SEO-optimized description (up to 500 characters)
   - **Category**: Select the most relevant category
   - **Visibility**: Set to "Public" for maximum reach

3. Example for Daily Deal Darling "Beauty Finds" board:
   ```
   Name: Beauty Finds & Makeup Deals | Daily Deal Darling
   Description: Discover the best drugstore dupes, Amazon beauty finds,
   and affordable makeup products. Budget-friendly skincare routines and
   beauty tips for every occasion. Save money while looking amazing!
   Category: Beauty
   ```

### 1.3 Get the Board ID

1. Open the newly created board
2. Look at the URL: `https://pinterest.com/username/board-name/`
3. The board slug (e.g., `beauty-finds-makeup-deals-daily-deal-darling`) is used in the code
4. For Make.com, you may need the numeric board ID:
   - Click Settings (gear icon) on the board
   - The numeric ID appears in some API responses
   - Or use the slug format with Make.com's Pinterest module

**Document the Board:**
```
Board Name: Beauty Finds & Makeup Deals | Daily Deal Darling
Board Slug: beauty-finds-makeup-deals-daily-deal-darling
Board ID (numeric): [if needed]
Created: [date]
Purpose: Beauty and makeup related deals and finds
Target Content: Drugstore dupes, Amazon beauty, skincare routines
```

---

## Step 2: Update Make.com Scenarios

### 2.1 Access Make.com Dashboard

1. Log into Make.com
2. Navigate to "Scenarios"
3. Find the Pinterest posting scenario

### 2.2 Option A: Use Existing Scenario with Board Selection

If your scenario supports dynamic board selection:

1. The scenario should have a Router or conditional logic
2. Add a new route for the board:
   - Add a filter condition (e.g., `board_name equals "beauty-finds"`)
   - Connect to a Pinterest module configured for the new board
   - Set up the pin creation parameters

3. Test the route:
   ```json
   // Test webhook payload
   {
     "type": "idea_pin",
     "board_id": "beauty-finds-makeup-deals-daily-deal-darling",
     "title": "Test Beauty Pin",
     "pages": [
       {
         "media_url": "https://example.com/test-video.mp4",
         "description": "Test description"
       }
     ]
   }
   ```

### 2.3 Option B: Create New Scenario for Board

If a dedicated scenario is needed:

1. Clone the existing Pinterest scenario
2. Rename it (e.g., "Pinterest - Beauty Finds Board")
3. Update the Pinterest module to point to the new board:
   - Open the Pinterest "Create Pin" module
   - Change the Board field to the new board ID/slug
4. Save and enable the scenario
5. Copy the new webhook URL

### 2.4 Get the Webhook URL

1. Click on the Webhook module in your scenario
2. Copy the URL displayed
3. This URL will be used in the code configuration
4. Example format: `https://hook.us1.make.com/xxxxxxxxxxxxxxxxx`

---

## Step 3: Update Code Configuration

### 3.1 Update Brand Platform Config

Edit `/video_automation/cross_platform_poster.py`:

```python
# Find the BRAND_PLATFORM_CONFIG dictionary
BRAND_PLATFORM_CONFIG = {
    "daily_deal_darling": {
        "pinterest_board_id": "daily-deal-darling-tips",  # Default board
        # Add additional boards
        "pinterest_boards": {
            "tips": "daily-deal-darling-tips",
            "beauty": "beauty-finds-makeup-deals-daily-deal-darling",
            "home": "home-organization-deals",
            "seasonal": "seasonal-deals-and-finds"
        },
        "youtube_playlist_id": None,
        "tiktok_account": "dailydealdarling",
        "instagram_account": "dailydealdarling"
    },
    # ... other brands
}
```

### 3.2 Update Content Bank (if needed)

If the new board needs specific content types, add to `/video_automation/content_bank/deal_topics.json`:

```json
{
  "categories": {
    "beauty": {
      "topics": [
        "Drugstore dupes for high-end products",
        "Amazon beauty finds under $20",
        "Skincare routine on a budget"
      ],
      "target_board": "beauty-finds-makeup-deals-daily-deal-darling"
    }
  }
}
```

### 3.3 Update Pinterest Posting Logic

If board selection needs to be dynamic, edit `/video_automation/pinterest_idea_pins.py`:

```python
def create_video_idea_pin(
    self,
    board_id: str,
    title: str,
    description: str,
    video_url: str,
    link: Optional[str] = None,
    content_category: Optional[str] = None  # Add category parameter
) -> dict:
    """Create a video-based Idea Pin.

    Args:
        board_id: Pinterest board ID or name (or auto-select based on category)
        title: Pin title (max 100 characters)
        description: Pin description
        video_url: URL of the video to pin
        link: Optional destination link
        content_category: Optional category for board selection
    """
    # If category provided, look up the appropriate board
    if content_category:
        board_id = self._get_board_for_category(board_id, content_category)

    # ... rest of the method
```

### 3.4 Update Environment Variables (if new webhook)

If you created a new Make.com scenario:

1. Add new environment variable:
   ```bash
   # .env file
   MAKE_COM_PINTEREST_BEAUTY_WEBHOOK=https://hook.us1.make.com/xxxxx
   ```

2. Update `/utils/config.py` to include the new webhook:
   ```python
   @property
   def make_com_pinterest_beauty_webhook(self) -> str:
       return os.getenv("MAKE_COM_PINTEREST_BEAUTY_WEBHOOK", "")
   ```

3. Add to GitHub Secrets:
   - Repository > Settings > Secrets and variables > Actions
   - Add `MAKE_COM_PINTEREST_BEAUTY_WEBHOOK`

4. Update workflow files to include the new secret:
   ```yaml
   # In .github/workflows/video-automation-*.yml
   env:
     MAKE_COM_PINTEREST_BEAUTY_WEBHOOK: ${{ secrets.MAKE_COM_PINTEREST_BEAUTY_WEBHOOK }}
   ```

---

## Step 4: Update Content Generation Prompts

### 4.1 Update Video Content Generator

Edit `/video_automation/video_content_generator.py` to include board-specific content generation:

```python
# In BRAND_CONFIG, add board-specific configurations
BRAND_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "niche": "lifestyle deals, beauty finds, home organization",
        "tone": "friendly, excited, relatable",
        "audience": "budget-conscious women 25-45",
        "board_content_focus": {
            "daily-deal-darling-tips": {
                "focus": "general deals and lifestyle tips",
                "hashtags": ["#deals", "#amazonfinds", "#budgetfriendly"]
            },
            "beauty-finds-makeup-deals-daily-deal-darling": {
                "focus": "beauty products, makeup dupes, skincare",
                "hashtags": ["#beautyfinds", "#drugstoremakeup", "#skincaretips", "#makeupdupes"]
            }
        }
    }
}
```

### 4.2 Update Topic Selection

Modify topic generation to consider the target board:

```python
def _generate_topic(self, brand: str, content_type: str, target_board: str = None) -> str:
    """Generate a topic using AI based on brand and content type."""
    brand_config = BRAND_CONFIG.get(brand, BRAND_CONFIG["daily_deal_darling"])

    # Get board-specific focus if available
    board_focus = ""
    if target_board and "board_content_focus" in brand_config:
        board_config = brand_config["board_content_focus"].get(target_board, {})
        board_focus = f"\nContent focus for this board: {board_config.get('focus', '')}"

    prompt = f"""Generate ONE specific, engaging video topic for {brand_config['name']}.
Niche: {brand_config['niche']}
Audience: {brand_config['audience']}
Content type: {content_type}
{board_focus}

Return ONLY the topic as a single line, no explanation."""

    topic = self.gemini_client.generate_content(prompt, max_tokens=100)
    return topic.strip().strip('"').strip("'")
```

---

## Step 5: Testing Procedures

### 5.1 Test Make.com Webhook

```bash
# Test the webhook directly
curl -X POST "YOUR_NEW_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "idea_pin",
       "board_id": "beauty-finds-makeup-deals-daily-deal-darling",
       "title": "Test Pin - Please Delete",
       "pages": [
         {
           "media_url": "https://www.pexels.com/video/123456/",
           "description": "Test description for automation"
         }
       ]
     }'
```

Expected response: HTTP 200 with success message

### 5.2 Test Pinterest Posting via Code

```bash
python -c "
from video_automation.pinterest_idea_pins import PinterestIdeaPinCreator

poster = PinterestIdeaPinCreator()

# Test posting to the new board
result = poster.create_video_idea_pin(
    board_id='beauty-finds-makeup-deals-daily-deal-darling',
    title='[TEST] Automation Test Pin',
    description='Testing the new board configuration. Please delete.',
    video_url='https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
)

print('Result:', result)
"
```

### 5.3 Verify Pin Appears on Pinterest

1. Log into Pinterest
2. Navigate to the new board
3. Verify the test pin appears
4. Delete the test pin after verification

### 5.4 Test Full Content Generation Pipeline

```bash
# Dry run with the new board configuration
python -m video_automation.daily_video_generator \
    --brand daily_deal_darling \
    --dry-run \
    --content-category beauty

# Check the output for:
# - Correct board selection
# - Appropriate content topics
# - Proper hashtags for the board
```

### 5.5 Test Workflow Run

1. Trigger a manual workflow run:
   - Go to GitHub Actions
   - Select "Video Automation - Morning"
   - Click "Run workflow"
   - Use `dry_run: true` for testing

2. Monitor the workflow execution
3. Check logs for any board-related errors

---

## Troubleshooting

### Board Not Found Error

**Symptom:** "Board not found" error when posting

**Fixes:**
1. Verify board ID/slug is correct
2. Check the board is public (not secret)
3. Verify Pinterest account has access to the board
4. Re-authenticate Pinterest in Make.com

### Pin Created on Wrong Board

**Symptom:** Pins appearing on default board instead of new board

**Fixes:**
1. Check board selection logic in code
2. Verify webhook is configured correctly
3. Check Make.com scenario routing conditions
4. Ensure environment variables are updated

### Content Not Matched to Board

**Symptom:** Generic content instead of board-specific content

**Fixes:**
1. Verify content bank has board-specific entries
2. Check content category parameter is passed
3. Update prompt templates with board context

---

## Rollback Procedure

If issues occur after adding a new board:

1. **Immediate:** Disable the new board routing in Make.com
2. **Code Rollback:**
   ```bash
   git checkout HEAD~1 -- video_automation/cross_platform_poster.py
   git checkout HEAD~1 -- video_automation/pinterest_idea_pins.py
   ```
3. **Remove environment variables** from GitHub Secrets
4. **Document the issue** for future debugging

---

## Documentation Updates

After successfully adding a new board, update:

1. **CLAUDE.md** - Add the new board to brand configuration documentation
2. **Content Bank README** - Document new content categories
3. **This SOP** - Add any lessons learned or new steps discovered

---

## Related Procedures

- [Troubleshooting Guide](troubleshooting-guide.md)
- [Add New Product Categories](add-new-product-categories.md)
- [Performance Monitoring](performance-monitoring.md)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-27 | 1.0 | Initial creation |
