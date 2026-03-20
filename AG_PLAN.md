# AG_PLAN: PilotTools.ai Content Calendar & Quality Upgrade

## User Request Summary
Expand PilotTools content generation pipeline with:
1. TASK 1: Populate content calendar with 200+ new items (pricing, alternatives, comparisons, listicles, profession/task pages)
2. TASK 2: Execute the population script immediately
3. TASK 3: Enhance generate-content.js with better quality rules and NEW article/listicle generators

## Execution Plan

### TASK 1: Create populate-calendar.js Script
**File**: `/Users/homefolder/Desktop/social-media-empire/ai-tools-hub/scripts/populate-calendar.js`

**What it does**:
1. Reads existing `ai-tools-hub/config/content-calendar.json` and `ai-tools-hub/content/tools.json`
2. Builds lists of existing items (by slug) to avoid duplicates
3. Generates 200+ new calendar items across 7 categories:
   - Pricing pages: `[tool] pricing 2026` (50+ tools)
   - Alternatives pages: `best [tool] alternatives 2026` (30+ tools)
   - Comparisons: 20+ new pairs (claude-vs-gemini, cursor-vs-tabnine, etc.)
   - Profession listicles: 25 items (best AI for students, freelancers, etc.)
   - Task listicles: 25 items (best AI for email-writing, blog-posts, etc.)
   - "Is it worth it" articles: 20 tools
   - "How to use" how-tos: 15-20 items
4. Assigns sequential IDs starting from 100 (avoiding conflicts)
5. Sets appropriate priority (high/medium/low) based on type
6. Writes updated calendar back to file
7. Reports final counts

**Idempotent**: Checks `slug` field to avoid re-adding duplicates on re-runs

### TASK 2: Run the Script
```bash
cd /Users/homefolder/Desktop/social-media-empire
node ai-tools-hub/scripts/populate-calendar.js
```
Then verify calendar was updated by counting items.

### TASK 3: Enhance generate-content.js

**Part A: Quality Rules for Reviews**
In `generateReview()` prompt, add:
- Description must be 400+ words (not 2-3 sentences) — reference actual features, pricing, use cases
- Open with direct answer in first 50 words (GEO citation optimization)
- Use first-person language: "In our testing", "We found", "Our team reviewed"
- Include real pricing with dates: "As of March 2026"
- Exclude filler: "In today's digital landscape", "In the world of AI", etc.

**Part B: New `generateArticle()` Function**
For "article" type items (pricing pages, alternatives, "is it worth it"):
- Accepts: item (from calendar)
- Returns: { slug, title, content (HTML), meta_description, keywords, published_date, word_count }
- Content requirements: 2000+ words, H2/H3 structure, FAQ section, 2+ internal links to pilottools.ai tool pages, affiliate CTAs
- Uses Gemini API with maxTokens: 8000
- Appends to `ai-tools-hub/content/articles.json`

**Part C: New `generateListicle()` Function**
For "listicle" type items (best AI tools for profession/task):
- Reads tool data from tools.json for tools in `item.tool_slugs`
- Generates: { slug, title, content (HTML), tool_cards (array), comparison_table, verdict, meta_description, word_count }
- Content: 2000+ words, tool cards with features/pricing, comparison table, final verdict
- Uses Gemini API with maxTokens: 8000
- Appends to `ai-tools-hub/content/articles.json`

**Part D: Update main() Function**
- Handle "article" type: call generateArticle(), append to articles.json
- Handle "listicle" type: call generateListicle(), append to articles.json
- Skip existing articles by checking slug

**Part E: Rate Limit Improvement**
- Increase wait from 3s to 5s between API calls (avoid 429s with high volume)

## Implementation Checklist
- [ ] Create /scripts/populate-calendar.js with full calendar generation logic
- [ ] Run script and verify counts
- [ ] Update generateReview() prompt with quality rules
- [ ] Create generateArticle() function with HTML output
- [ ] Create generateListicle() function with tool card logic
- [ ] Update main() to handle "article" and "listicle" types
- [ ] Change rate limit from 3000ms to 5000ms
- [ ] Test that reviews still generate unchanged
- [ ] Test that comparisons still generate unchanged
- [ ] Verify articles.json is created/updated with new content types

## Status: READY FOR EXECUTION
