import Layout from '../../components/Layout'

const SITE_URL = 'https://pilottools.ai'

export default function EditorialGuidelines() {
  return (
    <Layout
      title="Editorial Guidelines - PilotTools"
      description="How PilotTools reviews AI tools: our testing methodology, scoring criteria, editorial independence policy, and conflict of interest disclosure."
      canonical={`${SITE_URL}/editorial-guidelines/`}
    >
      <div className="max-w-3xl mx-auto px-4 py-12">
        <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">Editorial Guidelines</h1>
        <p className="text-lg text-dt-muted mb-8">How we evaluate, rate, and recommend AI tools.</p>

        <div className="prose prose-lg max-w-none">
          <h2>Our Testing Process</h2>
          <p>
            Every tool listed on PilotTools goes through a structured evaluation before we publish any recommendation.
            We do not accept payment for reviews, sponsored placements, or preferential treatment. Here is exactly how
            our process works:
          </p>
          <ol>
            <li><strong>Discovery</strong> — We identify new tools through product launches, user requests, and competitive analysis. We track 50+ AI tool categories.</li>
            <li><strong>Hands-On Testing</strong> — A team member uses the tool on real projects for a minimum of 15 hours across at least 5 different use cases relevant to the tool&apos;s category.</li>
            <li><strong>Feature Mapping</strong> — We document every feature, integration, and limitation. We compare feature sets against the top 3-5 competitors in the same category.</li>
            <li><strong>Pricing Analysis</strong> — We calculate true cost of ownership including hidden fees, per-seat costs, API charges, and overage fees. We track pricing changes monthly.</li>
            <li><strong>Scoring</strong> — Each tool is scored 0-5.0 across five dimensions: Output Quality, Ease of Use, Feature Set, Pricing Value, and Community Reputation.</li>
            <li><strong>Peer Review</strong> — Reviews are checked for accuracy and bias before publication.</li>
            <li><strong>Publication + Updates</strong> — Published reviews are re-evaluated quarterly or when significant updates ship.</li>
          </ol>

          <h2>Scoring Criteria</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="py-2">Dimension</th>
                <th className="py-2">Weight</th>
                <th className="py-2">What We Evaluate</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-dark-border">
                <td className="py-2">Output Quality</td>
                <td className="py-2">30%</td>
                <td className="py-2">Accuracy, reliability, consistency of results across multiple tests</td>
              </tr>
              <tr className="border-b border-dark-border">
                <td className="py-2">Ease of Use</td>
                <td className="py-2">20%</td>
                <td className="py-2">Onboarding time, UI intuitiveness, documentation quality</td>
              </tr>
              <tr className="border-b border-dark-border">
                <td className="py-2">Feature Set</td>
                <td className="py-2">20%</td>
                <td className="py-2">Breadth of capabilities, integrations, customization options</td>
              </tr>
              <tr className="border-b border-dark-border">
                <td className="py-2">Pricing Value</td>
                <td className="py-2">20%</td>
                <td className="py-2">Cost relative to capabilities, free tier generosity, pricing transparency</td>
              </tr>
              <tr className="border-b border-dark-border">
                <td className="py-2">Community</td>
                <td className="py-2">10%</td>
                <td className="py-2">User reviews, support responsiveness, update frequency, company stability</td>
              </tr>
            </tbody>
          </table>

          <h2>Conflict of Interest Policy</h2>
          <ul>
            <li>We never accept payment for reviews or ratings.</li>
            <li>Affiliate commissions do not influence our scores. Tools with no affiliate program receive the same evaluation rigor as those with one.</li>
            <li>If a tool offers us free access for testing, we disclose it. Free access does not guarantee a positive review.</li>
            <li>Our editorial team does not have access to revenue data from individual affiliate links — they cannot see which tools earn us more commission.</li>
            <li>We will always disclose if we have a financial relationship with any tool we review.</li>
          </ul>

          <h2>Update Policy</h2>
          <p>
            AI tools evolve rapidly. We commit to:
          </p>
          <ul>
            <li>Re-testing our top picks every quarter</li>
            <li>Updating reviews within 48 hours when major features ship or pricing changes</li>
            <li>Marking reviews with &quot;Last Updated&quot; dates so you know how current our information is</li>
            <li>Removing tools that shut down or degrade significantly in quality</li>
          </ul>

          <h2>How to Request a Review</h2>
          <p>
            If you&apos;ve built an AI tool and want us to review it, <a href="/contact/">contact us</a>.
            We evaluate all submissions but cannot guarantee coverage. We prioritize tools that serve
            our audience of creators, freelancers, and small business owners. Requesting a review does not
            guarantee a positive outcome — we publish honest assessments regardless of the tool maker&apos;s relationship with us.
          </p>

          <h2>Corrections</h2>
          <p>
            Found something inaccurate? We take corrections seriously. Email us at hello@pilottools.ai
            with the specific issue and we&apos;ll investigate within 24 hours. All corrections are logged and timestamped.
          </p>
        </div>
      </div>
    </Layout>
  )
}
