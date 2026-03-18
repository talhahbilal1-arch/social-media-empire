import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'

const SITE_URL = 'https://pilottools.ai'

export default function AboutPage() {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "PilotTools",
    "url": SITE_URL,
    "description": "Independent AI tool reviews and comparisons",
    "foundingDate": "2026"
  }

  return (
    <Layout
      title="About PilotTools - Independent AI Tool Reviews"
      description="Learn about PilotTools: our mission, how we test AI tools, and why our reviews are trusted by thousands of professionals."
      canonical={`${SITE_URL}/about/`}
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'About' }]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">About PilotTools</h1>
          <p className="text-lg text-dt-muted">Independent AI tool reviews you can trust.</p>
        </div>

        <div className="prose prose-lg max-w-none">
          <h2>Our Mission</h2>
          <p>
            The AI tools market is exploding. New products launch every week, each claiming to be the best.
            PilotTools exists to cut through the noise with honest, data-driven reviews that help you
            make informed decisions &mdash; and save you money.
          </p>

          <h2>How We Test</h2>
          <p>Every tool we review goes through a rigorous evaluation process:</p>
          <ul>
            <li><strong>Hands-on testing</strong> &mdash; We use each tool on real-world tasks, not synthetic benchmarks</li>
            <li><strong>Feature analysis</strong> &mdash; We map every feature and compare it against competitors</li>
            <li><strong>Pricing transparency</strong> &mdash; We track pricing changes and hidden costs so you see the real picture</li>
            <li><strong>Regular updates</strong> &mdash; AI tools evolve fast. We re-test and update our reviews regularly</li>
          </ul>

          <h2>Our Rating System</h2>
          <p>
            Our ratings combine output quality, ease of use, pricing value, feature set, and community reputation.
            Each factor is weighted based on how important it is for the specific tool category.
            We never accept payment for higher ratings.
          </p>

          <h2>Affiliate Disclosure</h2>
          <p>
            Some links on PilotTools are affiliate links. If you purchase through these links,
            we may earn a commission at no additional cost to you. This revenue supports our
            independent review process. Our ratings and recommendations are never influenced
            by affiliate partnerships. See our full <Link href="/affiliate-disclosure/">affiliate disclosure</Link>.
          </p>
        </div>
      </div>
    </Layout>
  )
}
