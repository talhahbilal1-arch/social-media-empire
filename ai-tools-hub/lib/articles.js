import articles from '../content/articles.json'

export function getAllArticles() {
  return articles.sort((a, b) => new Date(b.published_date) - new Date(a.published_date))
}

export function getArticleBySlug(slug) {
  return articles.find(a => a.slug === slug)
}

export function getArticlesByCategory(category) {
  return articles.filter(a => a.category === category)
}

export function getFeaturedArticles(limit = 3) {
  return getAllArticles().filter(a => a.featured).slice(0, limit)
}

export function getReadingTime(wordCount) {
  const minutes = Math.ceil(wordCount / 250)
  return `${minutes} min read`
}
