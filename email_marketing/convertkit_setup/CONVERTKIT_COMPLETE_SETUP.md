# ConvertKit Complete Setup Guide

## Overview
This guide covers setting up ConvertKit for all Social Media Empire brands with automated email sequences, tagging, and integration.

---

## Account Structure

### Forms (One per brand/lead magnet)

| Form Name | Brand | Lead Magnet | Form ID |
|-----------|-------|-------------|---------|
| DDD - Main Signup | Daily Deal Darling | Free Deals Guide | [FORM_ID] |
| DDD - Quiz Result | Daily Deal Darling | Quiz Results | [FORM_ID] |
| Menopause - Symptom Tracker | Menopause Planner | Symptom Tracker PDF | [FORM_ID] |
| Menopause - Quiz | Menopause Planner | Quiz Results | [FORM_ID] |
| Nurse - Shift Planner | Nurse Planner | Shift Planner PDF | [FORM_ID] |
| ADHD - Productivity Guide | ADHD Planner | Productivity Guide | [FORM_ID] |

### Tags Structure

```
📁 Brands
  ├── brand-daily-deal-darling
  ├── brand-menopause-planner
  ├── brand-nurse-planner
  └── brand-adhd-planner

📁 Source
  ├── source-website-popup
  ├── source-website-inline
  ├── source-website-footer
  ├── source-quiz
  ├── source-social-media
  └── source-referral

📁 Lead Magnets
  ├── lead-magnet-deals-guide
  ├── lead-magnet-symptom-tracker
  ├── lead-magnet-shift-planner
  └── lead-magnet-adhd-guide

📁 Engagement
  ├── engagement-high (opened 5+ emails)
  ├── engagement-medium (opened 2-4 emails)
  ├── engagement-low (opened 0-1 emails)
  └── engagement-clicked-link

📁 Sequences
  ├── sequence-welcome-started
  ├── sequence-welcome-completed
  └── sequence-newsletter-active

📁 Interests (from quiz/behavior)
  ├── interest-beauty
  ├── interest-home
  ├── interest-lifestyle
  ├── interest-hot-flashes
  ├── interest-sleep
  └── interest-productivity
```

---

## Automation Sequences

### Sequence 1: Welcome Sequence (All Brands)

**Trigger**: Subscribes to any form
**Duration**: 14 days, 7 emails

```
Day 0: Welcome + Lead Magnet Delivery
  └── Add tag: sequence-welcome-started

Day 2: Quick Win / Most Popular Product
  └── Check: Opened email 1?
      ├── Yes: Continue
      └── No: Send reminder with different subject line

Day 4: Value Email (Tips)

Day 6: Personal Story

Day 8: Category Spotlight

Day 11: Social Proof

Day 14: Re-engagement + Clear CTA
  └── Add tag: sequence-welcome-completed
  └── Add tag: sequence-newsletter-active
```

### Sequence 2: Re-engagement Sequence

**Trigger**: No opens in 30 days
**Duration**: 7 days, 3 emails

```
Day 0: "We miss you!" email
  └── Subject: "Are you still interested in [benefit]?"

Day 3: Value email with compelling content
  └── Subject: "[First Name], you're missing out on this"

Day 7: Final email
  └── Subject: "Last chance before we part ways 💔"
  └── If no open: Add tag: unengaged-remove
```

### Sequence 3: Post-Purchase Sequence (Future)

**Trigger**: Purchase tag added
**Duration**: 7 days, 4 emails

```
Day 0: Thank you + What's next
Day 1: How to get started
Day 3: Tips for success
Day 7: Request for review/feedback
```

---

## Visual Automations

### Automation 1: New Subscriber Flow

```
[Form Submitted]
       │
       ▼
[Add Brand Tag]
       │
       ▼
[Add Source Tag]
       │
       ▼
[Send to Welcome Sequence]
       │
       ▼
[Wait 14 days]
       │
       ▼
[Check: Completed sequence?]
       │
   ┌───┴───┐
   │       │
  Yes     No
   │       │
   ▼       ▼
[Add to   [Send sequence
 Newsletter] reminder]
```

