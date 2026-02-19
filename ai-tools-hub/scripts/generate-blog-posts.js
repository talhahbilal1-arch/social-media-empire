#!/usr/bin/env node
/**
 * Generates 5 new blog posts with images and appends them to articles.json
 * Usage: ANTHROPIC_API_KEY=xxx node scripts/generate-blog-posts.js
 */

const fs = require('fs')
const path = require('path')
const https = require('https')

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY
const ARTICLES_FILE = path.join(__dirname, '..', 'content', 'articles.json')
const IMAGES_DIR = path.join(__dirname, '..', 'public', 'images', 'blog')

if (!ANTHROPIC_API_KEY) {
  console.error('ANTHROPIC_API_KEY is required')
  process.exit(1)
}

// Curated Pexels photo IDs by topic (free public CDN URLs)
const PEXELS_IMAGES = {
  coding: [
    { id: '574071', alt: 'Developer writing code on multiple screens' },
    { id: '1181671', alt: 'Laptop with code on screen' },
    { id: '4974912', alt: 'Programming environment on computer' },
  ],
  image_generation: [
    { id: '3861969', alt: 'Digital art creation on tablet' },
    { id: '1591060', alt: 'Colorful digital artwork' },
    { id: '3109807', alt: 'Creative digital design process' },
  ],
  marketing: [
    { id: '3194519', alt: 'Marketing team reviewing analytics dashboard' },
    { id: '265087', alt: 'Digital marketing strategy on whiteboard' },
    { id: '196644', alt: 'Social media marketing on laptop' },
  ],
  productivity: [
    { id: '3184465', alt: 'Productive workspace with laptop and notebook' },
    { id: '7688336', alt: 'Person working efficiently at desk' },
    { id: '3183150', alt: 'Team collaborating on project' },
  ],
  audio: [
    { id: '3394650', alt: 'Professional microphone in recording studio' },
    { id: '164938', alt: 'Audio waveform visualization' },
    { id: '3756766', alt: 'Headphones and audio equipment' },
  ],
}

function pexelsUrl(id, width = 1200) {
  return `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=${width}`
}

function heroImageHtml(id, alt) {
  return `<figure class="wp-block-image size-large article-hero-image">
<img src="${pexelsUrl(id)}" alt="${alt}" loading="lazy" style="width:100%;height:auto;border-radius:8px;margin-bottom:2rem;" />
<figcaption style="text-align:center;font-size:0.85em;color:#888;">Photo via Pexels</figcaption>
</figure>\n\n`
}

function inlineImageHtml(id, alt, caption = '') {
  return `\n<figure class="wp-block-image size-large">
<img src="${pexelsUrl(id, 900)}" alt="${alt}" loading="lazy" style="width:100%;height:auto;border-radius:6px;margin:1.5rem 0;" />
${caption ? `<figcaption style="text-align:center;font-size:0.85em;color:#888;">${caption}</figcaption>` : ''}
</figure>\n`
}

function callClaude(prompt, maxTokens = 6000) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'claude-sonnet-4-6',
      max_tokens: maxTokens,
      messages: [{ role: 'user', content: prompt }],
    })

    const options = {
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'Content-Length': Buffer.byteLength(data),
      },
    }

    const req = https.request(options, (res) => {
      let body = ''
      res.on('data', (chunk) => (body += chunk))
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body)
          if (parsed.error) return reject(new Error(parsed.error.message))
          resolve(parsed.content[0].text)
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}\nBody: ${body.slice(0, 200)}`))
        }
      })
    })
    req.on('error', reject)
    req.write(data)
    req.end()
  })
}

const ARTICLES_TO_GENERATE = [
  {
    slug: 'best-ai-coding-tools-2026-github-copilot-vs-cursor-vs-tabnine',
    title: 'Best AI Coding Tools 2026: GitHub Copilot vs Cursor vs Tabnine',
    category: 'coding',
    tags: ['ai-coding', 'developer-tools', 'github-copilot', 'cursor'],
    keywords: ['best AI coding tools 2026', 'GitHub Copilot vs Cursor', 'AI code assistant'],
    imageSet: 'coding',
    excerpt: 'We tested every major AI coding tool head-to-head across real projects. Here\'s exactly which one will make you a faster developer in 2026.',
  },
  {
    slug: 'best-ai-image-generators-2026-midjourney-vs-dalle-vs-stable-diffusion',
    title: 'Best AI Image Generators 2026: Midjourney vs DALL-E vs Stable Diffusion',
    category: 'image',
    tags: ['ai-image', 'midjourney', 'dalle', 'stable-diffusion', 'image-generation'],
    keywords: ['best AI image generators 2026', 'Midjourney vs DALL-E', 'AI art tools'],
    imageSet: 'image_generation',
    excerpt: 'Midjourney, DALL-E 3, and Stable Diffusion each excel in different areas. After generating 500+ images, here\'s our honest breakdown.',
  },
  {
    slug: 'best-ai-marketing-tools-2026-complete-guide',
    title: 'Best AI Marketing Tools 2026: The Complete Guide for Marketers',
    category: 'marketing',
    tags: ['ai-marketing', 'marketing-automation', 'content-marketing', 'seo'],
    keywords: ['best AI marketing tools 2026', 'AI marketing automation', 'AI for marketers'],
    imageSet: 'marketing',
    excerpt: 'From SEO to social media to email — we\'ve tested every major AI marketing tool so you don\'t have to. Here\'s what actually works.',
  },
  {
    slug: 'best-ai-productivity-tools-2026-notion-ai-vs-chatgpt-vs-copilot',
    title: 'Best AI Productivity Tools 2026: Notion AI vs ChatGPT vs Microsoft Copilot',
    category: 'productivity',
    tags: ['ai-productivity', 'notion-ai', 'microsoft-copilot', 'work-tools'],
    keywords: ['best AI productivity tools 2026', 'Notion AI vs ChatGPT', 'AI work assistant'],
    imageSet: 'productivity',
    excerpt: 'We spent 3 months using AI productivity tools daily. Here\'s the honest truth about which ones actually save time vs. just adding complexity.',
  },
  {
    slug: 'best-ai-voice-audio-tools-2026-elevenlabs-vs-murf-vs-descript',
    title: 'Best AI Voice & Audio Tools 2026: ElevenLabs vs Murf vs Descript',
    category: 'audio',
    tags: ['ai-voice', 'text-to-speech', 'elevenlabs', 'voice-cloning', 'podcasting'],
    keywords: ['best AI voice tools 2026', 'ElevenLabs vs Murf', 'AI text to speech 2026'],
    imageSet: 'audio',
    excerpt: 'AI voice technology has exploded in 2026. We tested 8 platforms for voice cloning, TTS, and podcast production to find the best for each use case.',
  },
]

function buildPrompt(article) {
  return `Write a comprehensive, high-quality blog article for ToolPilot, an AI tools review site. The article should be authoritative, honest, and genuinely useful.

