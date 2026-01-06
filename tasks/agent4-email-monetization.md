# Agent 4: Email Monetization Setup

**Started:** January 6, 2026
**Status:** COMPLETE

---

## Summary

Agent 4 has set up the email marketing infrastructure for quiz-based email capture using ConvertKit (now called Kit). This system captures emails after quiz completions and sends personalized product recommendations via a 5-email welcome sequence.

---

## Files Created

| File | Purpose |
|------|---------|
| `core/convertkit_client.py` | Python API client for ConvertKit |
| `content/email_templates/email_1_quiz_results.md` | Immediate: Quiz results + top picks |
| `content/email_templates/email_2_common_mistake.md` | Day 2: Common mistake education |
| `content/email_templates/email_3_reader_favorite.md` | Day 4: Single product focus |
| `content/email_templates/email_4_new_arrivals.md` | Day 7: Fresh products + urgency |
| `content/email_templates/email_5_hidden_gems.md` | Day 14: Re-engage + high-margin products |
| `content/email_templates/etsy_product_mapping.json` | Etsy product mappings for Menopause Planner |

---

## Task 1: ConvertKit Setup (MANUAL REQUIRED)

### Step 1: Create Account
1. Go to https://kit.com (formerly convertkit.com)
2. Sign up for FREE account (up to 10,000 subscribers free)
3. Complete email verification

### Step 2: Create Form
1. Go to **Grow** > **Landing Pages & Forms**
2. Click **Create New** > **Form**
3. Name it: "Get Your Personalized Product Guide"
4. Design the form with fields:
   - Email (required)
   - First Name (optional)
5. Save and get the Form ID from the URL

### Step 3: Create Tags
Create the following tags in **Grow** > **Subscribers** > **Tags**:

**Quiz Type Tags:**
- `quiz-morning`
- `quiz-organization`
- `quiz-selfcare`
- `quiz-beauty`
- `quiz-lifestyle`

**Brand Tags:**
- `daily-deal-darling`
- `menopause-planner`

### Step 4: Get API Credentials
1. Go to **Settings** > **Advanced** > **API**
2. Copy your **API Key**
3. Copy your **API Secret** (for subscriber lookups)

### Step 5: Add to GitHub Secrets
Go to: https://github.com/talhahbilal1-arch/social-media-empire/settings/secrets/actions

Add these secrets:
```
CONVERTKIT_API_KEY = [your API key]
CONVERTKIT_API_SECRET = [your API secret]
CONVERTKIT_FORM_ID = [your form ID]
```

---

## Task 2: Quiz Email Capture Integration

### How It Works

The `core/convertkit_client.py` provides:

1. **ConvertKitClient** - Low-level API wrapper
2. **QuizEmailCapture** - High-level helper for quiz flows
3. **capture_quiz_email()** - Quick function for immediate use

### Usage Example

```python
from core.convertkit_client import capture_quiz_email

# After quiz completion on dailydealdarling.com
result = capture_quiz_email(
    email="user@example.com",
    quiz_type="morning",
    quiz_result="early_bird",
    brand="daily-deal-darling",
    first_name="Jane"
)

# Result includes:
# - subscribed: True/False
# - subscriber_id: ConvertKit subscriber ID
# - tags_applied: List of tag IDs
# - recommendations: List of product recommendations
```

### For Quiz Pages

Add this JavaScript/API call AFTER quiz results display, BEFORE showing product recommendations:

```javascript
// Example frontend implementation
async function captureQuizEmail(email, firstName) {
    const response = await fetch('/api/quiz-subscribe', {
        method: 'POST',
        body: JSON.stringify({
            email: email,
            first_name: firstName,
            quiz_type: currentQuizType,
            quiz_result: userQuizResult,
            brand: 'daily-deal-darling'
        })
    });
    return response.json();
}
```

---

## Task 3: Email Sequence (5 Emails)

### Sequence Overview

| Email | Day | Subject | Goal |
|-------|-----|---------|------|
| 1 | Immediate | "Your [Quiz] Results + Top Picks" | Deliver value, first products |
| 2 | Day 2 | "The #1 Mistake [Quiz] People Make" | Educate, build authority |
| 3 | Day 4 | "Reader Favorite: [Product]" | Social proof, single focus |
| 4 | Day 7 | "New Arrivals for Your [Quiz]" | Fresh products, urgency |
| 5 | Day 14 | "Hidden Gems" | Re-engage, higher margins |

### Setting Up in ConvertKit

1. Go to **Send** > **Sequences**
2. Click **Create Sequence**
3. Name it: "Quiz Welcome Sequence"
4. Add 5 emails using the templates from `content/email_templates/`
5. Set timing: Immediate, Day 2, Day 4, Day 7, Day 14
6. Link to your form as the trigger

### Template Variables

