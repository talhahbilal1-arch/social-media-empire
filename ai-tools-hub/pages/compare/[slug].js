import Head from 'next/head'
import Layout from '../../components/Layout'
import ComparisonTable from '../../components/ComparisonTable'
import StarRating from '../../components/StarRating'
import AffiliateLink, { AffiliateDisclosure } from '../../components/AffiliateLink'
import TLDRBox from '../../components/TLDRBox'
import FAQAccordion from '../../components/FAQAccordion'
import Breadcrumbs from '../../components/Breadcrumbs'
import AdSlot from '../../components/AdSlot'
import Link from 'next/link'
import { getAllComparisons, getComparisonBySlug, getToolBySlug, formatPrice, getAffiliateUrl } from '../../lib/tools'

const SITE_URL = 'https://pilottools.ai'

function generateFAQs(comparison, tool1, tool2) {
  return [
    { question: `Is ${tool1.name} better than ${tool2.name}?`, answer: comparison.verdict || `${tool1.name} excels at ${(tool1.best_for || []).slice(0, 2).join(' and ')}, while ${tool2.name} is better for ${(tool2.best_for || []).slice(0, 2).join(' and ')}.` },
    { question: `Which is cheaper, ${tool1.name} or ${tool2.name}?`, answer: `${tool1.name} starts at ${formatPrice(tool1.pricing.starting_price)}, while ${tool2.name} starts at ${formatPrice(tool2.pricing.starting_price)}. ${tool1.pricing.free_tier && tool2.pricing.free_tier ? 'Both offer free tiers.' : tool1.pricing.free_tier ? `${tool1.name} offers a free tier.` : tool2.pricing.free_tier ? `${tool2.name} offers a free tier.` : 'Neither offers a free tier.'}` },
    { question: `Can I use ${tool1.name} and ${tool2.name} together?`, answer: `Yes, many professionals use both. ${tool1.name} is preferred for ${(tool1.best_for || ['general tasks']).slice(0, 1).join('')}, while ${tool2.name} shines at ${(tool2.best_for || ['general tasks']).slice(0, 1).join('')}.` },
    { question: `Which has better ratings, ${tool1.name} or ${tool2.name}?`, answer: `${tool1.name} has ${tool1.rating}/5 (${tool1.review_count.toLocaleString()} reviews), ${tool2.name} has ${tool2.rating}/5 (${tool2.review_count.toLocaleString()} reviews). ${tool1.rating > tool2.rating ? `${tool1.name} is rated higher.` : tool2.rating > tool1.rating ? `${tool2.name} is rated higher.` : 'Both are rated equally.'}` },
  ]
}

