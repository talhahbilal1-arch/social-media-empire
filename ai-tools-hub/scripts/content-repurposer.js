#!/usr/bin/env node
/**
 * PilotTools Content Repurposer Script
 * Converts articles/tools/comparisons into multi-platform content
 *
 * Usage:
 *   GEMINI_API_KEY=xxx node scripts/content-repurposer.js
 *   GEMINI_API_KEY=xxx node scripts/content-repurposer.js --slug chatgpt-pricing
 *   GEMINI_API_KEY=xxx node scripts/content-repurposer.js --count 3
 */

const fs = require('fs')
const path = require('path')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')
const QUEUE_FILE = path.join(__dirname, '..', 'config', 'social-queue.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}

const requestedSlug = getArg('slug') || null
const maxCount = parseInt(getArg('count') || '1', 10)

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

// ---------- Content Generators ----------

async function generateTwitterContent(sourceData, sourceType) {
  let context = ''

  if (sourceType === 'article') {
    context = `Article: "${sourceData.title}"\nExcerpt: ${sourceData.excerpt}`
  } else if (sourceType === 'tool') {
    context = `Tool: ${sourceData.name}\nDescription: ${sourceData.description.substring(0, 200)}`
  } else if (sourceType === 'comparison') {
    context = `Comparison: ${sourceData.title}`
  }

  const prompt = `Generate Twitter/X content for: ${context}

Create:
1. A single tweet hook (280 chars max)
2. A 3-tweet thread (280 chars each)
3. A comparison tweet if applicable

Return JSON:
{
  "tweet": "single tweet text",
  "thread": ["tweet 1", "tweet 2", "tweet 3"]
}

Tweets should be engaging, include relevant hashtags, and include a link to https://pilottools.ai.`

  const text = await callGemini(prompt)
  try {
    const match = text.match(/\{[\s\S]*\}/)
    if (match) {
      return JSON.parse(match[0])
    }
  } catch (e) {
    console.error(`  Error parsing Twitter content: ${e.message}`)
  }

  return {
    tweet: `Check out this on PilotTools: ${sourceData.name || sourceData.title}. https://pilottools.ai`,
    thread: [
      `Thread: Learn about ${sourceData.name || sourceData.title}`,
      `Key feature: More details on pilottools.ai`,
      `Check it out: https://pilottools.ai #AItools`
    ]
  }
}

async function generateLinkedInContent(sourceData, sourceType) {
  let context = ''

  if (sourceType === 'article') {
    context = `Article: "${sourceData.title}"\nExcerpt: ${sourceData.excerpt}`
  } else if (sourceType === 'tool') {
    context = `Tool: ${sourceData.name}\nTagline: ${sourceData.tagline}\nPricing: ${sourceData.pricing.starting_price ? '$' + sourceData.pricing.starting_price + '/mo' : 'Free'}`
  } else if (sourceType === 'comparison') {
    context = `Comparison: ${sourceData.title}\nVerdict: ${sourceData.verdict}`
  }

  const prompt = `Write a professional LinkedIn post (800-1200 chars) based on: ${context}

The post should:
- Be suitable for a business/AI professional audience
- Include specific insights or takeaways
- Mention the tool/article features or findings
- Include relevant hashtags (#AItools, #Business, etc.)
- Have a CTA linking to https://pilottools.ai
- Be conversational yet professional

Return ONLY the post text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 3000)
}

async function generatePinterestContent(sourceData, sourceType) {
  let context = ''

  if (sourceType === 'article') {
    context = `Article: "${sourceData.title}"\nTopic: ${sourceData.category}`
  } else if (sourceType === 'tool') {
    context = `Tool: ${sourceData.name} (${sourceData.categories[0]})\nCategory: ${sourceData.category}`
  } else if (sourceType === 'comparison') {
    context = `Comparison: ${sourceData.title}\nCategory: ${sourceData.category}`
  }

  const prompt = `Generate 2-3 Pinterest pin descriptions for: ${context}

Create JSON with pin specs:
{
  "pins": [
    {
      "title": "Pin title (under 50 chars, keyword-rich)",
      "description": "2-3 sentence description with keywords (100-150 chars)",
      "board": "Recommended Pinterest board name"
    }
  ]
}

Pins should be designed for the ${sourceType === 'tool' ? sourceData.category : sourceData.category || 'AI Tools'} audience.
Include relevant keywords and a natural CTA mentioning pilottools.ai.`

  const text = await callGemini(prompt)
  try {
    const match = text.match(/\{[\s\S]*\}/)
    if (match) {
      return JSON.parse(match[0])
    }
  } catch (e) {
    console.error(`  Error parsing Pinterest content: ${e.message}`)
  }

  return {
    pins: [
      {
        title: `${sourceData.name || sourceData.title} Guide`,
        description: `Discover tips and insights about ${sourceData.name || sourceData.title}. Read our full guide on PilotTools.`,
        board: sourceData.category || 'AI Tools'
      }
    ]
  }
}

async function generateNewsletterContent(sourceData, sourceType) {
  let context = ''

  if (sourceType === 'article') {
    context = `Article: "${sourceData.title}"\nExcerpt: ${sourceData.excerpt}`
  } else if (sourceType === 'tool') {
    context = `Tool: ${sourceData.name}\nTagline: ${sourceData.tagline}`
  } else if (sourceType === 'comparison') {
    context = `Comparison: ${sourceData.title}`
  }

  const prompt = `Write a 2-3 sentence newsletter blurb for: ${context}

The blurb should:
- Hook the reader immediately
- Mention key value prop or insight
- End with a CTA (e.g., "Read the full article on PilotTools")
- Be conversational and friendly
- Include link to https://pilottools.ai/${sourceType}s/${sourceData.slug}

Return ONLY the blurb text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 500)
}

