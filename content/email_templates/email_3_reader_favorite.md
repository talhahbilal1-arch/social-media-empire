# Email 3: Reader Favorite - [Top Product]
**Timing:** Day 4 after signup
**Goal:** Social proof, single product focus, drive conversion

---

## Subject Lines (A/B Test)
- "This product has 10,000+ 5-star reviews"
- "Our readers' #1 favorite for {{quiz_type}}"
- "{{first_name}}, you need to see this..."

## Preview Text
"The product everyone's talking about"

---

## Email Body

Hi {{first_name | default: "there"}},

I had to share this with you.

Remember how you're a **{{quiz_result}}**? Well, there's ONE product that our {{quiz_result}} readers absolutely love.

### Meet: {{featured_product_name}}

{{featured_product_image}}

**Why everyone loves it:**

- {{benefit_1}}
- {{benefit_2}}
- {{benefit_3}}
- {{benefit_4}}

### What Readers Are Saying

> "{{testimonial_1}}" - {{testimonial_1_author}}

> "{{testimonial_2}}" - {{testimonial_2_author}}

### The Details

**Price:** {{product_price}}
**Rating:** {{product_rating}} ({{review_count}} reviews)
**Best for:** {{quiz_result}} types

[See It Here]({{product_link}})

---

### For Menopause Planner (Additional Block)

**Pair it with:** Our **{{etsy_product_name}}** for the complete solution.
[Shop on Etsy]({{etsy_product_url}})

---

This is genuinely one of my favorites, and I think you'll love it too.

Let me know if you have any questions!

Cheers,
{{brand_name}} Team

P.S. This product tends to sell out during sales - just a heads up!

---

## Variables Required
- {{first_name}}
- {{quiz_result}}
- {{quiz_type}}
- {{featured_product_name}}
- {{featured_product_image}} - product image URL
- {{benefit_1}} through {{benefit_4}}
- {{testimonial_1}}, {{testimonial_1_author}}
- {{testimonial_2}}, {{testimonial_2_author}}
- {{product_price}}
- {{product_rating}}
- {{review_count}}
- {{product_link}} (with affiliate tag)
- {{etsy_product_name}}, {{etsy_product_url}} - for Menopause Planner
- {{brand_name}}
