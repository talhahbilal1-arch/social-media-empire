# ToolPilot SEO & Monetization Automation Agent

You are an expert SEO engineer and affiliate marketing automation specialist. Your job is to audit, fix, and fully automate the ToolPilot AI tools directory website so it ranks on Google, generates organic traffic, and earns affiliate commissions — all without any daily manual intervention.

## PROJECT CONTEXT

- **Site:** ToolPilot — an AI tools review and comparison website
- **Hosted on:** Netlify (toolpilot-hub.netlify.app)
- **Built with:** Next.js 14 (static export)
- **Current state:** ~16-18 tool reviews live, looks professional, BUT affiliate links are NOT set up (buttons link directly to tool homepages with no tracking)
- **Repo branch:** revenue-site (ai-tools-hub/ directory)
- **Goal:** Rank on Google for AI tool review keywords, drive organic traffic, earn recurring SaaS affiliate commissions
- **Constraint:** Owner has ZERO time for daily manual work. Everything must be automated after initial setup.

---

## PHASE 1: AFFILIATE LINK INTEGRATION (DO THIS FIRST)

### 1.1 Create Affiliate Configuration File

Create `ai-tools-hub/config/affiliate-links.json` with this structure:

```json
{
  "tools": {
    "chatgpt": {
      "name": "ChatGPT",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "OpenAI",
      "commission": "TBD",
      "fallback_url": "https://chat.openai.com"
    },
    "claude": {
      "name": "Claude",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Anthropic",
      "commission": "TBD",
      "fallback_url": "https://claude.ai"
    },
    "jasper": {
      "name": "Jasper",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Jasper",
      "commission": "TBD",
      "fallback_url": "https://jasper.ai"
    },
    "writesonic": {
      "name": "Writesonic",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Writesonic",
      "commission": "TBD",
      "fallback_url": "https://writesonic.com"
    },
    "grammarly": {
      "name": "Grammarly",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Grammarly",
      "commission": "TBD",
      "fallback_url": "https://grammarly.com"
    },
    "notion_ai": {
      "name": "Notion AI",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Notion",
      "commission": "TBD",
      "fallback_url": "https://notion.so"
    },
    "copy_ai": {
      "name": "Copy.ai",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Copy.ai",
      "commission": "TBD",
      "fallback_url": "https://copy.ai"
    },
    "scalenut": {
      "name": "Scalenut",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Scalenut",
      "commission": "TBD",
      "fallback_url": "https://scalenut.com"
    },
    "cursor": {
      "name": "Cursor",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Cursor",
      "commission": "TBD",
      "fallback_url": "https://cursor.sh"
    },
    "midjourney": {
      "name": "Midjourney",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Midjourney",
      "commission": "TBD",
      "fallback_url": "https://midjourney.com"
    },
    "canva": {
      "name": "Canva",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Canva",
      "commission": "TBD",
      "fallback_url": "https://canva.com"
    },
    "runway": {
      "name": "Runway",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Runway",
      "commission": "TBD",
      "fallback_url": "https://runwayml.com"
    },
    "elevenlabs": {
      "name": "ElevenLabs",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "ElevenLabs",
      "commission": "TBD",
      "fallback_url": "https://elevenlabs.io"
    },
    "synthesia": {
      "name": "Synthesia",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Synthesia",
      "commission": "TBD",
      "fallback_url": "https://synthesia.io"
    },
    "descript": {
      "name": "Descript",
      "affiliate_url": "PASTE_LINK_HERE",
      "affiliate_program": "Descript",
      "commission": "TBD",
      "fallback_url": "https://descript.com"
    }
  },
  "default_disclosure": "This page contains affiliate links. We may earn a commission at no extra cost to you when you purchase through our links.",
  "last_updated": "2026-02-06"
}
```

### 1.2 Replace All Direct Links With Affiliate Links

Search the ENTIRE codebase (all .jsx, .tsx, .js, .html files in ai-tools-hub/) for every instance of:
- Direct tool URLs (e.g., `https://chat.openai.com`, `https://jasper.ai`, etc.)
- "Try" buttons, "Visit Website" buttons, "Get Started" buttons, CTA links

Replace each with the corresponding affiliate_url from the config file. If an affiliate_url is still "PASTE_LINK_HERE", use the fallback_url instead.

**IMPORTANT:** 
- Add `rel="nofollow sponsored"` to ALL affiliate links (Google requires this)
- Add `target="_blank"` to all affiliate links
- Keep the affiliate disclosure visible on every page that contains affiliate links
- Do NOT add `rel="nofollow"` to internal links — only external affiliate links

### 1.3 Add Click Tracking (Simple)

Create a lightweight click tracking utility that logs affiliate clicks to help measure which tools/pages convert best. Use a simple approach:

