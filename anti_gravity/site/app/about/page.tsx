import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About — Anti-Gravity',
  description: 'Anti-Gravity is a home office optimization resource helping you build a healthier, more productive workspace.',
}

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">About Anti-Gravity</h1>

      <div className="space-y-5 text-gray-300 leading-relaxed">
        <p>
          Anti-Gravity is a home office optimization resource helping you build a healthier,
          more productive workspace. We believe that where you work directly impacts how you
          work, and that small improvements to your desk setup can have outsized effects on
          your comfort, focus, and long-term health.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">What We Do</h2>
        <p>
          We publish independent, in-depth reviews and buying guides for home office products
          including standing desks, ergonomic chairs, monitor arms, desk accessories, and
          complete setup guides. Our goal is to cut through the noise and help you make
          informed decisions without overspending.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Affiliate Disclosure</h2>
        <p>
          Some of the links on this site are affiliate links, which means we may earn a small
          commission if you make a purchase through them. This comes at no additional cost to
          you. Our reviews and recommendations are based on independent research and are not
          influenced by affiliate partnerships. We only recommend products we believe provide
          genuine value.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Contact</h2>
        <p>
          Questions or feedback? Reach us at{' '}
          <a href="mailto:hello@pilottools.ai" className="text-emerald-400 hover:text-emerald-300 transition-colors">
            hello@pilottools.ai
          </a>
        </p>
      </div>
    </div>
  )
}
