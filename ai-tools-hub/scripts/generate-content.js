#!/usr/bin/env node
/**
 * ToolPilot Content Generation Script
 * Reads from content-calendar.json, picks the next pending item,
 * generates content via Claude API, and writes to the appropriate data file.
 *
 * Usage:
 *   ANTHROPIC_API_KEY=xxx node scripts/generate-content.js
 *   ANTHROPIC_API_KEY=xxx node scripts/generate-content.js --type comparison
 *   ANTHROPIC_API_KEY=xxx node scripts/generate-content.js --type review --count 3
 *   ANTHROPIC_API_KEY=xxx node scripts/generate-content.js --topic "github-copilot"
 */

const fs = require('fs')
const path = require('path')
const https = require('https')

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
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

// ---------- Claude API ----------

async function callClaude(prompt, maxTokens = 3000) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: maxTokens,
      messages: [{ role: 'user', content: prompt }]
    })

    const options = {
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Length': Buffer.byteLength(data)
      }
    }

    const req = https.request(options, (res) => {
      let body = ''
      res.on('data', chunk => body += chunk)
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body)
          if (parsed.content && parsed.content[0]) {
            resolve(parsed.content[0].text)
          } else {
            reject(new Error(`Unexpected API response: ${body.substring(0, 300)}`))
          }
        } catch (e) {
          reject(new Error(`Failed to parse API response: ${e.message}`))
        }
      })
    })

    req.on('error', reject)
    req.write(data)
    req.end()
  })
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

IMPORTANT RULES:
- Use REAL, ACCURATE information about ${toolName}
- Pricing should reflect actual current rates
- Be HONEST in pros and cons — credibility matters
- Every field must have substantive, specific content (no generic filler)
- The description should explain what makes this tool notable, not just what it does

Return ONLY valid JSON (no markdown, no explanation) matching this exact structure:
{
  "slug": "${slug}",
  "name": "${toolName}",
  "tagline": "short tagline under 80 chars — be specific, not generic",
  "description": "2-3 sentences. What the tool does, who it's for, and what makes it stand out.",
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
  "company": "Actual Company Name",
  "money_use_cases": ["3-4 specific ways people make money using this tool (e.g., 'Freelance blog writing at $0.10-0.20/word', 'Creating and selling online courses')"],
  "free_tier_verdict": "1-2 sentences: Is the free tier good enough for real use? What can you actually accomplish without paying?"
}`

  console.log(`  Calling Claude API for ${toolName} review...`)
  const response = await callClaude(prompt)
  return extractJson(response)
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

// ---------- Listicle/Article Generation ----------

async function generateListicle(item, existingTools) {
  const slug = item.slug
  const title = item.title
  const keyword = item.keyword
  const moneyAngle = item.money_angle || ''

  // Build context from existing tools if tool_slugs are specified
  let toolContext = ''
  if (item.tool_slugs && item.tool_slugs.length > 0) {
    const tools = item.tool_slugs
      .map(s => existingTools.find(t => t.slug === s))
      .filter(Boolean)
    if (tools.length > 0) {
      toolContext = `\nExisting tool data to reference:\n${tools.map(t =>
        `- ${t.name}: ${t.rating}/5, ${t.pricing.free_tier ? 'free tier' : '$' + t.pricing.starting_price + '/mo'}, best for: ${t.best_for.slice(0, 2).join(', ')}`
      ).join('\n')}`
    }
  }

  const prompt = `Write a comprehensive buyer's guide article titled "${title}" targeting the keyword "${keyword}".
${toolContext}
${moneyAngle ? `\nMONEY ANGLE: ${moneyAngle}` : ''}

IMPORTANT RULES:
- Write from a "Make Money & Save Money with AI" perspective
- Include practical, actionable money-making or money-saving tips for EACH tool mentioned
- Include real pricing data and honest free tier assessments
- Write 2000-3000 words of substantive, specific content
- Use HTML formatting (h2, h3, p, ul/li, strong, a tags, figure/table)
- Include a comparison table near the top
- Include an FAQ section with 4-5 questions using schema.org FAQPage markup
- Internal links should use relative paths like /tools/slug/ and /compare/slug/
- NO markdown — only valid HTML
- Be honest and specific, not generic or fluffy

Return ONLY valid JSON matching this structure:
{
  "slug": "${slug}",
  "title": "${title}",
  "excerpt": "150-160 chars summarizing the article with the main keyword",
  "html": "<p>Full article HTML content here...</p>",
  "category": "the most relevant category (writing, coding, image, video, marketing, productivity, audio, seo, research, design)",
  "tags": ["4-6 relevant tags as kebab-case strings"],
  "word_count": approximate word count (number),
  "published_date": "${new Date().toISOString().split('T')[0]}",
  "author": "ToolPilot Team",
  "featured": ${item.priority === 'high' ? 'true' : 'false'},
  "meta_title": "SEO-optimized title under 60 chars",
  "meta_description": "150-160 char meta description with primary keyword",
  "keywords": ["${keyword}", "2-3 more relevant keywords"]
}`

  console.log(`  Calling Claude API for listicle "${title}"...`)
  const response = await callClaude(prompt, 8000)
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
  if (!ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is required')
    process.exit(1)
  }

  const calendar = JSON.parse(fs.readFileSync(CALENDAR_FILE, 'utf8'))
  const existingTools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const existingComparisons = JSON.parse(fs.readFileSync(COMPARISONS_FILE, 'utf8'))
  const toolSlugs = new Set(existingTools.map(t => t.slug))
  const compSlugs = new Set(existingComparisons.map(c => c.slug))

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

      } else if (item.type === 'listicle') {
        const existingArticles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
        const articleSlugs = new Set(existingArticles.map(a => a.slug))

        if (articleSlugs.has(item.slug)) {
          console.log(`  Skipping — ${item.slug} already exists in articles.json`)
          markPublished(calendar, item.id)
          continue
        }

        const article = await generateListicle(item, existingTools)
        existingArticles.push(article)
        fs.writeFileSync(ARTICLES_FILE, JSON.stringify(existingArticles, null, 2))
        console.log(`  Done: ${article.title} (${article.word_count} words)`)
      }

      markPublished(calendar, item.id)
      generated++

      // Rate limit between API calls
      if (i < maxCount - 1) {
        console.log('  Waiting 3s (rate limit)...')
        await new Promise(r => setTimeout(r, 3000))
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

  const existingArticles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
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
