import Layout from '../../components/Layout'
import Link from 'next/link'
import { getAllComparisons } from '../../lib/tools'

export default function ComparePage({ comparisons }) {
  return (
    <Layout
      title="AI Tool Comparisons - Side-by-Side Reviews"
      description="Compare the best AI tools side-by-side. ChatGPT vs Claude, Jasper vs Writesonic, Midjourney vs Runway, and more detailed comparisons."
      canonical="https://ai-tools-hub-lilac.vercel.app/compare/"
    >
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Tool Comparisons</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Detailed side-by-side comparisons to help you choose the right AI tool for your needs.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {comparisons.map(comp => (
            <Link
              key={comp.slug}
              href={`/compare/${comp.slug}/`}
              className="card hover:border-primary-300 group"
            >
              <div className="flex items-center justify-center space-x-4 mb-4">
                <span className="text-xl font-bold text-gray-900">
                  {comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
                <span className="text-primary-500 font-bold text-lg">VS</span>
                <span className="text-xl font-bold text-gray-900">
                  {comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              </div>
              <h2 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors text-center mb-3">
                {comp.title}
              </h2>
              <p className="text-sm text-gray-600 text-center">{comp.verdict}</p>
              <div className="mt-4 text-center">
                <span className="text-primary-600 font-medium text-sm">Read Full Comparison &rarr;</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}

export async function getStaticProps() {
  return {
    props: { comparisons: getAllComparisons() },
  }
}
