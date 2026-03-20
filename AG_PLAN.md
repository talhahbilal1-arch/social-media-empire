# AG_PLAN: PilotTools.ai Marketing Execution

## Context
Scale PilotTools.ai from 0 to 50K+ monthly visitors using a multi-channel marketing engine. Full strategy in `tasks/todo.md`. 8 phases, prioritized by ROI vs effort.

## Current State
- 80 tools, 100+ indexed pages, 5 GitHub Actions workflows running
- SEO content generation Mon-Fri (Gemini 2.0)
- Newsletter via ConvertKit (weekly)
- Pinterest pins generated but NOT auto-posted for PilotTools
- NO X/Twitter, Reddit, LinkedIn, YouTube automation

## Execution Order

### Phase 1: SEO Scale-Up (START HERE)
1. Read `ai-tools-hub/content/tools.json` to get all 80 tool slugs
2. Generate 135+ content calendar items covering:
   - `[tool] pricing 2026` × 80 tools
   - `[tool] alternatives` × 80 tools
   - `best AI tools for [profession]` × 25
   - `best AI tools for [task]` × 25
3. Write items to `ai-tools-hub/config/content-calendar.json` (status: pending, priority: high/medium)
4. Update `toolpilot-content.yml` default count from 1 to 3
5. Update `scripts/generate-content.js` to enforce: 2000+ words, first-person, GEO-optimized first paragraph, 2+ internal links

### Phase 2: Pinterest (Add PilotTools as 4th Brand)
1. Create `video_automation/pilottools_pin_generator.py` — reads tools.json, generates pin data
2. Add PilotTools config to content_brain.py BRAND_CONFIGS (or separate module)
3. User: Create Make.com webhook scenario + Pinterest biz account + 5 boards
4. Add MAKE_WEBHOOK_PILOTTOOLS to GitHub secrets
5. Add PilotTools posting phase to content-engine.yml or new workflow

### Phase 3: X/Twitter
1. User: Create X developer account, get API credentials
2. Create `video_automation/twitter_poster.py` — 4 post types, Gemini copy
3. Create `toolpilot-twitter.yml` — 2-3 posts/day schedule
4. Create `twitter_posts` Supabase table
5. Add GitHub secrets: TWITTER_API_KEY, TWITTER_API_SECRET, etc.

### Phase 4: Content Repurposer
1. Create `video_automation/content_repurposer.py` — article → multi-platform content
2. Create `social_content_queue` Supabase table
3. Integrate into toolpilot-content.yml post-generation step

### Phase 5-8: LinkedIn, Email Growth, YouTube, Backlinks
See `tasks/todo.md` for full details.

## Status: AWAITING USER REVIEW
