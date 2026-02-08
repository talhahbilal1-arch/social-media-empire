#!/usr/bin/env node
/**
 * Sends the ToolPilot weekly health report via Resend email.
 * Reads JSON report from stdin (piped from site-health-check.js --json).
 *
 * Usage:
 *   node scripts/site-health-check.js --json | node scripts/send-report-email.js
 *
 * Requires:
 *   RESEND_API_KEY  — Resend API key
 *   ALERT_EMAIL     — recipient email address
 */

const https = require('https')

const RESEND_API_KEY = process.env.RESEND_API_KEY
const ALERT_EMAIL = process.env.ALERT_EMAIL

if (!RESEND_API_KEY || !ALERT_EMAIL) {
  console.log('RESEND_API_KEY or ALERT_EMAIL not set — skipping email report')
  process.exit(0)
}

function sendEmail(to, subject, html) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      from: 'ToolPilot Reports <onboarding@resend.dev>',
      to: [to],
      subject,
      html
    })

    const req = https.request({
      hostname: 'api.resend.com',
      path: '/emails',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = ''
      res.on('data', chunk => body += chunk)
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(JSON.parse(body))
        } else {
          reject(new Error(`Resend API ${res.statusCode}: ${body}`))
        }
      })
    })
    req.on('error', reject)
    req.write(data)
    req.end()
  })
}

function buildEmailHtml(report) {
  const healthColor = report.overallHealth === 'healthy' ? '#16a34a' :
                      report.overallHealth === 'degraded' ? '#d97706' : '#dc2626'
  const healthIcon = report.overallHealth === 'healthy' ? '&#9989;' :
                     report.overallHealth === 'degraded' ? '&#9888;&#65039;' : '&#10060;'

  const brokenLinksHtml = (report.brokenLinks && report.brokenLinks.broken && report.brokenLinks.broken.length > 0)
    ? report.brokenLinks.broken.map(b =>
        `<tr><td style="padding:4px 8px;border:1px solid #e5e7eb;font-size:13px;">${b.url}</td><td style="padding:4px 8px;border:1px solid #e5e7eb;font-size:13px;color:#dc2626;">${b.error || 'HTTP ' + b.status}</td></tr>`
      ).join('')
    : ''

  const brokenAffiliateHtml = (report.affiliateLinks && report.affiliateLinks.broken && report.affiliateLinks.broken.length > 0)
    ? report.affiliateLinks.broken.map(b =>
        `<tr><td style="padding:4px 8px;border:1px solid #e5e7eb;font-size:13px;">${b.tool}</td><td style="padding:4px 8px;border:1px solid #e5e7eb;font-size:13px;">${b.url}</td><td style="padding:4px 8px;border:1px solid #e5e7eb;font-size:13px;color:#dc2626;">${b.error || 'HTTP ' + b.status}</td></tr>`
      ).join('')
    : ''

  return `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;padding:20px;color:#1f2937;">

<div style="background:linear-gradient(135deg,#2563eb,#1d4ed8);color:white;padding:24px;border-radius:12px;margin-bottom:24px;">
  <h1 style="margin:0;font-size:22px;">ToolPilot Weekly Report</h1>
  <p style="margin:8px 0 0;opacity:0.9;font-size:14px;">${new Date(report.generated).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
</div>

<div style="background:${healthColor}15;border:1px solid ${healthColor}40;border-radius:8px;padding:16px;margin-bottom:20px;">
  <span style="font-size:20px;">${healthIcon}</span>
  <strong style="color:${healthColor};font-size:16px;margin-left:8px;">Overall: ${report.overallHealth.toUpperCase()}</strong>
  ${report.issues && report.issues.length > 0 ? `<p style="margin:8px 0 0;font-size:13px;color:#6b7280;">${report.issues.join(' • ')}</p>` : ''}
</div>

<h2 style="font-size:16px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;">Content Inventory</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
  <tr><td style="padding:6px 0;color:#6b7280;">Tool reviews</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.content.tools}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Comparisons</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.content.comparisons}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Categories</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.content.categories}</td></tr>
  <tr style="border-top:1px solid #e5e7eb;"><td style="padding:6px 0;font-weight:600;">Total pages</td><td style="padding:6px 0;font-weight:700;text-align:right;color:#2563eb;">${report.content.totalPages}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Calendar published</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.content.calendar.published}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Calendar pending</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.content.calendar.pending}</td></tr>
  ${report.content.calendar.thisWeek > 0 ? `<tr><td style="padding:6px 0;color:#16a34a;font-weight:600;">Published this week</td><td style="padding:6px 0;font-weight:700;text-align:right;color:#16a34a;">${report.content.calendar.thisWeek}</td></tr>` : ''}
</table>

${report.sitemap && !report.sitemap.skipped ? `
<h2 style="font-size:16px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;">Sitemap</h2>
<p style="font-size:14px;">${report.sitemap.ok ? `&#9989; OK — ${report.sitemap.urlCount} URLs indexed` : `&#10060; ${report.sitemap.error}`}</p>
${report.sitemap.ok && report.sitemap.urlCount !== report.content.totalPages ? `<p style="font-size:13px;color:#d97706;">&#9888;&#65039; Sitemap has ${report.sitemap.urlCount} URLs but site has ${report.content.totalPages} pages</p>` : ''}
` : ''}

${!report.brokenLinks.skipped ? `
<h2 style="font-size:16px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;">Broken Links</h2>
${report.brokenLinks.broken.length === 0
  ? `<p style="font-size:14px;">&#9989; All ${report.brokenLinks.checked} pages OK</p>`
  : `<p style="font-size:14px;color:#dc2626;">${report.brokenLinks.broken.length} broken out of ${report.brokenLinks.checked}:</p>
     <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
       <tr><th style="text-align:left;padding:4px 8px;background:#f9fafb;border:1px solid #e5e7eb;font-size:13px;">URL</th><th style="text-align:left;padding:4px 8px;background:#f9fafb;border:1px solid #e5e7eb;font-size:13px;">Error</th></tr>
       ${brokenLinksHtml}
     </table>`
}
` : ''}

${report.affiliateLinks && !report.affiliateLinks.skipped ? `
<h2 style="font-size:16px;border-bottom:2px solid #e5e7eb;padding-bottom:8px;">Affiliate Links</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:12px;">
  <tr><td style="padding:6px 0;color:#6b7280;">Total tools</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.affiliateLinks.checked}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Links healthy</td><td style="padding:6px 0;font-weight:600;text-align:right;color:#16a34a;">${report.affiliateLinks.healthy}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Real affiliate URLs</td><td style="padding:6px 0;font-weight:600;text-align:right;">${report.affiliateLinks.withAffiliateUrl}</td></tr>
  <tr><td style="padding:6px 0;color:#6b7280;">Using fallback URL</td><td style="padding:6px 0;font-weight:600;text-align:right;color:#d97706;">${report.affiliateLinks.usingFallback}</td></tr>
