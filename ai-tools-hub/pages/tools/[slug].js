import { useState, useEffect } from 'react'
import Layout from '../../components/Layout'
import StarRating from '../../components/StarRating'
import AffiliateLink, { AffiliateDisclosure, trackAffiliateClick } from '../../components/AffiliateLink'
import TLDRBox from '../../components/TLDRBox'
import FAQAccordion from '../../components/FAQAccordion'
import Breadcrumbs from '../../components/Breadcrumbs'
import AdSlot from '../../components/AdSlot'
import Link from 'next/link'
import { getAllTools, getToolBySlug, getToolsByCategory, formatPrice, getAllComparisons, getAffiliateUrl, getAlternativesForTool } from '../../lib/tools'

const SITE_URL = 'https://pilottools.ai'

export default function ToolPage({ tool, relatedComparisons, relatedTools, alternatives }) {
  if (!tool) return null

  const [showStickyCTA, setShowStickyCTA] = useState(false)

  useEffect(() => {
    const handleScroll = () => setShowStickyCTA(window.scrollY > 400)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const affiliateUrl = tool.affiliateUrlWithUtm
  const canonicalUrl = `${SITE_URL}/tools/${tool.slug}/`
  const primaryCTA = tool.pricing.free_tier ? `Start ${tool.name} Free Today` : `See ${tool.name} Pricing & Plans`

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
        "author": { "@type": "Organization", "name": "PilotTools" },
        "datePublished": "2026-02-06",
        "dateModified": tool.updated_date || "2026-03-18",
        "reviewRating": { "@type": "Rating", "ratingValue": tool.rating, "bestRating": 5 },
        "reviewBody": `${tool.name} review: ${tool.tagline}. ${tool.description}`
      }
    },
    ...(tool.faqs ? [{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": tool.faqs.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    }] : [])
  ]

  return (
    <Layout
      title={`${tool.name} Review 2026: Pricing, Features & Alternatives`}
      description={`${tool.name} review: ${tool.tagline}. Compare pricing, features, pros and cons. Is ${tool.name} worth it in 2026?`}
      canonical={canonicalUrl}
      ogType="article"
      structuredData={structuredData}
    >
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: tool.category.charAt(0).toUpperCase() + tool.category.slice(1), href: `/category/${tool.category}/` },
        { label: tool.name }
      ]} />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 md:p-12">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center space-x-4 mb-3">
                {/* Tool logo */}
                {tool.website && (
                  <img
                    src={`https://www.google.com/s2/favicons?domain=${new URL(tool.website).hostname}&sz=64`}
                    alt={`${tool.name} logo`}
                    width={48}
                    height={48}
                    className="w-12 h-12 rounded-xl bg-dark-surface-hover p-1"
                  />
                )}
                <h1 className="text-3xl md:text-4xl font-bold text-dt">{tool.name}</h1>
                {tool.pricing.free_tier && <span className="badge-green">Free Tier</span>}
              </div>
              <p className="text-lg text-dt-muted mb-2">{tool.tagline}</p>
              <p className="text-sm text-dt-muted mt-1">Last updated: {tool.updated_date || 'March 2026'}</p>
              <div className="flex items-center space-x-3 mt-3">
                <StarRating rating={tool.rating} size="lg" />
                <span className="text-lg font-bold text-dt">{tool.rating}/5</span>
                <span className="text-dt-muted">Expert reviewed</span>
              </div>
            </div>
            <div className="mt-6 md:mt-0 flex flex-col items-start md:items-end space-y-3">
              <div className="text-right">
                <span className="text-sm text-dt-muted">Starting at</span>
                <p className="text-3xl font-bold text-dt">{formatPrice(tool.pricing.starting_price)}</p>
              </div>
              <AffiliateLink href={affiliateUrl} tool={tool.slug} className="btn-primary" placement="hero_cta">
                {primaryCTA} &rarr;
              </AffiliateLink>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <AffiliateDisclosure />

        {/* TL;DR */}
        {tool.tldr && (
          <TLDRBox
            rating={tool.rating}
            verdict={tool.tldr}
            bestFor={tool.best_for?.slice(0, 2).join(', ')}
            price={formatPrice(tool.pricing.starting_price)}
            ctaUrl={affiliateUrl}
            ctaText={tool.pricing.free_tier ? `Try ${tool.name} Free` : `See ${tool.name} Plans`}
          />
        )}

        <AdSlot position="header" />

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            <section>
              <h2 className="text-2xl font-bold text-dt mb-4">Overview</h2>
              <div className="prose prose-lg max-w-none"><p>{tool.description}</p></div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-dt mb-4">Key Features</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {tool.features.map(feature => (
                  <div key={feature} className="flex items-center space-x-2 p-3 bg-dark-surface border border-dark-border rounded-lg">
                    <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-dt-muted">{feature}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="grid md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-2xl font-bold text-dt mb-4">Pros</h2>
                <ul className="space-y-3">
                  {tool.pros.map(pro => (
                    <li key={pro} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-dt-muted">{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-dt mb-4">Cons</h2>
                <ul className="space-y-3">
                  {tool.cons.map(con => (
                    <li key={con} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="text-dt-muted">{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            <AdSlot position="mid-content" />

            {/* Mid-content CTA */}
            <section className="bg-dark-surface border border-accent/20 rounded-xl p-6 text-center">
              <p className="text-lg font-semibold text-dt mb-2">Ready to try {tool.name}?</p>
              <p className="text-dt-muted mb-4 text-sm">
                {tool.pricing.free_tier
                  ? `Get started with ${tool.name}'s free tier \u2014 no credit card required.`
                  : `See all ${tool.name} plans and find the right fit for your needs.`}
              </p>
              <AffiliateLink
                href={affiliateUrl}
                tool={tool.slug}
                className="btn-primary"
                placement="mid_content_cta"
              >
                {primaryCTA} &rarr;
              </AffiliateLink>
            </section>

            {/* Pricing */}
            <section>
              <h2 className="text-2xl font-bold text-dt mb-4">{tool.name} Pricing</h2>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {tool.pricing.plans.map((plan, idx) => (
                  <div key={plan.name} className={`card ${idx === 1 ? 'border-accent ring-2 ring-accent/20' : ''}`}>
                    {idx === 1 && <span className="badge-blue text-xs mb-2">Most Popular</span>}
                    <h3 className="font-bold text-lg text-dt">{plan.name}</h3>
                    <p className="text-2xl font-bold text-dt my-2">
                      {plan.price === 0 ? 'Free' : plan.price === null ? 'Custom' : `$${plan.price}/mo`}
                    </p>
                    <ul className="space-y-2 mt-4">
                      {plan.features.map(f => (
                        <li key={f} className="flex items-center space-x-2 text-sm text-dt-muted">
                          <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-center">
                <Link href={`/pricing/${tool.slug}/`} className="text-accent hover:text-cyan-300 text-sm font-medium transition-colors">
                  See full pricing breakdown &rarr;
                </Link>
              </div>
            </section>

            {/* Best For */}
            <section>
              <h2 className="text-2xl font-bold text-dt mb-4">Best For</h2>
              <div className="flex flex-wrap gap-2">
                {tool.best_for.map(use => (
                  <span key={use} className="badge-purple">{use}</span>
                ))}
              </div>
            </section>

            {/* FAQ */}
            {tool.faqs && tool.faqs.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-dt mb-4">Frequently Asked Questions</h2>
                <FAQAccordion faqs={tool.faqs} />
              </section>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="card sticky top-20">
              <h3 className="font-bold text-lg text-dt mb-4">Quick Info</h3>
              <dl className="space-y-3">
                {[
                  ['Company', tool.company],
                  ['Founded', tool.founded],
                  ['Free Tier', tool.pricing.free_tier ? 'Yes' : 'No'],
                  ['Starting Price', formatPrice(tool.pricing.starting_price)],
                  ['Rating', `${tool.rating}/5`],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <dt className="text-dt-muted">{label}</dt>
                    <dd className="font-medium text-dt">{value}</dd>
                  </div>
                ))}
              </dl>
              <AffiliateLink href={affiliateUrl} tool={tool.slug} className="btn-primary w-full justify-center mt-6" placement="sidebar_cta">
                {primaryCTA} &rarr;
              </AffiliateLink>
              <a href={tool.website} target="_blank" rel="noopener noreferrer" className="btn-secondary w-full justify-center mt-2 text-sm">
                Visit Website
              </a>
            </div>

            {relatedComparisons.length > 0 && (
              <div className="card">
                <h3 className="font-bold text-lg text-dt mb-4">Comparisons</h3>
                <ul className="space-y-3">
                  {relatedComparisons.map(comp => (
                    <li key={comp.slug}>
                      <Link href={`/compare/${comp.slug}/`} className="text-accent hover:text-cyan-300 text-sm font-medium transition-colors">
                        {comp.title.split(':')[0]} &rarr;
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Alternatives sidebar link */}
            {alternatives.length > 0 && (
              <div className="card">
                <h3 className="font-bold text-lg text-dt mb-4">Alternatives</h3>
                <ul className="space-y-3">
                  {alternatives.slice(0, 3).map(alt => (
                    <li key={alt.slug}>
                      <Link href={`/tools/${alt.slug}/`} className="text-accent hover:text-cyan-300 text-sm font-medium transition-colors">
                        {alt.name} &rarr;
                      </Link>
                      <p className="text-xs text-dt-muted">{alt.reason}</p>
                    </li>
                  ))}
                </ul>
                <Link href={`/alternatives/${tool.slug}/`} className="text-accent hover:text-cyan-300 text-xs font-medium mt-3 inline-block transition-colors">
                  See all alternatives &rarr;
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Related Tools */}
      {relatedTools.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <h2 className="text-2xl font-bold text-dt mb-6">Related Tools You Might Like</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedTools.map(related => (
              <Link key={related.slug} href={`/tools/${related.slug}/`} className="card hover:border-accent/30">
                <h3 className="font-bold text-dt">{related.name}</h3>
                <p className="text-sm text-dt-muted mt-1 line-clamp-2">{related.tagline}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-sm font-medium text-accent">{related.rating}/5</span>
                  <span className="text-sm text-dt-muted">{formatPrice(related.pricing.starting_price)}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      <AdSlot position="footer" />

      {/* Sticky Mobile CTA */}
      {showStickyCTA && (
        <div className="fixed bottom-0 left-0 right-0 z-50 p-3 bg-dark-surface border-t border-dark-border shadow-lg md:hidden">
          <a href={affiliateUrl} target="_blank" rel="noopener noreferrer sponsored"
             className="block w-full py-3 px-6 text-center text-dark-bg font-bold rounded-lg bg-accent hover:bg-cyan-300 transition-all"
             onClick={() => trackAffiliateClick(tool.name, 'sticky_mobile')}>
            {tool.pricing.free_tier ? `Try ${tool.name} Free \u2192` : `See ${tool.name} Plans \u2192`}
          </a>
        </div>
      )}
    </Layout>
  )
}

export async function getStaticPaths() {
  return {
    paths: getAllTools().map(t => ({ params: { slug: t.slug } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const tool = getToolBySlug(params.slug)
  const relatedComparisons = getAllComparisons().filter(c => c.tools.includes(params.slug))
  const affiliateUrlWithUtm = getAffiliateUrl(params.slug, 'review')
  const alternatives = getAlternativesForTool(params.slug)
  const relatedTools = getToolsByCategory(tool.category)
    .filter(t => t.slug !== params.slug)
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 3)

  return {
    props: {
      tool: { ...tool, affiliateUrlWithUtm },
      relatedComparisons,
      relatedTools,
      alternatives,
    },
  }
}
