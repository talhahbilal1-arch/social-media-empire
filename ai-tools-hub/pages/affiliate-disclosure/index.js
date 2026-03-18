import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'

export default function AffiliateDisclosurePage() {
  return (
    <Layout
      title="Affiliate Disclosure"
      description="PilotTools affiliate disclosure. Learn how we earn revenue and how it affects our reviews."
      canonical="https://pilottools.ai/affiliate-disclosure/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Affiliate Disclosure' }]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-dt mb-8">Affiliate Disclosure</h1>
        <div className="prose prose-lg max-w-none">
          <p><strong>Last updated: March 18, 2026</strong></p>

          <p>
            PilotTools (pilottools.ai) is an independently operated AI tool review and comparison website.
            Some of the links on this site are affiliate links, meaning we may earn a commission if you
            click through and make a purchase or sign up for a service. This comes at no additional cost to you.
          </p>

          <h2>How Affiliate Links Work</h2>
          <p>
            When you click an affiliate link on PilotTools and subsequently purchase a product or service,
            the company may pay us a small referral fee. This fee is paid by the company, not by you,
            and does not increase the price you pay.
          </p>

          <h2>Our Independence</h2>
          <p>
            Affiliate partnerships do <strong>not</strong> influence our reviews, ratings, or recommendations.
            Our editorial team evaluates every tool independently based on features, pricing, ease of use,
            and overall value. Tools that pay higher commissions do not receive higher ratings.
          </p>

          <h2>FTC Compliance</h2>
          <p>
            In accordance with the Federal Trade Commission (FTC) guidelines, we disclose that PilotTools
            participates in affiliate marketing programs. All affiliate links are marked with appropriate
            rel=&quot;sponsored&quot; attributes and disclosure notices are displayed on pages containing affiliate links.
          </p>

          <h2>Questions?</h2>
          <p>
            If you have questions about our affiliate relationships, please contact us at{' '}
            <a href="mailto:hello@pilottools.ai">hello@pilottools.ai</a>.
          </p>
        </div>
      </div>
    </Layout>
  )
}
