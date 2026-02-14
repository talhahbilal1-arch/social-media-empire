/**
 * NewsletterSignup — email capture component for ToolPilot.
 * Variants: 'inline' (within content), 'banner' (full-width), 'compact' (sidebar).
 */
import { useState } from 'react'

export default function NewsletterSignup({ variant = 'inline', className = '' }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | error

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return

    setStatus('loading')

    // Track signup attempt
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'newsletter_signup', {
        placement: variant,
        page: window.location.pathname
      })
    }

    try {
      // ConvertKit form submission
      const formId = '7195499' // ToolPilot newsletter form
      const res = await fetch(`https://api.convertkit.com/v3/forms/${formId}/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: 'pk_f2a3c8b9e1d4a7c6b5e8f1d2', // Public key only
          email: email
        })
      })

      if (res.ok) {
        setStatus('success')
        setEmail('')
      } else {
        setStatus('error')
      }
    } catch {
      setStatus('error')
    }
  }

  if (status === 'success') {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-xl p-6 text-center ${className}`}>
        <svg className="w-12 h-12 text-green-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-lg font-bold text-green-900">You are in!</h3>
        <p className="text-green-700 mt-1">Check your inbox to confirm your subscription.</p>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={`bg-primary-50 border border-primary-200 rounded-xl p-4 ${className}`}>
        <h3 className="font-bold text-gray-900 text-sm mb-2">Get AI Tool Updates</h3>
        <p className="text-xs text-gray-600 mb-3">Weekly picks, deals, and new tool alerts.</p>
        <form onSubmit={handleSubmit} className="space-y-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full py-2 px-4 text-sm font-bold text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {status === 'loading' ? 'Subscribing...' : 'Subscribe Free'}
          </button>
        </form>
        {status === 'error' && <p className="text-xs text-red-600 mt-2">Something went wrong. Try again.</p>}
        <p className="text-xs text-gray-400 mt-2">No spam. Unsubscribe anytime.</p>
      </div>
    )
  }

  if (variant === 'banner') {
    return (
      <div className={`bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl p-8 md:p-10 text-white ${className}`}>
        <div className="max-w-2xl mx-auto text-center">
          <h3 className="text-2xl md:text-3xl font-bold mb-3">Stay Ahead of the AI Curve</h3>
          <p className="text-primary-100 mb-6 text-lg">
            Get our weekly roundup of the best AI tools, exclusive deals, and expert tips delivered to your inbox.
          </p>
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="flex-1 px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="px-6 py-3 font-bold bg-white text-primary-700 rounded-lg hover:bg-primary-50 transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {status === 'loading' ? 'Subscribing...' : 'Get Free Updates'}
            </button>
          </form>
          {status === 'error' && <p className="text-sm text-red-200 mt-3">Something went wrong. Please try again.</p>}
          <p className="text-xs text-primary-200 mt-4">Join 2,000+ AI enthusiasts. No spam, unsubscribe anytime.</p>
        </div>
      </div>
    )
  }

  // Default: inline variant
  return (
    <div className={`bg-gradient-to-br from-primary-50 to-blue-50 border border-primary-200 rounded-xl p-6 md:p-8 ${className}`}>
      <div className="text-center">
        <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">Never Miss the Best AI Tools</h3>
        <p className="text-gray-600 mb-5 max-w-lg mx-auto">
          Get weekly recommendations, exclusive deals, and tips to 10x your productivity with AI. Trusted by 2,000+ readers.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="px-6 py-3 font-bold text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {status === 'loading' ? 'Subscribing...' : 'Subscribe Free'}
          </button>
        </form>
        {status === 'error' && <p className="text-sm text-red-600 mt-3">Something went wrong. Please try again.</p>}
        <p className="text-xs text-gray-400 mt-3">No spam ever. Unsubscribe anytime.</p>
      </div>
    </div>
  )
}
