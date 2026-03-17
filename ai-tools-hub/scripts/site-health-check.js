#!/usr/bin/env node
/**
 * ToolPilot Site Health Check & Weekly Report Generator
 *
 * Checks:
 *  1. Total pages on site (tools, comparisons, categories, static)
 *  2. Content published this week (from content-calendar.json)
 *  3. Broken internal links (crawls sitemap URLs)
 *  4. Affiliate link health (HEAD request to each configured URL)
 *  5. Sitemap validity
 *
 * Usage:
 *   node scripts/site-health-check.js              # full report (stdout)
 *   node scripts/site-health-check.js --json        # JSON output
 *   node scripts/site-health-check.js --skip-live   # skip live URL checks (offline mode)
 */

const https = require('https')
const http = require('http')
const fs = require('fs')
const path = require('path')

const SITE_URL = 'https://toolpilot-hub.netlify.app'
const args = process.argv.slice(2)
const JSON_OUTPUT = args.includes('--json')
const SKIP_LIVE = args.includes('--skip-live')

// ── Helpers ─────────────────────────────────────────────────────

function httpGet(url, method = 'GET', timeout = 10000) {
  return new Promise((resolve) => {
    const mod = url.startsWith('https') ? https : http
    const req = mod.request(url, { method, timeout, headers: { 'User-Agent': 'ToolPilot-HealthCheck/1.0' } }, (res) => {
      let body = ''
      res.on('data', chunk => body += chunk)
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }))
    })
    req.on('error', (err) => resolve({ status: 0, error: err.message }))
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, error: 'timeout' }) })
    req.end()
  })
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms))
}

// ── 1. Content Inventory ────────────────────────────────────────

function getContentInventory() {
  const contentDir = path.join(__dirname, '..', 'content')
  const configDir = path.join(__dirname, '..', 'config')

  const tools = JSON.parse(fs.readFileSync(path.join(contentDir, 'tools.json'), 'utf8'))
  const comparisons = JSON.parse(fs.readFileSync(path.join(contentDir, 'comparisons.json'), 'utf8'))
  const categories = JSON.parse(fs.readFileSync(path.join(contentDir, 'categories.json'), 'utf8'))

  // Static pages: /, /compare/
  const staticPages = 2

  const totalPages = staticPages + tools.length + comparisons.length + categories.length

  // Content calendar stats
  let calendarStats = { published: 0, pending: 0, thisWeek: 0 }
  const calendarPath = path.join(configDir, 'content-calendar.json')
  if (fs.existsSync(calendarPath)) {
    const calendar = JSON.parse(fs.readFileSync(calendarPath, 'utf8'))
    const now = new Date()
    const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000)

    for (const item of calendar.items) {
      if (item.status === 'published') {
        calendarStats.published++
        if (item.published_date && new Date(item.published_date) >= weekAgo) {
          calendarStats.thisWeek++
        }
      } else {
        calendarStats.pending++
      }
    }
  }

  return {
    tools: tools.length,
    comparisons: comparisons.length,
    categories: categories.length,
    staticPages,
    totalPages,
    calendar: calendarStats,
    toolSlugs: tools.map(t => t.slug),
    comparisonSlugs: comparisons.map(c => c.slug),
    categorySlugs: categories.map(c => c.slug)
  }
}

// ── 2. Sitemap Check ────────────────────────────────────────────

async function checkSitemap() {
  if (SKIP_LIVE) return { ok: true, skipped: true, urlCount: 0 }

  const res = await httpGet(`${SITE_URL}/sitemap.xml`)
  if (res.status !== 200) {
    return { ok: false, error: `Sitemap returned status ${res.status}` }
  }

  // Count <loc> entries
  const locs = res.body.match(/<loc>/g)
  const urlCount = locs ? locs.length : 0

  // Extract all URLs from sitemap
  const urlRegex = /<loc>(.*?)<\/loc>/g
  const urls = []
  let match
  while ((match = urlRegex.exec(res.body)) !== null) {
    urls.push(match[1])
  }

  return { ok: true, urlCount, urls }
}

// ── 3. Broken Link Check ────────────────────────────────────────

async function checkBrokenLinks(sitemapUrls) {
  if (SKIP_LIVE || !sitemapUrls || sitemapUrls.length === 0) {
    return { checked: 0, broken: [], skipped: SKIP_LIVE }
  }

  const broken = []
  const checked = []

  // Check all sitemap URLs with rate limiting
  for (const url of sitemapUrls) {
    const res = await httpGet(url, 'HEAD')
    checked.push(url)

    if (res.status === 0 || res.status >= 400) {
      broken.push({ url, status: res.status, error: res.error || `HTTP ${res.status}` })
    }

    await sleep(200) // rate limit: 5 req/sec
  }

  return { checked: checked.length, broken }
}

