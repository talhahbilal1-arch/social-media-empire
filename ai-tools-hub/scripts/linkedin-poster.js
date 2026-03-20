#!/usr/bin/env node
/**
 * PilotTools LinkedIn Poster Script
 * Generates and posts content to LinkedIn
 *
 * Usage:
 *   GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js
 *   GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js --type tool-of-week
 *   GEMINI_API_KEY=xxx LINKEDIN_ACCESS_TOKEN=xxx LINKEDIN_PERSON_ID=xxx node scripts/linkedin-poster.js --count 1
 */

const fs = require('fs')
const path = require('path')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''
const LINKEDIN_ACCESS_TOKEN = process.env.LINKEDIN_ACCESS_TOKEN || ''
const LINKEDIN_PERSON_ID = process.env.LINKEDIN_PERSON_ID || ''
const LINKEDIN_ORG_ID = process.env.LINKEDIN_ORG_ID || ''

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
const HISTORY_FILE = path.join(__dirname, '..', 'config', 'linkedin-history.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}

const requestedType = getArg('type') || null
const maxCount = parseInt(getArg('count') || '1', 10)

// ---------- Gemini API ----------

async function callGemini(prompt, maxTokens = 1500) {
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

// ---------- LinkedIn API ----------

async function postToLinkedIn(text) {
  if (!LINKEDIN_ACCESS_TOKEN || (!LINKEDIN_PERSON_ID && !LINKEDIN_ORG_ID)) {
    console.warn('  No LinkedIn credentials available. Skipping post.')
    return null
  }

  try {
    const actorId = LINKEDIN_PERSON_ID ? `urn:li:person:${LINKEDIN_PERSON_ID}` : `urn:li:organization:${LINKEDIN_ORG_ID}`

    const payload = {
      contentDistribution: {
        feedDistribution: 'MAIN_FEED',
        targetAudiences: []
      },
      author: actorId,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.PublishText': {
          text
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    }

    const resp = await fetch('https://api.linkedin.com/v2/ugcPosts', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LINKEDIN_ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    const json = await resp.json()
    if (resp.ok && json.id) {
      return json.id
    } else {
      console.error(`  LinkedIn API error: ${JSON.stringify(json)}`)
      return null
    }
  } catch (e) {
    console.error(`  Error posting to LinkedIn: ${e.message}`)
    return null
  }
}

// ---------- Content Generators ----------

async function generateToolOfWeek(tool) {
  const prompt = `Write a professional LinkedIn post (800-1300 chars) reviewing "${tool.name}" as the "Tool of the Week".

Include:
- What it does (1-2 sentences)
- Who it's for (specific use cases)
- Key strengths (2-3 bullet points)
- Pricing and value prop
- CTA: "Check out ${tool.name} and join thousands improving their productivity."
- Link to: https://pilottools.ai/tools/${tool.slug}
- Hashtags: #AItools #ArtificialIntelligence #MarTech #Productivity

Keep tone: professional, insightful, conversational (not salesy).
Return ONLY the post text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 3000)
}

async function generateCategoryPost(category, tools) {
  const toolNames = tools.slice(0, 5).map(t => t.name).join(', ')

  const prompt = `Write a professional LinkedIn post (800-1300 chars) about "AI Tools for ${category}".

Include:
- A hook about how AI is transforming ${category}
- 3-5 specific tools and one-line verdicts for each tool
- Why these tools matter for the role/function
- Link to: https://pilottools.ai/category/${category.toLowerCase().replace(/\s+/g, '-')}
- Hashtags relevant to ${category} (e.g., #${category.toLowerCase().replace(/\s+/g, '')}, #AItools, #Productivity)

Tools to mention: ${toolNames}

Keep tone: professional, thought-leadership, insider perspective.
Return ONLY the post text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 3000)
}

async function generateIndustryObservation() {
  const prompt = `Write a professional LinkedIn post (800-1300 chars) with an industry observation about AI tools trends in 2026.

Structure:
- Title: "3 Things I Learned Testing 50+ AI Tools This Quarter"
- Share 3 specific observations (not generic advice)
- Each observation should be surprising or counter-intuitive
- CTA: "What's your biggest AI tool discovery this year? Share in the comments."
- Link to: https://pilottools.ai

Keep tone: thought leadership, authentic, conversational expertise.
Return ONLY the post text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 3000)
}

// ---------- History Management ----------

function loadHistory() {
  if (fs.existsSync(HISTORY_FILE)) {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'))
  }
  return { posts: [] }
}

function saveHistory(history) {
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2))
}

function hasRecentContent(history, type, identifier, days = 7) {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)

  return history.posts.some(
    p => p.type === type && p.identifier === identifier && new Date(p.posted_date) > cutoff
  )
}

function addToHistory(history, type, identifier, text) {
  history.posts.push({
    type,
    identifier,
    text: text.substring(0, 100),
    posted_date: new Date().toISOString()
  })
  // Keep only last 50 posts
  if (history.posts.length > 50) {
    history.posts = history.posts.slice(-50)
  }
  saveHistory(history)
}

// ---------- Weighted Random Selection ----------

function selectByWeight(items, weights) {
  const total = weights.reduce((a, b) => a + b, 0)
  let random = Math.random() * total
  for (let i = 0; i < items.length; i++) {
    random -= weights[i]
    if (random <= 0) return items[i]
  }
  return items[items.length - 1]
}

// ---------- Main ----------

async function main() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY environment variable is required')
    process.exit(1)
  }

  if (!LINKEDIN_ACCESS_TOKEN || (!LINKEDIN_PERSON_ID && !LINKEDIN_ORG_ID)) {
    console.error('Error: LinkedIn credentials required (LINKEDIN_ACCESS_TOKEN + LINKEDIN_PERSON_ID or LINKEDIN_ORG_ID)')
    process.exit(1)
  }

  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const articles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
  const history = loadHistory()

  console.log(`Loaded: ${tools.length} tools`)

  const postTypes = ['tool-of-week', 'category', 'observation']
  const weights = [0.4, 0.35, 0.25]

  let posted = 0

  for (let i = 0; i < maxCount; i++) {
    let type = requestedType || selectByWeight(postTypes, weights)

    console.log(`\n[${i + 1}/${maxCount}] Generating: ${type}`)

    try {
      let postId = null

      if (type === 'tool-of-week') {
        const tool = tools[Math.floor(Math.random() * tools.length)]
        if (hasRecentContent(history, 'tool-of-week', tool.slug)) {
          console.log(`  Skipping ${tool.name} — recent review already posted`)
          continue
        }
        const text = await generateToolOfWeek(tool)
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        postId = await postToLinkedIn(text)
        if (postId) {
          addToHistory(history, 'tool-of-week', tool.slug, text)
          console.log(`  Posted (ID: ${postId})`)
          posted++
        }

      } else if (type === 'category') {
        const categories = [
          'Sales Automation',
          'Marketing Intelligence',
          'Customer Success',
          'Finance & Operations',
          'HR & Recruiting',
          'Engineering Tools'
        ]
        const category = categories[Math.floor(Math.random() * categories.length)]
        const relevantTools = tools.filter(t =>
          t.categories && (
            t.categories.includes(category.toLowerCase()) ||
            t.categories.includes(category.split(' ')[0].toLowerCase())
          )
        ).slice(0, 5)

        if (relevantTools.length === 0) {
          console.log(`  No tools found for ${category}`)
          continue
        }

        if (hasRecentContent(history, 'category', category)) {
          console.log(`  Skipping ${category} — recent post already posted`)
          continue
        }

        const text = await generateCategoryPost(category, relevantTools)
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        postId = await postToLinkedIn(text)
        if (postId) {
          addToHistory(history, 'category', category, text)
          console.log(`  Posted (ID: ${postId})`)
          posted++
        }

      } else if (type === 'observation') {
        if (hasRecentContent(history, 'observation', 'industry-trend')) {
          console.log(`  Skipping observation — recent post already posted`)
          continue
        }
        const text = await generateIndustryObservation()
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        postId = await postToLinkedIn(text)
        if (postId) {
          addToHistory(history, 'observation', 'industry-trend', text)
          console.log(`  Posted (ID: ${postId})`)
          posted++
        }
      }

      // Rate limit
      if (i < maxCount - 1) {
        console.log('  Waiting 3s (rate limit)...')
        await new Promise(r => setTimeout(r, 3000))
      }

    } catch (err) {
      console.error(`  Error: ${err.message}`)
    }
  }

  console.log(`\n=== Summary ===`)
  console.log(`Posted: ${posted} items`)
  console.log(`History size: ${history.posts.length}`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
