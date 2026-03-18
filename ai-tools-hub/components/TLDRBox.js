import StarRating from './StarRating'
import AffiliateLink from './AffiliateLink'

export default function TLDRBox({ rating, verdict, bestFor, price, ctaUrl, ctaText }) {
  return (
    <div className="bg-dark-surface border-l-4 border-accent rounded-xl p-6 mb-8">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-accent">TL;DR</span>
      </div>
      <p className="text-dt text-lg mb-4">{verdict}</p>
      <div className="flex flex-wrap items-center gap-4 mb-4">
        {rating && (
          <div className="flex items-center gap-2">
            <StarRating rating={rating} size="sm" />
            <span className="text-sm font-bold text-dt">{rating}/5</span>
          </div>
        )}
        {price && <span className="text-sm text-dt-muted">Starting at <strong className="text-dt">{price}</strong></span>}
        {bestFor && <span className="text-sm text-dt-muted">Best for: <strong className="text-dt">{bestFor}</strong></span>}
      </div>
      {ctaUrl && ctaText && (
        <AffiliateLink href={ctaUrl} className="btn-primary text-sm" placement="tldr_cta">
          {ctaText} &rarr;
        </AffiliateLink>
      )}
    </div>
  )
}
