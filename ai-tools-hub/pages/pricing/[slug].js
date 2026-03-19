import Layout from '../../components/Layout'
import PricingTable from '../../components/PricingTable'
import FAQAccordion from '../../components/FAQAccordion'
import Breadcrumbs from '../../components/Breadcrumbs'
import AffiliateLink from '../../components/AffiliateLink'
import AdSlot from '../../components/AdSlot'
import Link from 'next/link'
import { getAllTools, getToolBySlug, formatPrice, getAffiliateUrl, getAlternativesForTool } from '../../lib/tools'

export default function PricingPage({ tool, affiliateUrl, alternatives }) {
  if (!tool) return null

  const faqs = [
    { question: `Is ${tool.name} free?`, answer: tool.pricing.free_tier ? `Yes, ${tool.name} offers a free tier with limited features. Paid plans start at ${formatPrice(tool.pricing.starting_price)}.` : `No, ${tool.name} does not have a free tier. Plans start at ${formatPrice(tool.pricing.starting_price)}.` },
    { question: `What is the best ${tool.name} plan?`, answer: `For most users, the ${tool.pricing.plans.length > 1 ? tool.pricing.plans[1].name : tool.pricing.plans[0].name} plan offers the best value. It includes ${tool.pricing.plans.length > 1 ? tool.pricing.plans[1].features.slice(0, 2).join(' and ') : 'core features'}.` },
    { question: `Is ${tool.name} worth the price?`, answer: `With a rating of ${tool.rating}/5, ${tool.name} is ${tool.rating >= 4.5 ? 'highly rated and generally considered excellent value' : 'well-regarded'} for ${tool.best_for.slice(0, 2).join(' and ')}.` },
  ]

  return (
    <Layout
      title={`${tool.name} Pricing 2026: Plans, Costs & Best Value`}
      description={`${tool.name} pricing breakdown for 2026. Compare all plans, features, and costs. ${tool.pricing.free_tier ? 'Free tier available.' : `Starting at ${formatPrice(tool.pricing.starting_price)}.`}`}
      canonical={`https://pilottools.ai/pricing/${tool.slug}/`}
    >
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Pricing', href: '/pricing/' },
        { label: `${tool.name} Pricing` }
      ]} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">{tool.name} Pricing 2026</h1>
          <p className="text-lg text-dt-muted">
            {tool.pricing.free_tier ? `Free tier available. Paid plans from ${formatPrice(tool.pricing.starting_price)}.` : `Plans starting at ${formatPrice(tool.pricing.starting_price)}.`}
          </p>
        </div>

        <PricingTable
          plans={tool.pricing.plans}
          highlightPlan={tool.pricing.plans.length > 1 ? tool.pricing.plans[1].name : null}
          affiliateUrl={affiliateUrl}
          toolSlug={tool.slug}
        />

        <AdSlot position="mid-content" />

        {/* Is it worth the price? */}
        <section className="card">
          <h2 className="text-2xl font-bold text-dt mb-4">Is {tool.name} Worth the Price?</h2>
          <p className="text-dt-muted mb-4">
            {tool.name} has a {tool.rating}/5 rating based on our expert testing. It&apos;s best for {tool.best_for.slice(0, 3).join(', ')}.
            {tool.pricing.free_tier ? ` The free tier lets you try it risk-free before committing to a paid plan.` : ''}
          </p>
          <AffiliateLink href={affiliateUrl} tool={tool.slug} className="btn-primary" placement="pricing_verdict">
            {tool.pricing.free_tier ? 'Start Free Today' : 'See Plans'} &rarr;
          </AffiliateLink>
        </section>

        {/* Alternatives by price */}
        {alternatives.length > 0 && (
          <section>
            <h2 className="text-2xl font-bold text-dt mb-4">Alternatives to Consider</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {alternatives.map(alt => (
                <Link key={alt.slug} href={`/tools/${alt.slug}/`} className="card hover:border-accent/30">
                  <h3 className="font-bold text-dt">{alt.name}</h3>
                  <p className="text-sm text-dt-muted mt-1">{alt.reason}</p>
                  <div className="flex justify-between mt-3 text-sm">
                    <span className="text-accent">{alt.rating}/5</span>
                    <span className="text-dt-muted">{formatPrice(alt.pricing.starting_price)}</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section>
          <h2 className="text-2xl font-bold text-dt mb-4">FAQ</h2>
          <FAQAccordion faqs={faqs} />
        </section>

        <div className="text-center">
          <Link href={`/tools/${tool.slug}/`} className="btn-secondary">Read Full {tool.name} Review &rarr;</Link>
        </div>
      </div>
    </Layout>
  )
}

export async function getStaticPaths() {
  return { paths: getAllTools().map(t => ({ params: { slug: t.slug } })), fallback: false }
}

export async function getStaticProps({ params }) {
  const tool = getToolBySlug(params.slug)
  return {
    props: {
      tool,
      affiliateUrl: getAffiliateUrl(params.slug, 'pricing'),
      alternatives: getAlternativesForTool(params.slug),
    },
  }
}
