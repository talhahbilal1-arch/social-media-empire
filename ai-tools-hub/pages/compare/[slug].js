import Layout from '../../components/Layout'
import ComparisonTable from '../../components/ComparisonTable'
import StarRating from '../../components/StarRating'
import AffiliateLink, { AffiliateDisclosure } from '../../components/AffiliateLink'
import Link from 'next/link'
import { getAllComparisons, getComparisonBySlug, getToolBySlug, formatPrice, getAffiliateUrl } from '../../lib/tools'

export default function ComparisonPage({ comparison, tool1, tool2 }) {
  if (!comparison || !tool1 || !tool2) return null

  const tool1Wins = comparison.comparison_points.filter(p => p.winner === comparison.tools[0]).length
  const tool2Wins = comparison.comparison_points.filter(p => p.winner === comparison.tools[1]).length
  const ties = comparison.comparison_points.filter(p => p.winner === 'tie').length

  return (
    <Layout
      title={comparison.title}
      description={comparison.meta_description}
    >
      {/* Breadcrumb */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li><Link href="/" className="hover:text-primary-600">Home</Link></li>
          <li>/</li>
          <li><Link href="/compare/" className="hover:text-primary-600">Compare</Link></li>
          <li>/</li>
          <li className="text-gray-900 font-medium">{tool1.name} vs {tool2.name}</li>
        </ol>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-center">
            {comparison.title}
          </h1>

          {/* Score Summary */}
          <div className="flex items-center justify-center space-x-8 md:space-x-16">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{tool1.name}</p>
              <div className="flex items-center justify-center mt-2">
                <StarRating rating={tool1.rating} size="lg" />
                <span className="ml-2 font-bold">{tool1.rating}</span>
              </div>
              <p className="text-primary-600 font-bold mt-2">{tool1Wins} wins</p>
            </div>
            <div className="text-center">
              <span className="text-3xl font-bold text-gray-400">VS</span>
              {ties > 0 && <p className="text-sm text-gray-500 mt-1">{ties} tie{ties > 1 ? 's' : ''}</p>}
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{tool2.name}</p>
              <div className="flex items-center justify-center mt-2">
                <StarRating rating={tool2.rating} size="lg" />
                <span className="ml-2 font-bold">{tool2.rating}</span>
              </div>
              <p className="text-primary-600 font-bold mt-2">{tool2Wins} wins</p>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-12">
        <AffiliateDisclosure />

        {/* Verdict */}
        <section className="bg-green-50 border border-green-200 rounded-xl p-6 md:p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-3">Our Verdict</h2>
          <p className="text-gray-700 text-lg">{comparison.verdict}</p>
        </section>

        {/* Comparison Table */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Feature-by-Feature Comparison</h2>
          <div className="card p-0 overflow-hidden">
            <ComparisonTable comparison={comparison} tool1={tool1} tool2={tool2} />
          </div>
        </section>

        {/* Detailed Notes */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Detailed Analysis</h2>
          <div className="space-y-4">
            {comparison.comparison_points.map((point, idx) => (
              <div key={idx} className="card">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-gray-900">{point.feature}</h3>
                  {point.winner === 'tie' ? (
                    <span className="badge bg-gray-100 text-gray-700">Tie</span>
                  ) : (
                    <span className="badge bg-green-100 text-green-700">
                      Winner: {point.winner === comparison.tools[0] ? tool1.name : tool2.name}
                    </span>
                  )}
                </div>
                <p className="text-gray-600">{point.notes}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Pricing Comparison */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Pricing Comparison</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[tool1, tool2].map(tool => (
              <div key={tool.slug} className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-4">{tool.name} Pricing</h3>
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 text-sm font-medium text-gray-500">Plan</th>
                      <th className="text-right py-2 text-sm font-medium text-gray-500">Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tool.pricing.plans.map(plan => (
                      <tr key={plan.name} className="border-b last:border-0">
                        <td className="py-2 font-medium text-gray-900">{plan.name}</td>
                        <td className="py-2 text-right font-bold text-gray-900">
                          {plan.price === 0 ? 'Free' : plan.price === null ? 'Custom' : `$${plan.price}/mo`}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <AffiliateLink
                  href={tool.affiliateUrlWithUtm}
                  tool={tool.slug}
                  className="btn-primary w-full justify-center mt-4"
                >
                  Try {tool.name} &rarr;
                </AffiliateLink>
              </div>
            ))}
          </div>
        </section>

        {/* Individual Reviews */}
        <section className="flex flex-col sm:flex-row gap-4">
          <Link href={`/tools/${tool1.slug}/`} className="btn-secondary flex-1 justify-center">
            Full {tool1.name} Review &rarr;
          </Link>
          <Link href={`/tools/${tool2.slug}/`} className="btn-secondary flex-1 justify-center">
            Full {tool2.name} Review &rarr;
          </Link>
        </section>
      </div>

      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": comparison.title,
            "description": comparison.meta_description,
            "datePublished": "2026-02-06",
            "dateModified": "2026-02-06"
          })
        }}
      />
    </Layout>
  )
}

export async function getStaticPaths() {
  const comparisons = getAllComparisons()
  return {
    paths: comparisons.map(c => ({ params: { slug: c.slug } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const comparison = getComparisonBySlug(params.slug)
  const tool1 = getToolBySlug(comparison.tools[0])
  const tool2 = getToolBySlug(comparison.tools[1])

  // Pre-compute affiliate URLs with UTM tracking
  const tool1WithUtm = { ...tool1, affiliateUrlWithUtm: getAffiliateUrl(tool1.slug, 'comparison') }
  const tool2WithUtm = { ...tool2, affiliateUrlWithUtm: getAffiliateUrl(tool2.slug, 'comparison') }

  return {
    props: { comparison, tool1: tool1WithUtm, tool2: tool2WithUtm },
  }
}
