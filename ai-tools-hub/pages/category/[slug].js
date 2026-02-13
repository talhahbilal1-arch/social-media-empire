import Layout from '../../components/Layout'
import ToolCard from '../../components/ToolCard'
import Link from 'next/link'
import { getAllCategories, getCategoryBySlug, getToolsByCategory } from '../../lib/tools'

const SITE_URL = 'https://toolpilot-hub.netlify.app'

export default function CategoryPage({ category, tools }) {
  if (!category) return null

  const canonicalUrl = `${SITE_URL}/category/${category.slug}/`
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL },
      { "@type": "ListItem", "position": 2, "name": category.name }
    ]
  }

  return (
    <Layout
      title={category.meta_title}
      description={category.meta_description}
      canonical={canonicalUrl}
      structuredData={structuredData}
    >
      {/* Breadcrumb */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol className="flex items-center space-x-2 text-sm text-gray-500">
          <li><Link href="/" className="hover:text-primary-600">Home</Link></li>
          <li>/</li>
          <li className="text-gray-900 font-medium">{category.name}</li>
        </ol>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-2xl p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Best {category.name} in 2026
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl">
            {category.description}
          </p>
          <p className="mt-4 text-sm text-gray-500">
            {tools.length} tools compared | Updated February 2026
          </p>
        </div>
      </section>

      {/* Tools Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools
            .sort((a, b) => b.rating - a.rating)
            .map((tool, idx) => (
              <ToolCard key={tool.slug} tool={tool} rank={idx + 1} />
            ))}
        </div>

        {tools.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No tools in this category yet. Check back soon!</p>
          </div>
        )}
      </section>

      {/* SEO Content */}
      <section className="bg-gray-50 py-16">
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
            <li><strong>Support & updates</strong> &mdash; Is the tool actively maintained and improved?</li>
          </ul>
        </div>
      </section>
    </Layout>
  )
}

export async function getStaticPaths() {
  const categories = getAllCategories()
  return {
    paths: categories.map(c => ({ params: { slug: c.slug } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const category = getCategoryBySlug(params.slug)
  const tools = getToolsByCategory(params.slug)

  return {
    props: { category, tools },
  }
}
