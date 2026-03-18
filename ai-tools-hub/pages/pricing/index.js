import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'
import { getAllTools, formatPrice } from '../../lib/tools'

export default function PricingIndex({ tools }) {
  return (
    <Layout
      title="AI Tool Pricing Comparison 2026"
      description="Compare pricing for 20+ AI tools side by side. Free tiers, starting prices, and best plans compared."
      canonical="https://pilottools.ai/pricing/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Pricing' }]} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-dt mb-4">AI Tool Pricing Guide 2026</h1>
          <p className="text-lg text-dt-muted max-w-2xl mx-auto">
            Compare pricing across all AI tools in one place. Find the best value for your budget.
          </p>
        </div>

        <div className="card p-0 overflow-hidden overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-dark-surface-hover">
                <th className="text-left p-4 font-semibold text-dt border-b border-dark-border">Tool</th>
                <th className="text-center p-4 font-semibold text-dt border-b border-dark-border">Free Tier</th>
                <th className="text-center p-4 font-semibold text-dt border-b border-dark-border">Starting Price</th>
                <th className="text-center p-4 font-semibold text-dt border-b border-dark-border">Rating</th>
                <th className="text-center p-4 font-semibold text-dt border-b border-dark-border">Details</th>
              </tr>
            </thead>
            <tbody>
              {tools.map((tool, idx) => (
                <tr key={tool.slug} className={idx % 2 === 0 ? '' : 'bg-dark-surface-hover/50'}>
                  <td className="p-4 border-b border-dark-border">
                    <Link href={`/tools/${tool.slug}/`} className="font-medium text-dt hover:text-accent transition-colors">{tool.name}</Link>
                    <p className="text-xs text-dt-muted">{tool.company}</p>
                  </td>
                  <td className="p-4 border-b border-dark-border text-center">
                    {tool.pricing.free_tier ? (
                      <span className="badge-green text-xs">Yes</span>
                    ) : (
                      <span className="text-dt-muted text-sm">No</span>
                    )}
                  </td>
                  <td className="p-4 border-b border-dark-border text-center font-bold text-dt">
                    {formatPrice(tool.pricing.starting_price)}
                  </td>
                  <td className="p-4 border-b border-dark-border text-center text-star font-medium">
                    {tool.rating}/5
                  </td>
                  <td className="p-4 border-b border-dark-border text-center">
                    <Link href={`/pricing/${tool.slug}/`} className="text-accent hover:text-cyan-300 text-sm font-medium transition-colors">
                      Full Pricing &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  )
}

export async function getStaticProps() {
  const tools = getAllTools().sort((a, b) => (a.pricing.starting_price || 0) - (b.pricing.starting_price || 0))
  return { props: { tools } }
}
