import Layout from '../components/Layout'
import ToolCard from '../components/ToolCard'
import NewsletterSignup from '../components/NewsletterSignup'
import Search from '../components/Search'
import AdSlot from '../components/AdSlot'
import HeroIllustration, { WaveDivider } from '../components/HeroIllustration'
import Link from 'next/link'
import { getAllTools, getAllCategories, getAllComparisons, getFeaturedTools } from '../lib/tools'
import { getAllArticles, getReadingTime } from '../lib/articles'

export default function Home({ featuredTools, categories, comparisons, totalTools, allTools, latestGuides }) {
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
            Updated May 2026 &mdash; {totalTools}+ tools reviewed &bull; by Talhah Bilal, ISSA Certified
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

          <div className="grid grid-cols-2 sm:flex sm:flex-wrap justify-center gap-3 sm:gap-4 animate-fade-in-up stagger-4">
            <Link href="/category/writing/" className="btn-primary font-bold w-full sm:w-auto text-center">
              AI Writing Tools
            </Link>
            <Link href="/category/coding/" className="btn-secondary font-bold w-full sm:w-auto text-center">
              AI Coding Tools
            </Link>
            <Link href="/compare/" className="btn-secondary font-bold w-full sm:w-auto text-center">
              Compare Tools
            </Link>
            <Link href="/submit/" className="btn-secondary font-bold border-accent/30 text-accent w-full sm:w-auto text-center">
              Submit Your Tool
            </Link>
          </div>
        </div>
      </section>

      <WaveDivider color="#111118" />

      {/* Social Proof Bar */}
      <section className="bg-dark-surface border-b border-dark-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:flex md:flex-wrap justify-center items-center gap-4 md:gap-10 text-sm text-dt-muted">
            {[
              { icon: '🔍', stat: `${totalTools}+`, label: 'tools reviewed' },
              { icon: '⏱️', stat: '4,800+', label: 'hours of testing' },
              { icon: '📊', stat: '10', label: 'categories covered' },
              { icon: '✅', stat: '0', label: 'paid placements' },
              { icon: '🔄', stat: 'Weekly', label: 'updated' },
            ].map(item => (
              <div key={item.label} className="flex items-center space-x-2 text-center sm:text-left">
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
                <span className="font-bold text-lg text-dt">{(comp.tools[0] || '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                <span className="text-accent font-bold">VS</span>
                <span className="font-bold text-lg text-dt">{(comp.tools[1] || '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
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

      {/* Guides & Editorial — signals editorial depth beyond the tool directory */}
      {latestGuides && latestGuides.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-end justify-between mb-10 flex-wrap gap-4">
            <div>
              <h2 className="text-3xl font-bold text-dt mb-2">Guides &amp; Deep Dives</h2>
              <p className="text-dt-muted max-w-2xl">
                Long-form reviews, how-tos, and category explainers from the PilotTools editors — beyond the tool directory.
              </p>
            </div>
            <Link href="/blog/" className="btn-secondary whitespace-nowrap">
              View all guides &rarr;
            </Link>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {latestGuides.map(article => (
              <Link
                key={article.slug}
                href={`/blog/${article.slug}/`}
                className="card hover:border-accent/30 flex flex-col"
              >
                <span className="badge-blue self-start mb-3">{article.category}</span>
                <h3 className="font-bold text-dt mb-2 leading-snug">{article.title}</h3>
                <p className="text-sm text-dt-muted line-clamp-3 mb-4">{article.excerpt}</p>
                <div className="mt-auto flex items-center gap-3 text-xs text-dt-muted">
                  <span>{article.author}</span>
                  <span>·</span>
                  <span>{article.readingTime}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Newsletter Signup */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <NewsletterSignup variant="banner" />
      </section>

      {/* SEO Content Block */}
      <section className="bg-dark-surface/50 py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 prose prose-lg">
          <h2>Why Use PilotTools to Find AI Tools?</h2>
          <p>
            PilotTools was built by <Link href="/about/"><strong>Talhah Bilal</strong></Link>, an ISSA-certified
            professional and AI automation practitioner who got tired of affiliate-first &ldquo;review&rdquo; sites
            that rank tools by commission rate rather than quality. Every tool on PilotTools has been
            hands-on tested across real workflows &mdash; minimum 15 hours per tool, 5+ distinct use cases.
          </p>
          <h3>What Makes Our Reviews Different</h3>
          <ul>
            <li><strong>Hands-on testing only</strong> &mdash; Every tool is evaluated on real-world tasks, not synthetic benchmarks or marketing demos</li>
            <li><strong>Transparent scoring</strong> &mdash; Our 0–5.0 ratings break down into five weighted dimensions: output quality, ease of use, features, pricing, and community</li>
            <li><strong>Updated pricing</strong> &mdash; We track pricing changes monthly so you always see the real cost of ownership</li>
            <li><strong>Side-by-side comparisons</strong> &mdash; Feature and pricing comparisons against the top 3–5 competitors per category</li>
            <li><strong>Zero paid rankings</strong> &mdash; No tool can pay for a better position. Our affiliate disclosure is public.</li>
          </ul>
          <h3>Finding the Right AI Tool for You</h3>
          <p>
            Whether you need an AI writing assistant for blog posts, an AI code editor for development,
            an image generator for marketing visuals, or a video tool for content creation,
            our curated directory and detailed comparisons will help you find the right match.
            Try our <Link href="/quiz/">Tool Finder Quiz</Link> for personalized recommendations, or browse
            our <Link href="/editorial-guidelines/">editorial guidelines</Link> to understand exactly how we evaluate tools.
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
      totalTools: 460,
      allTools: getAllTools().map(t => ({ slug: t.slug, name: t.name, category: t.category, tagline: t.tagline, rating: t.rating, best_for: t.best_for })),
      latestGuides: getAllArticles().slice(0, 6).map(a => ({
        slug: a.slug,
        title: a.title || '',
        excerpt: a.excerpt || a.meta_description || '',
        category: a.category || 'Guide',
        author: a.author || 'PilotTools Editors',
        readingTime: getReadingTime(a.word_count || 0),
      })),
    },
  }
}
