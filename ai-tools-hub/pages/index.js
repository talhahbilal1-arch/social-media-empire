import Layout from '../components/Layout'
import ToolCard from '../components/ToolCard'
import Link from 'next/link'
import { getAllTools, getAllCategories, getAllComparisons, getFeaturedTools } from '../lib/tools'
import { getAllArticles } from '../lib/articles'

export default function Home({ featuredTools, categories, comparisons, totalTools, moneyArticles }) {
  return (
    <Layout
      canonical="https://toolpilot-hub.netlify.app/"
    >
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Make Money &amp; Save Money with AI Tools
          </h1>
          <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Honest reviews, side-by-side comparisons, and money-making guides for {totalTools}+ AI tools. Find the right tool to grow your income.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/blog/" className="btn-primary bg-white text-primary-700 hover:bg-primary-50">
              Make Money with AI
            </Link>
            <Link href="/category/writing/" className="btn-primary bg-primary-500 hover:bg-primary-400 border border-primary-400">
              Best Free AI Tools
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

      {/* Make Money with AI Section */}
      {moneyArticles.length > 0 && (
        <section className="bg-gray-50 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Make Money with AI</h2>
              <p className="text-gray-600">Practical guides to earning more and spending less using AI tools.</p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {moneyArticles.map(article => (
                <Link
                  key={article.slug}
                  href={`/blog/${article.slug}/`}
                  className="card hover:border-primary-300"
                >
                  <span className="badge-blue text-xs mb-2">{article.category}</span>
                  <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">{article.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-3">{article.excerpt}</p>
                  <span className="text-primary-600 text-sm font-medium mt-3 inline-block">Read guide &rarr;</span>
                </Link>
              ))}
            </div>
            <div className="text-center mt-8">
              <Link href="/blog/" className="btn-secondary">
                View All Guides &rarr;
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* SEO Content Block */}
      <section className="bg-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>Why Use ToolPilot to Find AI Tools?</h2>
          <p>
            AI tools can save you thousands of dollars a year in software costs and help you
            earn more as a freelancer, content creator, or small business owner.
            ToolPilot cuts through the noise with honest, data-driven reviews and side-by-side
            comparisons focused on real ROI.
          </p>
          <h3>Save Money with Free AI Tools</h3>
          <ul>
            <li><strong>Free tier deep-dives</strong> &mdash; We test what you can actually do without paying</li>
            <li><strong>Updated pricing</strong> &mdash; We track pricing changes so you always see current rates</li>
            <li><strong>Comparison tables</strong> &mdash; Side-by-side feature and pricing comparisons</li>
            <li><strong>No sponsored rankings</strong> &mdash; Our rankings are based purely on quality and value</li>
          </ul>
          <h3>Make Money with AI Tools</h3>
          <p>
            From freelance writing with AI assistants to building entire businesses with free tools,
            we show you practical ways to turn AI tools into income. Our guides cover specific
            workflows, realistic earnings, and the exact tools top earners use.
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
            "description": "Make money and save money with AI tools. Honest reviews, comparisons, and money-making guides.",
            "url": "https://toolpilot-hub.netlify.app"
          })
        }}
      />
    </Layout>
  )
}

export async function getStaticProps() {
  const allArticles = getAllArticles()
  return {
    props: {
      featuredTools: getFeaturedTools(),
      categories: getAllCategories(),
      comparisons: getAllComparisons(),
      totalTools: getAllTools().length,
      moneyArticles: allArticles.slice(0, 6).map(a => ({
        slug: a.slug,
        title: a.title,
        excerpt: a.excerpt || a.meta_description || '',
        category: a.category,
      })),
    },
  }
}
