#!/usr/bin/env node
/**
 * PilotTools Content Generation Script
 * Reads from content-calendar.json, picks the next pending item,
 * generates content via Claude API, and writes to the appropriate data file.
 *
 * Usage:
 *   GEMINI_API_KEY=xxx node scripts/generate-content.js
 *   GEMINI_API_KEY=xxx node scripts/generate-content.js --type comparison
 *   GEMINI_API_KEY=xxx node scripts/generate-content.js --type review --count 3
 *   GEMINI_API_KEY=xxx node scripts/generate-content.js --topic "github-copilot"
 */

const fs = require('fs')
const path = require('path')
const https = require('https')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || process.env.ANTHROPIC_API_KEY
const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')
const CALENDAR_FILE = path.join(__dirname, '..', 'config', 'content-calendar.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}

const requestedType = getArg('type') || 'auto'
const requestedTopic = getArg('topic') || ''
const maxCount = parseInt(getArg('count') || '1', 10)

// ---------- Gemini API ----------

async function callClaude(prompt, maxTokens = 3000) {
  // Function name kept as callClaude for backward compatibility with callers
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`

  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: maxTokens, temperature: 0.7 }
        })
      })

      if (resp.status === 429 && attempt < 2) {
        const wait = 15000 * (attempt + 1)
        console.log(`Gemini 429 rate limit — waiting ${wait / 1000}s (attempt ${attempt + 1}/3)`)
        await new Promise(r => setTimeout(r, wait))
        continue
      }

      const json = await resp.json()
      if (json.candidates && json.candidates[0] && json.candidates[0].content) {
        return json.candidates[0].content.parts[0].text
      } else {
        throw new Error(`Unexpected API response: ${JSON.stringify(json).substring(0, 300)}`)
      }
    } catch (e) {
      if (attempt === 2) throw e
      if (e.message && e.message.includes('429')) {
        await new Promise(r => setTimeout(r, 15000 * (attempt + 1)))
        continue
      }
      throw e
    }
  }
}

function extractJson(text) {
  // Try to extract JSON object or array from Claude's response
  const objMatch = text.match(/\{[\s\S]*\}/)
  if (objMatch) return JSON.parse(objMatch[0])
  const arrMatch = text.match(/\[[\s\S]*\]/)
  if (arrMatch) return JSON.parse(arrMatch[0])
  throw new Error('Could not extract JSON from response')
}

// ---------- Review Generation ----------

async function generateReview(toolName, category) {
  const slug = toolName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '')

  const prompt = `Generate a JSON object for an AI tool review of "${toolName}" in the "${category}" category.

IMPORTANT QUALITY RULES FOR 2026:
- Use REAL, ACCURATE information about ${toolName} as of March 2026
- Pricing must reflect actual current rates (include March 2026 date)
- Description MUST be 400+ words, not 2-3 sentences. Include:
  * Direct answer in first 50 words (for Google's GEO citations)
  * Real features with specific examples
  * Pricing details with dates ("As of March 2026")
  * Use cases and who it's best for
  * How it compares to main competitors
  * First-person language: "In our testing", "We found", "Our team reviewed"
- NO filler phrases: "In today's digital landscape", "In the world of AI", "Cutting-edge technology"
- Be HONEST in pros/cons — credibility matters. Every tool has real weaknesses
- Every field must be substantive and specific

Return ONLY valid JSON (no markdown, no explanation) matching this exact structure:
{
  "slug": "${slug}",
  "name": "${toolName}",
  "tagline": "short tagline under 80 chars — be specific, not generic",
  "description": "400+ words as detailed above. Start with direct answer. Use first-person. Include real pricing with March 2026 date.",
  "category": "${category}",
  "categories": ["${category}", "add 1-2 other relevant categories from: writing, coding, image, video, marketing, productivity, audio, seo, research, design"],
  "pricing": {
    "free_tier": true or false,
    "starting_price": number or null (for custom pricing),
    "currency": "USD",
    "billing": "monthly",
    "plans": [
      {"name": "Plan Name", "price": number or null, "features": ["3-4 specific features"]}
    ]
  },
  "rating": number between 4.0 and 4.9 (realistic, not everything is 4.8+),
  "review_count": realistic number based on the tool's actual popularity,
  "affiliate_url": "https://actual-website-url.com",
  "website": "https://actual-website-url.com",
  "features": ["6-8 specific features of this tool"],
  "pros": ["4-5 honest pros"],
  "cons": ["3-4 honest cons — every tool has real weaknesses"],
  "best_for": ["3-4 specific use cases"],
  "logo": "/logos/${slug}.svg",
  "founded": year (real founding year),
  "company": "Actual Company Name"
}`

  console.log(`  Calling Claude API for ${toolName} review...`)
  const response = await callClaude(prompt, 4000)
  return extractJson(response)
}

// ---------- Article Generation (Pricing, Alternatives, "Is It Worth It") ----------

async function generateArticle(item, existingTools) {
  const slug = item.slug
  let prompt = ''

  if (item.slug.includes('pricing')) {
    // Pricing page
    const toolName = item.tool_name
    prompt = `You are writing a detailed pricing guide article for "${toolName}" on an AI tools review site.

Generate a JSON object with:
- slug: "${slug}"
- title: "${item.title}"
- html: 2000+ words of HTML-formatted article with <h2>, <h3>, <p>, <ul>, <table> tags
- meta_description: compelling 155-160 char description including "pricing 2026"
- keywords: ["${toolName.toLowerCase()} pricing", "${toolName.toLowerCase()} plans 2026", "pricing comparison"]
- published_date: "2026-03-20"

Article structure (2000+ words):
1. Intro (200 words) — Direct answer: What is ${toolName}'s pricing model? Why does it matter?
2. Pricing Breakdown (400+ words) — All plans, features per plan, free tier details
3. Annual vs Monthly (200 words) — Discounts, lock-in terms, flexibility
4. ROI Analysis (400 words) — Cost per feature, value for [students/freelancers/agencies], ROI examples
5. Comparison Table (200 words) — ${toolName} vs 3 competitors in pricing tiers, features, value
6. FAQ Section (400 words) — 5-8 Q&A covering: free trial, refund policy, payment methods, discounts, hidden costs, upgrade process, enterprise options
7. Verdict (200 words) — Final recommendation: who should choose ${toolName} at each price tier

CONTENT RULES:
- Use first-person: "We compared ${toolName} to 50+ tools", "In our testing"
- Include real March 2026 pricing data
- Add 2+ internal links to pilottools.ai tool pages (e.g. <a href="/tools/chatgpt">ChatGPT</a>)
- Add affiliate CTAs: "Check current ${toolName} pricing"
- NO filler phrases like "In today's world" or "Cutting-edge"
- Use <table> for pricing comparison
- Use <strong> for emphasis on key points

Return ONLY valid JSON (no markdown).`

  } else if (item.slug.includes('alternatives')) {
    // Alternatives page
    const toolName = item.tool_name
    prompt = `You are writing an alternatives guide for "${toolName}" on an AI tools review site.

Generate a JSON object with:
- slug: "${slug}"
- title: "${item.title}"
- content: 2000+ words of HTML-formatted article
- meta_description: compelling 155-160 char description
- keywords: ["${toolName.toLowerCase()} alternatives", "best ${toolName.toLowerCase()} alternatives 2026", "tools like ${toolName.toLowerCase()}"]
- published_date: "2026-03-20"

Article structure (2000+ words):
1. Intro (200 words) — Direct answer: What are the best ${toolName} alternatives in 2026? Why consider alternatives?
2. Comparison Overview (300 words) — Quick matrix: tool, pricing, best for, top feature
3. Top Alternatives (1200+ words) — 4-5 detailed alternatives, 200+ words each:
   - Tool name, pricing, best for
   - Key differences from ${toolName}
   - Pros and cons
   - Ideal use case
   - Link to review page
4. Feature Comparison Table (200 words) — ${toolName} vs 4 alternatives: price, free tier, ease of use, best feature
5. How to Choose (300 words) — Decision factors: budget, features, learning curve, integrations
6. FAQ (200 words) — 4-5 questions about finding alternatives, migration tips

CONTENT RULES:
- First-person: "We tested ${toolName} and 10 alternatives", "In our comparison"
- Add 2+ internal links to pilottools.ai tool reviews
- Add affiliate CTAs per tool: "Try [Alternative Tool]"
- Real March 2026 pricing
- Balanced recommendations — don't just say alternatives are better
- Use <a> tags for internal links
- Use <table> for feature comparison

Return ONLY valid JSON (no markdown).`

  } else if (item.slug.includes('worth-it')) {
    // "Is it worth it" page
    const toolName = item.tool_name
    prompt = `You are writing a ROI analysis article: "Is ${toolName} Worth It in 2026?"

Generate a JSON object with:
- slug: "${slug}"
- title: "${item.title}"
- content: 2000+ words of HTML-formatted article
- meta_description: compelling 155-160 char description
- keywords: ["is ${toolName.toLowerCase()} worth it", "${toolName.toLowerCase()} value for money 2026"]
- published_date: "2026-03-20"

Article structure (2000+ words):
1. Direct Answer (200 words) — Yes/no/maybe with conditions. What makes it worth it?
2. Pricing Breakdown (300 words) — Cost analysis, free tier, pricing tiers, annual cost
3. Real-World ROI (500 words) — Case study with 3 scenarios:
   - Freelancer: cost vs time savings vs income boost
   - Agency: team cost vs productivity gains vs billable hours increase
   - Solo creator: subscription cost vs revenue generated
   - Include real numbers and percentages
4. Pros Worth the Cost (300 words) — 5-6 features that justify the price, with real examples
5. Cons That Might Not Be Worth It (300 words) — Limitations, cheaper alternatives for specific needs
6. Verdict (200 words) — Who should buy, who shouldn't, what to know first
7. FAQ (200 words) — 5-6 questions about ROI, when it's worth it, free alternatives

CONTENT RULES:
- First-person: "In our testing", "We found", "Our analysis shows"
- Real March 2026 pricing
- Specific use case examples
- Include 2+ internal links to competitor reviews
- Add affiliate CTA
- Be balanced — not every tool is worth it for everyone
- Use realistic numbers/percentages

Return ONLY valid JSON (no markdown).`
  }

  console.log(`  Calling Gemini API for article: ${slug}...`)
  const response = await callClaude(prompt, 8000)
  const article = extractJson(response)

  // Ensure required fields
  article.slug = article.slug || slug
  article.published_date = article.published_date || new Date().toISOString().split('T')[0]

  return article
}

// ---------- Listicle Generation ----------

async function generateListicle(item, existingTools) {
  const slug = item.slug
  const title = item.title

  // Extract profession or task from slug
  const match = slug.match(/best-ai-tools-(.+)$/)
  const subject = match ? match[1].replace(/-/g, ' ') : 'AI tools'

  const prompt = `You are writing a listicle: "${title}" for an AI tools review site.

The subject is: ${subject}

Generate a JSON object with:
- slug: "${slug}"
- title: "${title}"
- html: 2000+ words of HTML-formatted listicle with tool cards, comparison table, verdict
- meta_description: compelling 155-160 char description
- keywords: ["best ai tools for ${subject}", "${subject} ai tools 2026"]
- published_date: "2026-03-20"

Article structure (2000+ words):
1. Intro (200 words) — Direct answer: What are the best AI tools for ${subject}? Why does this matter for [job/task]?
2. Quick Comparison (300 words) — Table: tool name, price, best feature, rating
3. Detailed Tool Reviews (1200+ words) — 4-6 tools, 150-200 words each:
   - Tool name and logo
   - Tagline
   - Best for: specific use case for ${subject}
   - Key features with [Feature: Description]
   - Pricing: starting price, free tier
   - Why we chose it for ${subject}
   - Link to full review: <a href="/tools/[tool-slug]">[Tool Name] full review</a>
4. Feature Comparison Table (200 words) — Tools vs features needed for ${subject}
5. How to Choose (300 words) — Decision criteria: budget, features, learning curve, integrations
6. Verdict (200 words) — Top pick recommendation with reasoning
7. FAQ (300 words) — 5-6 common questions for ${subject}

OUTPUT FORMAT for tool cards in content:
<div class="tool-card">
  <h3>[Tool Name]</h3>
  <p><strong>Starting Price:</strong> \$X/month</p>
  <p><strong>Best For:</strong> [Use case for ${subject}]</p>
  <ul>
    <li>[Feature 1]: [Benefit]</li>
    <li>[Feature 2]: [Benefit]</li>
    <li>[Feature 3]: [Benefit]</li>
  </ul>
  <p><a href="/tools/[tool-slug]">Read full [Tool Name] review</a></p>
</div>

CONTENT RULES:
- First-person: "In our testing for ${subject}", "We found these tools help [job/task]"
- Real March 2026 pricing
- Specific ${subject} use cases and examples
- Include 4+ internal links to pilottools.ai tool reviews
- Add affiliate CTAs per tool
- Focus on ROI for ${subject}: time saved, quality improvement, cost savings
- No generic filler — be specific to ${subject}

Return ONLY valid JSON (no markdown).`

  console.log(`  Calling Gemini API for listicle: ${slug}...`)
  const response = await callClaude(prompt, 8000)
  const listicle = extractJson(response)

  // Ensure required fields
  listicle.slug = listicle.slug || slug
  listicle.published_date = listicle.published_date || new Date().toISOString().split('T')[0]

  return listicle
}

// ---------- Comparison Generation ----------

async function generateComparison(tool1Name, tool2Name, tool1Data, tool2Data) {
  const slug = `${tool1Name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-vs-${tool2Name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`.replace(/-+/g, '-')

  // Build context from existing tool data if available
  let context = ''
  if (tool1Data) {
    context += `\n${tool1Name} data: Rating ${tool1Data.rating}/5, ${tool1Data.pricing.free_tier ? 'has free tier' : 'no free tier'}, starting at $${tool1Data.pricing.starting_price || 'custom'}/mo. Features: ${tool1Data.features.slice(0, 4).join(', ')}.`
  }
  if (tool2Data) {
    context += `\n${tool2Name} data: Rating ${tool2Data.rating}/5, ${tool2Data.pricing.free_tier ? 'has free tier' : 'no free tier'}, starting at $${tool2Data.pricing.starting_price || 'custom'}/mo. Features: ${tool2Data.features.slice(0, 4).join(', ')}.`
  }

  const prompt = `Generate a JSON comparison of "${tool1Name}" vs "${tool2Name}" for an AI tools review site.
${context}

IMPORTANT RULES:
- Be HONEST and balanced — don't always pick the more popular tool
- Each comparison point needs specific, insightful notes (not vague statements)
- The verdict should help someone make a real decision
- Use "tie" when tools are genuinely equal on a feature

Return ONLY valid JSON matching this structure:
{
  "slug": "${slug}",
  "title": "${tool1Name} vs ${tool2Name}: Which Is Better in 2026?",
  "meta_description": "150-160 char description comparing ${tool1Name} and ${tool2Name}. Include primary keyword and value prop.",
  "tools": ["${tool1Data ? tool1Data.slug : tool1Name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}", "${tool2Data ? tool2Data.slug : tool2Name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}"],
  "category": "the most relevant category",
  "keywords": ["${tool1Name.toLowerCase()} vs ${tool2Name.toLowerCase()}", "2-3 more relevant search terms"],
  "verdict": "2-3 sentences. Clear recommendation: who should pick which tool and why. Be specific.",
  "comparison_points": [
    {
      "feature": "Feature Name (e.g., Writing Quality, Ease of Use, Pricing, etc.)",
      "tool1_score": number 3.0-5.0,
      "tool2_score": number 3.0-5.0,
      "winner": "tool1_slug" or "tool2_slug" or "tie",
      "notes": "Specific explanation of why one wins. Reference actual features."
    }
  ]
}

Include 6-8 comparison points covering: core quality, ease of use, features, pricing, integrations, support, and 1-2 category-specific aspects. Use the actual tool slugs for the winner field.`

  console.log(`  Calling Claude API for ${tool1Name} vs ${tool2Name}...`)
  const response = await callClaude(prompt, 4000)
  return extractJson(response)
}

// ---------- Calendar Logic ----------

function getNextItem(calendar, type) {
  const pending = calendar.items
    .filter(item => item.status === 'pending')
    .filter(item => type === 'auto' || item.type === type)
    .sort((a, b) => {
      // Sort by priority (high > medium > low), then by id
      const priorityOrder = { high: 0, medium: 1, low: 2 }
      const pDiff = (priorityOrder[a.priority] || 2) - (priorityOrder[b.priority] || 2)
      return pDiff !== 0 ? pDiff : a.id - b.id
    })

  if (requestedTopic) {
    return pending.find(item => item.slug === requestedTopic) || null
  }

  return pending[0] || null
}

function markPublished(calendar, itemId) {
  const item = calendar.items.find(i => i.id === itemId)
  if (item) {
    item.status = 'published'
    item.published_date = new Date().toISOString().split('T')[0]
  }
  calendar.last_updated = new Date().toISOString().split('T')[0]
  fs.writeFileSync(CALENDAR_FILE, JSON.stringify(calendar, null, 2))
}

// ---------- Main ----------

async function main() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY environment variable is required')
    process.exit(1)
  }

  const calendar = JSON.parse(fs.readFileSync(CALENDAR_FILE, 'utf8'))
  const existingTools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const existingComparisons = JSON.parse(fs.readFileSync(COMPARISONS_FILE, 'utf8'))
  let existingArticles = []
  const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
  if (fs.existsSync(ARTICLES_FILE)) {
    existingArticles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
  }

  const toolSlugs = new Set(existingTools.map(t => t.slug))
  const compSlugs = new Set(existingComparisons.map(c => c.slug))
  const articleSlugs = new Set(existingArticles.map(a => a.slug))

  let generated = 0

  for (let i = 0; i < maxCount; i++) {
    const item = getNextItem(calendar, requestedType)

    if (!item) {
      console.log('No more pending items in the calendar.')
      break
    }

    console.log(`\n[${i + 1}/${maxCount}] Generating: ${item.type} — ${item.slug} (priority: ${item.priority})`)

    try {
      if (item.type === 'review') {
        if (toolSlugs.has(item.slug)) {
          console.log(`  Skipping — ${item.slug} already exists in tools.json`)
          markPublished(calendar, item.id)
          continue
        }

        const review = await generateReview(item.tool_name, item.category)
        existingTools.push(review)
        fs.writeFileSync(TOOLS_FILE, JSON.stringify(existingTools, null, 2))
        toolSlugs.add(item.slug)
        console.log(`  Done: ${review.name} (${review.rating}/5)`)

      } else if (item.type === 'comparison') {
        if (compSlugs.has(item.slug)) {
          console.log(`  Skipping — ${item.slug} already exists in comparisons.json`)
          markPublished(calendar, item.id)
          continue
        }

        // Resolve tool names
        const toolNames = item.tool_names || item.tools.map(slug => {
          const t = existingTools.find(t => t.slug === slug)
          return t ? t.name : slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        })
        const tool1Data = existingTools.find(t => t.slug === item.tools[0]) || null
        const tool2Data = existingTools.find(t => t.slug === (item.tools[1] || '')) || null

        const comparison = await generateComparison(toolNames[0], toolNames[1], tool1Data, tool2Data)
        existingComparisons.push(comparison)
        fs.writeFileSync(COMPARISONS_FILE, JSON.stringify(existingComparisons, null, 2))
        compSlugs.add(item.slug)
        console.log(`  Done: ${comparison.title}`)

      } else if (item.type === 'article') {
        if (articleSlugs.has(item.slug)) {
          console.log(`  Skipping — ${item.slug} already exists in articles.json`)
          markPublished(calendar, item.id)
          continue
        }

        const article = await generateArticle(item, existingTools)
        existingArticles.push(article)
        fs.writeFileSync(ARTICLES_FILE, JSON.stringify(existingArticles, null, 2))
        articleSlugs.add(item.slug)
        console.log(`  Done: ${article.title}`)

      } else if (item.type === 'listicle') {
        if (articleSlugs.has(item.slug)) {
          console.log(`  Skipping — ${item.slug} already exists in articles.json`)
          markPublished(calendar, item.id)
          continue
        }

        const listicle = await generateListicle(item, existingTools)
        existingArticles.push(listicle)
        fs.writeFileSync(ARTICLES_FILE, JSON.stringify(existingArticles, null, 2))
        articleSlugs.add(item.slug)
        console.log(`  Done: ${listicle.title}`)

      }

      markPublished(calendar, item.id)
      generated++

      // Rate limit between API calls (increased to 5s)
      if (i < maxCount - 1) {
        console.log('  Waiting 5s (rate limit)...')
        await new Promise(r => setTimeout(r, 5000))
      }

    } catch (err) {
      console.error(`  Error generating ${item.slug}: ${err.message}`)
    }
  }

  // Regenerate sitemap if content was added
  if (generated > 0) {
    console.log('\nRegenerating sitemap...')
    require('./generate-sitemap.js')
    console.log('\nRegenerating Pinterest pins...')
    require('./generate-pins.js')
  }

  console.log(`\n=== Summary ===`)
  console.log(`Generated: ${generated} items`)
  console.log(`Total tools: ${existingTools.length}`)
  console.log(`Total comparisons: ${existingComparisons.length}`)
  console.log(`Total articles: ${existingArticles.length}`)
  const remaining = calendar.items.filter(i => i.status === 'pending').length
  console.log(`Calendar items remaining: ${remaining}`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
