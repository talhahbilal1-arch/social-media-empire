#!/usr/bin/env node
/**
 * Ping Google to re-crawl the sitemap after new content is published.
 * Uses the public ping endpoint (no API key needed).
 *
 * Usage: node scripts/ping-google.js
 */

const https = require('https')

const SITE_URL = 'https://ai-tools-hub-lilac.vercel.app'
const SITEMAP_URL = `${SITE_URL}/sitemap.xml`

function pingGoogle() {
  return new Promise((resolve, reject) => {
    const url = `https://www.google.com/ping?sitemap=${encodeURIComponent(SITEMAP_URL)}`

    https.get(url, (res) => {
      let body = ''
      res.on('data', chunk => body += chunk)
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`Google pinged successfully (status ${res.statusCode})`)
          resolve(true)
        } else {
          console.log(`Google ping returned status ${res.statusCode}`)
          resolve(false)
        }
      })
    }).on('error', (err) => {
      console.error(`Google ping failed: ${err.message}`)
      resolve(false)
    })
  })
}

function pingBing() {
  return new Promise((resolve, reject) => {
    const url = `https://www.bing.com/ping?sitemap=${encodeURIComponent(SITEMAP_URL)}`

    https.get(url, (res) => {
      let body = ''
      res.on('data', chunk => body += chunk)
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`Bing pinged successfully (status ${res.statusCode})`)
          resolve(true)
        } else {
          console.log(`Bing ping returned status ${res.statusCode}`)
          resolve(false)
        }
      })
    }).on('error', (err) => {
      console.error(`Bing ping failed: ${err.message}`)
      resolve(false)
    })
  })
}

async function main() {
  console.log(`Pinging search engines with sitemap: ${SITEMAP_URL}`)
  console.log()

  await Promise.all([
    pingGoogle(),
    pingBing()
  ])

  console.log('\nDone. Search engines will re-crawl within 24-48 hours.')
}

main()
