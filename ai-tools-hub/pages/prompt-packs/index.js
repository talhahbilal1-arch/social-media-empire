import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'
import Link from 'next/link'

const SITE_URL = 'https://pilottools.ai'

const PRODUCTS = [
  {
    name: 'AI Fitness Coach Vault',
    price: '$27',
    oldPrice: '$37',
    url: 'https://talhahbilal.gumroad.com/l/lupkl',
    description: '75 copy-paste AI prompts for fitness coaches working with men over 35. Generate complete training programs, nutrition plans, recovery protocols, and client management templates in minutes.',
    features: ['75 battle-tested prompts', '4-8 week program generation', 'Nutrition plan builder', 'Recovery protocols', 'Client onboarding templates', 'Progress tracking prompts'],
    audience: 'Personal trainers, fitness coaches, online coaches',
    badge: 'Best Seller',
    color: 'from-green-500/10 to-emerald-500/10',
    borderColor: 'border-green-500/30',
    badgeColor: 'bg-green-500/20 text-green-400',
  },
  {
    name: 'Pinterest Automation Blueprint',
    price: '$47',
    oldPrice: '$67',
    url: 'https://talhahbilal.gumroad.com/l/epjybe',
    description: 'The complete system for posting 15+ Pinterest pins per day on autopilot using free AI tools. Includes Claude prompts, Make.com webhook setup, Pexels integration, and content strategy templates.',
    features: ['Full automation system guide', 'Claude AI pin copy prompts', 'Make.com webhook blueprints', 'Pexels image integration', 'Content calendar templates', '3-brand management system'],
    audience: 'Content creators, Pinterest marketers, digital entrepreneurs',
    badge: 'Most Comprehensive',
    color: 'from-purple-500/10 to-violet-500/10',
    borderColor: 'border-purple-500/30',
    badgeColor: 'bg-purple-500/20 text-purple-400',
  },
  {
    name: 'Online Coach AI Client Machine',
    price: '$17',
    oldPrice: '$27',
    url: 'https://talhahbilal.gumroad.com/l/weaaa',
    description: '50 AI prompts and scripts that handle every step of client acquisition — from first DM to signed client. Discovery call scripts, follow-up sequences, objection handlers, and onboarding flows.',
    features: ['50 prompts + scripts', 'Discovery call scripts', 'DM conversation templates', 'Follow-up sequences', 'Objection handling scripts', 'Client onboarding flows'],
    audience: 'Online coaches, consultants, service providers',
    badge: 'Best Value',
    color: 'from-blue-500/10 to-cyan-500/10',
    borderColor: 'border-blue-500/30',
    badgeColor: 'bg-blue-500/20 text-blue-400',
  },
  {
    name: 'AI Automation Empire Bundle',
    price: '$87',
    oldPrice: '$131',
    url: 'https://talhahbilal.gumroad.com/l/rwzcy',
    description: 'All 3 prompt packs in one bundle — save 33%. Get the complete AI toolkit for fitness coaching, Pinterest automation, and client acquisition. Everything you need to build an automated online business.',
    features: ['All 3 products included', '175+ total prompts', 'Save 33% vs buying separately', 'Lifetime updates', 'Priority support', 'Bonus: automation templates'],
    audience: 'Entrepreneurs building AI-powered businesses',
    badge: 'Save 33%',
    color: 'from-amber-500/10 to-orange-500/10',
    borderColor: 'border-amber-500/30',
    badgeColor: 'bg-amber-500/20 text-amber-400',
  },
]

const FREE_LEAD_MAGNET = {
  name: '5 Free AI Fitness Prompts',
  url: 'https://talhahbilal.gumroad.com/l/dkschg',
  description: 'Try before you buy. Get 5 of our best-performing AI fitness coaching prompts completely free. No email required.',
}

