# PilotTools Social Media Automation Scripts

Three Node.js scripts for automating social media content generation and distribution across Twitter/X, LinkedIn, and Pinterest.

## Scripts Overview

### 1. twitter-poster.js
Generates and posts tweets to Twitter/X. Uses Gemini 2.0 Flash API for content generation.

**4 Post Types (weighted random selection):**
- **Tip** (40%) — Pick a random tool, generate actionable productivity tips
  - Format: "[Tool] trick most people don't know: [tip]. #AItools"
- **Comparison** (25%) — Pick 2 tools, generate opinionated comparison
  - Format: "Unpopular opinion: [Tool A] is better than [Tool B]..."
- **Article Alert** (20%) — Pick a recent article, create promotion tweet
  - Format: "[Hook about topic]. We published: [link] #AItools"
- **Thread** (15%) — Generate 5-7 tweet thread about AI category
  - Tweet 1: Hook, Tweets 2-6: One tool each, Final: Category link

**Features:**
- OAuth 1.0a signing implemented in pure Node.js (no external deps)
- 7-day dedup window to avoid repeating same tool/topic
- Rate limiting between API calls
- History tracking to `config/twitter-history.json`

**Usage:**
```bash
GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js
GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js --type tip
GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js --count 2
```

**Environment Variables:**
- `GEMINI_API_KEY` — Required (for content generation)
- `TWITTER_BEARER_TOKEN` — For reading (optional)
- `TWITTER_API_KEY`, `TWITTER_API_SECRET` — For OAuth 1.0a posting
- `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` — For OAuth 1.0a posting

### 2. linkedin-poster.js
Generates and posts professional content to LinkedIn. Uses Gemini 2.0 Flash API.

**3 Post Types (weighted random selection):**
- **Tool of the Week** (40%) — Professional review of one tool
  - 800-1300 chars, business-focused angle
  - Includes: what it does, who it's for, pricing, CTA to pilottools.ai
- **AI Tools for [Function]** (35%) — Curated list for specific role
  - Pick from: Sales, Marketing, HR, Finance, Operations, Customer Success, Engineering, Design
  - List 3-5 tools with one-line verdicts
- **Industry Observation** (25%) — Thought leadership on AI trends
  - "3 things I learned testing 50+ AI tools..."
  - Professional, insightful tone

**Features:**
- LinkedIn API v2 (OAuth 2.0 Bearer Token)
- 7-day dedup window per topic
- History tracking to `config/linkedin-history.json`
- Category-based tool filtering

**Usage:**
```bash
GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js
GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js --type tool-of-week
GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js --count 1
```

**Environment Variables:**
- `GEMINI_API_KEY` — Required (for content generation)
- `LINKEDIN_ACCESS_TOKEN` — Required (OAuth 2.0 Bearer Token)
- `LINKEDIN_PERSON_ID` — For personal profile posting
- `LINKEDIN_ORG_ID` — Alternative for company page posting (use one of PERSON_ID or ORG_ID)

### 3. content-repurposer.js
Converts a recently published article/tool/comparison into multi-platform content. Creates content for Twitter, LinkedIn, Pinterest, and newsletter at once. Queues output for later use by individual poster scripts.

**Output Structure (per item):**
```json
{
  "source_slug": "chatgpt-pricing",
  "source_type": "article",
  "generated_at": "2026-03-20",
  "twitter": {
    "tweet": "single tweet hook",
    "thread": ["tweet 1", "tweet 2", "tweet 3"]
  },
  "linkedin": {
    "post": "full linkedin post text"
  },
  "pinterest": {
    "pins": [
      {
        "title": "pin title",
        "description": "pin description",
        "board": "board name"
      }
    ]
  },
  "newsletter": {
    "segment": "2-3 sentence newsletter blurb"
  }
}
```

**Features:**
- Processes articles, tools, and comparisons
- Generates platform-specific content in one run
- Appends to `config/social-queue.json`
- Avoids reprocessing the same source
- Can target specific slug with `--slug` flag

**Usage:**
```bash
GEMINI_API_KEY=xxx node scripts/content-repurposer.js
GEMINI_API_KEY=xxx node scripts/content-repurposer.js --slug chatgpt-pricing
GEMINI_API_KEY=xxx node scripts/content-repurposer.js --count 3
```

**Environment Variables:**
- `GEMINI_API_KEY` — Required (for content generation)

## Config Files

All scripts use JSON config files in `ai-tools-hub/config/`:

