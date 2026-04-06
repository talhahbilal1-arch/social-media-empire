import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service — Anti-Gravity',
  description: 'Terms of service for Anti-Gravity home office optimization guides.',
}

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
      <p className="text-sm text-gray-500 mb-8">Last updated: April 6, 2026</p>

      <div className="space-y-5 text-gray-300 leading-relaxed">
        <p>
          By accessing and using Anti-Gravity (anti-gravity-blog.vercel.app), you agree to
          be bound by these Terms of Service. If you do not agree with any part of these
          terms, please do not use our site.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Content</h2>
        <p>
          All content on this site, including articles, reviews, and guides, is provided for
          informational purposes only. We make every effort to ensure accuracy, but we do not
          guarantee that all information is complete, current, or error-free. Product
          specifications, prices, and availability may change without notice.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Affiliate Links</h2>
        <p>
          Our site contains affiliate links to products on Amazon and other retailers. When
          you click these links and make a purchase, we may earn a commission at no additional
          cost to you. Our editorial content is independent of our affiliate partnerships.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Intellectual Property</h2>
        <p>
          All original content on this site, including text, graphics, and design, is the
          property of Anti-Gravity and is protected by copyright law. You may not reproduce,
          distribute, or create derivative works without our prior written consent.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Disclaimer of Warranties</h2>
        <p>
          This site is provided &quot;as is&quot; without warranties of any kind, either express or
          implied. We do not warrant that the site will be uninterrupted, error-free, or free
          of viruses or other harmful components. Your use of the site is at your own risk.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Limitation of Liability</h2>
        <p>
          In no event shall Anti-Gravity be liable for any indirect, incidental, special, or
          consequential damages arising out of or in connection with your use of this site or
          any products purchased through affiliate links.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Changes to These Terms</h2>
        <p>
          We reserve the right to modify these terms at any time. Changes will be effective
          immediately upon posting. Your continued use of the site after changes constitutes
          acceptance of the updated terms.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Contact</h2>
        <p>
          Questions about these terms? Contact us at{' '}
          <a href="mailto:hello@pilottools.ai" className="text-emerald-400 hover:text-emerald-300 transition-colors">
            hello@pilottools.ai
          </a>
        </p>
      </div>
    </div>
  )
}
