#!/usr/bin/env node
/**
 * PilotTools Backlink Outreach Automator
 * Generates personalized outreach emails via Gemini and sends via Resend API.
 *
 * Usage:
 *   node scripts/outreach-automator.js --type testimonial --dry-run
 *   RESEND_API_KEY=x GEMINI_API_KEY=x node scripts/outreach-automator.js --type testimonial --send
 *   node scripts/outreach-automator.js --type testimonial --count 5 --send
 */

const fs = require('fs')
const path = require('path')

const GEMINI_API_KEY = process.env.GEMINI_API_KEY
const RESEND_API_KEY = process.env.RESEND_API_KEY
const FROM_EMAIL = process.env.FROM_EMAIL || 'hello@pilottools.ai'

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const LOG_FILE = path.join(__dirname, '..', 'config', 'outreach-log.json')

// Parse CLI args
const args = process.argv.slice(2)
function getArg(name) {
  const idx = args.indexOf(`--${name}`)
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null
}
const emailType = getArg('type') || 'testimonial'
const maxCount = Math.min(parseInt(getArg('count') || '5', 10), 5) // cap at 5
const shouldSend = args.includes('--send')

// ---------- Gemini API ----------

async function callGemini(prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}`
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { maxOutputTokens: 1500, temperature: 0.7 }
        })
      })
      if (resp.status === 429 && attempt < 2) {
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
  const m = text.match(/\{[\s\S]*\}/)
  if (m) return JSON.parse(m[0])
  throw new Error('Could not extract JSON')
}

// ---------- Outreach Log ----------

function loadLog() {
  try { return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8')) } catch { return [] }
}

function saveLog(log) {
  fs.writeFileSync(LOG_FILE, JSON.stringify(log, null, 2))
}

function wasContactedRecently(log, identifier, days = 30) {
  const cutoff = Date.now() - days * 86400000
  return log.some(l => l.identifier === identifier && new Date(l.sent_at).getTime() > cutoff)
}

// ---------- Email Generators ----------

async function generateTestimonialEmail(tool) {
  const prompt = `Generate a short, professional outreach email to the team at ${tool.company || tool.name}.

Context: We run PilotTools.ai, an AI tools review site. We wrote a detailed review of ${tool.name} and rated it ${tool.rating}/5. The review is at https://pilottools.ai/tools/${tool.slug}/

Goal: Let them know about the review and offer them permission to quote it in their marketing. This builds a relationship that may lead to a backlink.

Return ONLY valid JSON:
{
  "subject": "email subject line (short, specific, not spammy)",
  "body": "email body — 3-4 short paragraphs. Professional but warm. Mention specific things we liked. End with offering to be quoted. Sign off as 'The PilotTools Team'. Keep under 200 words."
}`
  return extractJson(await callGemini(prompt))
}

async function generateResourcePageEmail(tool) {
  const prompt = `Generate a short outreach email pitching PilotTools.ai for inclusion on an AI tools resource page.

Context: PilotTools.ai reviews ${tool ? 'tools like ' + tool.name : '80+ AI tools'} with detailed comparisons and pricing. We want to be added to resource pages that list AI tool directories.

Return ONLY valid JSON:
{
  "subject": "concise subject line about adding PilotTools to their resource page",
  "body": "3 short paragraphs. Introduce PilotTools, mention we review 80+ tools with honest ratings, suggest they add us to their resource page. Professional tone. Under 150 words. Sign off as 'The PilotTools Team'."
}`
  return extractJson(await callGemini(prompt))
}

async function generateGuestPostEmail(tool) {
  const category = tool?.category || 'writing'
  const prompt = `Generate a guest post pitch email to a tech/marketing blog.

Context: We're from PilotTools.ai. We want to pitch a guest article titled "How to Choose the Right AI ${category.charAt(0).toUpperCase() + category.slice(1)} Tool for Your Business in 2026".

