import { useState } from 'react'

export default function NewsletterSignup({ variant = 'inline', className = '' }) {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState('idle')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email) return

    setStatus('loading')

    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'newsletter_signup', {
        placement: variant,
        page: window.location.pathname
      })
    }

    try {
      const formId = '7195499'
      const res = await fetch(`https://api.convertkit.com/v3/forms/${formId}/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: 'pk_f2a3c8b9e1d4a7c6b5e8f1d2',
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
      <div className={`bg-green-900/20 border border-green-800/30 rounded-xl p-6 text-center ${className}`}>
        <svg className="w-12 h-12 text-green-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-lg font-bold text-green-400">You are in!</h3>
        <p className="text-green-300/80 mt-1">Check your inbox to confirm your subscription.</p>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={`bg-dark-surface border border-dark-border rounded-xl p-4 ${className}`}>
        <h3 className="font-bold text-dt text-sm mb-2">Get AI Tool Updates</h3>
        <p className="text-xs text-dt-muted mb-3">Weekly picks, deals, and new tool alerts.</p>
        <form onSubmit={handleSubmit} className="space-y-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="w-full px-3 py-2 text-sm bg-dark-bg border border-dark-border rounded-lg text-dt placeholder-dt-muted focus:ring-2 focus:ring-accent/50 focus:border-accent/50"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full py-2 px-4 text-sm font-bold text-dark-bg bg-accent hover:bg-cyan-300 rounded-lg transition-colors disabled:opacity-50"
          >
            {status === 'loading' ? 'Subscribing...' : 'Subscribe Free'}
          </button>
        </form>
        {status === 'error' && <p className="text-xs text-red-400 mt-2">Something went wrong. Try again.</p>}
        <p className="text-xs text-dt-muted mt-2">No spam. Unsubscribe anytime.</p>
      </div>
    )
  }

  if (variant === 'banner') {
    return (
      <div className={`bg-gradient-to-r from-accent/10 to-accent-purple/10 border border-accent/20 rounded-2xl p-8 md:p-10 ${className}`}>
        <div className="max-w-2xl mx-auto text-center">
          <h3 className="text-2xl md:text-3xl font-bold text-dt mb-3">Stay Ahead of the AI Curve</h3>
          <p className="text-dt-muted mb-6 text-lg">
            Get our weekly roundup of the best AI tools, exclusive deals, and expert tips delivered to your inbox.
          </p>
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="flex-1 px-4 py-3 rounded-lg bg-dark-bg border border-dark-border text-dt placeholder-dt-muted focus:ring-2 focus:ring-accent/50"
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="px-6 py-3 font-bold bg-accent text-dark-bg rounded-lg hover:bg-cyan-300 transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              {status === 'loading' ? 'Subscribing...' : 'Get Free Updates'}
            </button>
          </form>
          {status === 'error' && <p className="text-sm text-red-400 mt-3">Something went wrong. Please try again.</p>}
          <p className="text-xs text-dt-muted mt-4">Free weekly AI tool updates. No spam, unsubscribe anytime.</p>
        </div>
      </div>
    )
  }

  // Default: inline variant
  return (
    <div className={`bg-dark-surface border border-dark-border rounded-xl p-6 md:p-8 ${className}`}>
      <div className="text-center">
        <h3 className="text-xl md:text-2xl font-bold text-dt mb-2">Never Miss the Best AI Tools</h3>
        <p className="text-dt-muted mb-5 max-w-lg mx-auto">
          Get weekly recommendations, exclusive deals, and tips to 10x your productivity with AI.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            required
            className="flex-1 px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-dt placeholder-dt-muted focus:ring-2 focus:ring-accent/50 focus:border-accent/50"
          />
          <button
            type="submit"
            disabled={status === 'loading'}
            className="px-6 py-3 font-bold text-dark-bg bg-accent hover:bg-cyan-300 rounded-lg transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {status === 'loading' ? 'Subscribing...' : 'Subscribe Free'}
          </button>
        </form>
        {status === 'error' && <p className="text-sm text-red-400 mt-3">Something went wrong. Please try again.</p>}
        <p className="text-xs text-dt-muted mt-3">No spam ever. Unsubscribe anytime.</p>
      </div>
    </div>
  )
}
