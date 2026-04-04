import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'

export default function PrivacyPage() {
  return (
    <Layout
      title="Privacy Policy"
      description="PilotTools privacy policy. Learn how we handle your data, cookies, and analytics."
      canonical="https://pilottools.ai/privacy/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Privacy Policy' }]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-dt mb-8">Privacy Policy</h1>
        <div className="prose prose-lg max-w-none">
          <p><strong>Last updated: April 3, 2026</strong></p>

          <h2>Information We Collect</h2>
          <p>PilotTools collects minimal data to provide and improve our service:</p>
          <ul>
            <li><strong>Analytics data</strong> &mdash; We use Google Analytics 4 (GA4) to collect anonymized usage data including page views, time on site, and device type</li>
            <li><strong>Email addresses</strong> &mdash; Only if you voluntarily subscribe to our newsletter via ConvertKit</li>
            <li><strong>No personal data is sold</strong> &mdash; We do not sell, trade, or share your personal information with third parties for marketing purposes</li>
          </ul>

          <h2>Cookies</h2>
          <p>
            We use first-party cookies through Google Analytics to understand how visitors use our site.
            These cookies do not personally identify you. You can disable cookies in your browser settings.
          </p>

          <h2>Third-Party Services</h2>
          <ul>
            <li><strong>Google Analytics 4</strong> &mdash; Web analytics (privacy-friendly, IP anonymization enabled)</li>
            <li><strong>ConvertKit</strong> &mdash; Email newsletter management (only if you subscribe)</li>
            <li><strong>Netlify</strong> &mdash; Website hosting</li>
            <li><strong>Google AdSense</strong> &mdash; Advertising (displays relevant ads and may use cookies for ad personalization)</li>
          </ul>

          <h2>Affiliate Links</h2>
          <p>
            Our affiliate links may use tracking cookies set by the affiliate partner to attribute referrals.
            These cookies are governed by the respective partner&apos;s privacy policies.
          </p>

          <h2>Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Request access to your personal data</li>
            <li>Request deletion of your data</li>
            <li>Unsubscribe from our newsletter at any time</li>
            <li>Opt out of analytics tracking via browser settings</li>
          </ul>

          <h2>Contact</h2>
          <p>For privacy-related inquiries, contact us at <a href="mailto:hello@pilottools.ai">hello@pilottools.ai</a>.</p>
        </div>
      </div>
    </Layout>
  )
}
