import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'

const SITE_URL = 'https://pilottools.ai'

const STATS = [
  { value: '460+', label: 'AI Tools Reviewed' },
  { value: '4,800+', label: 'Hours of Testing' },
  { value: '3+', label: 'Years Tracking AI' },
  { value: '0', label: 'Paid Placements. Ever.' },
]

const METHODOLOGY_STEPS = [
  {
    num: '01',
    title: 'Discovery',
    desc: 'We track product launches, user requests, and competitive shifts across 50+ AI categories. A tool must have genuine user traction or solve a specific problem before we invest testing time.',
  },
  {
    num: '02',
    title: 'Hands-On Testing',
    desc: 'Every tool is used on real-world tasks for a minimum of 15 hours across at least 5 distinct use cases. No synthetic benchmarks. No screenshots from marketing pages.',
  },
  {
    num: '03',
    title: 'Feature Mapping',
    desc: 'We document every feature, integration, and hard limitation — then compare against the top 3–5 competitors in the same category, side by side.',
  },
  {
    num: '04',
    title: 'Pricing Analysis',
    desc: 'We calculate true cost of ownership: monthly and annual rates, per-seat charges, API fees, overage costs, and hidden upgrade requirements. We track pricing changes monthly.',
  },
  {
    num: '05',
    title: 'Scoring',
    desc: 'Each tool receives a 0–5.0 score across five weighted dimensions: Output Quality (30%), Ease of Use (20%), Feature Set (20%), Pricing Value (20%), and Community Reputation (10%).',
  },
  {
    num: '06',
    title: 'Peer Review',
    desc: 'Before publication, every review is checked for factual accuracy and editorial bias by a second reviewer who did not conduct the primary testing.',
  },
  {
    num: '07',
    title: 'Ongoing Updates',
    desc: 'AI tools ship major updates constantly. We re-evaluate top picks quarterly, and update reviews within 48 hours when significant pricing or feature changes ship.',
  },
]

const CREDENTIALS = [
  {
    icon: '🎓',
    title: 'ISSA Certified Professional',
    desc: 'International Sports Sciences Association certification with 6+ years of professional practice. Systematic, evidence-based methodology applied to every tool evaluation.',
  },
  {
    icon: '🏢',
    title: 'Equinox & SBM Fitness',
    desc: 'Professional experience in performance environments where data, precision, and repeatable systems matter. That same rigor is applied to every AI tool review.',
  },
  {
    icon: '🤖',
    title: 'AI Automation Practitioner',
    desc: 'Built production AI workflows for content pipelines, scheduling systems, and client automation. We test tools the way professionals actually use them, not as tourists.',
  },
  {
    icon: '📊',
    title: '3+ Years in the AI Tools Space',
    desc: 'Tracking the AI landscape since 2022 across writing, coding, image generation, video, and marketing — before most review sites existed.',
  },
]

const SCORE_BANDS = [
  { range: '4.5 – 5.0', label: 'Excellent', color: 'text-green-400' },
  { range: '4.0 – 4.4', label: 'Very Good', color: 'text-accent' },
  { range: '3.5 – 3.9', label: 'Good', color: 'text-yellow-400' },
  { range: '< 3.5', label: 'Not Recommended', color: 'text-red-400' },
]

const SCORE_DIMS = [
  ['Output Quality', '30%', 'Accuracy, reliability, and consistency of results across multiple test runs'],
  ['Ease of Use', '20%', 'Onboarding time, UI intuitiveness, documentation quality'],
  ['Feature Set', '20%', 'Breadth of capabilities, integrations, customization options'],
  ['Pricing Value', '20%', 'Cost relative to capabilities, free tier generosity, pricing transparency'],
  ['Community', '10%', 'User reviews, support responsiveness, update frequency, company stability'],
]

