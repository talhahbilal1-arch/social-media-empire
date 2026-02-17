# Cross-Brand Re-Engagement Email Sequence

## Overview
- **Brands**: All (Fit Over 35, Daily Deal Darling, Menopause Planner)
- **Sequence Length**: 3 emails over 14 days
- **Trigger**: Subscriber has not opened any email in 14+ days
- **Goal**: Re-engage inactive subscribers or gracefully remove them to maintain list health
- **Key Metrics**: Re-engagement rate, unsubscribe rate, list hygiene improvement

---

## Email 1: We Miss You! Here's What You've Been Missing
**Send**: Day 14 of no opens
**Subject Line Options (A/B test by brand)**:
- Fit Over 35: "You've been quiet -- here's what you missed this week"
- Daily Deal Darling: "We miss you! Here's what you've been missing"
- Menopause Planner: "Checking in -- we have something for you"

**Preview Text**: Your best content from the last 2 weeks, plus something exclusive

### Content (Fit Over 35 Version):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>We Miss You</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; color: #333333;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">

    <!-- Header -->
    <div style="background-color: #1a1a2e; padding: 30px; text-align: center;">
      <h1 style="color: #e94560; margin: 0; font-size: 28px; letter-spacing: 1px;">FIT OVER 35</h1>
      <p style="color: #cccccc; margin: 10px 0 0; font-size: 14px;">We noticed you've been away...</p>
    </div>

    <!-- Main Content -->
    <div style="padding: 30px;">
      <h2 style="color: #1a1a2e; font-size: 24px; margin-top: 0;">Hey {first_name}, we've missed you.</h2>

      <p style="font-size: 16px; line-height: 1.6;">It has been a couple of weeks since we have heard from you. Life gets busy -- especially when you are juggling work, family, and trying to stay in shape after 35. No judgment here.</p>

      <p style="font-size: 16px; line-height: 1.6;">But you signed up for a reason, and I do not want you to miss the good stuff. Here is what has been happening while you were away:</p>

      <!-- Content Recap Box -->
      <div style="background-color: #f8f9fa; border-left: 4px solid #e94560; padding: 20px; margin: 25px 0; border-radius: 0 6px 6px 0;">
        <h3 style="color: #1a1a2e; margin-top: 0; font-size: 18px;">What You Missed:</h3>
        <ul style="font-size: 15px; line-height: 1.8; padding-left: 20px;">
          <li><strong>New Article:</strong> "The 5 Best Compound Exercises for Men Over 35" -- full video breakdowns included</li>
          <li><strong>Training Tip:</strong> How to warm up properly in under 5 minutes (most guys skip this and get hurt)</li>
          <li><strong>Nutrition Guide:</strong> High-protein meal prep that takes less than 30 minutes on Sunday</li>
          <li><strong>Community Win:</strong> Mark, 42, just finished Phase 2 and added 40 lbs to his squat</li>
        </ul>
      </div>

      <!-- Exclusive Offer -->
      <div style="background-color: #fff3f5; padding: 20px; margin: 25px 0; border-radius: 6px;">
        <h3 style="color: #e94560; margin-top: 0; font-size: 18px; text-align: center;">Exclusive: Just For You</h3>
        <p style="font-size: 15px; line-height: 1.6; text-align: center;">As a thank you for being part of the community, here is our <strong>Quick-Start Mobility Guide</strong> -- a 10-minute daily routine that loosens up tight hips, shoulders, and ankles. It is the perfect complement to your 12-week program.</p>
        <div style="text-align: center; margin-top: 15px;">
          <a href="https://fitover35.com/mobility-guide" style="display: inline-block; background-color: #e94560; color: #ffffff; text-decoration: none; padding: 14px 36px; font-size: 16px; font-weight: bold; border-radius: 6px;">DOWNLOAD THE FREE MOBILITY GUIDE</a>
        </div>
      </div>

      <p style="font-size: 16px; line-height: 1.6;">We will keep sending you our best training content unless you tell us to stop. But we would love to have you back in the mix.</p>

      <p style="font-size: 16px; line-height: 1.6;">Stay strong,<br><strong>The Fit Over 35 Team</strong></p>
    </div>

    <!-- Footer -->
    <div style="background-color: #1a1a2e; padding: 20px 30px; text-align: center;">
      <p style="color: #888888; font-size: 13px; margin: 0;">
        <a href="https://fitover35.com" style="color: #e94560; text-decoration: none;">fitover35.com</a> |
        <a href="{unsubscribe_url}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
      </p>
    </div>

  </div>
