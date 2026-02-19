import Layout from '../../components/Layout'
import Link from 'next/link'
import { getAllArticles, getReadingTime } from '../../lib/articles'

const SITE_URL = 'https://ai-tools-hub-lilac.vercel.app'

export default function BlogIndex({ articles }) {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Blog",
    "name": "ToolPilot Blog",
    "description": "In-depth guides, reviews, and buyer's guides for the best AI tools in 2026.",
    "url": `${SITE_URL}/blog/`,
    "publisher": {
      "@type": "Organization",
      "name": "ToolPilot"
    }
  }

  return (
    <Layout
      title="Blog - AI Tool Guides & Reviews"
      description="In-depth guides, buyer's guides, and expert reviews for the best AI tools. Get actionable insights to choose the right AI tools for your workflow."
      canonical={`${SITE_URL}/blog/`}
      structuredData={structuredData}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">Blog</h1>
          <p className="text-lg text-gray-600">
            In-depth guides and expert reviews to help you pick the right AI tools.
          </p>
        </div>

        {articles.length === 0 ? (
          <p className="text-gray-500">No articles yet. Check back soon!</p>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <Link
                key={article.slug}
                href={`/blog/${article.slug}/`}
                className="card group hover:shadow-lg transition-shadow overflow-hidden"
              >
                {article.hero_image && (
                  <div className="w-full h-48 overflow-hidden bg-gray-100">
                    <img
                      src={article.hero_image}
                      alt={article.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="badge badge-blue text-xs">{article.category}</span>
                    <span className="text-xs text-gray-400">{getReadingTime(article.word_count)}</span>
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors mb-2">
                    {article.title}
                  </h2>
                  <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                    {article.excerpt}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>{article.author}</span>
                    <span>{new Date(article.published_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}

export async function getStaticProps() {
  const articles = getAllArticles()
  return { props: { articles: articles.map(({ html, ...rest }) => rest) } }
}
