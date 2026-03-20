#!/usr/bin/env node
/**
 * Populate PilotTools Content Calendar with 200+ Items
 *
 * Reads existing calendar and tools.json, then adds:
 * - Pricing pages (one per tool)
 * - Alternatives pages (one per popular tool)
 * - New comparisons (20+ pairs)
 * - Profession listicles (25 professions)
 * - Task listicles (25 tasks)
 * - "Is it worth it" articles (20 tools)
 * - "How to use" how-tos (15-20 items)
 *
 * Idempotent: checks slug to avoid duplicates on re-runs
 * Starts IDs from 100 to avoid conflicts
 *
 * Usage:
 *   node scripts/populate-calendar.js
 */

const fs = require('fs')
const path = require('path')

const CALENDAR_FILE = path.join(__dirname, '..', 'config', 'content-calendar.json')
const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')

// ========== HELPERS ==========

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'))
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2))
}

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

// ========== DATA SOURCES ==========

const EXISTING_TOOLS = [
  'chatgpt', 'claude', 'jasper', 'midjourney', 'cursor', 'writesonic',
  'copy-ai', 'synthesia', 'grammarly', 'notion-ai', 'elevenlabs', 'canva',
  'descript', 'runway', 'perplexity', 'scalenut', 'surfer-seo', 'otter-ai',
  'stable-diffusion', 'luma-ai'
]

const NEW_TOOLS = [
  'github-copilot', 'gemini', 'bolt-new', 'v0-dev', 'murf-ai', 'pictory',
  'tome', 'beautiful-ai', 'kling-ai', 'adobe-firefly', 'leonardo-ai', 'pika',
  'heygen', 'invideo-ai', 'fliki', 'wondershare-filmora-ai', 'gamma-ai',
  'simplified', 'rytr', 'wordtune', 'quillbot', 'deepl', 'fireflies-ai',
  'krisp', 'whisper-ai', 'tabnine', 'codeium', 'replit-ai', 'amazon-codewhisperer',
  'windsurf'
]

const ALL_TOOLS = [...EXISTING_TOOLS, ...NEW_TOOLS]

const PROFESSIONS = [
  'students', 'freelancers', 'real-estate-agents', 'lawyers', 'teachers',
  'doctors', 'nurses', 'accountants', 'hr-managers', 'project-managers',
  'ux-designers', 'photographers', 'podcasters', 'youtubers', 'etsy-sellers',
  'amazon-sellers', 'small-business-owners', 'agencies', 'startups', 'nonprofits',
  'authors', 'journalists', 'marketers', 'salespeople', 'customer-service-teams'
]

const TASKS = [
  'email-writing', 'blog-posts', 'social-media-captions', 'resume-writing',
  'cover-letters', 'product-descriptions', 'seo-content', 'ad-copy',
  'video-editing', 'image-editing', 'voice-cloning', 'transcription',
  'meeting-notes', 'data-analysis', 'presentations', 'spreadsheets',
  'customer-support', 'lead-generation', 'code-review', 'debugging',
  'content-repurposing', 'logo-design', 'website-building', 'podcast-editing',
  'photo-editing'
]

const COMPARISONS = [
  ['claude', 'chatgpt'],
  ['gemini', 'claude'],
  ['gemini', 'perplexity'],
  ['cursor', 'tabnine'],
  ['cursor', 'codeium'],
  ['cursor', 'github-copilot'],
  ['midjourney', 'leonardo-ai'],
  ['midjourney', 'adobe-firefly'],
  ['synthesia', 'heygen'],
  ['descript', 'runway'],
  ['canva', 'midjourney'],
  ['jasper', 'chatgpt'],
  ['elevenlabs', 'whisper-ai'],
  ['grammarly', 'quillbot'],
  ['writesonic', 'rytr'],
  ['notion-ai', 'jasper'],
  ['github-copilot', 'tabnine'],
  ['bolt-new', 'v0-dev'],
  ['replit-ai', 'cursor'],
  ['pika', 'runway']
]

// ========== MAIN LOGIC ==========

