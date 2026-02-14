import Layout from '../../components/Layout'
import StarRating from '../../components/StarRating'
import AffiliateLink, { AffiliateDisclosure } from '../../components/AffiliateLink'
import NewsletterSignup from '../../components/NewsletterSignup'
import Link from 'next/link'
import { getAllTools, getToolBySlug, getToolsByCategory, formatPrice, getAllComparisons, getAffiliateUrl } from '../../lib/tools'

const SITE_URL = 'https://toolpilot-hub.netlify.app'

export default function ToolPage({ tool, relatedComparisons, relatedTools }) {
  if (!tool) return null

  const canonicalUrl = `${SITE_URL}/tools/${tool.slug}/`

  // Combined structured data: SoftwareApplication + Review + BreadcrumbList
  const structuredData = [
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": tool.name,
      "description": tool.description,
      "applicationCategory": "AI Tool",
      "operatingSystem": "Web",
      "url": tool.website,
      "offers": {
        "@type": "AggregateOffer",
        "lowPrice": tool.pricing.starting_price || 0,
        "priceCurrency": "USD",
        "offerCount": tool.pricing.plans.length
      },
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": tool.rating,
        "reviewCount": tool.review_count,
        "bestRating": 5
      },
      "review": {
        "@type": "Review",
        "author": { "@type": "Organization", "name": "ToolPilot" },
        "datePublished": "2026-02-06",
        "reviewRating": {
          "@type": "Rating",
          "ratingValue": tool.rating,
          "bestRating": 5
        },
        "reviewBody": `${tool.name} review: ${tool.tagline}. ${tool.description}`
      }
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL },
        { "@type": "ListItem", "position": 2, "name": tool.category.charAt(0).toUpperCase() + tool.category.slice(1), "item": `${SITE_URL}/category/${tool.category}/` },
        { "@type": "ListItem", "position": 3, "name": tool.name }
      ]
    }
  ]

  return (
    <Layout
      title={`${tool.name} Review 2026: Pricing, Features & Alternatives`}
      description={`${tool.name} review: ${tool.tagline}. Compare pricing, features, pros and cons. Is ${tool.name} worth it in 2026?`}
      canonical={canonicalUrl}
      ogType="article"
      structuredData={structuredData}
    >
      {/* Breadcrumb */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li><Link href="/" className="hover:text-primary-600">Home</Link></li>
          <li>/</li>
          <li><Link href={`/category/${tool.category}/`} className="hover:text-primary-600">{tool.category}</Link></li>
          <li>/</li>
          <li className="text-gray-900 font-medium">{tool.name}</li>
        </ol>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl p-8 md:p-12">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-3">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900">{tool.name}</h1>
                {tool.pricing.free_tier && <span className="badge-green">Free Tier</span>}
              </div>
              <p className="text-lg text-gray-600 mb-4">{tool.tagline}</p>
              <div className="flex items-center space-x-3">
                <StarRating rating={tool.rating} size="lg" />
                <span className="text-lg font-bold text-gray-900">{tool.rating}/5</span>
                <span className="text-gray-500">({tool.review_count.toLocaleString()} reviews)</span>
              </div>
            </div>
            <div className="mt-6 md:mt-0 flex flex-col items-start md:items-end space-y-3">
              <div className="text-right">
                <span className="text-sm text-gray-500">Starting at</span>
                <p className="text-3xl font-bold text-gray-900">{formatPrice(tool.pricing.starting_price)}</p>
              </div>
              <AffiliateLink
                href={tool.affiliateUrlWithUtm}
                tool={tool.slug}
                className="btn-primary"
              >
                Try {tool.name} Free &rarr;
              </AffiliateLink>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <AffiliateDisclosure />
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Overview */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Overview</h2>
              <div className="prose prose-lg max-w-none">
                <p>{tool.description}</p>
              </div>
            </section>

            {/* Key Features */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Key Features</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {tool.features.map(feature => (
                  <div key={feature} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                    <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Pros and Cons */}
            <section className="grid md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Pros</h2>
                <ul className="space-y-3">
                  {tool.pros.map(pro => (
                    <li key={pro} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-gray-700">{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Cons</h2>
                <ul className="space-y-3">
                  {tool.cons.map(con => (
                    <li key={con} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-gray-700">{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* Pricing */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">{tool.name} Pricing</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {tool.pricing.plans.map((plan, idx) => (
                  <div key={plan.name} className={`card ${idx === 1 ? 'border-primary-500 ring-2 ring-primary-200' : ''}`}>
                    {idx === 1 && <span className="badge-blue text-xs mb-2">Most Popular</span>}
                    <h3 className="font-bold text-lg text-gray-900">{plan.name}</h3>
                    <p className="text-2xl font-bold text-gray-900 my-2">
                      {plan.price === 0 ? 'Free' : plan.price === null ? 'Custom' : `$${plan.price}/mo`}
                    </p>
                    <ul className="space-y-2 mt-4">
                      {plan.features.map(f => (
                        <li key={f} className="flex items-center space-x-2 text-sm text-gray-600">
                          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            {/* Best For */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Best For</h2>
              <div className="flex flex-wrap gap-2">
                {tool.best_for.map(use => (
                  <span key={use} className="badge-purple">{use}</span>
                ))}
              </div>
            </section>

            {/* How to Make Money */}
            {tool.money_use_cases && tool.money_use_cases.length > 0 && (
              <section className="bg-green-50 border border-green-200 rounded-xl p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">How to Make Money with {tool.name}</h2>
                <ul className="space-y-3">
                  {tool.money_use_cases.map(useCase => (
                    <li key={useCase} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-gray-700">{useCase}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Free Tier Verdict */}
            {tool.free_tier_verdict && (
              <section className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-2">Free Tier Verdict</h2>
                <p className="text-gray-700">{tool.free_tier_verdict}</p>
              </section>
            )}

            {/* Free Alternative Callout */}
            {!tool.pricing.free_tier && relatedTools.some(t => t.pricing.free_tier) && (
              <section className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-3">Looking for a Free Alternative?</h2>
                <div className="space-y-2">
                  {relatedTools.filter(t => t.pricing.free_tier).slice(0, 2).map(alt => (
                    <Link key={alt.slug} href={`/tools/${alt.slug}/`} className="flex items-center justify-between p-3 bg-white rounded-lg hover:ring-2 hover:ring-amber-300 transition-all">
                      <div>
                        <span className="font-semibold text-gray-900">{alt.name}</span>
                        <span className="text-sm text-gray-500 ml-2">{alt.rating}/5</span>
                      </div>
                      <span className="badge-green text-xs">Free Tier</span>
                    </Link>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info Card */}
            <div className="card sticky top-20">
              <h3 className="font-bold text-lg text-gray-900 mb-4">Quick Info</h3>
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-gray-500">Company</dt>
                  <dd className="font-medium text-gray-900">{tool.company}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Founded</dt>
                  <dd className="font-medium text-gray-900">{tool.founded}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Free Tier</dt>
                  <dd className="font-medium text-gray-900">{tool.pricing.free_tier ? 'Yes' : 'No'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Starting Price</dt>
                  <dd className="font-medium text-gray-900">{formatPrice(tool.pricing.starting_price)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500">Rating</dt>
                  <dd className="font-medium text-gray-900">{tool.rating}/5</dd>
                </div>
              </dl>

              <AffiliateLink
                href={tool.affiliateUrlWithUtm}
                tool={tool.slug}
                className="btn-primary w-full justify-center mt-6"
              >
                Try {tool.name} &rarr;
              </AffiliateLink>

              <a
                href={tool.website}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary w-full justify-center mt-2 text-sm"
              >
                Visit Website
              </a>
            </div>

            {/* Newsletter Signup */}
            <NewsletterSignup variant="sidebar" />

            {/* Related Comparisons */}
            {relatedComparisons.length > 0 && (
              <div className="card">
                <h3 className="font-bold text-lg text-gray-900 mb-4">Comparisons</h3>
                <ul className="space-y-3">
                  {relatedComparisons.map(comp => (
                    <li key={comp.slug}>
                      <Link href={`/compare/${comp.slug}/`} className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                        {comp.title.split(':')[0]} &rarr;
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Related Tools */}
      {relatedTools.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Tools You Might Like</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedTools.map(related => (
              <Link key={related.slug} href={`/tools/${related.slug}/`} className="card hover:border-primary-300">
                <h3 className="font-bold text-gray-900">{related.name}</h3>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">{related.tagline}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-sm font-medium text-primary-600">{related.rating}/5</span>
                  <span className="text-sm text-gray-500">{formatPrice(related.pricing.starting_price)}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </Layout>
  )
}

export async function getStaticPaths() {
  const tools = getAllTools()
  return {
    paths: tools.map(t => ({ params: { slug: t.slug } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const tool = getToolBySlug(params.slug)
  const allComparisons = getAllComparisons()
  const relatedComparisons = allComparisons.filter(c => c.tools.includes(params.slug))

  // Pre-compute affiliate URL with UTM tracking
  const affiliateUrlWithUtm = getAffiliateUrl(params.slug, 'review')

  // Related tools: same category, excluding self, top 3 by rating
  const relatedTools = getToolsByCategory(tool.category)
    .filter(t => t.slug !== params.slug)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 3)

  return {
    props: {
      tool: { ...tool, affiliateUrlWithUtm },
      relatedComparisons,
      relatedTools,
    },
  }
}
