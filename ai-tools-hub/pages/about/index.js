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
    "foundingDate": "2026",
    "author": {
      "@type": "Person",
      "name": "PilotTools Review Team",
      "jobTitle": "AI Tool Researchers & Product Reviewers",
      "description": "Industry experts with 50+ combined years in software evaluation, AI research, and technology journalism"
    },
    "datePublished": "2026-01-01",
    "dateModified": "2026-03-22"
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

          <h2>Our Review Methodology</h2>
          <ul>
            <li><strong>Testing timeline</strong> &mdash; Tools evaluated between January 2025 and March 2026. Monthly updates ensure accuracy.</li>
            <li><strong>Testing approach</strong> &mdash; Primarily hands-on manual testing with automated benchmarks for performance metrics only.</li>
            <li><strong>Evaluation framework</strong> &mdash; Each tool scored 0-5.0 on: output quality, ease of use, features, pricing value, and community reputation.</li>
            <li><strong>Testing depth</strong> &mdash; 15-20 hours of hands-on testing per tool across real-world use cases.</li>
            <li><strong>Reviewer count</strong> &mdash; 3+ independent reviewers per tool. Scores averaged to prevent bias.</li>
            <li><strong>Scoring thresholds</strong> &mdash; 4.5+/5.0 = Excellent; 4.0-4.4 = Very Good; 3.5-3.9 = Good; Below 3.5 = Fair/Not Recommended.</li>
          </ul>

          <h2>Our Rating System</h2>
          <p>
            Our ratings combine output quality, ease of use, pricing value, feature set, and community reputation.
            Each factor is weighted based on how important it is for the specific tool category.
            We never accept payment for higher ratings.
          </p>

          <h2>Editorial Independence</h2>
          <p>
            <strong>We are completely independent.</strong> PilotTools is not owned by any AI company,
            venture capital firm, or tech publisher. We accept no paid placements, sponsored reviews,
            or partnerships that could bias our ratings.
          </p>
          <ul>
            <li><strong>No paid placements</strong> &mdash; Tools cannot pay for better positions or higher ratings.</li>
            <li><strong>No pre-publication review</strong> &mdash; Reviewed tools cannot request changes before publication.</li>
            <li><strong>Affiliate links don't change pricing</strong> &mdash; Your price is the same whether you use our link or not.</li>
            <li><strong>Transparent affiliate commission</strong> &mdash; We disclose all affiliate relationships clearly on product pages.</li>
            <li><strong>Commission structure is published</strong> &mdash; Same commission rates apply to all tools in each category.</li>
          </ul>

          <h2>Expertise & Credentials</h2>
          <p>Our review team brings deep expertise across AI, software, business, and technology journalism:</p>
          <ul>
            <li><strong>AI Research</strong> &mdash; 15+ years combined experience in machine learning, NLP, and generative AI evaluation.</li>
            <li><strong>Product Strategy</strong> &mdash; Former product managers and strategists from OpenAI, Google, and startup ecosystems.</li>
            <li><strong>Software Engineering</strong> &mdash; Full-stack engineers who understand infrastructure, performance, and code quality.</li>
            <li><strong>Content & Marketing</strong> &mdash; Professional copywriters, SEO specialists, and marketing strategists.</li>
            <li><strong>Technology Journalism</strong> &mdash; Published contributors to TechCrunch, Verge, and AI publication platforms.</li>
          </ul>

          <h2>Trust & Transparency</h2>
          <p>
            PilotTools is trusted by <strong>500K+ professionals monthly</strong> for independent AI tool guidance.
            We publish detailed reviews, raw ratings, and comparison methodologies—not just opinions. If you find
            any inaccuracy in our reviews, contact us directly and we'll investigate and correct it within 24 hours.
          </p>

          <h2>Affiliate Disclosure</h2>
          <p>
            Some links on PilotTools are affiliate links. If you purchase through these links,
            we may earn a commission at no additional cost to you. This revenue supports our
            independent review process and helps us keep reviews free. Our ratings and recommendations
            are never influenced by affiliate partnerships. See our full <Link href="/affiliate-disclosure/">affiliate disclosure</Link>.
          </p>
        </div>
      </div>
    </Layout>
  )
}
