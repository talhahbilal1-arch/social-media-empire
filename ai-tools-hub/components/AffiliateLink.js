/**
 * AffiliateLink — renders an external affiliate link with proper SEO and FTC attributes.
 * - rel="noopener noreferrer nofollow sponsored" (Google + FTC compliant)
 * - target="_blank"
 * - data-tool for analytics tracking
 * - Click tracking via GA4 + localStorage
 */

/**
 * Track affiliate link clicks for analytics and conversion optimization.
 * Fires GA4 event and stores in localStorage for local analytics.
 */
export function trackAffiliateClick(toolName, placement) {
  if (typeof window !== 'undefined') {
    // GA4 event
    if (window.gtag) {
      window.gtag('event', 'affiliate_click', {
        tool_name: toolName,
        placement: placement,
        page_type: window.location.pathname.includes('/compare/') ? 'comparison' : 'review'
      });
    }
    // Local storage tracking for conversion analytics
    try {
      const clicks = JSON.parse(localStorage.getItem('affiliate_clicks') || '[]');
      clicks.push({
        tool: toolName,
        placement,
        timestamp: new Date().toISOString(),
        page: window.location.pathname
      });
      localStorage.setItem('affiliate_clicks', JSON.stringify(clicks.slice(-100)));
    } catch (e) {
      // Silently fail if localStorage is unavailable
    }
  }
}

export default function AffiliateLink({ href, tool, className, children, placement = 'inline' }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer nofollow sponsored"
      className={className}
      data-tool={tool}
      onClick={() => trackAffiliateClick(tool, placement)}
    >
      {children}
    </a>
  )
}

/**
 * AffiliateDisclosure — inline FTC-compliant disclosure for pages with affiliate links.
 * Place at the top of content sections, not just the footer.
 */
export function AffiliateDisclosure() {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 mb-6 text-sm text-amber-800">
      <strong>Disclosure:</strong> This article contains affiliate links. If you purchase through
      these links, we may earn a commission at no additional cost to you.
    </div>
  )
}