- Add UTM parameters to all affiliate URLs: `?utm_source=toolpilot&utm_medium=review&utm_campaign={tool_slug}`
- If the affiliate program supports SubIDs, append those too
- Create a simple analytics component that fires a custom event on click (for future Google Analytics integration)

### 1.4 Verify Affiliate Disclosure Compliance

Ensure EVERY page that links to an affiliate has:
- A visible disclosure at the top of the content (not just footer)
- FTC-compliant language: "This article contains affiliate links. If you purchase through these links, we may earn a commission at no additional cost to you."
- The footer disclosure should remain as well

Ask me to paste in my affiliate links before proceeding to Phase 2. Show me the affiliate-links.json and ask me to fill in each URL.

---

## PHASE 2: SEO FOUNDATION (Critical for Google Ranking)

### 2.1 Technical SEO Audit & Fix

Check and fix ALL of the following:

**Sitemap:**
- Generate a comprehensive `sitemap.xml` in the public directory
- Include EVERY page: homepage, all tool reviews, all category pages, all comparison pages
- Include `<lastmod>`, `<changefreq>`, and `<priority>` tags
- Priority: homepage=1.0, comparison pages=0.9, tool reviews=0.8, category pages=0.7

**Robots.txt:**
- Create/update `robots.txt` in public directory
- Allow all search engines to crawl all content pages
- Disallow admin/api routes if any exist
- Reference the sitemap: `Sitemap: https://toolpilot-hub.netlify.app/sitemap.xml`

**Meta Tags (check EVERY page):**
- Unique `<title>` tag — format: `{Tool Name} Review 2026 | Pricing, Features & Alternatives | ToolPilot`
- Unique `<meta name="description">` — 150-160 chars, include primary keyword, include a value proposition
- `<meta name="robots" content="index, follow">`
- Canonical URL on every page: `<link rel="canonical" href="https://toolpilot-hub.netlify.app/{path}">`
- Open Graph tags (og:title, og:description, og:image, og:url, og:type)
- Twitter card tags

**For comparison pages, use this title format:**
`{Tool A} vs {Tool B} (2026): Which Is Better? | ToolPilot`

**Structured Data (Schema.org):**

Add JSON-LD structured data to EVERY review page:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{Tool Name}",
  "applicationCategory": "AI Tool",
  "review": {
    "@type": "Review",
    "author": {
      "@type": "Organization",
      "name": "ToolPilot"
    },
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": "{rating}",
      "bestRating": "5"
    },
    "datePublished": "{date}",
    "reviewBody": "{meta description}"
  },
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "{lowest_price}",
    "priceCurrency": "USD",
    "offerCount": "{number_of_plans}"
  }
}
```

Also add FAQ schema to pages that have FAQ sections:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{question}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{answer}"
      }
    }
  ]
}
```

Add BreadcrumbList schema to all pages:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://toolpilot-hub.netlify.app/"},
    {"@type": "ListItem", "position": 2, "name": "{Category}", "item": "https://toolpilot-hub.netlify.app/{category}"},
    {"@type": "ListItem", "position": 3, "name": "{Tool Name}"}
  ]
}
```

### 2.2 Internal Linking Structure

This is critical for SEO. Audit and fix internal linking:

- Every tool review page should link to 2-3 related comparison pages
- Every comparison page should link back to both individual review pages
- Every category page should link to all tools in that category
- Add a "Related Tools" or "You Might Also Like" section at the bottom of every review
- Add "See Also" links within article body text (contextual links, not just bottom-of-page)
- Ensure the navigation menu links to all category pages
- Add breadcrumb navigation to every page (visible, not just schema)

### 2.3 Page Speed Optimization

Check and optimize:
- All images should be WebP format or have `next/image` optimization
- Lazy load images below the fold
- Minimize JavaScript bundle size
- Ensure Core Web Vitals pass (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- Add `loading="lazy"` to images not in viewport
- Preload critical fonts and CSS

### 2.4 Mobile Responsiveness Check

Verify every page renders correctly on mobile since Google uses mobile-first indexing:
- Text is readable without zooming
- Buttons/links are tappable (min 44x44px touch targets)
- No horizontal scrolling
- Tables are responsive or scrollable

---

## PHASE 3: HIGH-VALUE CONTENT GENERATION (Automated)

### 3.1 Create Content Generation Script

Build `ai-tools-hub/scripts/generate-article.js` (or .py) that:

1. Accepts a content type parameter: `review`, `comparison`, `listicle`, or `guide`
2. Calls Claude API (Sonnet 4.5) with specialized prompts for each type
3. Generates complete, SEO-optimized HTML/MDX content
4. Includes proper affiliate links from the config file
5. Includes schema markup
6. Includes internal links to existing content
7. Updates the sitemap
8. Commits and pushes to trigger Netlify deploy

**Content Types & Templates:**

**REVIEW ARTICLE (for individual tools):**
```
Target keyword: "{tool name} review 2026"
Structure:
- H1: {Tool Name} Review 2026: Is It Worth It? [Honest Assessment]
- Quick verdict box (rating, best for, pricing, affiliate CTA)
- H2: What is {Tool Name}?
- H2: Key Features (with screenshots descriptions)
- H2: Pricing & Plans (detailed breakdown with comparison table)
- H2: Pros and Cons (honest — credibility matters)
- H2: Who Should Use {Tool Name}?
- H2: {Tool Name} vs Alternatives (brief, links to comparison pages)
- H2: FAQ (4-6 real questions people search for)
- H2: Final Verdict (with affiliate CTA)
Word count: 2,000-3,000 words
```

**COMPARISON ARTICLE (highest conversion — prioritize these):**
```
Target keyword: "{tool A} vs {tool B}"
Structure:
- H1: {Tool A} vs {Tool B} (2026): Complete Comparison
- Quick comparison table (features, pricing, rating, best for)
- H2: Overview of {Tool A}
- H2: Overview of {Tool B}
- H2: Feature-by-Feature Comparison
  - H3: {Feature 1}
  - H3: {Feature 2}
  - H3: {Feature 3}
