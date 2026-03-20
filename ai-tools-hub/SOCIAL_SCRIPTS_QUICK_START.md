# Social Media Scripts — Quick Start

## 3 New Scripts Created

### 1. twitter-poster.js
**Posts tweets to Twitter/X**

```bash
GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js
```

**Post Types:**
- Tip (40%): Tool productivity tricks
- Comparison (25%): "Tool A vs Tool B" takes
- Article Alert (20%): Promote new articles
- Thread (15%): 5-7 tweet category rankings

**CLI Options:**
```bash
--type tip           # Only generate tips
--count 2            # Generate 2 tweets
```

**Config Output:** `config/twitter-history.json` (tracks 7-day repeats)

---

### 2. linkedin-poster.js
**Posts professional content to LinkedIn**

```bash
GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js
```

**Post Types:**
- Tool of the Week (40%): 800-1300 char professional review
- AI Tools for [Role] (35%): Curated lists (Sales, Marketing, HR, Finance, etc.)
- Industry Observation (25%): Thought leadership posts

**CLI Options:**
```bash
--type tool-of-week  # Only generate tool reviews
--count 1            # Generate 1 post
```

**Config Output:** `config/linkedin-history.json` (tracks 7-day repeats)

---

### 3. content-repurposer.js
**Converts articles/tools/comparisons into multi-platform content in one run**

```bash
GEMINI_API_KEY=xxx node scripts/content-repurposer.js
```

**Generates all at once:**
- Twitter: 1 tweet + 3-tweet thread
- LinkedIn: 800-1300 char post
- Pinterest: 2-3 pin descriptions
- Newsletter: 2-3 sentence blurb

**CLI Options:**
```bash
--slug chatgpt       # Repurpose specific article/tool
--count 3            # Process 3 sources
```

**Config Output:** `config/social-queue.json` (append-only queue of repurposed content)

---

## Environment Variables Needed

### For Twitter Script
```bash
GEMINI_API_KEY=your_gemini_key
TWITTER_BEARER_TOKEN=your_bearer_token
# OR for posting (OAuth 1.0a):
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

### For LinkedIn Script
```bash
GEMINI_API_KEY=your_gemini_key
LINKEDIN_ACCESS_TOKEN=your_oauth_token
LINKEDIN_PERSON_ID=your_person_id    # OR LINKEDIN_ORG_ID for company page
```

### For Repurposer Script
```bash
GEMINI_API_KEY=your_gemini_key
```

---

## Quick Test (Dry Run)

**Test without posting:**
```bash
# Just generates content, doesn't post (no API credentials needed)
GEMINI_API_KEY=xxx node scripts/content-repurposer.js --count 1
```

This generates platform-specific content and stores in `config/social-queue.json` without needing Twitter/LinkedIn credentials.

---

## Key Features

✓ **No external npm dependencies** — Uses only Node.js built-ins
✓ **Gemini 2.0 Flash API** for all content generation
✓ **Rate-limited retry logic** — Automatic backoff for 429 errors
✓ **7-day dedup window** — Prevents repeating same tool/topic
✓ **OAuth 1.0a signing** — Pure crypto implementation (no libraries)
✓ **Content queue system** — Repurposer queues output for later distribution

---

## File Locations

```
ai-tools-hub/
├── scripts/
│   ├── twitter-poster.js          ← Posts tweets
│   ├── linkedin-poster.js         ← Posts LinkedIn content
│   └── content-repurposer.js      ← Queues multi-platform content
├── config/
│   ├── twitter-history.json       ← Dedup tracking
│   ├── linkedin-history.json      ← Dedup tracking
│   ├── social-queue.json          ← Repurposed content queue
│   └── ... (other config files)
├── content/
│   ├── tools.json                 ← AI tools database
│   ├── articles.json              ← Published articles
│   ├── comparisons.json           ← Tool comparisons
│   └── ... (other content)
├── SCRIPTS_README.md              ← Detailed docs
└── SOCIAL_SCRIPTS_QUICK_START.md  ← This file
```

---

## Workflow Examples

### Daily Posting Schedule

```bash
# 9am: Post a tweet
0 9 * * * cd ~/Desktop/social-media-empire/ai-tools-hub && \
  GEMINI_API_KEY=$GEMINI_API_KEY \
  TWITTER_BEARER_TOKEN=$TWITTER_BEARER_TOKEN \
  TWITTER_API_KEY=$TWITTER_API_KEY \
  TWITTER_API_SECRET=$TWITTER_API_SECRET \
  TWITTER_ACCESS_TOKEN=$TWITTER_ACCESS_TOKEN \
  TWITTER_ACCESS_SECRET=$TWITTER_ACCESS_SECRET \
  node scripts/twitter-poster.js

