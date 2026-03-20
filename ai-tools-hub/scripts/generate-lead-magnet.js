#!/usr/bin/env node
/**
 * PilotTools Lead Magnet Generator
 * Generates "2026 AI Tools Pricing Cheat Sheet" HTML from tools.json.
 * Run weekly to keep pricing current.
 *
 * Usage: node scripts/generate-lead-magnet.js
 */

const fs = require('fs')
const path = require('path')

const TOOLS_FILE = path.join(__dirname, '..', 'content', 'tools.json')
const OUTPUT_DIR = path.join(__dirname, '..', 'public', 'downloads')
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'ai-tools-pricing-2026.html')

function main() {
  const tools = JSON.parse(fs.readFileSync(TOOLS_FILE, 'utf8'))

  // Group by category
  const categories = {}
  for (const tool of tools) {
    const cat = tool.category || 'other'
    if (!categories[cat]) categories[cat] = []
    categories[cat].push(tool)
  }

  // Sort categories and tools
  const catOrder = ['writing', 'coding', 'image', 'video', 'marketing', 'productivity', 'audio', 'seo', 'research', 'design']
  const sortedCats = Object.keys(categories).sort((a, b) => {
    const ai = catOrder.indexOf(a), bi = catOrder.indexOf(b)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })

  const catLabels = {
    writing: 'AI Writing Tools', coding: 'AI Coding Tools', image: 'AI Image Generators',
    video: 'AI Video Tools', marketing: 'AI Marketing Tools', productivity: 'AI Productivity Tools',
    audio: 'AI Audio & Voice Tools', seo: 'AI SEO Tools', research: 'AI Research Tools', design: 'AI Design Tools'
  }

  const today = new Date().toISOString().split('T')[0]

  // Build category sections
  let sections = ''
  let totalTools = 0

  for (const cat of sortedCats) {
    const catTools = categories[cat].sort((a, b) => (b.rating || 0) - (a.rating || 0))
    totalTools += catTools.length
    const label = catLabels[cat] || cat.charAt(0).toUpperCase() + cat.slice(1)

    let rows = ''
    for (const t of catTools) {
      const freeTier = t.pricing?.free_tier ? '✅ Yes' : '❌ No'
      const price = t.pricing?.starting_price ? `$${t.pricing.starting_price}/mo` : 'Custom'
      const bestPlan = t.pricing?.plans?.find(p => p.price && p.price > 0)?.name || 'Free'
      const bestFor = (t.best_for?.[0] || t.tagline || '').substring(0, 60)
      const rating = t.rating ? `${t.rating}/5` : 'N/A'

      rows += `
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;font-weight:600;">${t.name}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;">${freeTier}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;font-weight:600;color:#2563eb;">${price}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">${bestPlan}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#6b7280;">${bestFor}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;font-weight:600;">${rating}</td>
        </tr>`
    }

    sections += `
      <div style="margin-bottom:40px;">
        <h2 style="font-size:22px;font-weight:700;color:#1e293b;margin-bottom:16px;padding-bottom:8px;border-bottom:3px solid #2563eb;">${label}</h2>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#f1f5f9;">
              <th style="padding:10px 12px;text-align:left;font-weight:600;color:#475569;">Tool</th>
              <th style="padding:10px 12px;text-align:center;font-weight:600;color:#475569;">Free Tier</th>
              <th style="padding:10px 12px;text-align:center;font-weight:600;color:#475569;">Starting Price</th>
              <th style="padding:10px 12px;text-align:left;font-weight:600;color:#475569;">Best Plan</th>
              <th style="padding:10px 12px;text-align:left;font-weight:600;color:#475569;">Best For</th>
              <th style="padding:10px 12px;text-align:center;font-weight:600;color:#475569;">Rating</th>
            </tr>
          </thead>
          <tbody>${rows}
          </tbody>
        </table>
      </div>`
  }

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Tools Pricing Guide 2026 — PilotTools.ai</title>
  <style>
    @media print {
      body { font-size: 12px; }
      .no-print { display: none; }
      table { page-break-inside: auto; }
      tr { page-break-inside: avoid; }
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 24px;
      color: #1e293b;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div style="text-align:center;margin-bottom:48px;">
    <h1 style="font-size:32px;font-weight:800;color:#0f172a;margin-bottom:8px;">AI Tools Pricing Guide 2026</h1>
    <p style="font-size:16px;color:#64748b;margin-bottom:4px;">Every plan, price, and feature — compared side by side</p>
    <p style="font-size:14px;color:#94a3b8;">by <a href="https://pilottools.ai" style="color:#2563eb;text-decoration:none;font-weight:600;">PilotTools.ai</a> | Last Updated: ${today}</p>
    <p style="font-size:14px;color:#64748b;margin-top:12px;">${totalTools} tools reviewed across ${sortedCats.length} categories</p>
  </div>

  <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:20px;margin-bottom:40px;">
    <p style="margin:0;font-size:14px;color:#1e40af;">
      <strong>How to use this guide:</strong> Find your category below, compare free tiers and pricing, then click through to pilottools.ai for detailed reviews with pros, cons, and our honest verdict.
    </p>
  </div>

  ${sections}

  <div style="text-align:center;margin-top:48px;padding-top:24px;border-top:1px solid #e5e7eb;">
    <p style="font-size:14px;color:#94a3b8;">
      Get the latest reviews and updates at <a href="https://pilottools.ai" style="color:#2563eb;">pilottools.ai</a>
    </p>
    <p style="font-size:12px;color:#cbd5e1;">© 2026 PilotTools. Prices verified as of ${today}. Prices may change — always verify on the official site.</p>
  </div>
</body>
</html>`

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true })
  }

  fs.writeFileSync(OUTPUT_FILE, html)
  console.log(`Lead magnet generated: ${OUTPUT_FILE}`)
  console.log(`Total tools: ${totalTools} across ${sortedCats.length} categories`)
}

main()
