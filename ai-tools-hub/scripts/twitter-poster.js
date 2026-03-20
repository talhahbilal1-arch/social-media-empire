#!/usr/bin/env node
/**
 * PilotTools Twitter/X Poster Script
 * Generates and posts tweets from tools.json and articles.json
 *
 * Usage:
 *   GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js
 *   GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js --type tip
 *   GEMINI_API_KEY=xxx TWITTER_BEARER_TOKEN=xxx node scripts/twitter-poster.js --count 2
 */

const fs = require('fs')
const path = require('path')
const crypto = require('crypto')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''
const TWITTER_BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN || ''
const TWITTER_API_KEY = process.env.TWITTER_API_KEY || ''
const TWITTER_API_SECRET = process.env.TWITTER_API_SECRET || ''
const TWITTER_ACCESS_TOKEN = process.env.TWITTER_ACCESS_TOKEN || ''
const TWITTER_ACCESS_SECRET = process.env.TWITTER_ACCESS_SECRET || ''

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
const HISTORY_FILE = path.join(__dirname, '..', 'config', 'twitter-history.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}

const requestedType = getArg('type') || null
const maxCount = parseInt(getArg('count') || '1', 10)

// ---------- Gemini API ----------

async function callGemini(prompt, maxTokens = 500) {
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

// ---------- OAuth 1.0a Signing ----------

function generateOAuth1Header(method, url, params) {
  const timestamp = Math.floor(Date.now() / 1000).toString()
  const nonce = crypto.randomBytes(32).toString('hex').substring(0, 32)

  // Build oauth parameters
  const oauthParams = {
    oauth_consumer_key: TWITTER_API_KEY,
    oauth_token: TWITTER_ACCESS_TOKEN,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: timestamp,
    oauth_nonce: nonce,
    oauth_version: '1.0'
  }

  // Combine oauth + request params for signature
  const allParams = { ...oauthParams, ...params }
  const paramString = Object.keys(allParams)
    .sort()
    .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(allParams[k])}`)
    .join('&')

  // Create base string
  const baseString = `${method.toUpperCase()}&${encodeURIComponent(url)}&${encodeURIComponent(paramString)}`

  // Sign
  const signingKey = `${encodeURIComponent(TWITTER_API_SECRET)}&${encodeURIComponent(TWITTER_ACCESS_SECRET)}`
  const signature = crypto
    .createHmac('sha1', signingKey)
    .update(baseString)
    .digest('base64')

  oauthParams.oauth_signature = signature

  // Build header
  const headerParts = Object.entries(oauthParams)
    .map(([k, v]) => `${k}="${encodeURIComponent(v)}"`)
    .join(', ')

  return `OAuth ${headerParts}`
}

// ---------- Twitter API ----------

async function postTweet(text, replyToId = null) {
  if (TWITTER_API_KEY && TWITTER_API_SECRET && TWITTER_ACCESS_TOKEN && TWITTER_ACCESS_SECRET) {
    // OAuth 1.0a
    const url = 'https://api.twitter.com/2/tweets'
    const params = {}
    const body = { text }
    if (replyToId) {
      body.reply = { in_reply_to_tweet_id: replyToId }
    }

    const authHeader = generateOAuth1Header('POST', url, params)
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      })

      const json = await resp.json()
      if (resp.ok && json.data && json.data.id) {
        return json.data.id
      } else {
        console.error(`  Twitter API error: ${JSON.stringify(json)}`)
        return null
      }
    } catch (e) {
      console.error(`  Error posting tweet: ${e.message}`)
      return null
    }
  } else if (TWITTER_BEARER_TOKEN) {
    // Bearer token fallback (read-only for v2 API, fallback only)
    console.warn('  Using Bearer token (read-only). OAuth 1.0a credentials required for posting.')
    return null
  } else {
    console.warn('  No Twitter credentials available. Skipping post.')
    return null
  }
}

// ---------- Content Generators ----------

async function generateToolTip(tool) {
  const prompt = `Generate a single Twitter/X tweet (max 280 chars) about a clever productivity tip using "${tool.name}".

The tweet should be:
- Actionable and specific (not generic)
- Surprising or counter-intuitive
- Include the tool name and hashtags
- Format: "[Tool] trick most people don't know: [tip]. #AItools #${tool.name.toLowerCase().replace(/\s+/g, '')}"

Return ONLY the tweet text, no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 280)
}

