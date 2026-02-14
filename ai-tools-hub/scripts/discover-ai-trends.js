#!/usr/bin/env node
/**
 * ToolPilot AI Trend Discovery
 * Calls Claude to analyze current AI tool trends, then auto-adds new content items
 * to the content calendar and saves newsletter highlights.
 *
 * Usage:
 *   ANTHROPIC_API_KEY=xxx node scripts/discover-ai-trends.js
 */

const fs = require('fs')
const path = require('path')
const https = require('https')

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
const CALENDAR_FILE = path.join(__dirname, '..', 'config', 'content-calendar.json')
const HIGHLIGHTS_FILE = path.join(__dirname, '..', 'config', 'newsletter-highlights.json')
const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')

async function callClaude(prompt, maxTokens = 4000) {
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

async function main() {
  if (!ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is required')
    process.exit(1)
  }

  // Load existing content for deduplication
  const calendar = JSON.parse(fs.readFileSync(CALENDAR_FILE, 'utf8'))
  const existingTools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const existingComparisons = JSON.parse(fs.readFileSync(COMPARISONS_FILE, 'utf8'))
  const existingArticles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))

  const existingSlugs = new Set([
    ...existingTools.map(t => t.slug),
    ...existingComparisons.map(c => c.slug),
    ...existingArticles.map(a => a.slug),
    ...calendar.items.map(i => i.slug),
  ])

  const existingToolNames = existingTools.map(t => t.name).join(', ')

  const prompt = `You are an AI tools market analyst. Analyze current AI tool trends for ${new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} and suggest new content for ToolPilot, an AI tools review site focused on "Make Money & Save Money with AI."

EXISTING TOOLS WE ALREADY COVER: ${existingToolNames}

EXISTING CONTENT SLUGS (DO NOT DUPLICATE): ${[...existingSlugs].join(', ')}

Based on your knowledge of the AI tools landscape, suggest:

1. ONE new AI tool review — a tool that's trending, recently updated, or gaining traction. Must NOT be one we already cover. Focus on tools with free tiers or money-making potential.

2. ONE new comparison — between two tools our readers would be deciding between. One tool can be from our existing list. The comparison slug must not exist.

3. ONE new article/listicle — money-focused, buyer-intent content. Something like "Best AI Tools for [specific use case]" or "How to [money goal] with AI Tools."

4. Newsletter highlights — trending topic, money tip, and free tool spotlight for this week's newsletter.

Return ONLY valid JSON:
{
  "new_review": {
    "slug": "tool-slug",
    "tool_name": "Tool Name",
    "category": "writing|coding|image|video|marketing|productivity|audio|seo|research|design",
    "keyword": "tool name review 2026",
    "why": "1-sentence reason this tool is trending now"
  },
  "new_comparison": {
    "slug": "tool1-vs-tool2",
    "tools": ["tool1-slug", "tool2-slug"],
    "tool_names": ["Tool 1 Name", "Tool 2 Name"],
    "keyword": "tool1 vs tool2 2026",
    "why": "1-sentence reason this comparison is relevant now"
  },
  "new_article": {
    "slug": "article-slug-here",
    "title": "Article Title Here",
    "keyword": "main keyword phrase",
    "money_angle": "specific money-making or money-saving angle",
    "why": "1-sentence reason this topic is relevant now"
  },
  "newsletter_highlights": {
    "trending_topic": "1-2 sentences about the biggest AI tool trend this week",
    "money_tip": "1-2 sentences with a specific money-saving or money-making tip using AI",
    "free_tool_spotlight": "Name and 1-sentence description of a great free AI tool"
  }
}`

  console.log('Discovering AI tool trends via Claude...')
  const response = await callClaude(prompt)

  const match = response.match(/\{[\s\S]*\}/)
  if (!match) {
    console.error('Failed to extract JSON from response')
    process.exit(1)
  }

  const discovery = JSON.parse(match[0])

  // Get next available ID
  const maxId = Math.max(...calendar.items.map(i => i.id), 0)
  let nextId = maxId + 1

  let added = 0

  // Add new review to calendar
  if (discovery.new_review && !existingSlugs.has(discovery.new_review.slug)) {
    calendar.items.push({
      id: nextId++,
      type: 'review',
      priority: 'high',
      status: 'pending',
      slug: discovery.new_review.slug,
      tool_name: discovery.new_review.tool_name,
      category: discovery.new_review.category,
      keyword: discovery.new_review.keyword,
    })
    console.log(`  Added review: ${discovery.new_review.tool_name} (${discovery.new_review.why})`)
    added++
  }

  // Add new comparison
  if (discovery.new_comparison && !existingSlugs.has(discovery.new_comparison.slug)) {
    calendar.items.push({
      id: nextId++,
      type: 'comparison',
      priority: 'high',
      status: 'pending',
      slug: discovery.new_comparison.slug,
      tools: discovery.new_comparison.tools,
      tool_names: discovery.new_comparison.tool_names,
      keyword: discovery.new_comparison.keyword,
    })
    console.log(`  Added comparison: ${discovery.new_comparison.slug} (${discovery.new_comparison.why})`)
    added++
  }

  // Add new article
  if (discovery.new_article && !existingSlugs.has(discovery.new_article.slug)) {
    calendar.items.push({
      id: nextId++,
      type: 'listicle',
      priority: 'high',
      status: 'pending',
      slug: discovery.new_article.slug,
      title: discovery.new_article.title,
      keyword: discovery.new_article.keyword,
      money_angle: discovery.new_article.money_angle,
    })
    console.log(`  Added article: ${discovery.new_article.title} (${discovery.new_article.why})`)
    added++
  }

  // Save updated calendar
  calendar.last_updated = new Date().toISOString().split('T')[0]
  fs.writeFileSync(CALENDAR_FILE, JSON.stringify(calendar, null, 2))
  console.log(`\nCalendar updated: ${added} new items added`)

  // Save newsletter highlights
  if (discovery.newsletter_highlights) {
    const highlights = {
      ...discovery.newsletter_highlights,
      generated_at: new Date().toISOString(),
    }
    fs.writeFileSync(HIGHLIGHTS_FILE, JSON.stringify(highlights, null, 2))
    console.log('Newsletter highlights saved')
  }

  console.log('\n=== Discovery Summary ===')
  console.log(`New items added to calendar: ${added}`)
  console.log(`Total calendar items: ${calendar.items.length}`)
  console.log(`Pending items: ${calendar.items.filter(i => i.status === 'pending').length}`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