Return ONLY valid JSON:
{
  "subject": "guest post pitch subject line",
  "body": "3 short paragraphs. Pitch the topic, mention our expertise (reviewed 80+ AI tools), propose 1500-2000 word article with original insights. Professional, not pushy. Under 150 words. Sign off as 'The PilotTools Team'."
}`
  return extractJson(await callGemini(prompt))
}

// ---------- Send via Resend ----------

async function sendEmail(to, subject, body) {
  if (!RESEND_API_KEY) {
    console.log(`  [DRY RUN] Would send to: ${to}`)
    console.log(`  Subject: ${subject}`)
    console.log(`  Body preview: ${body.substring(0, 100)}...`)
    return true
  }

  const resp = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${RESEND_API_KEY}`
    },
    body: JSON.stringify({
      from: FROM_EMAIL,
      to: [to],
      subject,
      text: body
    })
  })

  if (!resp.ok) {
    const err = await resp.text()
    console.log(`  Resend API error: ${resp.status} — ${err}`)
    return false
  }
  console.log(`  Email sent via Resend`)
  return true
}

// ---------- Main ----------

async function main() {
  if (!GEMINI_API_KEY) {
    console.error('Error: GEMINI_API_KEY required')
    process.exit(1)
  }

  if (!shouldSend) {
    console.log('=== DRY RUN MODE (use --send to actually send emails) ===\n')
  }

  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))
  const log = loadLog()
  let sent = 0

  // Build target list based on type
  const targets = []

  if (emailType === 'testimonial') {
    for (const tool of tools) {
      const identifier = `testimonial-${tool.slug}`
      if (wasContactedRecently(log, identifier)) continue
      // Use tool website domain for contact email guess
      const domain = tool.website ? new URL(tool.website).hostname.replace('www.', '') : null
      if (!domain) continue
      targets.push({
        tool,
        identifier,
        email: `hello@${domain}`,
        type: 'testimonial'
      })
    }
  } else if (emailType === 'resource') {
    // Generic outreach — cycle through tools for context
    for (const tool of tools.slice(0, 10)) {
      const identifier = `resource-${tool.slug}`
      if (wasContactedRecently(log, identifier)) continue
      targets.push({
        tool,
        identifier,
        email: null, // Would need manual input
        type: 'resource'
      })
    }
  } else if (emailType === 'guest-post') {
    const categories = [...new Set(tools.map(t => t.category))]
    for (const cat of categories) {
      const identifier = `guest-${cat}`
      if (wasContactedRecently(log, identifier)) continue
      const tool = tools.find(t => t.category === cat)
      targets.push({
        tool,
        identifier,
        email: null,
        type: 'guest-post'
      })
    }
  }

  console.log(`Found ${targets.length} targets for ${emailType} outreach`)
  const batch = targets.slice(0, maxCount)

  for (let i = 0; i < batch.length; i++) {
    const target = batch[i]
    console.log(`\n[${i + 1}/${batch.length}] ${target.type}: ${target.tool?.name || 'general'}`)

    try {
      let email
      if (target.type === 'testimonial') {
        email = await generateTestimonialEmail(target.tool)
      } else if (target.type === 'resource') {
        email = await generateResourcePageEmail(target.tool)
      } else {
        email = await generateGuestPostEmail(target.tool)
      }

      const toEmail = target.email || `contact@example.com`
      const success = shouldSend ? await sendEmail(toEmail, email.subject, email.body) : true

      log.push({
        identifier: target.identifier,
        type: target.type,
        tool_slug: target.tool?.slug,
        to: shouldSend ? toEmail : `[dry-run] ${toEmail}`,
        subject: email.subject,
        sent_at: new Date().toISOString(),
        status: shouldSend ? (success ? 'sent' : 'failed') : 'dry-run'
      })
      saveLog(log)

      if (success) sent++

      // Rate limit
      if (i < batch.length - 1) {
        await new Promise(r => setTimeout(r, 3000))
      }

    } catch (err) {
      console.error(`  Error: ${err.message}`)
    }
  }

  console.log(`\n=== Summary ===`)
  console.log(`${shouldSend ? 'Sent' : 'Generated'}: ${sent}/${batch.length} emails`)
  console.log(`Total outreach log: ${log.length} entries`)
}

main().catch(err => {
  console.error('Fatal error:', err.message)
  process.exit(1)
})
