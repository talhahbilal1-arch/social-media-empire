import { useState } from 'react'

// ConvertKit form config — update these after creating the form in ConvertKit dashboard
const CONVERTKIT_FORM_ID = process.env.NEXT_PUBLIC_CONVERTKIT_FORM_ID || ''
const CONVERTKIT_API_KEY = process.env.NEXT_PUBLIC_CONVERTKIT_API_KEY || ''
const CONVERTKIT_API_URL = 'https://api.convertkit.com/v3'

/**
 * Newsletter signup component with multiple variants.
 * Uses ConvertKit's public API (no server needed for static export).
 *
 * Variants: 'default' (footer), 'sidebar', 'inline' (blog articles)
 */
export default function NewsletterSignup({ variant = 'default' }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [errorMsg, setErrorMsg] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email || !CONVERTKIT_FORM_ID) return

    setStatus('loading')
    setErrorMsg('')

    try {
      const res = await fetch(`${CONVERTKIT_API_URL}/forms/${CONVERTKIT_FORM_ID}/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, api_key: CONVERTKIT_API_KEY }),
      })

      if (!res.ok) throw new Error('Subscription failed')

      setStatus('success')
      setEmail('')

      // GA4 event tracking
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'newsletter_signup', {
          event_category: 'engagement',
          event_label: variant,
        })
      }
    } catch (err) {
      setStatus('error')
      setErrorMsg('Something went wrong. Please try again.')
    }
  }

  if (status === 'success') {
    return (
      <div className={`rounded-xl p-6 text-center ${variant === 'inline' ? 'bg-green-50 border border-green-200 my-8' : 'bg-green-50'}`}>
        <h3 className="text-lg font-bold text-green-800 mb-2">You&apos;re In!</h3>
        <p className="text-green-700 text-sm">Check your email to confirm your subscription. Your free guide is on the way.</p>
      </div>
    )
  }

  // Inline variant (inside blog articles)
  if (variant === 'inline') {
    return (
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-200 rounded-xl p-6 my-8">
        <div className="text-center mb-4">
          <h3 className="text-xl font-bold text-gray-900">Free Guide: 10 Ways to Make Money with AI Tools</h3>
          <p className="text-gray-600 text-sm mt-1">Join 1,000+ readers getting weekly AI tool tips and money-making strategies.</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-lg mx-auto">
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="btn-primary whitespace-nowrap text-sm"
          >
            {status === 'loading' ? 'Joining...' : 'Get Free Guide'}
          </button>
        </form>
        {errorMsg && <p className="text-red-600 text-xs text-center mt-2">{errorMsg}</p>}
        <p className="text-gray-400 text-xs text-center mt-2">No spam. Unsubscribe anytime.</p>
      </div>
    )
  }

  // Sidebar variant
  if (variant === 'sidebar') {
    return (
      <div className="card bg-primary-50 border-primary-200">
        <h3 className="font-bold text-gray-900 mb-2">AI Money Maker Weekly</h3>
        <p className="text-sm text-gray-600 mb-4">Free guide + weekly AI tool tips to earn more and spend less.</p>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="btn-primary w-full justify-center text-sm"
          >
            {status === 'loading' ? 'Joining...' : 'Get Free Guide'}
          </button>
        </form>
        {errorMsg && <p className="text-red-600 text-xs mt-2">{errorMsg}</p>}
        <p className="text-gray-400 text-xs mt-2">No spam. Unsubscribe anytime.</p>
      </div>
    )
  }

  // Default variant (footer)
  return (
    <div className="bg-primary-600 rounded-xl p-8 text-center text-white mb-8">
      <h3 className="text-2xl font-bold mb-2">AI Money Maker Weekly</h3>
      <p className="text-primary-100 mb-1">Free Guide: 10 Ways to Make Money with AI Tools</p>
      <p className="text-primary-200 text-sm mb-6">Plus weekly tips on the best free AI tools and money-making strategies.</p>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-lg mx-auto">
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="flex-1 px-4 py-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-primary-300 focus:border-transparent"
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="px-6 py-3 bg-white text-primary-700 font-semibold rounded-lg hover:bg-primary-50 transition-colors whitespace-nowrap"
        >
          {status === 'loading' ? 'Joining...' : 'Get Free Guide'}
        </button>
      </form>
      {errorMsg && <p className="text-red-200 text-xs mt-2">{errorMsg}</p>}
      <p className="text-primary-300 text-xs mt-3">No spam. Unsubscribe anytime.</p>
    </div>
  )
}
