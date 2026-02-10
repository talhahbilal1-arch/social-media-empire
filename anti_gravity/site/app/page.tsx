import { getAllArticles } from './lib/articles'

export default function Home() {
  const articles = getAllArticles()

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-3">Latest Articles</h1>
        <p className="text-gray-400 text-lg">
          In-depth reviews and buying guides to help you make smarter decisions.
        </p>
      </div>

      {articles.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-500 text-lg">No articles yet. Run the Anti-Gravity pipeline to generate content.</p>
          <code className="block mt-4 text-sm text-emerald-400">
            python -m anti_gravity.main run --niche &quot;AI writing tools&quot; --count 1
          </code>
        </div>
      ) : (
        <div className="space-y-8">
          {articles.map((article) => (
            <a
              key={article.slug}
              href={`/articles/${article.slug}`}
              className="block group p-6 rounded-xl border border-gray-800 hover:border-emerald-800 transition-colors"
            >
              <h2 className="text-xl font-semibold group-hover:text-emerald-400 transition-colors mb-2">
                {article.title}
              </h2>
              <p className="text-gray-400 text-sm mb-3">{article.meta_description}</p>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>{article.word_count.toLocaleString()} words</span>
                <span>{new Date(article.created_at).toLocaleDateString()}</span>
                <span className="text-emerald-600">{article.keyword}</span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