async function generateComparison(tools) {
  if (tools.length < 2) return null

  const tool1 = tools[0]
  const tool2 = tools[1]

  const prompt = `Generate a single Twitter/X tweet (max 280 chars) with an opinionated, clever comparison of "${tool1.name}" vs "${tool2.name}".

The tweet should be:
- Concise and opinionated (e.g., "Hot take: X is better than Y for Z")
- Include a link placeholder: https://pilottools.ai/compare/[slug]
- Format: "Unpopular opinion: [Tool A] is better than [Tool B] for [use case]. Here's why: [brief reason]. Full comparison: [link]"

Return ONLY the tweet text (make it fit 280 chars), no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 280)
}

async function generateArticleAlert(article) {
  const prompt = `Generate a single Twitter/X tweet (max 280 chars) promoting this article: "${article.title}".

The tweet should:
- Start with an engaging hook about the topic
- Include the article link: https://pilottools.ai/blog/${article.slug}
- End with #AItools hashtag
- Format: "[Hook about article topic]. We just published our full breakdown: [link] #AItools"

Return ONLY the tweet text (keep it under 280 chars), no explanation.`

  const text = await callGemini(prompt)
  return text.trim().substring(0, 280)
}

async function generateThread(tools) {
  if (tools.length === 0) return []

  const toolList = tools.slice(0, 5).map(t => `${t.name} (${t.pricing.starting_price ? '$' + t.pricing.starting_price + '/mo' : 'free'})`).join(', ')
  const category = tools[0].categories ? tools[0].categories[0] : 'AI'

  const prompt = `Generate a Twitter/X thread (5-7 tweets) about AI ${category} tools.

Tweet 1 (hook): "We tested every AI ${category} tool. Here's our honest ranking:"
Tweets 2-6: One tool each, under 280 chars each. Format: "2️⃣ [Tool Name]: [One-line verdict] - [one specific strength or weakness]"
Final tweet: Link to comparison page: "Full comparison with pricing: https://pilottools.ai/category/${category.toLowerCase()}"

Return as JSON array of tweet strings, like ["tweet 1", "tweet 2", ...]. Ensure each is under 280 chars.`

  try {
    const text = await callGemini(prompt)
    const match = text.match(/\[[\s\S]*\]/)
    if (match) {
      const tweets = JSON.parse(match[0])
      return tweets.filter(t => typeof t === 'string').map(t => t.substring(0, 280))
    }
  } catch (e) {
    console.error(`  Error parsing thread: ${e.message}`)
  }

  return []
}

// ---------- History Management ----------

function loadHistory() {
  if (fs.existsSync(HISTORY_FILE)) {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'))
  }
  return { tweets: [] }
}

function saveHistory(history) {
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2))
}

function hasRecentContent(history, type, identifier, days = 7) {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)

  return history.tweets.some(
    t => t.type === type && t.identifier === identifier && new Date(t.posted_date) > cutoff
  )
}

function addToHistory(history, type, identifier, text) {
  history.tweets.push({
    type,
    identifier,
    text: text.substring(0, 100),
    posted_date: new Date().toISOString()
  })
  // Keep only last 100 tweets
  if (history.tweets.length > 100) {
    history.tweets = history.tweets.slice(-100)
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

  if (!TWITTER_BEARER_TOKEN && !(TWITTER_API_KEY && TWITTER_API_SECRET && TWITTER_ACCESS_TOKEN && TWITTER_ACCESS_SECRET)) {
    console.error('Error: Twitter credentials required (TWITTER_BEARER_TOKEN or OAuth 1.0a env vars)')
    process.exit(1)
  }

  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const articles = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
  const history = loadHistory()

  console.log(`Loaded: ${tools.length} tools, ${articles.length} articles`)

  const postTypes = ['tip', 'comparison', 'article', 'thread']
  const weights = [0.4, 0.25, 0.2, 0.15]

  let posted = 0

  for (let i = 0; i < maxCount; i++) {
    let type = requestedType || selectByWeight(postTypes, weights)

    console.log(`\n[${i + 1}/${maxCount}] Generating: ${type}`)

    try {
      let tweets = []
      let tweetId = null

      if (type === 'tip') {
        const tool = tools[Math.floor(Math.random() * tools.length)]
        if (hasRecentContent(history, 'tip', tool.slug)) {
          console.log(`  Skipping ${tool.name} — recent tip already posted`)
          continue
        }
        const text = await generateToolTip(tool)
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        tweetId = await postTweet(text)
        if (tweetId) {
          addToHistory(history, 'tip', tool.slug, text)
          console.log(`  Posted (ID: ${tweetId})`)
          posted++
        }

      } else if (type === 'comparison') {
        const selectedTools = [
          tools[Math.floor(Math.random() * tools.length)],
          tools[Math.floor(Math.random() * tools.length)]
        ]
        const cmpKey = [selectedTools[0].slug, selectedTools[1].slug].sort().join('-')
        if (hasRecentContent(history, 'comparison', cmpKey)) {
          console.log(`  Skipping comparison — recent comparison already posted`)
          continue
        }
        const text = await generateComparison(selectedTools)
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        tweetId = await postTweet(text)
        if (tweetId) {
          addToHistory(history, 'comparison', cmpKey, text)
          console.log(`  Posted (ID: ${tweetId})`)
          posted++
        }

      } else if (type === 'article') {
        const article = articles[Math.floor(Math.random() * articles.length)]
        if (hasRecentContent(history, 'article', article.slug)) {
          console.log(`  Skipping "${article.slug}" — recent alert already posted`)
          continue
        }
        const text = await generateArticleAlert(article)
        console.log(`  Generated: "${text.substring(0, 60)}..."`)
        tweetId = await postTweet(text)
        if (tweetId) {
          addToHistory(history, 'article', article.slug, text)
          console.log(`  Posted (ID: ${tweetId})`)
          posted++
        }

      } else if (type === 'thread') {
        const selectedTools = tools.slice(0, 5 + Math.floor(Math.random() * 3))
        const threadKey = `thread-${selectedTools[0].categories[0]}`
        if (hasRecentContent(history, 'thread', threadKey)) {
          console.log(`  Skipping thread — recent thread already posted`)
          continue
        }
        tweets = await generateThread(selectedTools)
        if (tweets.length > 0) {
          console.log(`  Generated ${tweets.length} tweets for thread`)
          for (let j = 0; j < tweets.length; j++) {
            console.log(`    Tweet ${j + 1}: "${tweets[j].substring(0, 60)}..."`)
            const newTweetId = await postTweet(tweets[j], tweetId)
            if (newTweetId) {
              tweetId = newTweetId
              await new Promise(r => setTimeout(r, 2000))
            }
          }
          if (tweetId) {
            addToHistory(history, 'thread', threadKey, tweets[0])
            console.log(`  Posted thread`)
            posted++
          }
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
  console.log(`History size: ${history.tweets.length}`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
