import Layout from '../../components/Layout'
import ToolCard from '../../components/ToolCard'
import Breadcrumbs from '../../components/Breadcrumbs'
import AdSlot from '../../components/AdSlot'
import Link from 'next/link'
import { getAllCategories, getCategoryBySlug, getToolsByCategory, getAllComparisons } from '../../lib/tools'

const SITE_URL = 'https://pilottools.ai'

export default function CategoryPage({ category, tools, relatedComparisons }) {
  if (!category) return null

  const canonicalUrl = `${SITE_URL}/category/${category.slug}/`

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `Best ${category.name} in 2026`,
    'description': category.description,
    'url': canonicalUrl,
    'numberOfItems': tools.length,
  }

  return (
    <Layout
      title={category.meta_title}
      description={category.meta_description}
      canonical={canonicalUrl}
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: category.name }]} />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">Best {category.name} in 2026</h1>
          <p className="text-lg text-dt-muted max-w-3xl">{category.description}</p>
          <p className="mt-4 text-sm text-dt-muted">{tools.length} tools compared | Updated March 2026</p>
        </div>
      </section>

      {/* Tools Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.sort((a, b) => b.rating - a.rating).map((tool, idx) => (
            <ToolCard key={tool.slug} tool={tool} rank={idx + 1} />
          ))}
        </div>
        {tools.length === 0 && (
          <div className="text-center py-12"><p className="text-dt-muted">No tools in this category yet.</p></div>
        )}
      </section>

      <AdSlot position="mid-content" />

      {/* Related Comparisons */}
      {relatedComparisons.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <h2 className="text-2xl font-bold text-dt mb-6">Popular Comparisons in {category.name}</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {relatedComparisons.map(comp => (
              <Link key={comp.slug} href={`/compare/${comp.slug}/`} className="card hover:border-accent/30">
                <div className="flex items-center justify-center space-x-3">
                  <span className="font-bold text-dt">{comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  <span className="text-accent font-bold">VS</span>
                  <span className="font-bold text-dt">{comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* SEO Content */}
      <section className="bg-dark-surface/50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>How We Rank {category.name}</h2>
          <p>
            Our rankings are based on hands-on testing, feature analysis, pricing value,
            user reviews, and real-world performance. We update these rankings regularly
            as tools evolve and new products launch.
          </p>
          <h3>What to Look For in {category.name.replace('AI ', '')}</h3>
          <ul>
            <li><strong>Output quality</strong> &mdash; Does the tool produce professional-grade results?</li>
            <li><strong>Ease of use</strong> &mdash; Can you get started quickly without a steep learning curve?</li>
            <li><strong>Pricing value</strong> &mdash; Does the pricing align with what you get?</li>
            <li><strong>Integration</strong> &mdash; Does it work with your existing tools and workflow?</li>
            <li><strong>Support &amp; updates</strong> &mdash; Is the tool actively maintained and improved?</li>
          </ul>
        </div>
      </section>
    </Layout>
  )
}

export async function getStaticPaths() {
  return { paths: getAllCategories().map(c => ({ params: { slug: c.slug } })), fallback: false }
}

export async function getStaticProps({ params }) {
  const category = getCategoryBySlug(params.slug)
  const tools = getToolsByCategory(params.slug)
  const relatedComparisons = getAllComparisons().filter(c => c.category === params.slug)
  return { props: { category, tools, relatedComparisons } }
}
