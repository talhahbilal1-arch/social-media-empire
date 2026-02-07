import { useEffect } from 'react'

/**
 * Simple analytics tracking component.
 * Logs page views and affiliate link clicks.
 *
 * In production, replace with:
 * - Google Analytics 4 (GA4)
 * - Plausible Analytics (privacy-friendly, free for <10K pageviews)
 * - Umami (self-hosted, free)
 *
 * For now, uses a lightweight localStorage-based tracker for demo purposes.
 */
export default function Analytics() {
  useEffect(() => {
    // Track page view
    trackEvent('pageview', { path: window.location.pathname })

    // Track affiliate link clicks
    const handler = (e) => {
      const link = e.target.closest('a[rel*="nofollow"]')
      if (link) {
        trackEvent('affiliate_click', {
          tool: link.textContent.trim(),
          url: link.href,
          page: window.location.pathname
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

    // Also log to console in development
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      console.log(`[Analytics] ${event}`, data)
    }
  } catch (e) {
    // Silently fail if localStorage is unavailable
  }
}