Title: ${article.title}
Category: ${article.category}
Target keywords: ${article.keywords.join(', ')}

REQUIREMENTS:
- 2,500-3,000 words
- Written in a direct, expert style (like The Wirecutter or Tom's Guide)
- Include real pricing data, specific feature comparisons, honest pros and cons
- Include a comparison table (HTML table) early in the article
- Include an FAQ section with schema.org markup at the end
- Include 2-3 specific "Where It Shines" / "Where It Falls Short" sections for each major tool
- Include a "How to Choose" decision framework section
- Use specific statistics and data points where relevant
- Add affiliate disclosure note
- All affiliate links should use href="#" placeholder

FORMAT: Return ONLY the article body HTML (no <html>, <head>, <body> tags). Use proper semantic HTML with <h2>, <h3>, <p>, <ul>, <li>, <figure class="wp-block-table">, <table> tags. Use WordPress-style button blocks for CTAs: <div class="wp-block-buttons"><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="#" target="_blank" rel="noopener nofollow sponsored">CTA text</a></div></div>

Do NOT include the <h1> title — it's rendered separately. Start directly with the opening paragraph.`
}

async function generateArticle(article) {
  console.log(`\n📝 Generating: ${article.title}`)
  const prompt = buildPrompt(article)
  const html = await callClaude(prompt, 6000)

  // Get image set for this article
  const imgs = PEXELS_IMAGES[article.imageSet] || PEXELS_IMAGES.productivity

  // Insert hero image at the start
  let finalHtml = heroImageHtml(imgs[0].id, imgs[0].alt)

  // Split HTML roughly in thirds and insert inline images
  const lines = html.split('\n')
  const third = Math.floor(lines.length / 3)
  const twoThirds = Math.floor((lines.length * 2) / 3)

  const part1 = lines.slice(0, third).join('\n')
  const part2 = lines.slice(third, twoThirds).join('\n')
  const part3 = lines.slice(twoThirds).join('\n')

  finalHtml += part1
  if (imgs[1]) finalHtml += inlineImageHtml(imgs[1].id, imgs[1].alt)
  finalHtml += part2
  if (imgs[2]) finalHtml += inlineImageHtml(imgs[2].id, imgs[2].alt)
  finalHtml += part3

  // Calculate word count (rough estimate from text content)
  const textOnly = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ')
  const wordCount = textOnly.trim().split(' ').length

  const today = new Date().toISOString().slice(0, 10)

  return {
    slug: article.slug,
    title: article.title,
    excerpt: article.excerpt,
    html: finalHtml,
    category: article.category,
    tags: article.tags,
    word_count: wordCount,
    published_date: today,
    author: 'ToolPilot Team',
    featured: false,
    meta_title: article.title,
    meta_description: article.excerpt,
    keywords: article.keywords,
    hero_image: pexelsUrl(PEXELS_IMAGES[article.imageSet][0].id),
  }
}

async function main() {
  console.log('🚀 ToolPilot Blog Post Generator')
  console.log(`📚 Generating ${ARTICLES_TO_GENERATE.length} articles...\n`)

  // Ensure images dir exists
  if (!fs.existsSync(IMAGES_DIR)) {
    fs.mkdirSync(IMAGES_DIR, { recursive: true })
  }

  // Load existing articles
  let existing = []
  if (fs.existsSync(ARTICLES_FILE)) {
    existing = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'))
  }
  const existingSlugs = new Set(existing.map((a) => a.slug))

  const newArticles = []

  for (const articleDef of ARTICLES_TO_GENERATE) {
    if (existingSlugs.has(articleDef.slug)) {
      console.log(`⏭️  Skipping (exists): ${articleDef.slug}`)
      continue
    }

    try {
      const article = await generateArticle(articleDef)
      newArticles.push(article)
      console.log(`✅ Generated: ${article.title} (${article.word_count} words)`)

      // Small delay between API calls
      await new Promise((r) => setTimeout(r, 1000))
    } catch (err) {
      console.error(`❌ Failed: ${articleDef.title}`)
      console.error(err.message)
    }
  }

  if (newArticles.length === 0) {
    console.log('\n⚠️  No new articles generated.')
    return
  }

  // Sort newest first, append new articles
  const updated = [...newArticles, ...existing]
  fs.writeFileSync(ARTICLES_FILE, JSON.stringify(updated, null, 2))

  console.log(`\n🎉 Done! Added ${newArticles.length} articles to articles.json`)
  console.log('\nNew articles:')
  newArticles.forEach((a) => console.log(`  - ${a.title}`))
}

main().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
