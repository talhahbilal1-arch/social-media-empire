import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy — Anti-Gravity',
  description: 'Privacy policy for Anti-Gravity home office optimization guides.',
}

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
      <p className="text-sm text-gray-500 mb-8">Last updated: April 6, 2026</p>

      <div className="space-y-5 text-gray-300 leading-relaxed">
        <p>
          Anti-Gravity (&quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) operates the website
          anti-gravity-blog.vercel.app. This page informs you of our policies regarding the
          collection, use, and disclosure of personal information when you use our site.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Information Collection</h2>
        <p>
          We do not directly collect personal information from visitors. However, we use
          third-party services that may collect information used to identify you.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Google Analytics</h2>
        <p>
          We use Google Analytics to understand how visitors interact with our site. Google
          Analytics collects information such as how often users visit the site, what pages
          they visit, and what other sites they used prior to coming to our site. We use this
          information solely to improve our content and user experience. Google Analytics
          collects the IP address assigned to you on the date you visit the site but does not
          combine it with any other data held by Google.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Amazon Affiliate Links</h2>
        <p>
          Anti-Gravity is a participant in the Amazon Services LLC Associates Program, an
          affiliate advertising program designed to provide a means for sites to earn
          advertising fees by advertising and linking to Amazon.com. When you click on an
          Amazon affiliate link on our site and make a purchase, Amazon may collect information
          about your purchase in accordance with their own privacy policy.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Cookies</h2>
        <p>
          Our site may use cookies through third-party services like Google Analytics and
          Amazon. Cookies are small files stored on your device that help these services
          function properly. You can instruct your browser to refuse all cookies or to
          indicate when a cookie is being sent. However, if you do not accept cookies, some
          portions of our site may not function properly.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Third-Party Links</h2>
        <p>
          Our site contains links to other websites, including Amazon.com. We are not
          responsible for the privacy practices of these external sites. We encourage you to
          review their privacy policies.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Changes to This Policy</h2>
        <p>
          We may update this privacy policy from time to time. We will notify you of any
          changes by posting the new policy on this page and updating the &quot;last updated&quot; date.
        </p>

        <h2 className="text-xl font-semibold text-white mt-8 mb-3">Contact Us</h2>
        <p>
          If you have any questions about this privacy policy, please contact us at{' '}
          <a href="mailto:hello@pilottools.ai" className="text-emerald-400 hover:text-emerald-300 transition-colors">
            hello@pilottools.ai
          </a>
        </p>
      </div>
    </div>
  )
}