export default function ComparisonPage({ comparison, tool1, tool2 }) {
  if (!comparison || !tool1 || !tool2) return null

  const tool1Wins = comparison.comparison_points.filter(p => p.winner === comparison.tools[0]).length
  const tool2Wins = comparison.comparison_points.filter(p => p.winner === comparison.tools[1]).length
  const ties = comparison.comparison_points.filter(p => p.winner === 'tie').length
  const canonicalUrl = `${SITE_URL}/compare/${comparison.slug}/`
  const faqItems = generateFAQs(comparison, tool1, tool2)

  const structuredData = [
    {
      "@context": "https://schema.org", "@type": "Article",
      "headline": comparison.title,
      "description": comparison.meta_description,
      "datePublished": "2026-02-06", "dateModified": "2026-03-18",
      "author": { "@type": "Organization", "name": "PilotTools" },
      "publisher": { "@type": "Organization", "name": "PilotTools" }
    }
  ]

  // FAQ schema - safe: build-time data from getStaticProps, no user input
  const faqSchema = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqItems.map(f => ({
      "@type": "Question", "name": f.question,
      "acceptedAnswer": { "@type": "Answer", "text": f.answer }
    }))
  })

  const verdictText = `${tool1Wins > tool2Wins ? tool1.name : tool2.name} wins ${Math.max(tool1Wins, tool2Wins)}-${Math.min(tool1Wins, tool2Wins)}${ties > 0 ? ` (${ties} tie${ties > 1 ? 's' : ''})` : ''}. ${comparison.verdict}`

  return (
    <Layout
      title={`${tool1.name} vs ${tool2.name} (2026): Which Is Better?`}
      description={comparison.meta_description}
      canonical={canonicalUrl}
      ogType="article"
      structuredData={structuredData}
    >
      <Head>
        {/* FAQ JSON-LD - safe: derived from build-time tool data only */}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: faqSchema }} />
      </Head>

      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Compare', href: '/compare/' },
        { label: `${tool1.name} vs ${tool2.name}` }
      ]} />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-2 text-center">{comparison.title}</h1>
          <p className="text-sm text-dt-muted text-center mb-6">Last updated: March 2026</p>
          <div className="flex items-center justify-center space-x-8 md:space-x-16">
            <div className="text-center">
              <p className="text-2xl font-bold text-dt">{tool1.name}</p>
              <div className="flex items-center justify-center mt-2">
                <StarRating rating={tool1.rating} size="lg" />
                <span className="ml-2 font-bold text-dt">{tool1.rating}</span>
              </div>
              <p className="text-accent font-bold mt-2">{tool1Wins} wins</p>
            </div>
            <div className="text-center">
              <span className="text-3xl font-bold text-dt-muted">VS</span>
              {ties > 0 && <p className="text-sm text-dt-muted mt-1">{ties} tie{ties > 1 ? 's' : ''}</p>}
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-dt">{tool2.name}</p>
              <div className="flex items-center justify-center mt-2">
                <StarRating rating={tool2.rating} size="lg" />
                <span className="ml-2 font-bold text-dt">{tool2.rating}</span>
              </div>
              <p className="text-accent font-bold mt-2">{tool2Wins} wins</p>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-12">
        <AffiliateDisclosure />

        <TLDRBox
          verdict={verdictText}
          ctaUrl={tool1.affiliateUrlWithUtm}
          ctaText={`Try ${tool1Wins >= tool2Wins ? tool1.name : tool2.name}`}
        />

        <AdSlot position="header" />

        <section>
          <h2 className="text-2xl font-bold text-dt mb-6">Feature-by-Feature Comparison</h2>
          <div className="card p-0 overflow-hidden">
            <ComparisonTable comparison={comparison} tool1={tool1} tool2={tool2} />
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-dt mb-6">Detailed Analysis</h2>
          <div className="space-y-4">
            {comparison.comparison_points.map((point, idx) => (
              <div key={idx} className="card">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-bold text-dt">{point.feature}</h3>
                  {point.winner === 'tie' ? (
                    <span className="badge bg-dark-surface-hover text-dt-muted border border-dark-border">Tie</span>
                  ) : (
                    <span className="badge bg-green-900/30 text-green-400 border border-green-800/30">
                      Winner: {point.winner === comparison.tools[0] ? tool1.name : tool2.name}
                    </span>
                  )}
                </div>
                <p className="text-dt-muted">{point.notes}</p>
              </div>
            ))}
          </div>
        </section>

        <AdSlot position="mid-content" />

        <section>
          <h2 className="text-2xl font-bold text-dt mb-6">Pricing Comparison</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[tool1, tool2].map(tool => (
              <div key={tool.slug} className="card">
                <h3 className="text-xl font-bold text-dt mb-4">{tool.name} Pricing</h3>
                <table className="w-full">
                  <thead><tr className="border-b border-dark-border"><th className="text-left py-2 text-sm font-medium text-dt-muted">Plan</th><th className="text-right py-2 text-sm font-medium text-dt-muted">Price</th></tr></thead>
                  <tbody>
                    {tool.pricing.plans.map(plan => (
                      <tr key={plan.name} className="border-b border-dark-border last:border-0">
                        <td className="py-2 font-medium text-dt">{plan.name}</td>
                        <td className="py-2 text-right font-bold text-dt">{plan.price === 0 ? 'Free' : plan.price === null ? 'Custom' : `$${plan.price}/mo`}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <AffiliateLink href={tool.affiliateUrlWithUtm} tool={tool.slug} className="btn-primary w-full justify-center mt-4" placement="comparison_pricing">
                  {tool.pricing.free_tier ? `Start ${tool.name} Free \u2192` : `See ${tool.name} Plans \u2192`}
                </AffiliateLink>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-dt mb-6">Frequently Asked Questions</h2>
          <FAQAccordion faqs={faqItems} />
        </section>

        <section className="flex flex-col sm:flex-row gap-4">
          <Link href={`/tools/${tool1.slug}/`} className="btn-secondary flex-1 justify-center">Full {tool1.name} Review &rarr;</Link>
          <Link href={`/tools/${tool2.slug}/`} className="btn-secondary flex-1 justify-center">Full {tool2.name} Review &rarr;</Link>
        </section>
      </div>
    </Layout>
  )
}

export async function getStaticPaths() {
  return { paths: getAllComparisons().map(c => ({ params: { slug: c.slug } })), fallback: false }
}

export async function getStaticProps({ params }) {
  const comparison = getComparisonBySlug(params.slug)
  const tool1 = getToolBySlug(comparison.tools[0])
  const tool2 = getToolBySlug(comparison.tools[1])
  return {
    props: {
      comparison,
      tool1: { ...tool1, affiliateUrlWithUtm: getAffiliateUrl(tool1.slug, 'comparison') },
      tool2: { ...tool2, affiliateUrlWithUtm: getAffiliateUrl(tool2.slug, 'comparison') },
    },
  }
}
