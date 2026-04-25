const fs = require('fs')
const path = require('path')

const SITE_URL = 'https://pilottools.ai'

const tools = require('../content/tools.json')
const categories = require('../content/categories.json')
const comparisons = require('../content/comparisons.json')
const articles = require('../content/articles.json')
const reviews = require('../content/reviews.json')

const today = new Date().toISOString().split('T')[0]

// Collect all use cases for /best/ pages
const useCasesSet = new Set()
tools.forEach(t => {
  if (t.use_cases) t.use_cases.forEach(uc => useCasesSet.add(uc))
})
const useCases = [...useCasesSet].sort()

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${SITE_URL}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${SITE_URL}/compare/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${SITE_URL}/quiz/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${SITE_URL}/pricing/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>${SITE_URL}/about/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.4</priority>
  </url>
  <url>
    <loc>${SITE_URL}/affiliate-disclosure/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>${SITE_URL}/privacy/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>${SITE_URL}/terms/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>${SITE_URL}/contact/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
${comparisons.map(c => `  <url>
    <loc>${SITE_URL}/compare/${c.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>`).join('\n')}
${tools.map(t => `  <url>
    <loc>${SITE_URL}/tools/${t.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${SITE_URL}/pricing/${t.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>${SITE_URL}/alternatives/${t.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>`).join('\n')}
${categories.map(c => `  <url>
    <loc>${SITE_URL}/category/${c.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`).join('\n')}
${useCases.map(uc => `  <url>
    <loc>${SITE_URL}/best/${slugify(uc)}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>`).join('\n')}
  <url>
    <loc>${SITE_URL}/blog/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
${articles.map(a => `  <url>
    <loc>${SITE_URL}/blog/${a.slug}/</loc>
    <lastmod>${a.published_date || today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`).join('\n')}
  <url>
    <loc>${SITE_URL}/reviews/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
${reviews.map(r => `  <url>
    <loc>${SITE_URL}/reviews/${r.slug}/</loc>
    <lastmod>${r.published_date || today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>`).join('\n')}
</urlset>`

const outDir = path.join(__dirname, '..', 'public')
fs.writeFileSync(path.join(outDir, 'sitemap.xml'), sitemap)

const totalUrls = 9 + comparisons.length + (tools.length * 3) + categories.length + useCases.length + 1 + articles.length + 1 + reviews.length
console.log(`Sitemap generated with ${totalUrls} URLs`)

const robots = `User-agent: *
Allow: /
Disallow: /api/

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: YouBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

Sitemap: ${SITE_URL}/sitemap.xml`

fs.writeFileSync(path.join(outDir, 'robots.txt'), robots)
console.log('robots.txt generated (GEO-optimized)')
