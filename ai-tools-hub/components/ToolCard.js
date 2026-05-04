import Link from 'next/link'
import { formatPrice } from '../lib/tools'
import StarRating from './StarRating'
import FeaturedBadge from './FeaturedBadge'

function getLogoUrl(website) {
  if (!website) return null
  try {
    const domain = new URL(website).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=64`
  } catch {
    return null
  }
}

export default function ToolCard({ tool, rank }) {
  const getRankBadgeClass = () => {
    if (rank === 1) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    if (rank === 2) return 'bg-gray-400/20 text-gray-300 border-gray-400/30'
    if (rank === 3) return 'bg-amber-600/20 text-amber-500 border-amber-600/30'
    return 'bg-accent/10 text-accent border-accent/20'
  }

  const logoUrl = getLogoUrl(tool.website)

  return (
    <div className={`card group gradient-border ${tool.featured ? 'border-yellow-500/20 shadow-[0_0_20px_rgba(234,179,8,0.08)]' : ''}`}>
      {tool.featured && (
        <div className="mb-3">
          <FeaturedBadge />
        </div>
      )}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {rank && (
            <span className={`flex-shrink-0 w-8 h-8 rounded-full font-bold text-sm flex items-center justify-center border ${getRankBadgeClass()}`}>
              {rank}
            </span>
          )}
          {/* Tool logo */}
          {logoUrl && (
            <img
              src={logoUrl}
              alt={`${tool.name} logo`}
              width={32}
              height={32}
              className="w-8 h-8 rounded-lg bg-dark-surface-hover"
              loading="lazy"
            />
          )}
          <div>
            <Link href={`/tools/${tool.slug}/`} className="text-lg font-bold text-dt group-hover:text-accent transition-colors">
              {tool.name}
            </Link>
            <p className="text-sm text-dt-muted flex items-center gap-1">
              {tool.company}
              <svg className="w-3.5 h-3.5 text-accent" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </p>
          </div>
        </div>
        {tool.pricing.starting_price === 0 || tool.pricing.starting_price === '0' ? (
          <span className="badge-green text-xs">Free</span>
        ) : tool.pricing.free_tier ? (
          <span className="badge-blue text-xs">Freemium</span>
        ) : (
          <span className="badge-purple text-xs">Paid</span>
        )}
      </div>

      <p className="text-dt-muted text-sm mb-4 line-clamp-2">{tool.tagline}</p>

      <div className="flex items-center space-x-2 mb-4">
        <StarRating rating={tool.rating} />
        <span className="text-sm font-medium text-dt">{tool.rating}</span>
        <span className="text-sm text-green-400 flex items-center gap-1 whitespace-nowrap">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"/></svg>
          Verified
        </span>
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
