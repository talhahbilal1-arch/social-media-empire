#!/usr/bin/env node
/**
 * Pinterest Pin Generator for ToolPilot
 * Generates pin content for each AI tool review and comparison.
 * Integrates with the existing social-media-empire Pinterest automation.
 *
 * Output: JSON array of pin data that can be fed to the content_brain pipeline.
 */

const fs = require('fs')
const path = require('path')

const SITE_URL = 'https://toolpilot-hub.netlify.app'
const tools = require('../content/tools.json')
const comparisons = require('../content/comparisons.json')
const articles = require('../content/articles.json')

function generateToolPins() {
  const pins = []

  // Tool review pins
  for (const tool of tools) {
    pins.push({
      type: 'tool_review',
      title: `${tool.name} Review 2026: Is It Worth It?`,
      description: `${tool.tagline}. Rating: ${tool.rating}/5. ${tool.pricing.free_tier ? 'Free tier available!' : `Starting at $${tool.pricing.starting_price}/mo.`} Read our full review with pros, cons, and pricing breakdown.`,
      link: `${SITE_URL}/tools/${tool.slug}/`,
      keywords: [tool.name, 'AI tool', tool.category, 'review', '2026'],
      board_suggestion: `AI ${tool.category.charAt(0).toUpperCase() + tool.category.slice(1)} Tools`
    })

    // "Best for" pins
    for (const useCase of tool.best_for.slice(0, 2)) {
      pins.push({
        type: 'best_for',
        title: `Best AI Tool for ${useCase}: ${tool.name}`,
        description: `Looking for the best AI tool for ${useCase.toLowerCase()}? ${tool.name} scores ${tool.rating}/5 with features like ${tool.features.slice(0, 3).join(', ')}. ${tool.pricing.free_tier ? 'Try it free!' : ''}`,
        link: `${SITE_URL}/tools/${tool.slug}/`,
        keywords: ['best AI tool', useCase, tool.name, '2026'],
        board_suggestion: 'AI Tools & Technology'
      })
    }
  }

  // Comparison pins
  for (const comp of comparisons) {
    const tool1Name = comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    const tool2Name = comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

    pins.push({
      type: 'comparison',
      title: `${tool1Name} vs ${tool2Name}: Which Is Better in 2026?`,
      description: comp.verdict,
      link: `${SITE_URL}/compare/${comp.slug}/`,
      keywords: [tool1Name, tool2Name, 'comparison', 'vs', '2026'],
      board_suggestion: 'AI Tool Comparisons'
    })
  }

  // Article pins
  for (const article of articles) {
    pins.push({
      type: 'article',
      title: article.title,
      description: article.excerpt || article.meta_description,
      link: `${SITE_URL}/blog/${article.slug}/`,
      keywords: article.keywords || [article.category, 'AI tools', '2026'],
      board_suggestion: 'AI Tools & Money'
    })
  }

  return pins
}

const pins = generateToolPins()
const outputPath = path.join(__dirname, '..', 'content', 'pinterest-pins.json')
fs.writeFileSync(outputPath, JSON.stringify(pins, null, 2))

console.log(`Generated ${pins.length} Pinterest pin ideas:`)
console.log(`  - ${pins.filter(p => p.type === 'tool_review').length} tool review pins`)
console.log(`  - ${pins.filter(p => p.type === 'best_for').length} "best for" pins`)
console.log(`  - ${pins.filter(p => p.type === 'comparison').length} comparison pins`)
console.log(`  - ${pins.filter(p => p.type === 'article').length} article pins`)
console.log(`Output: ${outputPath}`)
