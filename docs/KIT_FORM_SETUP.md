# Kit (ConvertKit) Form Setup Guide

## Overview

Each brand has an email capture popup and a `/free-guide` landing page that submit to Kit forms. The form action URLs currently contain placeholder IDs that need to be replaced with real Kit Form IDs.

## Step 1: Create Kit Forms

1. Log in to [Kit](https://app.kit.com)
2. Go to **Grow** > **Landing Pages & Forms** > **Create New** > **Form**
3. Create 3 forms (one per brand):

| Brand | Form Name | Tag to Apply |
|-------|-----------|--------------|
| FitOver35 | "FitOver35 - Free Meal Plan" | `fitover35-lead-magnet` |
| Daily Deal Darling | "DDD - Weekly Deals" | `ddd-lead-magnet` |
| Menopause Planner | "Menopause - Symptom Tracker" | `menopause-lead-magnet` |

4. For each form, set up:
   - **Incentive email**: Deliver the lead magnet PDF
   - **Tag**: Apply the brand-specific tag above
   - **Sequence**: Connect to the existing welcome sequence (see `email_marketing/sequences/`)
     - FitOver35 → `fitover35_welcome_sequence.md`
     - DDD → `daily_deal_darling_welcome_sequence.md`
     - Menopause → `menopause_planner_welcome_sequence.md`

## Step 2: Get Form IDs

1. After creating each form, click **Publish** or go to form settings
2. The Form ID is in the embed code URL: `https://app.kit.com/forms/XXXXXXX/subscriptions`
3. Copy the numeric ID (e.g., `7654321`)

## Step 3: Replace Placeholder IDs

Run these commands from the repo root to swap placeholders with real IDs:

```bash
# Replace FITOVER35_FORM_ID with your real ID
find outputs/fitover35-website -name '*.html' -exec sed -i 's/FITOVER35_FORM_ID/YOUR_REAL_ID/g' {} +

# Replace DDD_FORM_ID with your real ID
find dailydealdarling_website -name '*.html' -exec sed -i 's/DDD_FORM_ID/YOUR_REAL_ID/g' {} +

# Replace MENOPAUSE_FORM_ID with your real ID
find menopause-planner-site -name '*.html' -exec sed -i 's/MENOPAUSE_FORM_ID/YOUR_REAL_ID/g' {} +
```

**Example** (if FitOver35 Form ID is `7654321`):
```bash
find outputs/fitover35-website -name '*.html' -exec sed -i 's/FITOVER35_FORM_ID/7654321/g' {} +
```

## Step 4: Verify

After replacing, verify the forms work:

```bash
# Check no placeholders remain
grep -r 'FITOVER35_FORM_ID\|DDD_FORM_ID\|MENOPAUSE_FORM_ID' outputs/fitover35-website/ dailydealdarling_website/ menopause-planner-site/
```

If the command returns no output, all placeholders have been replaced.

## Files Affected

- `outputs/fitover35-website/email-capture.js` — popup form
- `outputs/fitover35-website/free-guide.html` — landing page form
- `outputs/fitover35-website/articles/*.html` — popup (via shared JS)
- `dailydealdarling_website/email-capture.js` — popup form
- `dailydealdarling_website/free-guide.html` — landing page form
- `dailydealdarling_website/articles/*.html` — popup (via shared JS)
- `dailydealdarling_website/quizzes/*.html` — popup (via shared JS)
- `menopause-planner-site/email-capture.js` — popup form
- `menopause-planner-site/free-guide.html` — landing page form

## Existing Welcome Sequences

Reference these when configuring Kit automation rules:
- `email_marketing/sequences/fitover35_welcome_sequence.md`
- `email_marketing/sequences/daily_deal_darling_welcome_sequence.md`
- `email_marketing/sequences/menopause_planner_welcome_sequence.md`
- `email_marketing/sequences/reengagement_sequence.md`
