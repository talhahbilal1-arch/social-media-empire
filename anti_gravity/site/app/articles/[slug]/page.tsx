import { notFound } from 'next/navigation'
import { getArticleBySlug, getAllSlugs } from '../../lib/articles'
import type { Metadata } from 'next'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  return getAllSlugs().map(slug => ({ slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const article = getArticleBySlug(params.slug)
  if (!article) return { title: 'Not Found' }

  return {
    title: article.title,
    description: article.meta_description,
    openGraph: {
      title: article.title,
      description: article.meta_description,
      type: 'article',
    },
  }
}

export default function ArticlePage({ params }: Props) {
  const article = getArticleBySlug(params.slug)
  if (!article) notFound()

  return (
    <article className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-10">
        <h1 className="text-3xl sm:text-4xl font-bold mb-4 leading-tight">{article.title}</h1>
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <time>{new Date(article.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}</time>
          <span>{article.word_count.toLocaleString()} words</span>
        </div>
        {article.meta_description && (
          <p className="mt-4 text-lg text-gray-400 leading-relaxed">
            {article.meta_description}
          </p>
        )}
      </header>

      <div
        className="article-content"
        dangerouslySetInnerHTML={{ __html: article.html }}
      />

      <footer className="mt-12 pt-8 border-t border-gray-800">
        <a
          href="/"
          className="text-emerald-400 hover:text-emerald-300 transition-colors"
        >
          &larr; Back to all articles
        </a>
      </footer>
    </article>
  )
}
