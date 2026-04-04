import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function CookieConsent() {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    try {
      const consent = localStorage.getItem('pilottools_cookie_consent')
      if (!consent) {
        setVisible(true)
      }
    } catch (e) {
      // localStorage not available
    }
  }, [])

  const handleConsent = (value) => {
    try {
      localStorage.setItem('pilottools_cookie_consent', value)
    } catch (e) {
      // localStorage not available
    }
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-dark-surface border-t border-dark-border p-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-sm text-dt-muted text-center sm:text-left">
          We use cookies for analytics and advertising. By continuing to use this site, you agree to our{' '}
          <Link href="/privacy/" className="text-accent hover:text-cyan-300 underline">Privacy Policy</Link>
          {' '}and{' '}
          <Link href="/terms/" className="text-accent hover:text-cyan-300 underline">Terms of Service</Link>.
        </p>
        <div className="flex gap-3 shrink-0">
          <button
            onClick={() => handleConsent('declined')}
            className="px-4 py-2 text-sm text-dt-muted hover:text-dt border border-dark-border rounded-lg transition-colors"
          >
            Decline
          </button>
          <button
            onClick={() => handleConsent('accepted')}
            className="px-4 py-2 text-sm font-medium bg-accent text-dark-bg rounded-lg hover:bg-cyan-400 transition-colors"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  )
}
