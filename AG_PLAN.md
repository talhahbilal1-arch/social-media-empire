# Execution Plan: Three PilotTools Automation Scripts

**Created:** 2026-03-20
**Status:** Ready for execution
**Executor:** Antigravity (executor agent)

---

## Overview
Build three Node.js scripts for PilotTools.ai automation:
1. `pinterest-poster.js` — Generates and posts Pinterest pins
2. `generate-lead-magnet.js` — Builds pricing cheat sheet HTML
3. `outreach-automator.js` — Sends personalized backlink outreach emails

All scripts use Gemini API for content generation, follow the pattern from `generate-content.js`, and require zero external npm dependencies (only built-in modules + fetch).

---

## SCRIPT 1: pinterest-poster.js

### Location
`/Users/homefolder/Desktop/social-media-empire/ai-tools-hub/scripts/pinterest-poster.js`

### Functionality
Generates 3-5 pins per run from tools.json, comparisons.json, articles.json and posts to Make.com webhook.

### Architecture
1. **Load data files:**
   - `ai-tools-hub/content/tools.json` (80+ tools with slug, name, rating, category, website, description)
   - `ai-tools-hub/content/comparisons.json` (50+ comparisons with slug, tools array, verdict)
   - `ai-tools-hub/content/articles.json` (articles with slug, title, category)