export default function AboutPage() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'AboutPage',
    name: 'About PilotTools',
    url: `${SITE_URL}/about/`,
    description:
      'PilotTools is an independent AI tool review site founded by Talhah Bilal, ISSA-certified professional and automation systems expert. Every tool is hands-on tested.',
    mainEntity: {
      '@type': 'Person',
      name: 'Talhah Bilal',
      jobTitle: 'Founder & Lead Reviewer',
      description:
        'ISSA-certified professional with 6+ years building AI-powered workflows. Former Equinox and SBM Fitness instructor turned full-time AI tools researcher.',
      url: `${SITE_URL}/about/`,
      sameAs: ['https://github.com/talhahbilal1-arch'],
      worksFor: {
        '@type': 'Organization',
        name: 'PilotTools',
        url: SITE_URL,
      },
    },
  }

  return (
    <Layout
      title="About PilotTools — Independent AI Tool Reviews by Talhah Bilal"
      description="PilotTools was built by Talhah Bilal, ISSA-certified professional with 6+ years in AI automation. 460+ tools reviewed, 4,800+ hours of hands-on testing. Zero paid placements."
      canonical={`${SITE_URL}/about/`}
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'About' }]} />

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="text-center mb-12">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-accent/10 text-accent border border-accent/20 mb-6">
            Independent &bull; Hands-On Tested &bull; Zero Paid Placements
          </span>
          <h1 className="text-3xl md:text-5xl font-bold text-dt mb-5 leading-tight">
            Honest AI Tool Reviews<br className="hidden md:block" /> From Someone Who Actually Uses Them
          </h1>
          <p className="text-lg text-dt-muted max-w-2xl mx-auto">
            PilotTools exists because the AI tools space is full of affiliate-first &ldquo;review&rdquo; sites that
            rank tools by commission rate, not quality. We do the opposite.
          </p>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-16">
          {STATS.map(({ value, label }) => (
            <div key={label} className="bg-dark-surface border border-dark-border rounded-xl p-5 text-center">
              <div className="text-2xl md:text-3xl font-extrabold text-accent mb-1">{value}</div>
              <div className="text-xs text-dt-muted leading-snug">{label}</div>
            </div>
          ))}
        </div>

        {/* Founder story */}
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 md:p-10 mb-14">
          <div className="flex items-start gap-6 mb-6">
            <div
              className="flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold text-dark-bg"
              style={{ backgroundColor: '#00d4ff' }}
              aria-label="Talhah Bilal avatar"
            >
              TB
            </div>
            <div>
              <h2 className="text-xl font-bold text-dt">Talhah Bilal</h2>
              <p className="text-dt-muted text-sm">
                Founder &amp; Lead Reviewer &bull; ISSA Certified &bull; Former Equinox &bull; SBM Fitness
              </p>
              <p className="text-dt-muted text-sm mt-1">
                hello@pilottools.ai &bull;{' '}
                <Link href="/contact/" className="text-accent hover:text-cyan-300 transition-colors">
                  Contact
                </Link>
              </p>
            </div>
          </div>

          <div className="prose prose-lg max-w-none">
            <h3 className="text-dt font-bold text-xl mb-3">Why I Built PilotTools</h3>
            <p className="text-dt-muted mb-4">
              I was a personal trainer at Equinox when I started building AI-powered systems for my
              coaching business in 2022. Client check-in automation, content pipelines, lead follow-up
              sequences &mdash; I needed AI tools that actually worked, not ones with slick landing pages.
            </p>
            <p className="text-dt-muted mb-4">
              The problem: every &ldquo;review&rdquo; I found ranked tools by who paid the highest affiliate
              commission. I spent thousands of dollars on tools that underdelivered because the people
              recommending them had never opened them outside a 10-minute demo.
            </p>
            <p className="text-dt-muted mb-4">
              I built PilotTools to fix that. Every tool on this site has been tested by me personally on
              real workflows &mdash; writing, coding, automation, image generation, video, marketing. My ISSA
              background and years of systematic client tracking taught me to be rigorous about evidence.
              I apply that same standard to AI tools.
            </p>
            <p className="text-dt-muted">
              PilotTools now covers 460+ tools across 10 categories, with 4,800+ cumulative hours of
              hands-on testing. Our only revenue is affiliate commissions on tools we genuinely
              recommend. We turn down paid placement requests. Our ratings have never been for sale.
            </p>
          </div>
        </div>

        {/* Credentials */}
        <div className="mb-14">
          <h2 className="text-2xl font-bold text-dt mb-6">Credentials &amp; Background</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {CREDENTIALS.map(({ icon, title, desc }) => (
              <div key={title} className="bg-dark-surface border border-dark-border rounded-xl p-5">
                <div className="text-2xl mb-3">{icon}</div>
                <h3 className="font-semibold text-dt mb-2">{title}</h3>
                <p className="text-sm text-dt-muted leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Testing methodology */}
        <div className="mb-14">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-dt">Our 7-Step Testing Process</h2>
            <Link href="/editorial-guidelines/" className="text-accent hover:text-cyan-300 text-sm font-medium transition-colors">
              Full guidelines &rarr;
            </Link>
          </div>
          <div className="space-y-4">
            {METHODOLOGY_STEPS.map((step) => (
              <div key={step.num} className="flex gap-5 bg-dark-surface border border-dark-border rounded-xl p-5">
                <div className="flex-shrink-0 text-accent font-mono font-bold text-sm pt-0.5">
                  {step.num}
                </div>
                <div>
                  <h3 className="font-semibold text-dt mb-1">{step.title}</h3>
                  <p className="text-sm text-dt-muted leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Editorial Independence */}
        <div className="mb-14">
          <h2 className="text-2xl font-bold text-dt mb-6">Editorial Independence</h2>
          <div className="bg-dark-surface border border-dark-border rounded-2xl p-8">
            <p className="text-dt-muted mb-4">
              <strong className="text-dt">PilotTools is not owned by any AI company, VC firm, or tech publisher.</strong>{' '}
              We accept no paid placements, sponsored reviews, or partnerships that change ratings.
            </p>
            <ul className="space-y-3 text-dt-muted">
              {[
                ['No paid rankings', 'Tools cannot pay for better positions or higher scores. Period.'],
                ['No pre-publication review by vendors', 'Tool makers cannot request changes before we publish.'],
                ['Affiliate commissions don\'t influence scores', 'Tools with no affiliate program get the same evaluation rigor as those paying 40% recurring.'],
                ['Free access doesn\'t guarantee positive reviews', 'If a tool gives us free access, we disclose it and review it the same way.'],
                ['Corrections are timestamped', 'Found an error? Email us and we update within 48 hours with a public timestamp.'],
              ].map(([bold, rest]) => (
                <li key={bold} className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span><strong className="text-dt">{bold}</strong> &mdash; {rest}</span>
                </li>
              ))}
            </ul>
            <p className="text-dt-muted mt-4">
              Our only revenue comes from affiliate commissions on tools we genuinely recommend. That
              alignment is intentional &mdash; your success with the right tool is the only way we build a
              sustainable business.
            </p>
          </div>
        </div>

        {/* Scoring system */}
        <div className="mb-14">
          <h2 className="text-2xl font-bold text-dt mb-6">Our Rating System</h2>
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-dark-border">
                  <th className="py-3 pr-4 font-semibold text-dt">Dimension</th>
                  <th className="py-3 pr-4 font-semibold text-dt">Weight</th>
                  <th className="py-3 font-semibold text-dt">What We Evaluate</th>
                </tr>
              </thead>
              <tbody className="text-dt-muted">
                {SCORE_DIMS.map(([dim, weight, what]) => (
                  <tr key={dim} className="border-b border-dark-border">
                    <td className="py-3 pr-4 font-medium text-dt">{dim}</td>
                    <td className="py-3 pr-4">
                      <span className="badge-blue">{weight}</span>
                    </td>
                    <td className="py-3">{what}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            {SCORE_BANDS.map(({ range, label, color }) => (
              <div key={range} className="bg-dark-surface border border-dark-border rounded-lg p-3">
                <div className={`font-bold ${color}`}>{range}</div>
                <div className="text-dt-muted text-xs mt-0.5">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 text-center">
          <h2 className="text-xl font-bold text-dt mb-3">Questions, Corrections, or Partnerships?</h2>
          <p className="text-dt-muted mb-6 max-w-xl mx-auto">
            Found an error in a review? Have an AI tool you&apos;d like us to evaluate? Interested in an
            affiliate partnership? We respond within 1&ndash;2 business days.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/contact/" className="btn-primary">Contact Us</Link>
            <Link href="/editorial-guidelines/" className="btn-secondary">Editorial Guidelines</Link>
          </div>
          <p className="mt-4 text-sm text-dt-muted">
            Email:{' '}
            <a href="mailto:hello@pilottools.ai" className="text-accent hover:text-cyan-300 transition-colors">
              hello@pilottools.ai
            </a>
          </p>
        </div>
      </section>
    </Layout>
  )
}