// ── 4. Affiliate Link Health ────────────────────────────────────

async function checkAffiliateLinks() {
  if (SKIP_LIVE) return { checked: 0, results: [], skipped: true }

  const configPath = path.join(__dirname, '..', 'config', 'affiliate-links.json')
  if (!fs.existsSync(configPath)) {
    return { checked: 0, results: [], error: 'affiliate-links.json not found' }
  }

  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'))
  const results = []

  for (const [slug, tool] of Object.entries(config.tools)) {
    const url = (tool.affiliate_url !== 'PASTE_LINK_HERE')
      ? tool.affiliate_url
      : tool.fallback_url

    const res = await httpGet(url, 'HEAD')

    const healthy = res.status > 0 && res.status < 400
    results.push({
      tool: tool.name,
      slug,
      url,
      isAffiliate: tool.affiliate_url !== 'PASTE_LINK_HERE',
      status: res.status,
      healthy,
      error: res.error || null
    })

    await sleep(300) // rate limit
  }

  return {
    checked: results.length,
    healthy: results.filter(r => r.healthy).length,
    broken: results.filter(r => !r.healthy),
    withAffiliateUrl: results.filter(r => r.isAffiliate).length,
    usingFallback: results.filter(r => !r.isAffiliate).length,
    results
  }
}

// ── 5. Robots.txt Check ─────────────────────────────────────────

async function checkRobotsTxt() {
  if (SKIP_LIVE) return { ok: true, skipped: true }

  const res = await httpGet(`${SITE_URL}/robots.txt`)
  if (res.status !== 200) {
    return { ok: false, error: `robots.txt returned status ${res.status}` }
  }

  const hasSitemap = res.body.includes('sitemap.xml')
  const allowsAll = res.body.includes('Allow: /')

  return { ok: true, hasSitemap, allowsAll, content: res.body.trim() }
}

// ── Main ────────────────────────────────────────────────────────

async function main() {
  const startTime = Date.now()
  const report = {
    generated: new Date().toISOString(),
    site: SITE_URL,
    content: null,
    sitemap: null,
    brokenLinks: null,
    affiliateLinks: null,
    robotsTxt: null,
    duration: null,
    overallHealth: 'healthy'
  }

  // 1. Content inventory (always works — reads local files)
  if (!JSON_OUTPUT) process.stdout.write('Checking content inventory... ')
  report.content = getContentInventory()
  if (!JSON_OUTPUT) console.log(`${report.content.totalPages} pages`)

  // 2. Sitemap
  if (!JSON_OUTPUT) process.stdout.write('Checking sitemap... ')
  report.sitemap = await checkSitemap()
  if (!JSON_OUTPUT) {
    if (report.sitemap.skipped) console.log('skipped (offline)')
    else if (report.sitemap.ok) console.log(`OK (${report.sitemap.urlCount} URLs)`)
    else console.log(`FAIL: ${report.sitemap.error}`)
  }

  // 3. Broken links
  if (!JSON_OUTPUT) process.stdout.write('Checking for broken links... ')
  report.brokenLinks = await checkBrokenLinks(report.sitemap.urls)
  if (!JSON_OUTPUT) {
    if (report.brokenLinks.skipped) console.log('skipped (offline)')
    else console.log(`${report.brokenLinks.checked} checked, ${report.brokenLinks.broken.length} broken`)
  }

  // 4. Affiliate links
  if (!JSON_OUTPUT) process.stdout.write('Checking affiliate links... ')
  report.affiliateLinks = await checkAffiliateLinks()
  if (!JSON_OUTPUT) {
    if (report.affiliateLinks.skipped) console.log('skipped (offline)')
    else console.log(`${report.affiliateLinks.healthy}/${report.affiliateLinks.checked} healthy, ${report.affiliateLinks.withAffiliateUrl} with real affiliate URLs`)
  }

  // 5. Robots.txt
  if (!JSON_OUTPUT) process.stdout.write('Checking robots.txt... ')
  report.robotsTxt = await checkRobotsTxt()
  if (!JSON_OUTPUT) {
    if (report.robotsTxt.skipped) console.log('skipped (offline)')
    else if (report.robotsTxt.ok) console.log('OK')
    else console.log(`FAIL: ${report.robotsTxt.error}`)
  }

  // Overall health assessment
  const issues = []
  if (report.sitemap && !report.sitemap.ok && !report.sitemap.skipped) issues.push('Sitemap error')
  if (report.brokenLinks && report.brokenLinks.broken && report.brokenLinks.broken.length > 0) issues.push(`${report.brokenLinks.broken.length} broken links`)
  if (report.affiliateLinks && report.affiliateLinks.broken && report.affiliateLinks.broken.length > 0) issues.push(`${report.affiliateLinks.broken.length} broken affiliate links`)
  if (report.robotsTxt && !report.robotsTxt.ok && !report.robotsTxt.skipped) issues.push('robots.txt error')

  if (issues.length > 2) report.overallHealth = 'unhealthy'
  else if (issues.length > 0) report.overallHealth = 'degraded'

  report.issues = issues
  report.duration = `${((Date.now() - startTime) / 1000).toFixed(1)}s`

  if (JSON_OUTPUT) {
    console.log(JSON.stringify(report, null, 2))
  } else {
    printTextReport(report)
  }

  // Exit with error code if unhealthy
  if (report.overallHealth === 'unhealthy') process.exit(1)
}