2. **Initialize tracking:**
   - Load or create `ai-tools-hub/config/pinterest-history.json` (empty object if doesn't exist)
   - Structure: `{ "[slug]": "YYYY-MM-DD", ... }` — tracks last post date per slug

3. **Generate pin count:** Default 3, override with `--count N` flag

4. **For each pin:**
   - **Pin type selection** (weighted random):
     - 40% Tool Review Pin
     - 30% Comparison Pin
     - 20% Category/Listicle Pin
     - 10% Article Pin

   - **Tool Review Pin:**
     - Select random tool from tools.json not posted in 14+ days
     - Prompt: "Generate a Pinterest pin about [Tool], rating [X]/5. Include key stats."
     - Result: `{ title, description, board_name }`
     - URL: `https://pilottools.ai/tools/[slug]/`
     - Board: map tool.category to BOARDS (writing → "AI Writing Tools", etc.)

   - **Comparison Pin:**
     - Select random comparison not posted in 14+ days
     - Prompt: "Generate a Pinterest pin for '[Tool A] vs [Tool B]' comparison. Include winner + key difference."
     - Result: `{ title, description, board_name }`
     - URL: `https://pilottools.ai/compare/[slug]/`
     - Board: "AI Tool Comparisons"

   - **Listicle Pin:**
     - Group tools by category, pick random category
     - Prompt: "Generate a 'Top N AI [Category] Tools 2026' pin. List top 3-4 briefly."
     - Result: `{ title, description, board_name }`
     - URL: `https://pilottools.ai/category/[category]/`
     - Board: `"Best " + [category title] + " Tools"`

   - **Article Pin:**
     - Select random article not posted in 14+ days
     - Prompt: "Generate a Pinterest pin promoting this article: [title]. Key takeaway + CTA."
     - Result: `{ title, description, board_name }`
     - URL: `https://pilottools.ai/blog/[slug]/`
     - Board: Derive from article category

   - **Dedup check:** If slug in pinterest-history and date difference < 14 days, skip and retry

5. **Post to Make.com:**
   - POST to `process.env.MAKE_WEBHOOK_PILOTTOOLS`
   - Headers: `Content-Type: application/json`
   - Body: `{ title, description, link, board_name, image_url: "https://pilottools.ai/og-image.png" }`
   - Retry 3x with exponential backoff on 429

6. **Update history:**
   - On successful POST, add `pinterest-history[slug] = today's date`
   - Write back to `ai-tools-hub/config/pinterest-history.json`

### Board Mapping
```javascript
const BOARDS = {
  writing: "AI Writing Tools",
  coding: "AI Coding Tools",
  image: "AI Image Generators",
  video: "AI Video Tools",
  marketing: "AI Marketing Tools",
  productivity: "AI Productivity Tools",
  audio: "AI Audio Tools",
  seo: "AI SEO Tools",
  research: "AI Research Tools",
  design: "AI Design Tools",
  comparison: "AI Tool Comparisons",
  general: "Best AI Tools 2026"
}
```

### CLI
```bash
MAKE_WEBHOOK_PILOTTOOLS=https://hook.us2.make.com/... GEMINI_API_KEY=xxx node scripts/pinterest-poster.js
MAKE_WEBHOOK_PILOTTOOLS=... GEMINI_API_KEY=xxx node scripts/pinterest-poster.js --count 5
```

---

## SCRIPT 2: generate-lead-magnet.js

### Location
`/Users/homefolder/Desktop/social-media-empire/ai-tools-hub/scripts/generate-lead-magnet.js`

### Functionality
Generates a static HTML pricing cheat sheet from all tools in tools.json.

### Architecture
1. **Create directories:**
   - Ensure `ai-tools-hub/public/downloads/` exists (mkdir -p if not)

2. **Load data:**
   - Read all tools from `ai-tools-hub/content/tools.json`
   - Group by category (writing, coding, image, etc.)

3. **Build HTML:**
   - Static HTML with inline CSS (no external stylesheets)
   - Professional, printable design
   - Sections:
     - Header: "AI Tools Pricing Guide 2026 — by PilotTools.ai"
     - Intro paragraph: "We've tested 80+ AI tools..."
     - For each category:
       - Category heading (h2)
       - Table with columns: Tool | Free Tier | Starting Price | Best Plan | Best For | Our Rating
       - Each row pulls tool data from tools.json
     - Footer: "Get the latest updates at pilottools.ai"
     - Timestamp: "Last Updated: [TODAY]"

4. **Table data extraction:**
   - Tool name: `tool.name`
   - Free Tier: Yes/No from `tool.pricing.free_tier`
   - Starting Price: `$${tool.pricing.starting_price}/mo` or "Custom"
   - Best Plan: `tool.pricing.plans[0].name` or "See site"
   - Best For: First 2 items from `tool.best_for[]` joined with ", "
   - Rating: `${tool.rating}/5` with star emoji (⭐)

5. **Save:**
   - Write to `ai-tools-hub/public/downloads/ai-tools-pricing-2026.html`

### CLI
```bash
node scripts/generate-lead-magnet.js
```

---

## SCRIPT 3: outreach-automator.js

### Location
`/Users/homefolder/Desktop/social-media-empire/ai-tools-hub/scripts/outreach-automator.js`

### Functionality
Generates personalized outreach emails via Gemini and sends via Resend API.

### Architecture
1. **Load data:**
   - Read tools.json
   - Load or create `ai-tools-hub/config/outreach-log.json` (empty array if doesn't exist)

2. **Parse CLI args:**
   - `--type` (testimonial|resource|guest-post) — default: testimonial
   - `--count` (1-5) — default: 5
   - `--send` flag — if absent, dry-run mode only
   - `--dry-run` explicit flag (overrides --send)

3. **Outreach types:**
   - **Testimonial:** Tool company contact pages — "We wrote a detailed review of [Tool]"
   - **Resource Page:** AI tools resource sites — "Addition for your AI tools resource page"
   - **Guest Post:** Tech/marketing blogs — "Guest post pitch: How to Choose the Right AI [Category] Tool"

4. **Email generation via Gemini:**
   - Prompt includes: tool name, website, category, tool description snippet
   - Output: `{ subject, body, recipient_email, recipient_name }`
   - Constraints: subject < 60 chars, body < 500 chars

5. **Dedup check:**
   - Check outreach-log for same email + type within 30 days
   - Skip if found

6. **Send via Resend API:**
   - POST to `https://api.resend.com/emails`
   - Headers: `Authorization: Bearer ${RESEND_API_KEY}`, `Content-Type: application/json`
   - Body: `{ from: "hello@pilottools.ai", to, subject, html: body }`
   - Retry 3x on 429 rate limit

7. **Safety limits:**
   - Max 5 emails per run
   - Error on tool failure (e.g., Gemini API fails)
   - Dry-run mode by default

### CLI
```bash
RESEND_API_KEY=xxx GEMINI_API_KEY=xxx node scripts/outreach-automator.js --type testimonial --send
RESEND_API_KEY=xxx GEMINI_API_KEY=xxx node scripts/outreach-automator.js --type testimonial --count 5 --dry-run
```

---

## Common Infrastructure

### Gemini API Pattern (reuse from generate-content.js)
- Fetch to `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- 3 retries with exponential backoff (15s, 30s, 45s) for 429 errors
- Extract JSON from response using regex: `text.match(/\{[\s\S]*\}/)` or `text.match(/\[[\s\S]*\]/)`

### File I/O Pattern
- Read JSON safely with try-catch, default to empty object/array
- Write JSON with `fs.writeFileSync(filepath, JSON.stringify(data, null, 2))`
- Use `path.join(__dirname, '..', ...)` for all relative paths

### CLI Arg Pattern
- Parse `process.argv.slice(2)`
- Extract with `args.indexOf('--flag')` and `args[idx + 1]`
- Check flags with `args.includes('--flag')`

### Error Handling
- Wrap main() in try-catch, exit with code 1 on error
- Log errors with prefix `[ERROR]`
- Continue on non-fatal errors (single generation fails)
- Crash on fatal errors (missing env var, JSON parse)

---

## Execution Order
1. **Script 1:** pinterest-poster.js (Pinterest posting infrastructure)
2. **Script 2:** generate-lead-magnet.js (Simpler — no API calls)
3. **Script 3:** outreach-automator.js (Email infrastructure)

---

## Status Checklist
- [ ] pinterest-poster.js created and tested
- [ ] generate-lead-magnet.js created and tested
- [ ] outreach-automator.js created and tested
- [ ] All env vars documented
- [ ] All CLI flags working
- [ ] All file paths using path.join(__dirname)
- [ ] Logging clear and consistent
