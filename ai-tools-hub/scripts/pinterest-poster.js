#!/usr/bin/env node
/**
 * PilotTools Pinterest Pin Poster
 * Generates pin content via Gemini and posts to Pinterest via Make.com webhook.
 *
 * Usage:
 *   MAKE_WEBHOOK_PILOTTOOLS=url GEMINI_API_KEY=x node scripts/pinterest-poster.js
 *   node scripts/pinterest-poster.js --count 5
 *   node scripts/pinterest-poster.js --type tool-review
 */

const fs = require('fs')
const path = require('path')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY
const WEBHOOK_URL = process.env.MAKE_WEBHOOK_PILOTTOOLS

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
const HISTORY_FILE = path.join(__dirname, '..', 'config', 'pinterest-history.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}
const maxCount = parseInt(getArg('count') || '3', 10)
const requestedType = getArg('type') || 'auto'

// Board mapping by category
const BOARDS = {
  writing: 'AI Writing Tools',
  coding: 'AI Coding Tools',
  image: 'AI Image Generators',
  video: 'AI Video Tools',
  marketing: 'AI Marketing Tools',
  productivity: 'AI Productivity Tools',
  audio: 'AI Audio Tools',
  seo: 'AI SEO Tools',
  research: 'AI Research Tools',
  design: 'AI Design Tools',
  comparison: 'AI Tool Comparisons',
  general: 'Best AI Tools 2026'
}

// ---------- Gemini API ----------

async function callGemini(prompt, maxTokens = 2000) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: maxTokens, temperature: 0.8 }
        })
      })
      if (resp.status === 429 && attempt < 2) {
        console.log(`  Gemini 429 — waiting ${15 * (attempt + 1)}s`)
        await new Promise(r => setTimeout(r, 15000 * (attempt + 1)))
        continue
      }
      const json = await resp.json()
      if (json.candidates?.[0]?.content) {
        return json.candidates[0].content.parts[0].text
      }
      throw new Error(`Unexpected response: ${JSON.stringify(json).substring(0, 200)}`)
    } catch (e) {
      if (attempt === 2) throw e
      if (e.message?.includes('429')) {
        await new Promise(r => setTimeout(r, 15000 * (attempt + 1)))
        continue
      }
      throw e
    }
  }
}

function extractJson(text) {
  const objMatch = text.match(/\{[\s\S]*\}/)
  if (objMatch) return JSON.parse(objMatch[0])
  throw new Error('Could not extract JSON from response')
}

// ---------- History / Dedup ----------

function loadHistory() {
  try {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'))
  } catch { return [] }
}

function saveHistory(history) {
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2))
}

function wasPostedRecently(history, slug, days = 14) {
  const cutoff = Date.now() - days * 86400000
  return history.some(h => h.slug === slug && new Date(h.posted_at).getTime() > cutoff)
}

// ---------- Pin Type Generators ----------

async function generateToolReviewPin(tool) {
  const prompt = `Generate a Pinterest pin for an AI tool review. Tool: "${tool.name}" (${tool.category}, rated ${tool.rating}/5, starting at $${tool.pricing.starting_price || 'Free'}/mo).

Return ONLY valid JSON:
{
  "title": "concise pin title under 100 chars — include tool name and a compelling hook",
  "description": "2-3 sentences about key features, who it's for, and pricing. Include keywords: ${tool.name}, AI tools, ${tool.category}. End with: 'Read our full review at pilottools.ai' (max 500 chars)"
}`
  const result = extractJson(await callGemini(prompt))
  return {
    ...result,
    link: `https://pilottools.ai/tools/${tool.slug}/`,
    board_name: BOARDS[tool.category] || BOARDS.general,
    source_slug: tool.slug,
    pin_type: 'tool-review'
  }
}

async function generateComparisonPin(comp) {
  const toolNames = comp.tool_names || comp.tools.map(s => s.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))
  const prompt = `Generate a Pinterest pin for an AI tool comparison: "${toolNames[0]} vs ${toolNames[1]}".
Verdict: ${comp.verdict || 'See the full comparison'}

Return ONLY valid JSON:
{
  "title": "compelling comparison title under 100 chars — include both tool names",
  "description": "Quick verdict + key differentiator + CTA. Include keywords. End with: 'Full comparison at pilottools.ai' (max 500 chars)"
}`
  const result = extractJson(await callGemini(prompt))
  return {
    ...result,
    link: `https://pilottools.ai/compare/${comp.slug}/`,
    board_name: BOARDS.comparison,
    source_slug: comp.slug,
    pin_type: 'comparison'
  }
}

