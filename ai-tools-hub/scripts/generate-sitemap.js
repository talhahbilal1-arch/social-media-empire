const fs = require('fs')
const path = require('path')

const SITE_URL = 'https://ai-tools-hub-lilac.vercel.app'

const tools = require('../content/tools.json')
const categories = require('../content/categories.json')
const comparisons = require('../content/comparisons.json')
const articles = require('../content/articles.json')

const today = new Date().toISOString().split('T')[0]

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
  </url>`).join('\n')}
${categories.map(c => `  <url>
    <loc>${SITE_URL}/category/${c.slug}/</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
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
</urlset>`

const outDir = path.join(__dirname, '..', 'public')
fs.writeFileSync(path.join(outDir, 'sitemap.xml'), sitemap)
console.log(`Sitemap generated with ${tools.length + categories.length + comparisons.length + articles.length + 3} URLs`)

const robots = `User-agent: *
Allow: /
Disallow: /api/

Sitemap: ${SITE_URL}/sitemap.xml`

fs.writeFileSync(path.join(outDir, 'robots.txt'), robots)
console.log('robots.txt generated')
