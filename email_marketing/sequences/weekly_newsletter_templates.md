# Weekly Newsletter Templates

## Overview
Templates for ongoing weekly newsletters across all brands.

---

## Daily Deal Darling - Weekly Finds

**Send**: Every Tuesday at 10 AM
**Subject Line Options**:
- "This week's finds are 🔥"
- "{number} deals you need to see this week"
- "Tuesday deals drop! Here's what I'm loving"

### Template:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
    .header { background: #E91E63; color: white; padding: 20px; text-align: center; }
    .product { border: 1px solid #eee; padding: 15px; margin: 10px 0; }
    .price { color: #E91E63; font-size: 24px; font-weight: bold; }
    .cta-button { background: #E91E63; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>This Week's Best Finds 💕</h1>
  </div>

  <p>Hey {first_name}!</p>
  <p>Here's what I'm obsessed with this week:</p>

  <!-- FEATURED DEAL -->
  <div class="product" style="background: #fff5f8;">
    <h2>⭐ Featured Find</h2>
    <img src="{product_1_image}" alt="{product_1_name}" style="max-width: 100%;">
    <h3>{product_1_name}</h3>
    <p class="price">${product_1_price}</p>
    <p>{product_1_description}</p>
    <a href="{product_1_link}" class="cta-button">Shop Now</a>
  </div>

  <!-- MORE FINDS -->
  <h2>More Finds You'll Love:</h2>

  <div class="product">
    <h3>{product_2_name}</h3>
    <p class="price">${product_2_price}</p>
    <a href="{product_2_link}">Get it here →</a>
  </div>

  <div class="product">
    <h3>{product_3_name}</h3>
    <p class="price">${product_3_price}</p>
    <a href="{product_3_link}">Get it here →</a>
  </div>

  <div class="product">
    <h3>{product_4_name}</h3>
    <p class="price">${product_4_price}</p>
    <a href="{product_4_link}">Get it here →</a>
  </div>

  <!-- TIP OF THE WEEK -->
  <div style="background: #f9f9f9; padding: 15px; margin: 20px 0;">
    <h3>💡 Tip of the Week</h3>
    <p>{weekly_tip}</p>
  </div>

  <p>Happy shopping!</p>
  <p>xo, [Name]</p>

  <hr>
  <p style="font-size: 12px; color: #999;">
    Follow me: <a href="https://instagram.com/dailydealdarling">Instagram</a> | <a href="https://pinterest.com/dailydealdarling">Pinterest</a>
  </p>
</body>
</html>
```

---

## Menopause Planner - Weekly Wellness

**Send**: Every Sunday at 9 AM
**Subject Line Options**:
- "Your weekly wellness update 💜"
- "This week's focus: {topic}"
- "Sunday self-care: {theme}"

### Template:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Georgia, serif; max-width: 600px; margin: 0 auto; color: #333; }
    .header { background: #9C27B0; color: white; padding: 30px; text-align: center; }
    .section { padding: 20px; border-bottom: 1px solid #E1BEE7; }
    .tip-box { background: #F3E5F5; padding: 15px; border-radius: 8px; margin: 15px 0; }
    .cta-button { background: #9C27B0; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Weekly Wellness 💜</h1>
    <p>{week_theme}</p>
  </div>

  <div class="section">
    <p>Hi {first_name},</p>
    <p>Happy Sunday! Here's your weekly dose of support and practical tips.</p>
  </div>

  <!-- FOCUS OF THE WEEK -->
  <div class="section">
    <h2>This Week's Focus: {focus_topic}</h2>
    <p>{focus_intro}</p>

    <div class="tip-box">
      <h3>Try This:</h3>
      <p>{actionable_tip}</p>
    </div>
  </div>

  <!-- SYMPTOM SPOTLIGHT -->
  <div class="section">
    <h2>Symptom Spotlight: {symptom}</h2>
    <p><strong>What it is:</strong> {symptom_explanation}</p>
    <p><strong>What helps:</strong></p>
    <ul>
      <li>{solution_1}</li>
      <li>{solution_2}</li>
      <li>{solution_3}</li>
    </ul>
  </div>

  <!-- SELF-CARE REMINDER -->
  <div class="section" style="background: #FFF8E1;">
    <h2>💛 Self-Care Reminder</h2>
    <p><em>"{self_care_quote}"</em></p>
    <p>{self_care_action}</p>
  </div>

  <!-- COMMUNITY QUESTION -->
  <div class="section">
    <h2>From the Community</h2>
    <p><strong>Q:</strong> {community_question}</p>
    <p><strong>A:</strong> {community_answer}</p>
  </div>

  <div class="section">
    <p>Remember, you're doing better than you think. 💜</p>
    <p>With support,<br>[Name]</p>
  </div>

  <hr>
  <p style="font-size: 12px; color: #999; text-align: center;">
    <a href="{planner_link}">Get the Menopause Planner</a> |
    <a href="{instagram_link}">Instagram</a>
  </p>
</body>
</html>
```

---

## Nurse Planner - Shift Survival

**Send**: Every Friday at 7 PM
**Subject Line Options**:
- "Weekend reset for nurses 🩺"
- "You survived another week! Here's your reward"
- "Nurse life hacks for next week"

### Template:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }
    .header { background: #00BCD4; color: white; padding: 20px; text-align: center; }
    .hack-box { background: #E0F7FA; padding: 15px; margin: 10px 0; border-left: 4px solid #00BCD4; }
    .cta-button { background: #00BCD4; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>You Made It! 🎉</h1>
    <p>Your weekend survival guide</p>
  </div>

  <p>Hey {first_name}!</p>
  <p>Another week down! Whether you're heading into the weekend or gearing up for more shifts, I've got you.</p>

  <!-- HACK OF THE WEEK -->
  <div class="hack-box">
    <h3>💡 Nurse Hack of the Week</h3>
    <p><strong>{hack_title}</strong></p>
    <p>{hack_description}</p>
  </div>

  <!-- SELF-CARE SECTION -->
  <h2>Weekend Self-Care Ideas:</h2>
  <ul>
    <li>🛁 {selfcare_1}</li>
    <li>😴 {selfcare_2}</li>
    <li>🍵 {selfcare_3}</li>
  </ul>

  <!-- QUICK TIP -->
  <h2>For Your Next Shift:</h2>
  <p>{shift_tip}</p>

  <!-- COMMUNITY -->
  <div style="background: #f5f5f5; padding: 15px; margin: 20px 0;">
    <h3>From a Fellow Nurse:</h3>
    <p><em>"{nurse_quote}"</em></p>
    <p>- {nurse_name}, {specialty}</p>
  </div>

  <p>Take care of yourself this weekend. You deserve it! 💙</p>
  <p>[Name]</p>
</body>
</html>
```

---

## ADHD Planner - Weekly Brain Dump

**Send**: Every Monday at 8 AM
**Subject Line Options**:
- "Your week, simplified 🧠"
- "ADHD-friendly week ahead"
- "Monday motivation (the ADHD way)"

### Template:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Nunito', Arial, sans-serif; max-width: 600px; margin: 0 auto; }
    .header { background: #FF9800; color: white; padding: 20px; text-align: center; }
    .chunk { background: #FFF8E1; padding: 15px; margin: 10px 0; border-radius: 8px; }
    .priority { border-left: 4px solid #FF5722; padding-left: 10px; }
    .cta-button { background: #FF9800; color: white; padding: 12px 24px; text-decoration: none; display: inline-block; border-radius: 5px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Weekly Brain Dump 🧠</h1>
    <p>Week of {week_date}</p>
  </div>

  <p>Hey {first_name}!</p>
  <p>Let's make this week work for your brain, not against it.</p>

  <!-- ONE FOCUS -->
  <div class="chunk priority">
    <h2>🎯 Your ONE Focus This Week:</h2>
    <p><strong>{weekly_focus}</strong></p>
    <p><em>Just this. Everything else is bonus.</em></p>
  </div>

  <!-- QUICK HACK -->
  <div class="chunk">
    <h2>⚡ Quick Hack:</h2>
    <p><strong>{hack_title}</strong></p>
    <p>{hack_description}</p>
  </div>

  <!-- DOPAMINE MENU ITEM -->
  <div class="chunk">
    <h2>🎮 Dopamine Menu Addition:</h2>
    <p>When you need a brain break, try: <strong>{dopamine_activity}</strong></p>
    <p><em>Set a timer for {time_limit} to avoid the rabbit hole!</em></p>
  </div>

  <!-- REMINDER -->
  <div style="background: #FFECB3; padding: 15px; margin: 20px 0; border-radius: 8px;">
    <h3>📌 Gentle Reminder:</h3>
    <p>{adhd_reminder}</p>
  </div>

  <!-- COMMUNITY TIP -->
  <h2>From the ADHD Community:</h2>
  <p><em>"{community_tip}"</em></p>
  <p>- Shared by {community_member}</p>

  <p>You've got this! (And if you don't, that's okay too.)</p>
  <p>🧡 [Name]</p>

  <p style="font-size: 12px; color: #999;">
    P.S. Save this email before you forget! ⭐
  </p>
</body>
</html>
```

---

## Newsletter Best Practices

### Subject Line Tips
- Keep under 50 characters
- Use emojis sparingly (1-2 max)
- Create curiosity or urgency
- Personalize when possible

### Send Time Guidelines
- Daily Deal Darling: Tuesday 10 AM (shopping mindset)
- Menopause Planner: Sunday 9 AM (reflection time)
- Nurse Planner: Friday 7 PM (end of week)
- ADHD Planner: Monday 8 AM (week planning)

### A/B Testing Priorities
1. Subject lines
2. Send times
3. CTA button text
4. Content length

### Engagement Tracking
- Open rate target: >25%
- Click rate target: >3%
- Unsubscribe threshold: <0.5%