function main() {
  console.log('Reading existing data...')
  const calendar = readJson(CALENDAR_FILE)
  const toolsData = readJson(TOOLS_FILE)

  const existingSlugs = new Set(calendar.items.map(item => item.slug))
  const toolNames = new Map()

  // Build tool name lookup from tools.json
  toolsData.forEach(tool => {
    toolNames.set(tool.slug, tool.name)
  })

  let nextId = Math.max(...calendar.items.map(i => i.id), 99) + 1
  const newItems = []

  console.log(`\nStarting calendar expansion from ID ${nextId}`)
  console.log(`Existing calendar items: ${calendar.items.length}`)
  console.log(`Existing slugs in calendar: ${existingSlugs.size}`)

  // ===== 1. PRICING PAGES =====
  console.log('\n[1] Generating pricing pages...')
  let pricingCount = 0
  ALL_TOOLS.forEach(toolSlug => {
    const slug = `${toolSlug}-pricing`
    const toolName = toolNames.get(toolSlug) || toolSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'article',
        priority: 'high',
        status: 'pending',
        slug: slug,
        keyword: `${toolSlug.replace(/-/g, ' ')} pricing 2026`,
        title: `${toolName} Pricing 2026: Plans, Costs & Best Value`,
        tool_name: toolName
      })
      pricingCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${pricingCount} pricing pages`)

  // ===== 2. ALTERNATIVES PAGES =====
  console.log('\n[2] Generating alternatives pages...')
  let altCount = 0
  const popularTools = ALL_TOOLS.slice(0, 30) // Top 30 most popular
  popularTools.forEach(toolSlug => {
    const slug = `${toolSlug}-alternatives`
    const toolName = toolNames.get(toolSlug) || toolSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'article',
        priority: 'high',
        status: 'pending',
        slug: slug,
        keyword: `best ${toolSlug.replace(/-/g, ' ')} alternatives 2026`,
        title: `Best ${toolName} Alternatives 2026`,
        tool_name: toolName
      })
      altCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${altCount} alternatives pages`)

  // ===== 3. NEW COMPARISONS =====
  console.log('\n[3] Generating comparison pairs...')
  let compCount = 0
  COMPARISONS.forEach(([tool1, tool2]) => {
    const slug = `${tool1}-vs-${tool2}`
    const tool1Name = toolNames.get(tool1) || tool1.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    const tool2Name = toolNames.get(tool2) || tool2.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'comparison',
        priority: 'high',
        status: 'pending',
        slug: slug,
        tools: [tool1, tool2],
        tool_names: [tool1Name, tool2Name],
        keyword: `${tool1.replace(/-/g, ' ')} vs ${tool2.replace(/-/g, ' ')} 2026`
      })
      compCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${compCount} comparison pairs`)

  // ===== 4. PROFESSION LISTICLES =====
  console.log('\n[4] Generating profession listicles...')
  let profCount = 0
  PROFESSIONS.forEach(profession => {
    const slug = `best-ai-tools-${profession}`
    const title = `Best AI Tools for ${profession.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} 2026`

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'listicle',
        priority: 'medium',
        status: 'pending',
        slug: slug,
        keyword: `best ai tools for ${profession.replace(/-/g, ' ')}`,
        title: title
      })
      profCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${profCount} profession listicles`)

  // ===== 5. TASK LISTICLES =====
  console.log('\n[5] Generating task listicles...')
  let taskCount = 0
  TASKS.forEach(task => {
    const slug = `best-ai-tools-${task}`
    const taskDisplay = task.replace(/-/g, ' ')
    const title = `Best AI Tools for ${taskDisplay.replace(/\b\w/g, l => l.toUpperCase())} 2026`

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'listicle',
        priority: 'medium',
        status: 'pending',
        slug: slug,
        keyword: `best ai tools for ${taskDisplay}`,
        title: title
      })
      taskCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${taskCount} task listicles`)

  // ===== 6. "IS IT WORTH IT" ARTICLES =====
  console.log('\n[6] Generating "is it worth it" articles...')
  let worthCount = 0
  const topTools = ALL_TOOLS.slice(0, 20)
  topTools.forEach(toolSlug => {
    const slug = `is-${toolSlug}-worth-it`
    const toolName = toolNames.get(toolSlug) || toolSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'article',
        priority: 'medium',
        status: 'pending',
        slug: slug,
        keyword: `is ${toolSlug.replace(/-/g, ' ')} worth it 2026`,
        title: `Is ${toolName} Worth It in 2026?`,
        tool_name: toolName
      })
      worthCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${worthCount} "is it worth it" articles`)

  // ===== 7. "HOW TO USE" ARTICLES =====
  console.log('\n[7] Generating "how to use" how-to articles...')
  let howCount = 0
  const howToCombos = [
    ['chatgpt', 'content-creation'],
    ['claude', 'coding-projects'],
    ['midjourney', 'logo-design'],
    ['cursor', 'web-development'],
    ['descript', 'podcast-editing'],
    ['synthesia', 'video-marketing'],
    ['perplexity', 'research-projects'],
    ['elevenlabs', 'voiceover-automation'],
    ['canva', 'social-media-graphics'],
    ['grammarly', 'professional-writing'],
    ['notion-ai', 'knowledge-management'],
    ['runwway', 'video-post-production'],
    ['github-copilot', 'code-automation'],
    ['bolt-new', 'rapid-prototyping'],
    ['gemini', 'market-research']
  ]

  howToCombos.forEach(([toolSlug, task]) => {
    const slug = `how-to-use-${toolSlug}-for-${task}`
    const toolName = toolNames.get(toolSlug) || toolSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    const taskDisplay = task.replace(/-/g, ' ')

    if (!existingSlugs.has(slug)) {
      newItems.push({
        id: nextId++,
        type: 'article',
        priority: 'low',
        status: 'pending',
        slug: slug,
        keyword: `how to use ${toolSlug.replace(/-/g, ' ')} for ${taskDisplay}`,
        title: `How to Use ${toolName} for ${taskDisplay.replace(/\b\w/g, l => l.toUpperCase())}`,
        tool_name: toolName
      })
      howCount++
      existingSlugs.add(slug)
    }
  })
  console.log(`  Added: ${howCount} "how to use" articles`)

  // ===== WRITE RESULTS =====
  console.log('\n=== SUMMARY ===')
  console.log(`Pricing pages:       ${pricingCount}`)
  console.log(`Alternatives pages:  ${altCount}`)
  console.log(`Comparison pairs:    ${compCount}`)
  console.log(`Profession listicles: ${profCount}`)
  console.log(`Task listicles:      ${taskCount}`)
  console.log(`"Worth it" articles: ${worthCount}`)
  console.log(`"How to use" articles: ${howCount}`)
  console.log(`\nTOTAL NEW ITEMS: ${newItems.length}`)
  console.log(`Previous calendar size: ${calendar.items.length}`)
  console.log(`New calendar size: ${calendar.items.length + newItems.length}`)

  // Merge and write
  calendar.items = calendar.items.concat(newItems)
  calendar.last_updated = new Date().toISOString().split('T')[0]
  writeJson(CALENDAR_FILE, calendar)

  console.log(`\nCalendar updated: ${CALENDAR_FILE}`)
  console.log('Done!')
}

main()
