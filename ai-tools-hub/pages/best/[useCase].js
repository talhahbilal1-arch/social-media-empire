import Layout from '../../components/Layout'
import ToolCard from '../../components/ToolCard'
import FAQAccordion from '../../components/FAQAccordion'
import Breadcrumbs from '../../components/Breadcrumbs'
import AdSlot from '../../components/AdSlot'
import { getAllUseCases, getToolsByUseCase } from '../../lib/tools'

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

function unslugify(slug) {
  return slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

export default function BestForPage({ useCase, useCaseSlug, tools }) {
  const displayName = useCase || unslugify(useCaseSlug)

  const faqs = [
    { question: `What is the best AI tool for ${displayName.toLowerCase()}?`, answer: tools.length > 0 ? `Based on our testing, ${tools[0].name} (${tools[0].rating}/5) is the top pick for ${displayName.toLowerCase()}.` : `We're still evaluating tools for this use case.` },
    { question: `Are there free AI tools for ${displayName.toLowerCase()}?`, answer: (() => { const free = tools.filter(t => t.pricing.free_tier); return free.length > 0 ? `Yes! ${free.map(t => t.name).join(', ')} ${free.length === 1 ? 'offers' : 'offer'} free tiers.` : 'Currently, all top tools for this use case require a paid plan.' })() },
    { question: `How do I choose an AI tool for ${displayName.toLowerCase()}?`, answer: `Consider your budget, the specific features you need, integration with your existing workflow, and output quality. Our reviews rate each tool on these factors.` },
  ]

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    'name': `Best AI Tools for ${displayName}`,
    'numberOfItems': tools.length,
    'itemListElement': tools.map((tool, i) => ({
      '@type': 'ListItem',
      'position': i + 1,
      'name': tool.name,
      'url': `https://pilottools.ai/tools/${tool.slug}/`,
    })),
  }

  return (
    <Layout
      title={`Best AI Tools for ${displayName} in 2026`}
      description={`Compare the best AI tools for ${displayName.toLowerCase()} in 2026. Ranked by features, pricing, and real user ratings.`}
      canonical={`https://pilottools.ai/best/${useCaseSlug}/`}
      structuredData={structuredData}
      robots="noindex,nofollow"
    >
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: `Best for ${displayName}` }
      ]} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">Best AI Tools for {displayName} in 2026</h1>
          <p className="text-lg text-dt-muted">{tools.length} tools ranked by rating, features, and value.</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tools.map((tool, idx) => (
            <ToolCard key={tool.slug} tool={tool} rank={idx + 1} />
          ))}
        </div>

        {tools.length === 0 && (
          <p className="text-center text-dt-muted">No tools found for this use case yet.</p>
        )}

        <AdSlot position="mid-content" />

        <section>
          <h2 className="text-2xl font-bold text-dt mb-4">FAQ</h2>
          <FAQAccordion faqs={faqs} />
        </section>
      </div>
    </Layout>
  )
}

export async function getStaticPaths() {
  const useCases = getAllUseCases()
  return {
    paths: useCases.map(uc => ({ params: { useCase: slugify(uc) } })),
    fallback: false,
  }
}

export async function getStaticProps({ params }) {
  const allUseCases = getAllUseCases()
  const useCase = allUseCases.find(uc => slugify(uc) === params.useCase) || null
  const tools = useCase ? getToolsByUseCase(useCase) : []
  return {
    props: { useCase, useCaseSlug: params.useCase, tools },
  }
}
