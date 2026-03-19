import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'
import { getAllComparisons } from '../../lib/tools'

export default function ComparePage({ comparisons }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': 'AI Tool Comparisons',
    'description': 'Detailed side-by-side comparisons to help you choose the right AI tool for your needs.',
    'url': 'https://pilottools.ai/compare/',
    'numberOfItems': comparisons.length,
  }

  return (
    <Layout
      title="AI Tool Comparisons - Side-by-Side Reviews"
      description="Compare the best AI tools side-by-side. ChatGPT vs Claude, Jasper vs Writesonic, Midjourney vs Runway, and more detailed comparisons."
      canonical="https://pilottools.ai/compare/"
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Compare' }]} />

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-dt mb-4">AI Tool Comparisons</h1>
          <p className="text-lg text-dt-muted max-w-2xl mx-auto">
            Detailed side-by-side comparisons to help you choose the right AI tool for your needs.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {comparisons.map(comp => (
            <Link key={comp.slug} href={`/compare/${comp.slug}/`} className="card hover:border-accent/30 group">
              <div className="flex items-center justify-center space-x-4 mb-4">
                <span className="text-xl font-bold text-dt">{comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="text-accent font-bold text-lg">VS</span>
                <span className="text-xl font-bold text-dt">{comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
              </div>
              <h2 className="text-lg font-semibold text-dt group-hover:text-accent transition-colors text-center mb-3">{comp.title}</h2>
              <p className="text-sm text-dt-muted text-center">{comp.verdict}</p>
              <div className="mt-4 text-center">
                <span className="text-accent font-medium text-sm">Read Full Comparison &rarr;</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}

export async function getStaticProps() {
  return { props: { comparisons: getAllComparisons() } }
}
