import { useState } from 'react'
import Layout from '../../components/Layout'
import ToolCard from '../../components/ToolCard'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'
import { getAllTools, getAllCategories, getToolsByCategory } from '../../lib/tools'

const BUDGET_OPTIONS = [
  { value: 'free', label: 'Free only', description: 'I need a free tier' },
  { value: 'budget', label: 'Under $25/mo', description: 'Budget-friendly options' },
  { value: 'any', label: 'Any budget', description: 'Show me the best regardless of price' },
]

export default function QuizPage({ allTools, categories }) {
  const [step, setStep] = useState(1)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [budget, setBudget] = useState(null)
  const [results, setResults] = useState([])

  const handleCategorySelect = (catSlug) => {
    setSelectedCategory(catSlug)
    setStep(2)
  }

  const handleBudgetSelect = (budgetValue) => {
    setBudget(budgetValue)
    let filtered = selectedCategory
      ? allTools.filter(t => t.categories.includes(selectedCategory))
      : allTools

    if (budgetValue === 'free') {
      filtered = filtered.filter(t => t.pricing.free_tier)
    } else if (budgetValue === 'budget') {
      filtered = filtered.filter(t => t.pricing.starting_price === 0 || (t.pricing.starting_price && t.pricing.starting_price <= 25))
    }

    const sorted = filtered.sort((a, b) => b.rating - a.rating).slice(0, 3)
    setResults(sorted)
    setStep(3)
  }

  const reset = () => { setStep(1); setSelectedCategory(null); setBudget(null); setResults([]) }

  return (
    <Layout
      title="AI Tool Finder Quiz - Find Your Perfect AI Tool"
      description="Answer 2 quick questions and get personalized AI tool recommendations based on your needs and budget."
      canonical="https://pilottools.ai/quiz/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Tool Finder' }]} />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-12">
          {[1, 2, 3].map(s => (
            <div key={s} className={`h-2 w-16 rounded-full ${s <= step ? 'bg-accent' : 'bg-dark-border'}`} />
          ))}
        </div>

        {step === 1 && (
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-dt mb-4">What do you need AI for?</h1>
            <p className="text-dt-muted mb-8">Pick a category to narrow down your recommendations.</p>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-3xl mx-auto">
              {categories.map(cat => (
                <button
                  key={cat.slug}
                  onClick={() => handleCategorySelect(cat.slug)}
                  className="p-4 bg-dark-surface border border-dark-border rounded-xl text-dt hover:border-accent/40 hover:shadow-glow transition-all text-left"
                >
                  <span className="font-medium">{cat.name.replace('AI ', '')}</span>
                </button>
              ))}
              <button
                onClick={() => handleCategorySelect(null)}
                className="p-4 bg-dark-surface border border-dark-border rounded-xl text-dt hover:border-accent/40 hover:shadow-glow transition-all text-left"
              >
                <span className="font-medium">Show me everything</span>
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="text-center">
            <h2 className="text-3xl font-bold text-dt mb-4">What is your budget?</h2>
            <p className="text-dt-muted mb-8">This helps us find tools that fit your wallet.</p>
            <div className="grid sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
              {BUDGET_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => handleBudgetSelect(opt.value)}
                  className="p-5 bg-dark-surface border border-dark-border rounded-xl text-dt hover:border-accent/40 hover:shadow-glow transition-all"
                >
                  <span className="font-bold block mb-1">{opt.label}</span>
                  <span className="text-sm text-dt-muted">{opt.description}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-dt mb-4">Your Top Recommendations</h2>
              <p className="text-dt-muted">Based on your needs, here are the best tools for you.</p>
            </div>

            {results.length > 0 ? (
              <div className="grid md:grid-cols-3 gap-6 mb-10">
                {results.map((tool, idx) => (
                  <ToolCard key={tool.slug} tool={tool} rank={idx + 1} />
                ))}
              </div>
            ) : (
              <p className="text-center text-dt-muted mb-10">No exact matches found. Try broadening your budget or category.</p>
            )}

            <div className="text-center space-x-4">
              <button onClick={reset} className="btn-secondary">Start Over</button>
              <Link href="/compare/" className="btn-primary">Compare These Tools</Link>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export async function getStaticProps() {
  return {
    props: {
      allTools: getAllTools(),
      categories: getAllCategories(),
    },
  }
}