# 2pm: Post to LinkedIn
0 14 * * * cd ~/Desktop/social-media-empire/ai-tools-hub && \
  GEMINI_API_KEY=$GEMINI_API_KEY \
  LINKEDIN_ACCESS_TOKEN=$LINKEDIN_ACCESS_TOKEN \
  LINKEDIN_PERSON_ID=$LINKEDIN_PERSON_ID \
  node scripts/linkedin-poster.js

# 7pm: Repurpose content for next day's distribution
0 19 * * * cd ~/Desktop/social-media-empire/ai-tools-hub && \
  GEMINI_API_KEY=$GEMINI_API_KEY \
  node scripts/content-repurposer.js --count 2
```

### All-in-One Run

```bash
#!/bin/bash
export GEMINI_API_KEY=xxx
export TWITTER_BEARER_TOKEN=xxx
export LINKEDIN_ACCESS_TOKEN=xxx
export LINKEDIN_PERSON_ID=xxx

cd ~/Desktop/social-media-empire/ai-tools-hub

# Generate 1 tweet + 1 LinkedIn post + 2 repurposed items
node scripts/twitter-poster.js --count 1
node scripts/linkedin-poster.js --count 1
node scripts/content-repurposer.js --count 2
```

---

## Error Messages & Fixes

| Error | Fix |
|-------|-----|
| `GEMINI_API_KEY environment variable is required` | Export your Gemini API key: `export GEMINI_API_KEY=xxx` |
| `Twitter credentials required` | Need `TWITTER_BEARER_TOKEN` or OAuth 1.0a env vars |
| `LinkedIn credentials required` | Need `LINKEDIN_ACCESS_TOKEN` + `LINKEDIN_PERSON_ID` or `LINKEDIN_ORG_ID` |
| `Gemini 429 rate limit` | Script auto-retries. If persists, increase delay between runs. |
| `No tools found for [category]` | That category doesn't exist in tools.json |

---

## What Each Script Does Internally

### twitter-poster.js
1. Loads tools.json, articles.json, twitter-history.json
2. Randomly picks post type (tip/comparison/article/thread)
3. Selects random tool/article for that type
4. Checks 7-day history to avoid repeats
5. Calls Gemini API to generate tweet text
6. Signs request with OAuth 1.0a (crypto module)
7. POSTs to Twitter API v2
8. Appends to twitter-history.json
9. Returns tweet ID on success

### linkedin-poster.js
1. Loads tools.json, linkedin-history.json
2. Randomly picks post type (tool-of-week/category/observation)
3. Filters tools by category or selects random tool
4. Checks 7-day history to avoid repeats
5. Calls Gemini API to generate LinkedIn-format text
6. POSTs to LinkedIn API v2 with Bearer token
7. Appends to linkedin-history.json
8. Returns post ID on success

### content-repurposer.js
1. Loads tools.json, articles.json, comparisons.json, social-queue.json
2. Selects random source (article/tool/comparison) or uses --slug
3. Checks if already in queue to avoid duplicates
4. Calls Gemini API 4 times (Twitter, LinkedIn, Pinterest, Newsletter)
5. Builds multi-platform content object
6. Appends to social-queue.json
7. Individual poster scripts can later consume queue items

---

## Adding to GitHub Actions

Create `.github/workflows/social-media.yml`:

```yaml
name: PilotTools Social Media

on:
  schedule:
    - cron: '0 9,14,19 * * *'  # 9am, 2pm, 7pm PST

jobs:
  social:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Post Twitter
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
        run: |
          cd ai-tools-hub
          node scripts/twitter-poster.js

      - name: Post LinkedIn
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          LINKEDIN_PERSON_ID: ${{ secrets.LINKEDIN_PERSON_ID }}
        run: |
          cd ai-tools-hub
          node scripts/linkedin-poster.js

      - name: Repurpose Content
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          cd ai-tools-hub
          node scripts/content-repurposer.js --count 2

      - name: Commit changes
        if: always()
        run: |
          cd ai-tools-hub
          git config user.name "Bot"
          git config user.email "bot@pilottools.ai"
          git add config/*.json
          git commit -m "chore: update social media history" || true
          git push
```

Then add these secrets to your GitHub repo:
- `GEMINI_API_KEY`
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_ID`

Done!