</body>
</html>
```

### Content (Daily Deal Darling Version):
```
Hey {first_name}!

I noticed you have not opened my emails in a while and I totally get it -- inboxes get crazy!

But you have been missing some AMAZING deals:

WHAT YOU MISSED:
- A viral beauty product that went 50% off (it sold out in 2 hours last time)
- My top 5 kitchen gadgets under $20 roundup
- An exclusive coupon code for subscribers only
- The $8 Amazon find that 3,000 people bought after my last email

As a "welcome back" gift, here is early access to this week's deal drop -- before I send it to anyone else:

[EARLY ACCESS TO THIS WEEK'S DEALS]

I have been working hard to find the best products at the lowest prices, and I would hate for you to miss out!

xo,
[Signature]
```

### Content (Menopause Planner Version):
```
Hi {first_name},

I noticed it has been a little while since we have connected, and I wanted to check in.

How are you doing? Really?

Menopause does not pause just because life gets busy. And neither does our support for you.

HERE'S WHAT YOU MISSED:
- New research on natural hot flash relief (3 approaches that actually work)
- A sleep hygiene checklist specifically for hormonal changes
- Community stories from women just like you who are thriving
- Updated symptom tracking tips

I put together a special resource just for you -- our "Quick Relief Guide" with the top 5 strategies that our community members say made the biggest difference:

[DOWNLOAD THE QUICK RELIEF GUIDE]

You are not alone in this. We are here whenever you are ready.

With care,
[Signature]
```

### Tags:
- `reengagement-email-1-sent`
- `reengaged` (if they open or click)

---

## Email 2: Last Chance: Free Resource Before We Clean Our List
**Send**: Day 21 of no opens (7 days after Email 1)
**Subject Line Options**:
- Fit Over 35: "Your free training resource expires soon"
- Daily Deal Darling: "Last chance: Free deal tracker before we clean our list"
- Menopause Planner: "We saved this for you -- but not for long"

**Preview Text**: We are cleaning our list soon -- grab this before you go

### Content (Fit Over 35 Version):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Last Chance</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; color: #333333;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">

    <!-- Header -->
    <div style="background-color: #1a1a2e; padding: 30px; text-align: center;">
      <h1 style="color: #e94560; margin: 0; font-size: 28px; letter-spacing: 1px;">FIT OVER 35</h1>
    </div>

    <!-- Main Content -->
    <div style="padding: 30px;">
      <h2 style="color: #1a1a2e; font-size: 24px; margin-top: 0;">Still want to hear from us, {first_name}?</h2>

      <p style="font-size: 16px; line-height: 1.6;">I am going to be straight with you -- I am cleaning up the Fit Over 35 email list soon.</p>

      <p style="font-size: 16px; line-height: 1.6;">I only want to send emails to people who actually want them. If our content is not for you, no hard feelings at all. But if you DO want to keep getting free training tips, nutrition advice, and program updates -- I need you to do one thing:</p>

      <!-- CTA Button -->
      <div style="text-align: center; margin: 30px 0;">
        <a href="https://fitover35.com/stay-subscribed?email={email_address}" style="display: inline-block; background-color: #e94560; color: #ffffff; text-decoration: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 6px; letter-spacing: 0.5px;">YES, KEEP ME SUBSCRIBED</a>
      </div>

      <p style="font-size: 16px; line-height: 1.6;">That is it. One click and you are back in.</p>

      <!-- Best Resource Offer -->
      <div style="background-color: #f8f9fa; border-left: 4px solid #e94560; padding: 20px; margin: 25px 0; border-radius: 0 6px 6px 0;">
        <h3 style="color: #1a1a2e; margin-top: 0; font-size: 18px;">Before you decide, here is our best free resource:</h3>
        <p style="font-size: 15px; line-height: 1.6;">The <strong>Complete Fit Over 35 Starter Kit</strong> -- everything in one place:</p>
        <ul style="font-size: 15px; line-height: 1.8; padding-left: 20px;">
          <li>12-Week Workout Program (full PDF)</li>
          <li>Meal Prep Template with grocery lists</li>
          <li>Mobility Guide (10-minute daily routine)</li>
          <li>Recovery Protocol checklist</li>
          <li>Progress tracking sheets</li>
        </ul>
        <div style="text-align: center; margin-top: 15px;">
          <a href="https://fitover35.com/starter-kit" style="color: #e94560; text-decoration: underline; font-weight: bold; font-size: 15px;">Download the Complete Starter Kit</a>
        </div>
      </div>

      <p style="font-size: 16px; line-height: 1.6;">If I do not hear from you in the next 7 days, I will remove you from the list. You can always re-subscribe later if you change your mind.</p>

      <p style="font-size: 16px; line-height: 1.6;">No pressure either way. I respect your inbox.</p>

      <p style="font-size: 16px; line-height: 1.6;">Stay strong,<br><strong>The Fit Over 35 Team</strong></p>
    </div>

    <!-- Footer -->
    <div style="background-color: #1a1a2e; padding: 20px 30px; text-align: center;">
      <p style="color: #888888; font-size: 13px; margin: 0;">
        <a href="https://fitover35.com" style="color: #e94560; text-decoration: none;">fitover35.com</a> |
        <a href="{unsubscribe_url}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
      </p>
    </div>

  </div>
</body>
</html>
```

### Content (Daily Deal Darling Version):
```
Hey {first_name},

I am doing a list clean-up soon and I want to make sure you do not get removed by accident!

If you still want my best deal finds delivered to your inbox, click here:

[YES, KEEP SENDING ME DEALS]

Before you decide, here is the best thing I can offer you -- my COMPLETE Deal Finder Toolkit:
- 50 Hidden Amazon Gems Under $25 (updated edition)
- Price tracking spreadsheet
- My personal coupon code list
- Seasonal deal calendar (know EXACTLY when to buy)

[GRAB THE FREE TOOLKIT BEFORE IT'S GONE]

If I do not hear from you in 7 days, I will remove you from the list. You can always come back later!

No hard feelings either way. Your inbox, your rules.

xo,
[Signature]
```

### Content (Menopause Planner Version):
```
Hi {first_name},

I wanted to let you know that I am cleaning up our email list soon.

I believe in only sending emails to people who find them valuable. If our menopause wellness content is not what you need right now, that is completely okay.

But if you DO want to stay connected, just click below:

[YES, KEEP ME SUBSCRIBED]

Before you go, I wanted to share our most comprehensive free resource -- the Menopause Wellness Starter Pack:
- Updated Symptom Tracker (printable)
- Hormone-Friendly Recipe Collection
- Sleep Optimization Guide
- Doctor Visit Preparation Checklist

[DOWNLOAD THE FREE WELLNESS PACK]

Whatever you decide, please know that your journey matters and you are not alone.

With warmth,
[Signature]
```

### Tags:
- `reengagement-email-2-sent`
- `confirmed-subscriber` (if they click "keep me subscribed")
- `reengaged` (if they open or click)

---

## Email 3: Goodbye? (Unless You Want to Stay)
**Send**: Day 28 of no opens (7 days after Email 2)
**Subject Line Options**:
- Fit Over 35: "Goodbye, {first_name}? (unless you want to stay)"
- Daily Deal Darling: "This is goodbye (unless you click)"
- Menopause Planner: "A warm goodbye -- unless you'd like to stay"

**Preview Text**: One click to stay, otherwise we will part ways

### Content (Fit Over 35 Version):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Goodbye</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; color: #333333;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">

    <!-- Header -->
    <div style="background-color: #1a1a2e; padding: 30px; text-align: center;">
      <h1 style="color: #e94560; margin: 0; font-size: 28px; letter-spacing: 1px;">FIT OVER 35</h1>
    </div>

    <!-- Main Content -->
    <div style="padding: 30px;">
      <h2 style="color: #1a1a2e; font-size: 24px; margin-top: 0;">This is my last email, {first_name}.</h2>

      <p style="font-size: 16px; line-height: 1.6;">I have sent you a couple of emails over the past few weeks and have not heard back. I get it -- maybe the timing is not right, maybe fitness is not a priority right now, or maybe my emails just are not what you are looking for.</p>

      <p style="font-size: 16px; line-height: 1.6;">All of that is okay.</p>

      <p style="font-size: 16px; line-height: 1.6;"><strong>This is the last email I will send you unless you click the button below.</strong></p>

      <!-- CTA Button -->
      <div style="text-align: center; margin: 30px 0;">
        <a href="https://fitover35.com/stay-subscribed?email={email_address}" style="display: inline-block; background-color: #e94560; color: #ffffff; text-decoration: none; padding: 18px 50px; font-size: 20px; font-weight: bold; border-radius: 6px; letter-spacing: 0.5px;">KEEP ME SUBSCRIBED</a>
      </div>

      <p style="font-size: 16px; line-height: 1.6;">If you do not click, I will remove you from the list tomorrow. No hard feelings. I only want to show up in inboxes where I am welcome.</p>

      <!-- Warm goodbye -->
      <div style="background-color: #f8f9fa; padding: 20px; margin: 25px 0; border-radius: 6px;">
        <p style="font-size: 15px; line-height: 1.6; margin: 0;"><strong>If this is goodbye:</strong> Thank you for giving Fit Over 35 a chance. I genuinely hope you find what works for you -- whether that is our program or something else entirely. Your health matters, and I am rooting for you regardless.</p>
      </div>

      <!-- Come back note -->
      <p style="font-size: 15px; line-height: 1.6; color: #666;"><em>P.S. You can always come back. The door is open at <a href="https://fitover35.com" style="color: #e94560;">fitover35.com</a> any time you are ready.</em></p>

      <p style="font-size: 16px; line-height: 1.6;">Stay strong -- wherever you are,<br><strong>The Fit Over 35 Team</strong></p>
    </div>

    <!-- Footer -->
    <div style="background-color: #1a1a2e; padding: 20px 30px; text-align: center;">
      <p style="color: #888888; font-size: 13px; margin: 0;">
        <a href="https://fitover35.com" style="color: #e94560; text-decoration: none;">fitover35.com</a> |
        <a href="{unsubscribe_url}" style="color: #888888; text-decoration: underline;">Unsubscribe</a>
      </p>
    </div>

  </div>
</body>
</html>
```

### Content (Daily Deal Darling Version):
```
Hey {first_name},

This is my last email to you.

I have sent a couple of check-in emails and have not heard back, so I am going to respect your inbox and remove you from the list.

BUT -- if you DO want to keep getting my deal finds, this is your last chance:

[KEEP ME SUBSCRIBED -- I WANT THE DEALS]

If you do not click, you will be removed tomorrow. No hard feelings!

If this is goodbye: Thank you for being part of the Deal Darlings family, even for a little while. I hope some of my finds made your life a little better (or at least saved you a few bucks!).

You are always welcome back at dailydealdarling.com.

xo,
[Signature]
```

### Content (Menopause Planner Version):
```
Hi {first_name},

This is my last email to you, and I want to make it count.

I have reached out a couple of times and have not heard back. I understand -- life during menopause is unpredictable, and sometimes we have to step back from things.

If you would like to continue receiving our wellness tips and community support, just click below:

[YES, I WANT TO STAY]

If not, I will remove you from the list tomorrow.

If this is goodbye: Please know that your wellness journey matters, whether or not we are part of it. The resources on our website will always be there for you whenever you need them.

Take care of yourself. You deserve it.

With warmth and respect,
[Signature]

P.S. Our website, blog, and free symptom tracker are always available at menopauseplanner.com -- no subscription needed.
```

### Tags:
- `reengagement-email-3-sent`
- `confirmed-subscriber` (if they click "keep me subscribed")
- `reengaged` (if they open or click)

### Automation After Email 3:
- If subscriber clicked "Keep me subscribed" in Email 2 or 3: Remove all `reengagement-*` tags, add `reengaged`, move back to active newsletter
- If no opens/clicks after 48 hours from Email 3: Add `churned` tag, unsubscribe via ConvertKit API

---

## Sequence Settings

### Timing
| Email | Trigger | Subject Focus | Main CTA |
|-------|---------|---------------|----------|
| 1 | Day 14 no opens | Content recap + exclusive resource | Download resource |
| 2 | Day 21 no opens | Urgency + best lead magnet | Keep me subscribed |
| 3 | Day 28 no opens | Final goodbye | Keep me subscribed |

### ConvertKit Setup

1. **Create Visual Automation:**
   - Entry: Tag `at_risk` added (subscriber has not opened in 14+ days)
   - Wait 0 days -> Send Email 1
   - Wait 7 days -> Check: Has subscriber opened any email? If yes -> Remove from sequence, add `reengaged` tag
   - If no -> Send Email 2
   - Wait 7 days -> Check again
   - If no -> Send Email 3
   - Wait 2 days -> If no click on "Keep me subscribed" -> Unsubscribe

2. **Engagement Monitoring Automation:**
   - Run weekly: Query subscribers with 0 opens in last 14 days
   - Add `at_risk` tag to trigger re-engagement sequence
   - Exclude subscribers who are still in welcome sequence

### Expected Outcomes
- Re-engagement rate target: 10-15% (Email 1), 5-8% (Email 2), 2-3% (Email 3)
- Total list reduction: 15-25% of inactive subscribers
- Deliverability improvement: 5-10% better inbox placement
- Cost savings: Reduced ConvertKit subscriber count
