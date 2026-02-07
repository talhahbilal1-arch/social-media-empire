#!/usr/bin/env node
/**
 * Content Generation Script
 * Uses Claude API to generate additional AI tool reviews and comparisons.
 * Run: ANTHROPIC_API_KEY=xxx node scripts/generate-content.js
 */

const fs = require('fs')
const path = require('path')
const https = require('https')

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const COMPARISONS_FILE = path.join(__dirname, '..', 'content', 'comparisons.json')

const ADDITIONAL_TOOLS = [
  { name: 'GitHub Copilot', slug: 'github-copilot', category: 'coding' },
  { name: 'Surfer SEO', slug: 'surfer-seo', category: 'seo' },
  { name: 'Otter.ai', slug: 'otter-ai', category: 'productivity' },
  { name: 'Stable Diffusion', slug: 'stable-diffusion', category: 'image' },
  { name: 'Luma AI', slug: 'luma-ai', category: 'video' },
  { name: 'Murf AI', slug: 'murf-ai', category: 'audio' },
  { name: 'Pictory', slug: 'pictory', category: 'video' },
  { name: 'Tome', slug: 'tome', category: 'productivity' },
  { name: 'Beautiful.ai', slug: 'beautiful-ai', category: 'design' },
  { name: 'Kling AI', slug: 'kling-ai', category: 'video' },
]

async function callClaude(prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 2000,
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
            reject(new Error(`Unexpected response: ${body.substring(0, 200)}`))
          }
        } catch (e) {
          reject(e)
        }
      })
    })

    req.on('error', reject)
    req.write(data)
    req.end()
  })
}

async function generateToolReview(toolName, category) {
  const slug = toolName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/, '')

  const prompt = `Generate a JSON object for an AI tool review of "${toolName}" in the "${category}" category.
Return ONLY valid JSON (no markdown, no explanation) matching this exact structure:
{
  "slug": "${slug}",
  "name": "${toolName}",
  "tagline": "short tagline under 80 chars",
  "description": "2-3 sentence description of what the tool does and why it's notable",
  "category": "${category}",
  "categories": ["${category}", "other relevant categories from: writing, coding, image, video, marketing, productivity, audio, seo, research, design"],
  "pricing": {
    "free_tier": true/false,
    "starting_price": number or null,
    "currency": "USD",
    "billing": "monthly",
    "plans": [{"name": "Plan Name", "price": number/null, "features": ["feature1", "feature2"]}]
  },
  "rating": number between 4.0 and 5.0,
  "review_count": realistic number,
  "affiliate_url": "https://website.com",
  "website": "https://website.com",
  "features": ["feature1", "feature2", "feature3", "feature4", "feature5", "feature6"],
  "pros": ["pro1", "pro2", "pro3", "pro4"],
  "cons": ["con1", "con2", "con3"],
  "best_for": ["use case 1", "use case 2", "use case 3"],
  "logo": "/logos/${slug}.svg",
  "founded": year number,
  "company": "Company Name"
}

Use real, accurate information about ${toolName}. Pricing should reflect current 2026 rates.`

  const response = await callClaude(prompt)

  // Extract JSON from response
  const jsonMatch = response.match(/\{[\s\S]*\}/)
  if (!jsonMatch) {
    throw new Error(`Could not extract JSON for ${toolName}`)
  }

  return JSON.parse(jsonMatch[0])
}

async function main() {
  if (!ANTHROPIC_API_KEY) {
    console.error('ANTHROPIC_API_KEY is required')
    process.exit(1)
  }

  const existingTools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const existingSlugs = new Set(existingTools.map(t => t.slug))

  const newTools = ADDITIONAL_TOOLS.filter(t => !existingSlugs.has(t.slug))

  if (newTools.length === 0) {
    console.log('All tools already exist. Nothing to generate.')
    return
  }

  console.log(`Generating ${newTools.length} new tool reviews...`)

  for (const tool of newTools) {
    try {
      console.log(`  Generating review for ${tool.name}...`)
      const review = await generateToolReview(tool.name, tool.category)
      existingTools.push(review)
      console.log(`  Done: ${tool.name} (${review.rating}/5)`)

      // Write after each tool to preserve progress
      fs.writeFileSync(TOOLS_FILE, JSON.stringify(existingTools, null, 2))

      // Rate limit: wait 2 seconds between API calls
      await new Promise(r => setTimeout(r, 2000))
    } catch (err) {
      console.error(`  Error generating ${tool.name}: ${err.message}`)
    }
  }

  console.log(`\nTotal tools: ${existingTools.length}`)
  console.log('Content generation complete!')
}

main().catch(console.error)