// ---------- Queue Management ----------

function loadQueue() {
  if (fs.existsSync(QUEUE_FILE)) {
    return JSON.parse(fs.readFileSync(QUEUE_FILE, 'utf8'))
  }
  return { items: [] }
}

function saveQueue(queue) {
  fs.writeFileSync(QUEUE_FILE, JSON.stringify(queue, null, 2))
}

function addToQueue(queue, item) {
  queue.items.push(item)
  // Keep queue size under 50 items
  if (queue.items.length > 50) {
    queue.items = queue.items.slice(-50)
  }
  saveQueue(queue)
}

// ---------- Main ----------

async function main() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY environment variable is required')
    process.exit(1)
  }

  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const articles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
  const comparisons = JSON.parse(fs.readFileSync(COMPARISONS_FILE, 'utf8'))
  const queue = loadQueue()

  console.log(`Loaded: ${tools.length} tools, ${articles.length} articles, ${comparisons.length} comparisons`)

  // Collect potential sources
  const sources = []
  articles.forEach(a => sources.push({ data: a, type: 'article', slug: a.slug }))
  tools.forEach(t => sources.push({ data: t, type: 'tool', slug: t.slug }))
  comparisons.forEach(c => sources.push({ data: c, type: 'comparison', slug: c.slug }))

  let processed = 0

  for (let i = 0; i < maxCount; i++) {
    // Select source
    let source
    if (requestedSlug) {
      source = sources.find(s => s.slug === requestedSlug)
      if (!source) {
        console.log(`Source not found: ${requestedSlug}`)
        break
      }
    } else {
      source = sources[Math.floor(Math.random() * sources.length)]
    }

    // Check if already queued
    const existing = queue.items.find(item => item.source_slug === source.slug)
    if (existing) {
      console.log(`${source.slug} already in queue, skipping`)
      continue
    }

    console.log(`\n[${i + 1}/${maxCount}] Repurposing: ${source.type} — ${source.slug}`)

    try {
      // Generate content for all platforms
      console.log(`  Generating Twitter content...`)
      const twitter = await generateTwitterContent(source.data, source.type)

      console.log(`  Generating LinkedIn content...`)
      const linkedin = await generateLinkedInContent(source.data, source.type)

      console.log(`  Generating Pinterest content...`)
      const pinterest = await generatePinterestContent(source.data, source.type)

      console.log(`  Generating newsletter content...`)
      const newsletter = await generateNewsletterContent(source.data, source.type)

      // Build queue item
      const queueItem = {
        source_slug: source.slug,
        source_type: source.type,
        generated_at: new Date().toISOString().split('T')[0],
        twitter,
        linkedin,
        pinterest,
        newsletter
      }

      addToQueue(queue, queueItem)
      console.log(`  Added to queue (total: ${queue.items.length})`)
      processed++

      // Rate limit
      if (i < maxCount - 1) {
        console.log('  Waiting 3s (rate limit)...')
        await new Promise(r => setTimeout(r, 3000))
      }

    } catch (err) {
      console.error(`  Error: ${err.message}`)
    }

    // Only process once if slug is specified
    if (requestedSlug) break
  }

  console.log(`\n=== Summary ===`)
  console.log(`Processed: ${processed} sources`)
  console.log(`Queue size: ${queue.items.length}`)
  console.log(`Queue file: ${QUEUE_FILE}`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
