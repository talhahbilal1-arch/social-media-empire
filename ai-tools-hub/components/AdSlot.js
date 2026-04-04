import { useEffect, useRef } from 'react'

export default function AdSlot({ position = 'default', format = 'auto', responsive = true }) {
  const adRef = useRef(null)
  const pushed = useRef(false)

  useEffect(() => {
    if (typeof window !== 'undefined' && !pushed.current && adRef.current) {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({})
        pushed.current = true
      } catch (e) {
        // AdSense not loaded yet or ad blocker active
      }
    }
  }, [])

  return (
    <div className={`ad-container ad-${position} my-6`} style={{ minHeight: '90px' }}>
      <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-7018489366035978"
        data-ad-format={format}
        data-full-width-responsive={responsive ? 'true' : 'false'}
        ref={adRef}
      />
    </div>
  )
}