- H2: Pricing Comparison
- H2: Which Should You Choose?
  - Choose {Tool A} if...
  - Choose {Tool B} if...
- H2: FAQ
- Affiliate CTAs for BOTH tools throughout
Word count: 2,500-3,500 words
```

**LISTICLE ARTICLE (traffic drivers):**
```
Target keyword: "best AI tools for {use case} 2026"
Structure:
- H1: {N} Best AI Tools for {Use Case} in 2026
- Quick picks table (tool, best for, price, rating)
- H2: each tool with mini-review (300-500 words each)
  - What it does
  - Key features
  - Pricing
  - Pros/Cons
  - Affiliate CTA
- H2: How We Tested
- H2: FAQ
Word count: 3,000-5,000 words
```

**GUIDE ARTICLE (authority builders):**
```
Target keyword: "how to {task} with AI"
Structure:
- H1: How to {Task} with AI: Complete Guide (2026)
- H2: sections walking through the process
- Naturally recommends tools with affiliate links
- H2: FAQ
Word count: 2,000-3,000 words
```

### 3.2 Keyword Research & Content Calendar

Create `ai-tools-hub/config/content-calendar.json`:

Generate a prioritized list of 100+ target keywords organized by:
1. **High intent / high conversion** (comparisons, "best X for Y", "X review", "X pricing")
2. **Medium intent** (how-to guides, tutorials)
3. **Traffic builders** (listicles, "what is X")

Priority order for content generation:
1. Comparison articles (these convert best — people are choosing between tools)
2. "Best X for Y" listicles (high search volume)
3. Individual reviews for tools NOT yet on the site
4. How-to guides

**Initial comparison articles to generate (these are your highest-value pages):**
- Claude vs ChatGPT 2026
- Jasper vs Copy.ai
- Jasper vs Writesonic
- Grammarly vs Jasper
- Midjourney vs Canva AI
- Runway vs Descript
- ElevenLabs vs Synthesia
- Cursor vs GitHub Copilot
- ChatGPT vs Gemini
- Notion AI vs ChatGPT
- Best AI writing tools 2026
- Best AI coding tools 2026
- Best AI image generators 2026
- Best AI video tools 2026
- Best free AI tools 2026
- Best AI tools for small business
- Best AI tools for content creators
- Best AI tools for marketers

### 3.3 Create Automated GitHub Actions Workflow

Create `.github/workflows/toolpilot-content.yml`:

```yaml
name: ToolPilot Daily Content
on:
  schedule:
    - cron: '0 6 * * 1-5'  # Mon-Fri at 6AM UTC (10PM PST previous day)
  workflow_dispatch:
    inputs:
      content_type:
        description: 'Type: review, comparison, listicle, guide'
        required: false
        default: 'comparison'
      specific_topic:
        description: 'Specific topic (optional — otherwise picks from calendar)'
        required: false

jobs:
  generate-content:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          ref: revenue-site
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: ai-tools-hub/package-lock.json
      
      - name: Install dependencies
        working-directory: ai-tools-hub
        run: npm ci
      
      - name: Generate content
        working-directory: ai-tools-hub
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          node scripts/generate-content.js \
            --type "${{ github.event.inputs.content_type || 'auto' }}" \
            --topic "${{ github.event.inputs.specific_topic || '' }}"
      
      - name: Update sitemap
        working-directory: ai-tools-hub
        run: node scripts/update-sitemap.js
      
      - name: Build site
        working-directory: ai-tools-hub
        run: npm run build
      
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: ai-tools-hub/out
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_API_TOKEN }}
          NETLIFY_SITE_ID: '616e7bf4-fe47-495b-b13e-934e51546d4c'
      
      - name: Commit content files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add -A
          git diff --staged --quiet || git commit -m "content: auto-generated article $(date +%Y-%m-%d)"
          git push
      
      - name: Summary
        run: echo "✅ New content generated and deployed" >> $GITHUB_STEP_SUMMARY
