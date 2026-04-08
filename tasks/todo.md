# PHASE 2: Convert Amazon Search URLs to Direct Product Links

## Current State
- **1591 total search URLs** across 3 brands (fitness, deals, menopause)
- Search URLs use format: `amazon.com/s?k=QUERY&tag=TAG`
- Goal: Replace with `/dp/ASIN?tag=TAG` for better affiliate conversion

## Strategy
Use approved ASIN list from `pin_article_generator.py` (AMAZON_AFFILIATE_LINKS dict):
- **Fitness**: 20 approved products (default: B001ARYU58)
- **Deals**: 10 approved products (default: B07DFDS56B)
- **Menopause**: 11 approved products (default: B001G7QUXW)

When search URL query doesn't match an approved product → use brand's _default ASIN

## Tasks

- [ ] 1. Create convert_search_urls.py script
- [ ] 2. Run script on all three brands
- [ ] 3. Verify count reduction (should be ~0 search URLs)
- [ ] 4. Git commit changes

## Constraints
- ✅ Correct affiliate tags: fitness=fitover3509-20, deals/menopause=dailydealdarl-20
- ✅ Use brand-specific default when no match found
