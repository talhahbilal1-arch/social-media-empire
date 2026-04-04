import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'

export default function TermsPage() {
  return (
    <Layout
      title="Terms of Service"
      description="PilotTools terms of service. Read our terms and conditions for using pilottools.ai."
      canonical="https://pilottools.ai/terms/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Terms of Service' }]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-dt mb-8">Terms of Service</h1>
        <div className="prose prose-lg max-w-none">
          <p><strong>Last updated: April 3, 2026</strong></p>

          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using PilotTools (pilottools.ai), you agree to be bound by these Terms of Service.
            If you do not agree to these terms, please do not use our website.
          </p>

          <h2>2. Description of Service</h2>
          <p>
            PilotTools is an AI tool review and comparison website. We provide editorial reviews, pricing comparisons,
            and recommendations to help users make informed decisions about AI tools and software products.
          </p>

          <h2>3. Use of Website</h2>
          <p>You agree to use PilotTools only for lawful purposes and in accordance with these Terms. You agree not to:</p>
          <ul>
            <li>Use the site in any way that violates applicable laws or regulations</li>
            <li>Attempt to gain unauthorized access to any portion of the website</li>
            <li>Use automated systems to scrape or extract content without permission</li>
            <li>Interfere with the proper functioning of the website</li>
          </ul>

          <h2>4. Intellectual Property</h2>
          <p>
            All content on PilotTools, including text, graphics, logos, and software, is the property of
            PilotTools or its content suppliers and is protected by copyright and intellectual property laws.
            You may not reproduce, distribute, or create derivative works without our written permission.
          </p>

          <h2>5. Reviews and Recommendations</h2>
          <p>
            Our reviews and recommendations are based on our editorial assessment and are provided for
            informational purposes only. We make no guarantees about the accuracy, completeness, or
            reliability of any third-party products or services reviewed on our site. Product features,
            pricing, and availability may change without notice.
          </p>

          <h2>6. Affiliate Links and Advertising</h2>
          <p>
            PilotTools contains affiliate links and advertisements. When you click on affiliate links and
            make a purchase, we may earn a commission at no additional cost to you. Advertisements displayed
            on our site are served by third-party advertising networks including Google AdSense. These
            advertising partners may use cookies to serve relevant ads based on your browsing behavior.
            See our <a href="/privacy/">Privacy Policy</a> and{' '}
            <a href="/affiliate-disclosure/">Affiliate Disclosure</a> for more details.
          </p>

          <h2>7. Third-Party Links</h2>
          <p>
            Our website contains links to third-party websites and services. We are not responsible for
            the content, privacy practices, or terms of any third-party sites. Visiting these links is
            at your own risk.
          </p>

          <h2>8. Disclaimer of Warranties</h2>
          <p>
            PilotTools is provided &quot;as is&quot; and &quot;as available&quot; without any warranties of any kind,
            either express or implied. We do not warrant that the website will be uninterrupted, error-free,
            or free of viruses or other harmful components.
          </p>

          <h2>9. Limitation of Liability</h2>
          <p>
            To the fullest extent permitted by law, PilotTools shall not be liable for any indirect,
            incidental, special, consequential, or punitive damages arising from your use of the website
            or reliance on any information provided.
          </p>

          <h2>10. Modifications to Terms</h2>
          <p>
            We reserve the right to modify these Terms of Service at any time. Changes will be posted on
            this page with an updated revision date. Your continued use of the website after changes
            constitutes acceptance of the modified terms.
          </p>

          <h2>11. Governing Law</h2>
          <p>
            These Terms shall be governed by and construed in accordance with the laws of the State of
            California, United States, without regard to conflict of law principles.
          </p>

          <h2>12. Contact</h2>
          <p>
            For questions about these Terms of Service, contact us at{' '}
            <a href="mailto:hello@pilottools.ai">hello@pilottools.ai</a>.
          </p>
        </div>
      </div>
    </Layout>
  )
}
