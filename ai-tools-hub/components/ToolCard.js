import Link from 'next/link'
import { formatPrice } from '../lib/tools'
import StarRating from './StarRating'

export default function ToolCard({ tool, rank }) {
  // Determine rank badge color
  const getRankBadgeClass = () => {
    if (rank === 1) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    if (rank === 2) return 'bg-gray-400/20 text-gray-300 border-gray-400/30'
    if (rank === 3) return 'bg-amber-600/20 text-amber-500 border-amber-600/30'
    return 'bg-accent/10 text-accent border-accent/20'
  }

  return (
    <div className="card group gradient-border">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {rank && (
            <span className={`flex-shrink-0 w-8 h-8 rounded-full font-bold text-sm flex items-center justify-center border ${getRankBadgeClass()}`}>
              {rank}
            </span>
          )}
          <div>
            <Link href={`/tools/${tool.slug}/`} className="text-lg font-bold text-dt group-hover:text-accent transition-colors">
              {tool.name}
            </Link>
            <p className="text-sm text-dt-muted">{tool.company}</p>
          </div>
        </div>
        {tool.pricing.free_tier && (
          <span className="badge-green text-xs">Free tier</span>
        )}
      </div>

      <p className="text-dt-muted text-sm mb-4 line-clamp-2">{tool.tagline}</p>

      <div className="flex items-center space-x-2 mb-4">
        <StarRating rating={tool.rating} />
        <span className="text-sm font-medium text-dt">{tool.rating}</span>
        <span className="text-sm text-dt-muted">({tool.review_count.toLocaleString()})</span>
      </div>

      <div className="flex flex-wrap gap-1 mb-4">
        {tool.categories.slice(0, 3).map(cat => (
          <span key={cat} className="badge-blue text-xs">{cat}</span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-dark-border">
        <div>
          <span className="text-sm text-dt-muted">Starting at </span>
          <span className="font-bold text-dt">
            {formatPrice(tool.pricing.starting_price)}
          </span>
        </div>
        <Link href={`/tools/${tool.slug}/`} className="text-sm text-accent hover:text-cyan-300 font-medium transition-colors">
          Full Review &rarr;
        </Link>
      </div>
    </div>
  )
}