```

### 3.4 Content Generation Script Logic

The `generate-content.js` script should:

1. Read `content-calendar.json` to find the next unpublished topic
2. Check what content already exists to avoid duplicates
3. Determine the best content type based on the topic
4. Call Claude API with the appropriate template prompt
5. Generate the full page with:
   - Proper SEO meta tags
   - Schema markup
   - Affiliate links pulled from config
   - Internal links to existing related content
   - "Last updated" timestamp
6. Write the HTML/component file to the correct directory
7. Update the sitemap
8. Mark the topic as "published" in the calendar
9. Log what was generated

**Content Quality Rules (embed these in the Claude prompt):**
- NEVER generate generic filler content — every paragraph must contain specific, useful information
- ALWAYS include real pricing (check before generating — use web search if needed)
- ALWAYS include honest pros AND cons (credibility > hype)
- ALWAYS mention at least 2 alternatives with internal links
- NEVER use phrases like "in today's fast-paced world" or "look no further" or other AI slop
- Write at a conversational, expert level — like a knowledgeable friend recommending tools
- Include specific use cases and scenarios, not just feature lists
- Every H2 section should be independently valuable (people skim)

---

## PHASE 4: GOOGLE SEARCH CONSOLE & INDEXING

### 4.1 Google Search Console Setup Checklist

Print these instructions for the owner to complete (one-time manual step):

```
=== MANUAL STEP REQUIRED ===

You need to set up Google Search Console to get your site indexed.
This takes 5 minutes and is the ONLY manual thing you need to do.

1. Go to https://search.google.com/search-console
2. Click "Add Property"
3. Choose "URL prefix" and enter: https://toolpilot-hub.netlify.app
4. Choose the "HTML tag" verification method
5. Copy the meta tag they give you
6. PASTE IT HERE so I can add it to the site's <head> tag
7. Once I deploy it, go back to Search Console and click "Verify"
8. After verification, go to "Sitemaps" in the left menu
9. Submit: https://toolpilot-hub.netlify.app/sitemap.xml
10. Done. Google will start crawling within 24-48 hours.

Also set up Google Analytics:
1. Go to https://analytics.google.com
2. Create a new GA4 property for toolpilot-hub.netlify.app
3. Get the Measurement ID (starts with G-)
4. PASTE IT HERE so I can add it to the site

=== END MANUAL STEP ===
```

### 4.2 Add Google Verification & Analytics

Once the owner provides the verification meta tag and GA4 ID:
- Add the Search Console verification meta tag to the site's `<head>`
- Add the GA4 tracking script to the site's `<head>`
- Deploy

### 4.3 Index Ping Script

Create a script that pings Google whenever new content is published:

```javascript
// scripts/ping-google.js
// Pings Google's indexing API to request faster crawling of new pages
// Called automatically after each content generation
```

This should use the Google Indexing API (if set up) or at minimum update the sitemap with new URLs and submit to Search Console via API.

---

## PHASE 5: MONITORING & REPORTING

### 5.1 Create Weekly SEO Report Workflow

Create `.github/workflows/toolpilot-report.yml` that runs weekly:

1. Count total pages on site
2. Check which pages are indexed (via Search Console API if available)
3. Report total content published this week
4. Check for any broken links
5. Verify affiliate links are still working (HEAD request to each)
6. Email summary report to ALERT_EMAIL via Resend

---

## EXECUTION ORDER

Do not skip steps. Complete each phase fully before moving to the next.

1. **PHASE 1** — Set up affiliate links config, replace all direct links, add tracking
   → ASK ME for my affiliate URLs before proceeding
2. **PHASE 2** — Complete SEO audit, fix all technical issues, add schema markup
3. **PHASE 3** — Build content generation system, create first batch of comparison articles
4. **PHASE 4** — Guide me through Search Console setup, add verification/analytics
5. **PHASE 5** — Set up monitoring

After each phase, show me exactly what was done and ask for confirmation before continuing.

## IMPORTANT RULES

1. Go through ONE phase at a time
2. Ask me for input when needed (affiliate links, Search Console tag, GA4 ID)
3. Test everything before moving on
4. Keep a running status log of what's complete
5. Every page must have affiliate links, meta tags, schema markup, and internal links
6. Content quality is NON-NEGOTIABLE — better to generate 1 great article than 5 mediocre ones
7. Always commit and deploy after changes so I can verify on the live site
8. The site must remain visually professional — don't break the existing design

Start with Phase 1. Show me the affiliate-links.json file and ask me to paste in my affiliate URLs one by one.