All templates use these variables (configure in ConvertKit):
- `{{first_name}}` - subscriber's first name
- `{{quiz_type}}` - type of quiz taken
- `{{quiz_result}}` - their result category
- Product-specific variables for each email

---

## Task 4: Etsy Product Connections

### Menopause Planner Brand

For quiz results on The Menopause Planner brand, include Etsy product recommendations alongside Amazon products.

### Product Mapping

See `content/email_templates/etsy_product_mapping.json` for full mapping.

| Quiz Result | Recommended Etsy Products |
|-------------|--------------------------|
| Early Menopause | Symptom Tracker, Hormone Tracker |
| Perimenopause | Hormone Tracker, Mood Tracker, Symptom Tracker |
| Hot Flash Heavy | Hot Flash Journal, Sleep Log |
| Mood Focused | Mood Tracker, Wellness Planner |
| Sleep Issues | Sleep Log, Mood Tracker |
| General | Wellness Planner, Symptom Tracker |

### Implementation

The `QuizEmailCapture` class automatically includes Etsy recommendations for Menopause Planner brand:

```python
result = capture_quiz_email(
    email="user@example.com",
    quiz_type="symptoms",
    quiz_result="hot_flash_heavy",
    brand="menopause-planner"  # This triggers Etsy recommendations
)

# result['recommendations'] will include:
# - Hot Flash Journal
# - Sleep Log
```

---

## Task 5: Testing the Full Flow

### Test Checklist

1. **ConvertKit Account**
   - [ ] Account created and verified
   - [ ] Form created with correct fields
   - [ ] All tags created
   - [ ] API credentials added to GitHub Secrets

2. **API Integration**
   - [ ] Test with `capture_quiz_email()` function
   - [ ] Verify subscriber appears in ConvertKit
   - [ ] Verify tags are applied correctly
   - [ ] Verify custom fields populate

3. **Email Sequence**
   - [ ] Sequence created with 5 emails
   - [ ] Timing set correctly (0, 2, 4, 7, 14 days)
   - [ ] Form linked as trigger
   - [ ] Test send to yourself

4. **Etsy Products (Menopause Planner)**
   - [ ] Verify Etsy links work
   - [ ] Verify correct products recommended for each quiz result

### Test Script

```python
# test_convertkit.py
import os
os.environ['CONVERTKIT_API_KEY'] = 'your_test_key'
os.environ['CONVERTKIT_FORM_ID'] = 'your_form_id'

from core.convertkit_client import ConvertKitClient, capture_quiz_email

# Test 1: Get tags
client = ConvertKitClient()
tags = client.get_tags()
print(f"Tags found: {len(tags)}")

# Test 2: Capture quiz email
result = capture_quiz_email(
    email="test@example.com",
    quiz_type="morning",
    quiz_result="early_bird",
    brand="daily-deal-darling"
)
print(f"Subscribed: {result['subscribed']}")
print(f"Tags applied: {result['tags_applied']}")
```

---

## Revenue Projections

### Assumptions
- Quiz completion rate: 60%
- Email capture rate: 30% of completers
- Email open rate: 35%
- Click rate: 5%
- Conversion rate: 3%
- Average order: $35
- Commission: 4% (Amazon Associates)

### Monthly Estimate (per 1,000 quiz takers)
- 600 complete quiz
- 180 submit email
- 63 open emails (avg)
- 9 click product links
- ~3 purchases
- = ~$4.20 commission/1,000 quiz takers

**At scale (10,000 quiz takers/month):** ~$42/month passive from email sequence alone

---

## Next Steps

1. **Complete ConvertKit manual setup** (see Task 1)
2. **Add GitHub Secrets** for API credentials
3. **Create email sequence in ConvertKit** using templates
4. **Integrate with quiz pages** on dailydealdarling.com
5. **Monitor performance** and optimize subject lines

---

## Files Changed This Session

1. `core/convertkit_client.py` - NEW
2. `content/email_templates/email_1_quiz_results.md` - NEW
3. `content/email_templates/email_2_common_mistake.md` - NEW
4. `content/email_templates/email_3_reader_favorite.md` - NEW
5. `content/email_templates/email_4_new_arrivals.md` - NEW
6. `content/email_templates/email_5_hidden_gems.md` - NEW
7. `content/email_templates/etsy_product_mapping.json` - NEW
8. `tasks/agent4-email-monetization.md` - Updated

---

## Review

**What was done:**
- Created ConvertKit API client with full functionality
- Created 5-email welcome sequence templates with personalization
- Set up Etsy product mapping for Menopause Planner brand
- Documented complete setup process

**What requires manual action:**
- ConvertKit account creation and configuration
- Adding API secrets to GitHub
- Creating the email sequence in ConvertKit UI
- Integrating email capture with existing quiz pages

**No files touched from other agents:**
- Did NOT modify: Make.com, video_factory.py, content_brain.py, YouTube, Repurpose.io