</table>
${report.affiliateLinks.broken.length > 0 ? `
<p style="font-size:13px;color:#dc2626;font-weight:600;">Broken affiliate links:</p>
<table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
  <tr><th style="text-align:left;padding:4px 8px;background:#f9fafb;border:1px solid #e5e7eb;font-size:12px;">Tool</th><th style="text-align:left;padding:4px 8px;background:#f9fafb;border:1px solid #e5e7eb;font-size:12px;">URL</th><th style="text-align:left;padding:4px 8px;background:#f9fafb;border:1px solid #e5e7eb;font-size:12px;">Error</th></tr>
  ${brokenAffiliateHtml}
</table>` : ''}
` : ''}

<div style="margin-top:24px;padding-top:16px;border-top:1px solid #e5e7eb;font-size:12px;color:#9ca3af;text-align:center;">
  <p>ToolPilot Health Report • <a href="${report.site}" style="color:#2563eb;">${report.site}</a></p>
  <p>Completed in ${report.duration}</p>
</div>

</body>
</html>`
}

async function main() {
  // Read JSON from stdin
  let input = ''
  process.stdin.setEncoding('utf8')
  for await (const chunk of process.stdin) {
    input += chunk
  }

  const report = JSON.parse(input)
  const subject = `ToolPilot Report: ${report.overallHealth.toUpperCase()} — ${report.content.totalPages} pages`

  console.log(`Sending report email to ${ALERT_EMAIL}...`)
  const result = await sendEmail(ALERT_EMAIL, subject, buildEmailHtml(report))
  console.log(`Email sent: ${result.id}`)
}

main().catch(err => {
  console.error('Failed to send report:', err.message)
  // Don't exit with error — email failure shouldn't fail the workflow
  process.exit(0)
})
