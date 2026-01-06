# Email 1: Your [Quiz Type] Results + Top Picks
**Timing:** Immediately after quiz completion
**Goal:** Deliver value, establish trust, first product recommendations

---

## Subject Lines (A/B Test)
- "Your {{quiz_type}} Results Are In! Here's What We Found..."
- "{{first_name}}, Your Personalized {{quiz_type}} Guide is Ready"
- "We Analyzed Your Answers - Here Are Your Perfect Matches"

## Preview Text
"Plus 5 handpicked products just for you"

---

## Email Body

Hi {{first_name | default: "there"}},

Thanks for taking our {{quiz_type}} quiz! Based on your answers, you're a **{{quiz_result}}**.

Here's what that means for you:

### What Your Results Tell Us

{{quiz_result_description}}

### Your Top 5 Personalized Picks

We've handpicked these products specifically for {{quiz_result}} types like you:

**1. {{product_1_name}}** ⭐ Top Pick
{{product_1_description}}
[Shop Now]({{product_1_link}})

**2. {{product_2_name}}**
{{product_2_description}}
[Shop Now]({{product_2_link}})

**3. {{product_3_name}}**
{{product_3_description}}
[Shop Now]({{product_3_link}})

**4. {{product_4_name}}**
{{product_4_description}}
[Shop Now]({{product_4_link}})

**5. {{product_5_name}}**
{{product_5_description}}
[Shop Now]({{product_5_link}})

---

### For Menopause Planner Brand (Additional Block)

**Exclusive from Our Shop:**
Get our **{{etsy_product_name}}** - designed specifically for women navigating menopause.
[Get Yours on Etsy]({{etsy_product_url}})

---

I'll be sending you more personalized recommendations over the next few days. Keep an eye on your inbox!

Cheers,
{{brand_name}} Team

P.S. Save 10% on your first order with code QUIZ10

---

## Variables Required
- {{first_name}} - subscriber first name
- {{quiz_type}} - type of quiz taken
- {{quiz_result}} - the category/result
- {{quiz_result_description}} - explanation of result
- {{product_1_name}} through {{product_5_name}}
- {{product_1_description}} through {{product_5_description}}
- {{product_1_link}} through {{product_5_link}} (with affiliate tags)
- {{etsy_product_name}} - for Menopause Planner brand
- {{etsy_product_url}} - Etsy shop link
- {{brand_name}} - Daily Deal Darling or The Menopause Planner
