import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'
import { getAllReviews, getReadingTime } from '../../lib/reviews'

const SITE_URL = 'https://pilottools.ai'

export default function ReviewsIndex({ reviews }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    'name': 'PilotTools Tool Reviews',
    'description': 'Honest, hands-on reviews of the AI tools we actually use.',
    'url': `${SITE_URL}/reviews/`,
    'numberOfItems': reviews.length,
    'itemListElement': reviews.map((review, index) => ({
      '@type': 'Review',
      'position': index + 1,
      'headline': review.title,
      'description': review.excerpt,
      'url': `${SITE_URL}/reviews/${review.slug}/`,
      'datePublished': review.published_date,
      'author': {
        '@type': 'Organization',
        'name': review.author,
      },
      'reviewRating': {
        '@type': 'Rating',
        'ratingValue': review.rating,
        'bestRating': 5,
      },
      'itemReviewed': {
        '@type': 'SoftwareApplication',
        'name': review.tool_name,
        'url': review.tool_website,
      },
    })),
  }

  return (
    <Layout
      title="Tool Reviews - In-Depth AI Software Reviews"
      description="Honest, hands-on reviews of the AI tools we actually use. Detailed testing, pricing breakdown, and when to use each tool."
      canonical={`${SITE_URL}/reviews/`}
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Reviews' }]} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-dt mb-3">Reviews</h1>
          <p className="text-lg text-dt-muted">Honest, hands-on reviews of the AI tools we actually use. Months of testing, real production work, and transparent pricing breakdowns.</p>
        </div>

        {reviews.length === 0 ? (
          <p className="text-dt-muted">No reviews yet. Check back soon!</p>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {reviews.map((review) => (
              <Link key={review.slug} href={`/reviews/${review.slug}/`} className="card group hover:shadow-glow overflow-hidden p-0">
                {review.hero_image && (
                  <div className="w-full h-48 overflow-hidden bg-dark-surface-hover">
                    <img src={review.hero_image} alt={review.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="badge-blue text-xs">{review.category}</span>
                    <span className="text-xs text-dt-muted">{getReadingTime(review.word_count)}</span>
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-semibold text-accent">
                      {'★'.repeat(Math.floor(review.rating))}
                      {review.rating % 1 !== 0 && '½'}
                    </span>
                    <span className="text-sm text-dt-muted font-medium">{review.rating}</span>
                  </div>
                  <h2 className="text-lg font-semibold text-dt group-hover:text-accent transition-colors mb-2">{review.tool_name}</h2>
                  <p className="text-sm text-dt-muted line-clamp-3 mb-4">{review.excerpt}</p>
                  <div className="flex items-center justify-between text-xs text-dt-muted">
                    <span>{review.author}</span>
                    <span>{new Date(review.published_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}

export async function getStaticProps() {
  const reviews = getAllReviews()
  return { props: { reviews: reviews.map(({ html, ...rest }) => rest) } }
}
