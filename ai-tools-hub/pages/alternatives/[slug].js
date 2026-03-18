import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import AdSlot from '../../components/AdSlot'
import AffiliateLink from '../../components/AffiliateLink'
import StarRating from '../../components/StarRating'
import Link from 'next/link'
import { getAllTools, getToolBySlug, formatPrice, getAffiliateUrl, getAlternativesForTool } from '../../lib/tools'

export default function AlternativesPage({ tool, alternatives, affiliateUrl }) {
  if (!tool) return null

  return (
    <Layout
      title={`${alternatives.length + 1} Best ${tool.name} Alternatives in 2026`}
      description={`Looking for ${tool.name} alternatives? Compare the top ${alternatives.length} alternatives with pricing, features, and ratings.`}
      canonical={`https://pilottools.ai/alternatives/${tool.slug}/`}
    >
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: tool.name, href: `/tools/${tool.slug}/` },
        { label: 'Alternatives' }
      ]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">Best {tool.name} Alternatives in 2026</h1>
          <p className="text-lg text-dt-muted">
            {tool.name} rated {tool.rating}/5 at {formatPrice(tool.pricing.starting_price)}. Here are the top alternatives.
          </p>
        </div>

        {/* Original tool card */}
        <div className="card border-accent/20">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-xl font-bold text-dt">{tool.name}</h2>
              <p className="text-sm text-dt-muted">{tool.tagline}</p>
            </div>
            <span className="badge-blue">Original</span>
          </div>
          <div className="flex items-center gap-4 mb-4">
            <StarRating rating={tool.rating} />
            <span className="text-dt font-medium">{tool.rating}/5</span>
            <span className="text-dt-muted">{formatPrice(tool.pricing.starting_price)}</span>
          </div>
          <AffiliateLink href={affiliateUrl} tool={tool.slug} className="btn-primary text-sm" placement="alternatives_original">
            Try {tool.name} &rarr;
          </AffiliateLink>
        </div>

        <AdSlot position="mid-content" />

        {/* Alternatives */}
        {alternatives.map((alt, idx) => (
          <div key={alt.slug} className="card">
            <div className="flex items-center justify-between mb-3">
              <div>
                <span className="text-accent text-sm font-bold">#{idx + 1} Alternative</span>
                <h2 className="text-xl font-bold text-dt">{alt.name}</h2>
                <p className="text-sm text-dt-muted">{alt.tagline}</p>
              </div>
            </div>
            <p className="text-dt-muted mb-4">{alt.reason}</p>
            <div className="flex items-center gap-4 mb-4">
              <StarRating rating={alt.rating} />
              <span className="text-dt font-medium">{alt.rating}/5</span>
              <span className="text-dt-muted">{formatPrice(alt.pricing.starting_price)}</span>
              {alt.pricing.free_tier && <span className="badge-green text-xs">Free tier</span>}
            </div>
            <div className="flex gap-3">
              <Link href={`/tools/${alt.slug}/`} className="btn-secondary text-sm">Full Review</Link>
              <AffiliateLink href={getAffiliateUrl(alt.slug, 'alternatives')} tool={alt.slug} className="btn-primary text-sm" placement="alternatives_cta">
                Try {alt.name} &rarr;
              </AffiliateLink>
            </div>
          </div>
        ))}

        <div className="text-center">
          <Link href={`/tools/${tool.slug}/`} className="btn-secondary">Back to {tool.name} Review &rarr;</Link>
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
      alternatives: getAlternativesForTool(params.slug),
      affiliateUrl: getAffiliateUrl(params.slug, 'alternatives'),
    },
  }
}
