import AffiliateLink from './AffiliateLink'

export default function PricingTable({ plans, highlightPlan, affiliateUrl, toolSlug }) {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {plans.map((plan) => {
        const isHighlighted = plan.name === highlightPlan
        return (
          <div
            key={plan.name}
            className={`card relative ${isHighlighted ? 'border-accent ring-2 ring-accent/20' : ''}`}
          >
            {isHighlighted && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 badge-blue text-xs">Most Popular</span>
            )}
            <h3 className="font-bold text-lg text-dt">{plan.name}</h3>
            <p className="text-2xl font-bold text-dt my-2">
              {plan.price === 0 ? 'Free' : plan.price === null ? 'Custom' : `$${plan.price}/mo`}
            </p>
            <ul className="space-y-2 mt-4">
              {plan.features.map(f => (
                <li key={f} className="flex items-center space-x-2 text-sm text-dt-muted">
                  <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            {affiliateUrl && (
              <AffiliateLink
                href={affiliateUrl}
                tool={toolSlug}
                className={`mt-4 w-full justify-center ${isHighlighted ? 'btn-primary' : 'btn-secondary'}`}
                placement="pricing_table"
              >
                {plan.price === 0 ? 'Start Free' : 'Get Started'} &rarr;
              </AffiliateLink>
            )}
          </div>
        )
      })}
    </div>
  )
}
