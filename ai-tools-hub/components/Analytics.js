import { useEffect } from 'react'

/**
 * Analytics tracking component.
 * Logs page views and affiliate link clicks with UTM data.
 *
 * In production, replace localStorage tracking with:
 * - Google Analytics 4 (GA4)
 * - Plausible Analytics (privacy-friendly)
 * - Umami (self-hosted, free)
 */
export default function Analytics() {
  useEffect(() => {
    trackEvent('pageview', { path: window.location.pathname })

    // Track affiliate link clicks (links with rel="sponsored")
    const handler = (e) => {
      const link = e.target.closest('a[rel*="sponsored"]')
      if (link) {
        const url = new URL(link.href, window.location.origin)
        trackEvent('affiliate_click', {
          tool: link.dataset.tool || link.textContent.trim(),
          url: link.href,
          page: window.location.pathname,
          utm_campaign: url.searchParams.get('utm_campaign') || '',
          utm_medium: url.searchParams.get('utm_medium') || ''
        })
      }
    }

    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [])

  return null
}

function trackEvent(event, data) {
  try {
    const events = JSON.parse(localStorage.getItem('tp_events') || '[]')
    events.push({
      event,
      ...data,
      timestamp: new Date().toISOString()
    })
    // Keep last 1000 events
    if (events.length > 1000) events.splice(0, events.length - 1000)
    localStorage.setItem('tp_events', JSON.stringify(events))

    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      console.log(`[Analytics] ${event}`, data)
    }
  } catch (e) {
    // Silently fail if localStorage is unavailable
  }
}