### Automation 2: Engagement Scoring

```
[Email Opened]
       │
       ▼
[Increment open_count field]
       │
       ▼
[Check: open_count >= 5?]
       │
   ┌───┴───┐
   │       │
  Yes     No
   │       │
   ▼       ▼
[Add tag:  [Check: open_count >= 2?]
 high-           │
 engagement]  ┌──┴──┐
             Yes   No
              │     │
              ▼     ▼
         [Add tag: [Add tag:
          medium-   low-
          engagement] engagement]
```

---

## API Integration

### Webhook Endpoints

Configure these webhooks in ConvertKit:

1. **New Subscriber**
   - URL: `https://yoursite.com/api/webhooks/convertkit/subscriber`
   - Events: subscriber.subscriber_activate

2. **Tag Added**
   - URL: `https://yoursite.com/api/webhooks/convertkit/tag`
   - Events: subscriber.tag_add

3. **Form Submitted**
   - URL: `https://yoursite.com/api/webhooks/convertkit/form`
   - Events: subscriber.form_subscribe

### API Credentials

Store these in your environment:
```
CONVERTKIT_API_KEY=your_api_key_here
CONVERTKIT_API_SECRET=your_api_secret_here
CONVERTKIT_FORM_ID_DDD=12345
CONVERTKIT_FORM_ID_MENOPAUSE=12346
CONVERTKIT_FORM_ID_NURSE=12347
CONVERTKIT_FORM_ID_ADHD=12348
```

---

## Email Templates

### Template Variables

Always available:
- `{{ subscriber.first_name }}` - First name
- `{{ subscriber.email_address }}` - Email
- `{{ subscriber.created_at }}` - Signup date

Custom fields to create:
- `lead_magnet_name` - Name of downloaded lead magnet
- `quiz_result` - Result from quiz
- `brand` - Which brand they signed up for

### Brand-Specific Templates

Create email templates for each brand with correct:
- Logo
- Colors
- Footer
- Social links
- Reply-to address

---

## Reporting & Analytics

### Key Metrics to Track

1. **Form Performance**
   - Conversion rate per form
   - Source of subscribers

2. **Sequence Performance**
   - Open rate per email
   - Click rate per email
   - Completion rate

3. **Engagement**
   - Active subscriber %
   - Unsubscribe rate
   - Growth rate

### Weekly Report Automation

Set up a Zap or automation to:
1. Pull ConvertKit stats via API
2. Calculate key metrics
3. Send summary email every Monday

---

## Migration Checklist

### Initial Setup
- [ ] Create ConvertKit account
- [ ] Set up sending domain (DNS records)
- [ ] Create all forms listed above
- [ ] Create all tags listed above
- [ ] Set up custom fields
- [ ] Create email templates for each brand

### Automations
- [ ] Build welcome sequence for each brand
- [ ] Set up new subscriber automation
- [ ] Set up engagement scoring automation
- [ ] Configure re-engagement sequence
- [ ] Test all automations with test email

### Integration
- [ ] Add form IDs to environment variables
- [ ] Configure webhook endpoints
- [ ] Test API connection
- [ ] Update website forms with correct form IDs
- [ ] Test end-to-end flow

### Go Live
- [ ] Import existing subscribers (if any)
- [ ] Apply appropriate tags to imported subscribers
- [ ] Activate all automations
- [ ] Monitor first 48 hours
- [ ] Check deliverability

---

## Troubleshooting

### Common Issues

1. **Emails going to spam**
   - Verify sending domain
   - Check content for spam triggers
   - Warm up sending reputation gradually

2. **Automation not triggering**
   - Verify trigger conditions
   - Check if subscriber matches conditions
   - Review automation logs

3. **API errors**
   - Verify API key is correct
   - Check rate limits (120 requests/minute)
   - Ensure correct endpoint URLs

### Support Resources
- ConvertKit Help: help.convertkit.com
- API Docs: developers.convertkit.com
- Status: status.convertkit.com
