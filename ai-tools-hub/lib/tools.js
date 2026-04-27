import tools from '../content/tools.json'
import categories from '../content/categories.json'
import comparisons from '../content/comparisons.json'
import affiliateConfig from '../config/affiliate-links.json'

export function getAllTools() {
  return tools
}

export function getToolBySlug(slug) {
  return tools.find(t => t.slug === slug)
}

export function getToolsByCategory(categorySlug) {
  return tools.filter(t => t.categories.includes(categorySlug))
}

export function getAllCategories() {
  return categories
}

export function getCategoryBySlug(slug) {
  return categories.find(c => c.slug === slug)
}

export function getAllComparisons() {
  return comparisons
}

export function getComparisonBySlug(slug) {
  return comparisons.find(c => c.slug === slug)
}

export function getToolsForComparison(comparison) {
  return comparison.tools.map(slug => getToolBySlug(slug)).filter(Boolean)
}

export function getFeaturedTools() {
  return tools.filter(t => t.rating >= 4.6).slice(0, 6)
}

export function getTopToolsByCategory(categorySlug, limit = 3) {
  return getToolsByCategory(categorySlug)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit)
}

export function formatPrice(price) {
  if (price === 0) return 'Free'
  if (price === null) return 'Custom'
  return `$${price}/mo`
}

export function generateStarRating(rating) {
  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 >= 0.3
  return { fullStars, hasHalf, emptyStars: 5 - fullStars - (hasHalf ? 1 : 0) }
}

export function getAffiliateUrl(slug, campaign) {
  const config = affiliateConfig.tools[slug]
  const tool = getToolBySlug(slug)

  let url = tool?.affiliate_url || ''
  if (config && config.affiliate_url !== 'PASTE_LINK_HERE') {
    url = config.affiliate_url
  } else if (config) {
    url = config.fallback_url
  }

  const utm = campaign || 'review'
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}utm_source=toolpilot&utm_medium=${utm}&utm_campaign=${slug}`
}

// --- New helpers for Phase 3+ ---

export function getAlternativesForTool(slug) {
  const tool = getToolBySlug(slug)
  if (!tool?.alternatives) return []
  return tool.alternatives
    .map(alt => {
      const fullTool = getToolBySlug(alt.slug)
      return fullTool ? { ...fullTool, reason: alt.reason } : null
    })
    .filter(Boolean)
}

export function getToolsByUseCase(useCase) {
  const lc = useCase.toLowerCase()
  return tools
    .filter(t => t.use_cases && t.use_cases.some(uc => uc.toLowerCase() === lc))
    .sort((a, b) => b.rating - a.rating)
}

export function getAllUseCases() {
  const set = new Set()
  tools.forEach(t => {
    if (t.use_cases) t.use_cases.forEach(uc => set.add(uc))
  })
  return [...set].sort()
}

export function getRelatedComparisons(toolSlug) {
  return comparisons.filter(c => c.tools.includes(toolSlug))
}

export function getOfferBadge(slug, freeTier) {
  const config = affiliateConfig.tools[slug]
  if (!config) return null
  if (freeTier) return 'Free Trial Available'
  if (config.commission && config.commission !== 'TBD') return 'Special Offer'
  return null
}