function printTextReport(report) {
  console.log('\n' + '='.repeat(60))
  console.log('  TOOLPILOT WEEKLY HEALTH REPORT')
  console.log('  ' + report.generated)
  console.log('='.repeat(60))

  // Content summary
  console.log('\n📊 CONTENT INVENTORY')
  console.log(`  Tool reviews:    ${report.content.tools}`)
  console.log(`  Comparisons:     ${report.content.comparisons}`)
  console.log(`  Categories:      ${report.content.categories}`)
  console.log(`  Total pages:     ${report.content.totalPages}`)
  console.log(`  Calendar:        ${report.content.calendar.published} published, ${report.content.calendar.pending} pending`)
  if (report.content.calendar.thisWeek > 0) {
    console.log(`  Published this week: ${report.content.calendar.thisWeek}`)
  }

  // Sitemap
  if (!report.sitemap.skipped) {
    console.log('\n🗺️  SITEMAP')
    if (report.sitemap.ok) {
      console.log(`  Status: OK (${report.sitemap.urlCount} URLs)`)
      if (report.sitemap.urlCount !== report.content.totalPages) {
        console.log(`  ⚠️  Sitemap has ${report.sitemap.urlCount} URLs but site has ${report.content.totalPages} pages`)
      }
    } else {
      console.log(`  Status: FAIL — ${report.sitemap.error}`)
    }
  }

  // Broken links
  if (!report.brokenLinks.skipped) {
    console.log('\n🔗 BROKEN LINKS')
    if (report.brokenLinks.broken.length === 0) {
      console.log(`  All ${report.brokenLinks.checked} pages OK`)
    } else {
      console.log(`  ${report.brokenLinks.broken.length} broken out of ${report.brokenLinks.checked}:`)
      for (const b of report.brokenLinks.broken) {
        console.log(`    ✗ ${b.url} → ${b.error}`)
      }
    }
  }

  // Affiliate links
  if (!report.affiliateLinks.skipped) {
    console.log('\n💰 AFFILIATE LINKS')
    console.log(`  Total tools:       ${report.affiliateLinks.checked}`)
    console.log(`  Links healthy:     ${report.affiliateLinks.healthy}`)
    console.log(`  Real affiliate URLs: ${report.affiliateLinks.withAffiliateUrl}`)
    console.log(`  Using fallback:    ${report.affiliateLinks.usingFallback}`)
    if (report.affiliateLinks.broken.length > 0) {
      console.log('  Broken:')
      for (const b of report.affiliateLinks.broken) {
        console.log(`    ✗ ${b.tool} (${b.url}) → ${b.error || 'HTTP ' + b.status}`)
      }
    }
  }

  // Overall
  console.log('\n' + '─'.repeat(60))
  const icon = report.overallHealth === 'healthy' ? '✅' :
               report.overallHealth === 'degraded' ? '⚠️' : '❌'
  console.log(`${icon} Overall health: ${report.overallHealth.toUpperCase()}`)
  if (report.issues.length > 0) {
    console.log('  Issues: ' + report.issues.join(', '))
  }
  console.log(`  Completed in ${report.duration}`)
  console.log('='.repeat(60))
}

main().catch(err => {
  console.error('Health check failed:', err.message)
  process.exit(1)
})
