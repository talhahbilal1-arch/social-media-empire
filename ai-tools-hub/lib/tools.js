import tools from '../content/tools.json'
import categories from '../content/categories.json'
import comparisons from '../content/comparisons.json'

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
