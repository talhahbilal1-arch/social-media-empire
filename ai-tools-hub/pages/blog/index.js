import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'
import { getAllArticles, getReadingTime } from '../../lib/articles'

const SITE_URL = 'https://pilottools.ai'

export default function BlogIndex({ articles }) {
  return (
    <Layout
      title="Blog - AI Tool Guides & Reviews"
      description="In-depth guides, buyer's guides, and expert reviews for the best AI tools."
      canonical={`${SITE_URL}/blog/`}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Blog' }]} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-dt mb-3">Blog</h1>
          <p className="text-lg text-dt-muted">In-depth guides and expert reviews to help you pick the right AI tools.</p>
        </div>

        {articles.length === 0 ? (
          <p className="text-dt-muted">No articles yet. Check back soon!</p>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <Link key={article.slug} href={`/blog/${article.slug}/`} className="card group hover:shadow-glow overflow-hidden p-0">
                {article.hero_image && (
                  <div className="w-full h-48 overflow-hidden bg-dark-surface-hover">
                    <img src={article.hero_image} alt={article.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="badge-blue text-xs">{article.category}</span>
                    <span className="text-xs text-dt-muted">{getReadingTime(article.word_count)}</span>
                  </div>
                  <h2 className="text-lg font-semibold text-dt group-hover:text-accent transition-colors mb-2">{article.title}</h2>
                  <p className="text-sm text-dt-muted line-clamp-3 mb-4">{article.excerpt}</p>
                  <div className="flex items-center justify-between text-xs text-dt-muted">
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
