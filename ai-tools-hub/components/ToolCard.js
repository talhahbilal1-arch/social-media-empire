import Link from 'next/link'
import { formatPrice } from '../lib/tools'
import StarRating from './StarRating'

export default function ToolCard({ tool, rank }) {
  return (
    <div className="card group">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {rank && (
            <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-bold text-sm flex items-center justify-center">
              {rank}
            </span>
          )}
          <div>
            <Link href={`/tools/${tool.slug}/`} className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
              {tool.name}
            </Link>
            <p className="text-sm text-gray-500">{tool.company}</p>
          </div>
        </div>
        {tool.pricing.free_tier && (
          <span className="badge-green text-xs">Free tier</span>
        )}
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{tool.tagline}</p>

      <div className="flex items-center space-x-2 mb-4">
        <StarRating rating={tool.rating} />
        <span className="text-sm font-medium text-gray-700">{tool.rating}</span>
        <span className="text-sm text-gray-400">({tool.review_count.toLocaleString()})</span>
      </div>

      <div className="flex flex-wrap gap-1 mb-4">
        {tool.categories.slice(0, 3).map(cat => (
          <span key={cat} className="badge-blue text-xs">{cat}</span>
        ))}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
        <div>
          <span className="text-sm text-gray-500">Starting at </span>
          <span className="font-bold text-gray-900">
            {formatPrice(tool.pricing.starting_price)}
          </span>
        </div>
        <div className="flex space-x-2">
          <Link href={`/tools/${tool.slug}/`} className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Full Review &rarr;
          </Link>
        </div>
      </div>
    </div>
  )
}
