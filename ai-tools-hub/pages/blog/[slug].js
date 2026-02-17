import Layout from '../../components/Layout'
import { AffiliateDisclosure } from '../../components/AffiliateLink'
import NewsletterSignup from '../../components/NewsletterSignup'
import Link from 'next/link'
import { getAllArticles, getArticleBySlug, getReadingTime } from '../../lib/articles'

const SITE_URL = 'https://ai-tools-hub-lilac.vercel.app'

export default function ArticlePage({ article }) {
  if (!article) return null

  const canonicalUrl = `${SITE_URL}/blog/${article.slug}/`

  const structuredData = [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": article.title,
      "description": article.meta_description || article.excerpt,
      "author": { "@type": "Organization", "name": "ToolPilot" },
      "publisher": {
        "@type": "Organization",
        "name": "ToolPilot",
        "url": SITE_URL
      },
      "datePublished": article.published_date,
      "mainEntityOfPage": canonicalUrl,
      "wordCount": article.word_count,
      "keywords": (article.keywords || []).join(', ')
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL },
        { "@type": "ListItem", "position": 2, "name": "Blog", "item": `${SITE_URL}/blog/` },
        { "@type": "ListItem", "position": 3, "name": article.title, "item": canonicalUrl }
      ]
    }
  ]

  // Split HTML content to insert newsletter mid-article
  const contentHtml = article.html || ''
  const midPoint = Math.floor(contentHtml.length / 2)
  // Find the nearest closing tag after the midpoint to avoid splitting inside a tag
  const splitIndex = contentHtml.indexOf('</p>', midPoint)
  const hasEnoughContent = contentHtml.length > 1000 && splitIndex !== -1
  const firstHalf = hasEnoughContent ? contentHtml.substring(0, splitIndex + 4) : contentHtml
  const secondHalf = hasEnoughContent ? contentHtml.substring(splitIndex + 4) : ''

  return (
    <Layout
      title={article.meta_title || article.title}
      description={article.meta_description || article.excerpt}
      canonical={canonicalUrl}
      ogType="article"
      structuredData={structuredData}
    >
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Breadcrumb */}
        <nav className="text-sm text-gray-500 mb-6">
          <Link href="/" className="hover:text-primary-600">Home</Link>
          <span className="mx-2">/</span>
          <Link href="/blog/" className="hover:text-primary-600">Blog</Link>
          <span className="mx-2">/</span>
          <span className="text-gray-700">{article.title}</span>
        </nav>

        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <span className="badge badge-blue">{article.category}</span>
            {article.tags && article.tags.slice(0, 3).map(tag => (
              <span key={tag} className="badge badge-green text-xs">{tag}</span>
            ))}
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4 leading-tight">
            {article.title}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>By {article.author}</span>
            <span>{new Date(article.published_date).toLocaleDateString('en-US', {
              year: 'numeric', month: 'long', day: 'numeric'
            })}</span>
            <span>{getReadingTime(article.word_count)}</span>
            <span>{article.word_count.toLocaleString()} words</span>
          </div>
        </header>

        <AffiliateDisclosure />

        {/* First half of article content */}
        <div
          className="prose prose-lg max-w-none mt-8"
          dangerouslySetInnerHTML={{ __html: firstHalf }}
        />

        {/* Mid-article newsletter signup */}
        {hasEnoughContent && (
          <div className="my-10">
            <NewsletterSignup variant="inline" />
          </div>
        )}

        {/* Second half of article content */}
        {hasEnoughContent && secondHalf && (
          <div
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: secondHalf }}
          />
        )}

        {/* End-of-article newsletter signup */}
        <div className="mt-12 mb-8">
          <NewsletterSignup variant="banner" />
        </div>

        {/* Footer */}
        <footer className="mt-8 pt-8 border-t border-gray-200">
          <Link href="/blog/" className="text-primary-600 hover:text-primary-700 font-medium">
            &larr; Back to all articles
          </Link>
        </footer>
      </article>
    </Layout>
  )
}

export async function getStaticPaths() {
  const articles = getAllArticles()
  return {
    paths: articles.map(a => ({ params: { slug: a.slug } })),
    fallback: false
  }
}

export async function getStaticProps({ params }) {
  const article = getArticleBySlug(params.slug)
  if (!article) return { notFound: true }
  return { props: { article } }
}
