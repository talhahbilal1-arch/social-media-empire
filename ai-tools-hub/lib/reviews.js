import reviews from '../content/reviews.json'

export function getAllReviews() {
  return reviews.sort((a, b) => new Date(b.published_date) - new Date(a.published_date))
}

export function getReviewBySlug(slug) {
  return reviews.find(r => r.slug === slug)
}

export function getReadingTime(wordCount) {
  const minutes = Math.ceil(wordCount / 250)
  return `${minutes} min read`
}