export default function PromptPacks() {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': 'AI Prompt Packs - PilotTools',
    'description': 'Professional AI prompt packs for fitness coaches, Pinterest marketers, and online coaches. Save hours every week with copy-paste prompts.',
    'url': `${SITE_URL}/prompt-packs/`,
  }

  return (
    <Layout
      title="AI Prompt Packs - Save Hours Every Week"
      description="Professional AI prompt packs for fitness coaches, Pinterest marketers, and online coaches. 175+ battle-tested prompts that automate your business."
      canonical={`${SITE_URL}/prompt-packs/`}
      structuredData={structuredData}
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Prompt Packs' }]} />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-accent/5 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '3s' }} />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center relative z-10">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-accent/10 text-accent border border-accent/20 mb-6">
            175+ Battle-Tested Prompts
          </span>
          <h1 className="text-3xl md:text-5xl font-extrabold text-dt mb-6 leading-tight">
            AI Prompt Packs That Actually<br className="hidden md:block" /> Save You Time
          </h1>
          <p className="text-lg md:text-xl text-dt-muted mb-8 max-w-2xl mx-auto">
            Copy-paste AI prompts built for real workflows. Stop writing from scratch —
            generate programs, content, and client scripts in minutes.
          </p>

          {/* Free lead magnet CTA */}
          <a
            href={FREE_LEAD_MAGNET.url}
            target="_blank"
            rel="noopener"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold bg-accent text-black hover:bg-accent/90 transition-all shadow-lg shadow-accent/20"
          >
            Try 5 Free Prompts First
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </section>

      {/* Products grid */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div className="grid md:grid-cols-2 gap-8">
          {PRODUCTS.map((product, idx) => (
            <div
              key={idx}
              className={`relative bg-gradient-to-br ${product.color} border ${product.borderColor} rounded-2xl p-8 hover:shadow-xl transition-all duration-300`}
            >
              {/* Badge */}
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${product.badgeColor} mb-4`}>
                {product.badge}
              </span>

              <h2 className="text-2xl font-bold text-dt mb-2">{product.name}</h2>

              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-3xl font-extrabold text-accent">{product.price}</span>
                {product.oldPrice && (
                  <span className="text-lg text-dt-muted line-through">{product.oldPrice}</span>
                )}
              </div>

              <p className="text-dt-muted mb-6 leading-relaxed">{product.description}</p>

              {/* Features */}
              <ul className="space-y-2 mb-6">
                {product.features.map((feature, fi) => (
                  <li key={fi} className="flex items-start gap-2 text-sm text-dt-muted">
                    <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <p className="text-xs text-dt-muted mb-6">For: {product.audience}</p>

              <a
                href={product.url}
                target="_blank"
                rel="noopener"
                className="block w-full text-center py-3 px-6 rounded-xl font-semibold bg-accent text-black hover:bg-accent/90 transition-all"
              >
                Get {product.name}
              </a>
            </div>
          ))}
        </div>

        {/* FAQ */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-dt mb-8 text-center">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div className="border border-dt-border rounded-xl p-6">
              <h3 className="font-semibold text-dt mb-2">What AI model do these prompts work with?</h3>
              <p className="text-dt-muted text-sm">These prompts are optimized for ChatGPT (GPT-4), Claude, and Gemini. They work with any large language model that accepts text prompts.</p>
            </div>
            <div className="border border-dt-border rounded-xl p-6">
              <h3 className="font-semibold text-dt mb-2">Do I get lifetime updates?</h3>
              <p className="text-dt-muted text-sm">Yes. When we update prompts or add new ones, you get access to the updated version at no extra cost via your Gumroad library.</p>
            </div>
            <div className="border border-dt-border rounded-xl p-6">
              <h3 className="font-semibold text-dt mb-2">Can I try before I buy?</h3>
              <p className="text-dt-muted text-sm">Absolutely. Grab our <a href={FREE_LEAD_MAGNET.url} target="_blank" rel="noopener" className="text-accent hover:underline">5 free AI fitness prompts</a> to see the quality before purchasing.</p>
            </div>
            <div className="border border-dt-border rounded-xl p-6">
              <h3 className="font-semibold text-dt mb-2">Is there a refund policy?</h3>
              <p className="text-dt-muted text-sm">Yes — Gumroad offers a 30-day refund policy. If the prompts don't save you time, you get your money back.</p>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  )
}
