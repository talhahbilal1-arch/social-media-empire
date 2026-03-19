import Layout from '../components/Layout'
import ToolCard from '../components/ToolCard'
import NewsletterSignup from '../components/NewsletterSignup'
import Search from '../components/Search'
import AdSlot from '../components/AdSlot'
import HeroIllustration, { WaveDivider } from '../components/HeroIllustration'
import Link from 'next/link'
import { getAllTools, getAllCategories, getAllComparisons, getFeaturedTools } from '../lib/tools'

export default function Home({ featuredTools, categories, comparisons, totalTools, allTools }) {
  // Category icons mapping
  const CATEGORY_ICONS = {
    writing: '✍️', coding: '💻', image: '🎨', video: '🎬', marketing: '📈',
    productivity: '⚡', audio: '🎵', seo: '🔍', research: '🔬', design: '🎯'
  }

  // WebSite schema - safe: hardcoded static values only
  const websiteSchema = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "PilotTools",
    "description": "Find the perfect AI tool with honest reviews and comparisons",
    "url": "https://pilottools.ai",
    "potentialAction": {
      "@type": "SearchAction",
      "target": "https://pilottools.ai/?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  })

  return (
    <Layout canonical="https://pilottools.ai/">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-mesh noise-overlay">
        {/* Floating orbs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent/5 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-accent-purple/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '3s' }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent/3 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />

        {/* Neural network illustration — desktop only */}
        <HeroIllustration />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20 text-center relative z-10">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-accent/10 text-accent border border-accent/20 mb-6">
            Updated March 2026 &mdash; {totalTools}+ tools reviewed
          </span>
          <h1 className="text-3xl md:text-6xl font-extrabold text-dt mb-6 leading-tight animate-fade-in-up">
            Stop Wasting Money on the<br className="hidden md:block" /> Wrong AI Tools
          </h1>
          <p className="text-lg md:text-2xl text-dt-muted mb-4 max-w-3xl mx-auto animate-fade-in-up stagger-1">
            Find the perfect AI tool in minutes with honest reviews, real pricing data, and side-by-side comparisons.
          </p>
          <p className="text-dt-muted mb-8 max-w-2xl mx-auto animate-fade-in-up stagger-2">
            Trusted by creators, marketers, and developers who need AI tools that actually deliver ROI.
          </p>

          {/* Search */}
          <div className="max-w-2xl mx-auto mb-8 animate-fade-in-up stagger-3">
            <Search tools={allTools} placeholder={`Search ${totalTools}+ AI tools by name, category, or use case...`} />
          </div>

          <div className="flex flex-wrap justify-center gap-4 animate-fade-in-up stagger-4">
            <Link href="/category/writing/" className="btn-primary font-bold">
              AI Writing Tools
            </Link>
            <Link href="/category/coding/" className="btn-secondary font-bold">
              AI Coding Tools
            </Link>
            <Link href="/compare/" className="btn-secondary font-bold">
              Compare Tools
            </Link>
            <Link href="/submit/" className="btn-secondary font-bold border-accent/30 text-accent">
              Submit Your Tool
            </Link>
          </div>
        </div>
      </section>

      <WaveDivider color="#111118" />

      {/* Social Proof Bar */}
      <section className="bg-dark-surface border-b border-dark-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-12 text-sm text-dt-muted">
            {[
              { icon: '🔍', stat: `${totalTools}+`, label: 'AI tools reviewed' },
              { icon: '📊', stat: '10', label: 'categories' },
              { icon: '⚡', stat: '5K+', label: 'monthly readers' },
              { icon: '✅', stat: '100%', label: 'independent & unbiased' },
              { icon: '🔄', stat: 'Weekly', label: 'updated' },
            ].map(item => (
              <div key={item.label} className="flex items-center space-x-2">
                <span className="text-lg">{item.icon}</span>
                <span><strong className="text-dt">{item.stat}</strong> <span className="text-dt-muted">{item.label}</span></span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <AdSlot position="header" />

      {/* Featured Tools */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-dt mb-4">Top-Rated AI Tools for 2026</h2>
          <p className="text-dt-muted max-w-2xl mx-auto">
            Our highest-rated AI tools across all categories. Each tool is hands-on tested and rated on features, pricing, ease of use, and value.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredTools.map((tool, idx) => (
            <div key={tool.slug} className="animate-scale-in" style={{ animationDelay: `${idx * 0.1}s` }}>
              <ToolCard tool={tool} rank={idx + 1} />
            </div>
          ))}
        </div>
      </section>

      <AdSlot position="mid-content" />

      {/* Categories */}
      <section className="bg-dark-surface/50 py-16 dot-grid-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-dt mb-4">Browse by Category</h2>
            <p className="text-dt-muted">Find AI tools organized by what you need them for.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {categories.map(cat => (
              <Link
                key={cat.slug}
                href={`/category/${cat.slug}/`}
                className="card text-center hover:border-accent/30"
              >
                <span className="text-3xl mb-2 block">{CATEGORY_ICONS[cat.slug] || '🤖'}</span>
                <h3 className="font-semibold text-dt mb-2">{cat.name}</h3>
                <p className="text-sm text-dt-muted line-clamp-2">{cat.description.split('.')[0]}.</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Comparisons */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-dt mb-4">Popular Comparisons</h2>
          <p className="text-dt-muted">Head-to-head comparisons of the most popular AI tools.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {comparisons.map(comp => (
            <Link
              key={comp.slug}
              href={`/compare/${comp.slug}/`}
              className="card gradient-border hover:border-accent/30"
            >
              <div className="flex items-center justify-center space-x-4 mb-4">
                <span className="font-bold text-lg text-dt">{comp.tools[0].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="text-accent font-bold">VS</span>
                <span className="font-bold text-lg text-dt">{comp.tools[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
              </div>
              <p className="text-sm text-dt-muted text-center line-clamp-2">{comp.verdict}</p>
            </Link>
          ))}
        </div>
        <div className="text-center mt-8">
          <Link href="/compare/" className="btn-secondary">
            View All Comparisons &rarr;
          </Link>
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NewsletterSignup variant="banner" />
      </section>

      {/* SEO Content Block */}
      <section className="bg-dark-surface/50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>Why Use PilotTools to Find AI Tools?</h2>
          <p>
            The AI tools landscape is evolving rapidly, with new products launching every week.
            PilotTools cuts through the noise with honest, data-driven reviews and side-by-side
            comparisons that help you make informed decisions &mdash; and save you money.
          </p>
          <h3>What Makes Our Reviews Different</h3>
          <ul>
            <li><strong>Hands-on testing</strong> &mdash; Every tool is evaluated on real-world tasks</li>
            <li><strong>Transparent scoring</strong> &mdash; Our ratings break down into specific categories</li>
            <li><strong>Updated pricing</strong> &mdash; We track pricing changes so you always see current rates</li>
            <li><strong>Comparison tables</strong> &mdash; Side-by-side feature and pricing comparisons</li>
            <li><strong>No sponsored rankings</strong> &mdash; Our rankings are based purely on quality and value</li>
          </ul>
          <h3>Finding the Right AI Tool for You</h3>
          <p>
            Whether you need an AI writing assistant for blog posts, an AI code editor for development,
            an image generator for marketing visuals, or a video tool for content creation,
            our curated directory and detailed comparisons will help you find the perfect match
            for your workflow and budget. Try our <Link href="/quiz/">Tool Finder Quiz</Link> to get personalized recommendations.
          </p>
        </div>
      </section>

      <AdSlot position="footer" />

      {/* WebSite schema JSON-LD - safe: hardcoded static values */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: websiteSchema }} />
    </Layout>
  )
}

export async function getStaticProps() {
  return {
    props: {
      featuredTools: getFeaturedTools(),
      categories: getAllCategories(),
      comparisons: getAllComparisons(),
      totalTools: getAllTools().length,
      allTools: getAllTools().map(t => ({ slug: t.slug, name: t.name, category: t.category, tagline: t.tagline, rating: t.rating, best_for: t.best_for })),
    },
  }
}
