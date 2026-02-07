import Layout from '../components/Layout'
import ToolCard from '../components/ToolCard'
import Link from 'next/link'
import { getAllTools, getAllCategories, getAllComparisons, getFeaturedTools } from '../lib/tools'

export default function Home({ featuredTools, categories, comparisons, totalTools }) {
  return (
    <Layout>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Find the Perfect AI Tool
          </h1>
          <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Honest reviews and side-by-side comparisons of {totalTools}+ AI tools for writing, coding, design, video, and marketing.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/category/writing/" className="btn-primary bg-white text-primary-700 hover:bg-primary-50">
              AI Writing Tools
            </Link>
            <Link href="/category/coding/" className="btn-primary bg-primary-500 hover:bg-primary-400 border border-primary-400">
              AI Coding Tools
            </Link>
            <Link href="/compare/" className="btn-primary bg-transparent hover:bg-primary-700 border border-primary-300">
              Compare Tools
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Tools */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Top-Rated AI Tools</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Our highest-rated AI tools across all categories, updated for 2026.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredTools.map((tool, idx) => (
            <ToolCard key={tool.slug} tool={tool} rank={idx + 1} />
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Browse by Category</h2>
            <p className="text-gray-600">Find AI tools organized by what you need them for.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {categories.map(cat => (
              <Link
                key={cat.slug}
                href={`/category/${cat.slug}/`}
                className="card text-center hover:border-primary-300"
              >
                <h3 className="font-semibold text-gray-900 mb-2">{cat.name}</h3>
                <p className="text-sm text-gray-500 line-clamp-2">{cat.description.split('.')[0]}.</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Comparisons */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Popular Comparisons</h2>
          <p className="text-gray-600">Head-to-head comparisons of the most popular AI tools.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {comparisons.map(comp => (
            <Link
              key={comp.slug}
              href={`/compare/${comp.slug}/`}
              className="card hover:border-primary-300"
            >
              <div className="flex items-center justify-center space-x-4 mb-4">
                <span className="font-bold text-lg text-gray-900">{comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="text-primary-500 font-bold">VS</span>
                <span className="font-bold text-lg text-gray-900">{comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
              </div>
              <p className="text-sm text-gray-600 text-center line-clamp-2">{comp.verdict}</p>
            </Link>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link href="/compare/" className="btn-secondary">
            View All Comparisons &rarr;
          </Link>
        </div>
      </section>

      {/* SEO Content Block */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>Why Use ToolPilot to Find AI Tools?</h2>
          <p>
            The AI tools landscape is evolving rapidly, with new products launching every week.
            ToolPilot cuts through the noise with honest, data-driven reviews and side-by-side
            comparisons that help you make informed decisions.
          </p>
          <h3>What Makes Our Reviews Different</h3>
          <ul>
            <li><strong>Hands-on testing</strong> &mdash; Every tool is evaluated on real-world tasks</li>
            <li><strong>Transparent scoring</strong> &mdash; Our ratings break down into specific categories</li>
            <li><strong>Updated pricing</strong> &mdash; We track pricing changes so you always see current rates</li>
            <li><strong>Comparison tables</strong> &mdash; Side-by-side feature and pricing comparisons</li>
            <li><strong>No sponsored rankings</strong> &mdash; Our rankings are based purely on quality and value</li>
          </ul>
          <h3>Finding the Right AI Tool for You</h3>
          <p>
            Whether you need an AI writing assistant for blog posts, an AI code editor for development,
            an image generator for marketing visuals, or a video tool for content creation,
            our curated directory and detailed comparisons will help you find the perfect match
            for your workflow and budget.
          </p>
        </div>
      </section>

      {/* JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "ToolPilot",
            "description": "Find the perfect AI tool with honest reviews and comparisons",
            "url": "https://toolpilot-hub.netlify.app"
          })
        }}
      />
    </Layout>
  )
}

export async function getStaticProps() {
  return {
    props: {
      featuredTools: getFeaturedTools(),
      categories: getAllCategories(),
      comparisons: getAllComparisons(),
      totalTools: getAllTools().length,
    },
  }
}