async function generateCategoryPin(category) {
  const prompt = `Generate a Pinterest pin for a "Best AI ${category} Tools 2026" roundup page on pilottools.ai.

Return ONLY valid JSON:
{
  "title": "compelling title under 100 chars for best AI ${category} tools roundup",
  "description": "Brief overview of top 3-4 tools in this category. Include keywords: best AI ${category} tools, AI tools 2026. End with: 'See the full list at pilottools.ai' (max 500 chars)"
}`
  const result = extractJson(await callGemini(prompt))
  return {
    ...result,
    link: `https://pilottools.ai/category/${category}/`,
    board_name: BOARDS[category] || BOARDS.general,
    source_slug: `category-${category}`,
    pin_type: 'category'
  }
}

async function generateArticlePin(article) {
  const prompt = `Generate a Pinterest pin for this article: "${article.title}".
Excerpt: ${(article.excerpt || '').substring(0, 200)}

Return ONLY valid JSON:
{
  "title": "compelling title under 100 chars based on the article",
  "description": "Key takeaway from the article + CTA. Include relevant AI tool keywords. End with: 'Read more at pilottools.ai' (max 500 chars)"
}`
  const result = extractJson(await callGemini(prompt))
  return {
    ...result,
    link: `https://pilottools.ai/blog/${article.slug}/`,
    board_name: BOARDS.general,
    source_slug: article.slug,
    pin_type: 'article'
  }
}

// ---------- Pin Selection ----------

function selectPinType() {
  if (requestedType !== 'auto') return requestedType
  const rand = Math.random()
  if (rand < 0.40) return 'tool-review'
  if (rand < 0.70) return 'comparison'
  if (rand < 0.90) return 'category'
  return 'article'
}

// ---------- Post to Make.com ----------

async function postToWebhook(pinData) {
  if (!WEBHOOK_URL) {
    console.log('  [DRY RUN] No MAKE_WEBHOOK_PILOTTOOLS — skipping post')
    console.log(`  Pin: ${pinData.title}`)
    console.log(`  Link: ${pinData.link}`)
    return true
  }

  const resp = await fetch(WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: pinData.title,
      description: pinData.description,
      link: pinData.link,
      board_name: pinData.board_name,
      image_url: 'https://pilottools.ai/og-image.png'
    })
  })

  if (!resp.ok) {
    console.log(`  Webhook POST failed: ${resp.status} ${resp.statusText}`)
    return false
  }
  console.log(`  Posted to Pinterest via Make.com webhook`)
  return true
}

// ---------- Main ----------

async function main() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY required')
    process.exit(1)
  }

  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  let comparisons = []
  try { comparisons = JSON.parse(fs.readFileSync(COMPARISONS_FILE, 'utf8')) } catch {}
  let articles = []
  try { articles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8')) } catch {}
  const categories = [...new Set(tools.map(t => t.category))]

  const history = loadHistory()
  let posted = 0

  for (let i = 0; i < maxCount; i++) {
    const pinType = selectPinType()
    console.log(`\n[${i + 1}/${maxCount}] Generating ${pinType} pin...`)

    try {
      let pinData

      if (pinType === 'tool-review') {
        const available = tools.filter(t => !wasPostedRecently(history, t.slug))
        if (available.length === 0) { console.log('  No tools available (all posted recently)'); continue }
        const tool = available[Math.floor(Math.random() * available.length)]
        console.log(`  Tool: ${tool.name}`)
        pinData = await generateToolReviewPin(tool)

      } else if (pinType === 'comparison') {
        const available = comparisons.filter(c => !wasPostedRecently(history, c.slug))
        if (available.length === 0) { console.log('  No comparisons available'); continue }
        const comp = available[Math.floor(Math.random() * available.length)]
        console.log(`  Comparison: ${comp.slug}`)
        pinData = await generateComparisonPin(comp)

      } else if (pinType === 'category') {
        const available = categories.filter(c => !wasPostedRecently(history, `category-${c}`))
        if (available.length === 0) { console.log('  No categories available'); continue }
        const cat = available[Math.floor(Math.random() * available.length)]
        console.log(`  Category: ${cat}`)
        pinData = await generateCategoryPin(cat)

      } else if (pinType === 'article') {
        const available = articles.filter(a => !wasPostedRecently(history, a.slug))
        if (available.length === 0) { console.log('  No articles available'); continue }
        const article = available[Math.floor(Math.random() * available.length)]
        console.log(`  Article: ${article.title}`)
        pinData = await generateArticlePin(article)
      }

      if (!pinData) continue

      const success = await postToWebhook(pinData)

      history.push({
        slug: pinData.source_slug,
        pin_type: pinData.pin_type,
        title: pinData.title,
        link: pinData.link,
        board: pinData.board_name,
        posted_at: new Date().toISOString(),
        success
      })
      saveHistory(history)
      posted++

      if (i < maxCount - 1) {
        await new Promise(r => setTimeout(r, 3000))
      }

    } catch (err) {
      console.error(`  Error: ${err.message}`)
    }
  }

  console.log(`\n=== Summary ===`)
  console.log(`Posted: ${posted}/${maxCount} pins`)
  console.log(`Total history: ${history.length} pins`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
