import Layout from '../components/Layout'
import ToolCard from '../components/ToolCard'
import NewsletterSignup from '../components/NewsletterSignup'
import Link from 'next/link'
import { getAllTools, getAllCategories, getAllComparisons, getFeaturedTools } from '../lib/tools'

export default function Home({ featuredTools, categories, comparisons, totalTools }) {
  return (
    <Layout
      canonical="https://toolpilot-hub.netlify.app/"
    >
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-purple-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-white/20 text-white mb-6">
            Updated February 2026 &mdash; {totalTools}+ tools reviewed
          </span>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Stop Wasting Money on the<br className="hidden md:block" /> Wrong AI Tools
          </h1>
          <p className="text-xl md:text-2xl text-primary-100 mb-4 max-w-3xl mx-auto">
            Find the perfect AI tool in minutes with honest reviews, real pricing data, and side-by-side comparisons. Save hours of research and hundreds of dollars.
          </p>
          <p className="text-primary-200 mb-8 max-w-2xl mx-auto">
            Trusted by creators, marketers, and developers who need AI tools that actually deliver ROI.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/category/writing/" className="btn-primary bg-white text-primary-700 hover:bg-primary-50 font-bold">
              AI Writing Tools
            </Link>
            <Link href="/category/coding/" className="btn-primary bg-primary-500 hover:bg-primary-400 border border-primary-400 font-bold">
              AI Coding Tools
            </Link>
            <Link href="/compare/" className="btn-primary bg-transparent hover:bg-primary-700 border border-primary-300 font-bold">
              Compare Tools
            </Link>
          </div>
        </div>
      </section>

      {/* Social Proof Bar */}
      <section className="bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-12 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span><strong>{totalTools}+</strong> AI tools reviewed</span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span><strong>10</strong> categories covered</span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span><strong>Updated</strong> February 2026</span>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span><strong>100%</strong> independent reviews</span>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Tools */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Top-Rated AI Tools for 2026</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Our highest-rated AI tools across all categories. Each tool is hands-on tested and rated on features, pricing, ease of use, and value.
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

      {/* Newsletter Signup */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NewsletterSignup variant="banner" />
      </section>

      {/* SEO Content Block */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>Why Use ToolPilot to Find AI Tools?</h2>
          <p>
            The AI tools landscape is evolving rapidly, with new products launching every week.
            ToolPilot cuts through the noise with honest, data-driven reviews and side-by-side
            comparisons that help you make informed decisions &mdash; and save you money.
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
