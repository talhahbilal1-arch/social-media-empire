# Email 4: New Arrivals for Your [Quiz Type]
**Timing:** Day 7 after signup
**Goal:** Fresh products, urgency, keep engagement

---

## Subject Lines (A/B Test)
- "Just dropped: New {{quiz_type}} picks for you"
- "{{first_name}}, fresh finds you'll love"
- "New this week (picked just for {{quiz_result}} types)"

## Preview Text
"Hot new products you haven't seen yet"

---

## Email Body

Hi {{first_name | default: "there"}},

It's been a week since you discovered you're a **{{quiz_result}}** - and I've got some fresh finds to share!

### New This Week

These just landed and I immediately thought of you:

---

**NEW** {{product_1_name}}
{{product_1_description}}
**{{product_1_price}}** | {{product_1_rating}}
[Shop Now]({{product_1_link}})

---

**TRENDING** {{product_2_name}}
{{product_2_description}}
**{{product_2_price}}** | {{product_2_rating}}
[Shop Now]({{product_2_link}})

---

**LIMITED** {{product_3_name}}
{{product_3_description}}
**{{product_3_price}}** | {{product_3_rating}}
[Shop Now]({{product_3_link}})

---

### Why These Made the List

I only share products that:
- Have stellar reviews (4+ stars)
- Actually work for {{quiz_result}} types
- Offer great value

### Flash Deal Alert

One of these is on sale for the next 48 hours. Hint: it's the one marked "LIMITED" above.

[See All Deals]({{deals_page_link}})

---

### For Menopause Planner (Additional Block)

**New in Our Shop:**
We just added new designs to our planner collection!
[Browse New Arrivals]({{etsy_shop_url}})

---

More good stuff coming your way soon!

{{brand_name}} Team

---

## Variables Required
- {{first_name}}
- {{quiz_result}}
- {{quiz_type}}
- {{product_1_name}}, {{product_1_description}}, {{product_1_price}}, {{product_1_rating}}, {{product_1_link}}
- {{product_2_name}}, {{product_2_description}}, {{product_2_price}}, {{product_2_rating}}, {{product_2_link}}
- {{product_3_name}}, {{product_3_description}}, {{product_3_price}}, {{product_3_rating}}, {{product_3_link}}
- {{deals_page_link}}
- {{etsy_shop_url}} - for Menopause Planner
- {{brand_name}}