- **twitter-history.json** — Tracks posted tweets (prevents 7-day repeats)
- **linkedin-history.json** — Tracks posted LinkedIn content (prevents 7-day repeats)
- **social-queue.json** — Repurposed content waiting for distribution

## Integration with Data Files

All scripts read from `ai-tools-hub/content/`:
- **tools.json** — List of AI tools (name, slug, categories, pricing, description, etc.)
- **articles.json** — Published articles (title, slug, excerpt, category, keywords)
- **comparisons.json** — Tool comparisons (title, slug, verdict, comparison_points)

## API Requirements

### Gemini 2.0 Flash
Used by all three scripts for content generation.
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- **Rate Limit Handling**: 3 retries with exponential backoff (15s, 30s, 45s)
- **Max Output Tokens**: 500-2000 depending on post type

### Twitter/X API v2
Used by twitter-poster.js for posting.
- **Authentication**: OAuth 1.0a (user context) for posting tweets
- **Endpoint**: `https://api.twitter.com/2/tweets`
- **Rate Limits**: 300 tweets/15min per account

### LinkedIn API v2
Used by linkedin-poster.js for posting.
- **Authentication**: OAuth 2.0 Bearer Token
- **Endpoint**: `https://api.linkedin.com/v2/ugcPosts`
- **Rate Limits**: 5 posts/day recommended

## Running Scripts Automatically

### Systemd Timer (Linux/macOS with bash)
```bash
# Create timer script
cat > /usr/local/bin/pilottools-social.sh <<'EOF'
#!/bin/bash
export GEMINI_API_KEY=xxx
export TWITTER_BEARER_TOKEN=xxx
export TWITTER_API_KEY=xxx
export TWITTER_API_SECRET=xxx
export TWITTER_ACCESS_TOKEN=xxx
export TWITTER_ACCESS_SECRET=xxx
export LINKEDIN_ACCESS_TOKEN=xxx
export LINKEDIN_PERSON_ID=xxx

cd /Users/homefolder/Desktop/social-media-empire/ai-tools-hub

# Run daily at 9am, 2pm, 7pm
node scripts/twitter-poster.js --count 1
node scripts/linkedin-poster.js --count 1
node scripts/content-repurposer.js --count 2
EOF

chmod +x /usr/local/bin/pilottools-social.sh
```

### GitHub Actions Workflow (Recommended)
```yaml
name: PilotTools Social Media

on:
  schedule:
    - cron: '0 9,14,19 * * *'  # 9am, 2pm, 7pm PST

jobs:
  post-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Post to Twitter
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TWITTER_BEARER_TOKEN: ${{ secrets.TWITTER_BEARER_TOKEN }}
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
        run: cd ai-tools-hub && node scripts/twitter-poster.js
      - name: Post to LinkedIn
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          LINKEDIN_PERSON_ID: ${{ secrets.LINKEDIN_PERSON_ID }}
        run: cd ai-tools-hub && node scripts/linkedin-poster.js
      - name: Repurpose Content
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: cd ai-tools-hub && node scripts/content-repurposer.js --count 2
```

## Error Handling

All scripts include:
- **Retry logic** for rate-limited Gemini API calls (3 attempts, exponential backoff)
- **Graceful fallbacks** for missing API credentials
- **Error logging** to console with specific error messages
- **Dedup checking** before content generation to avoid wasted API calls

## Development Notes

- **No external npm dependencies** — Uses only Node.js built-ins (fs, crypto, https)
- **Pure OAuth 1.0a signing** — crypto module used for HMAC-SHA1 signature generation
- **Gemini API only** — All content generation via Gemini 2.0 Flash (no Claude/OpenAI)
- **JSON-based state** — History and queue stored as plain JSON files in config/

## Troubleshooting

**"No Twitter credentials available"**
- Need either TWITTER_BEARER_TOKEN (for reading) or OAuth 1.0a env vars (for posting)

**"LinkedIn credentials required"**
- Need LINKEDIN_ACCESS_TOKEN + (LINKEDIN_PERSON_ID or LINKEDIN_ORG_ID)

**"Gemini 429 rate limit"**
- Script automatically retries 3x with exponential backoff
- Consider adding delay between --count runs

**API returns 400 Bad Request**
- Verify JSON request format in script
- Check that all required fields are present in POST body

**Content looks generic**
- Adjust temperature in callGemini function (default 0.8)
- Gemini may need more context in prompt for specific tone
