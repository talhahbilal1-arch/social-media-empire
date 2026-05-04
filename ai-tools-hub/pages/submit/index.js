import { useState } from 'react'
import Layout from '../../components/Layout'

const TIERS = [
  {
    id: 'free',
    name: 'Free Listing',
    price: null,
    priceLabel: 'Free',
    reviewTime: '7–14 days',
    badge: null,
    borderClass: 'border-dark-border',
    highlight: false,
    features: [
      'Basic directory listing',
      'Tool name, description & link',
      'Reviewed within 7–14 days',
      'Standard category placement',
      'Searchable in our directory',
    ],
    cta: 'Submit for Free',
    ctaClass: 'btn-secondary w-full justify-center',
    stripeUrl: null,
  },
  {
    id: 'featured',
    name: 'Featured',
    price: 49,
    priceLabel: '$49/mo',
    reviewTime: '24 hours',
    badge: '⭐ Featured',
    badgeClass: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    borderClass: 'border-accent/40',
    highlight: true,
    features: [
      'Everything in Free',
      'Priority review within 24 hours',
      '"Featured" gold badge on listing',
      'Top placement within category',
      'Highlighted border on tool card',
      'Included in "Featured Tools" sections',
      'Monthly performance report',
    ],
    cta: 'Get Featured',
    ctaClass: 'btn-primary w-full justify-center',
    stripeUrl: 'https://buy.stripe.com/PLACEHOLDER_FEATURED',
    popular: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 99,
    priceLabel: '$99/mo',
    reviewTime: '24 hours',
    badge: '👑 Premium',
    badgeClass: 'bg-accent-purple/20 text-purple-400 border border-accent-purple/30',
    borderClass: 'border-accent-purple/40',
    highlight: false,
    features: [
      'Everything in Featured',
      'Homepage showcase placement',
      'Dedicated hands-on review article',
      'Social media promotion (Pinterest + LinkedIn)',
      'Newsletter feature (5,000+ subscribers)',
      'Comparison page inclusion',
      'Quarterly strategy call',
    ],
    cta: 'Go Premium',
    ctaClass: 'w-full justify-center inline-flex items-center px-6 py-3 bg-accent-purple text-white font-semibold rounded-lg hover:bg-purple-500 transition-colors duration-200',
    stripeUrl: 'https://buy.stripe.com/PLACEHOLDER_PREMIUM',
  },
]

const FAQS = [
  {
    q: 'Who reads PilotTools?',
    a: 'Our audience of 5,000+ monthly readers are business owners, freelancers, and content creators actively evaluating AI tools. These are buyers, not casual browsers — they arrive from Google searches like "best AI writing tool" and "ChatGPT alternatives."',
  },
  {
    q: 'What happens after I submit?',
    a: 'For Free listings, we review your submission within 7–14 days. For Featured and Premium, you\'ll receive a confirmation within 24 hours and your listing goes live immediately after payment. Premium reviews include a full hands-on test of your tool.',
  },
  {
    q: 'Can I cancel my Featured or Premium subscription?',
    a: 'Yes — cancel any time from your Stripe customer portal. Your listing will revert to a Free basic listing at the end of the billing period. No lock-in.',
  },
  {
    q: 'How is "top placement" determined?',
    a: 'Featured and Premium tools appear first within their category and in curated "Featured Tools" sections throughout the site. Premium tools additionally appear on the homepage showcase.',
  },
  {
    q: 'Do you review tools you disagree with?',
    a: 'We publish honest reviews — including cons. A sponsored listing guarantees placement and promotion, not a positive score. Our readers trust us because we\'re candid.',
  },
  {
    q: 'What types of tools qualify?',
    a: 'Any AI-powered software product is eligible: writing, coding, image generation, video, audio, productivity, marketing, SEO, and more. If it uses AI and charges for it (or has a free tier), we\'ll list it.',
  },
]

function FAQ({ faq }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-dark-border rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-dark-surface-hover transition-colors"
      >
        <span className="font-semibold text-dt">{faq.q}</span>
        <svg
          className={`w-5 h-5 text-accent transition-transform duration-200 flex-shrink-0 ml-4 ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="px-6 pb-5 text-dt-muted text-sm leading-relaxed border-t border-dark-border bg-dark-surface">
          {faq.a}
        </div>
      )}
    </div>
  )
}

export default function SubmitTool() {
  const [selectedTier, setSelectedTier] = useState('featured')
  const [form, setForm] = useState({
    toolName: '',
    website: '',
    description: '',
    category: '',
    email: '',
    additionalInfo: '',
  })
  const [submitted, setSubmitted] = useState(false)

  const activeTier = TIERS.find(t => t.id === selectedTier)

  function handleChange(e) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    const tier = TIERS.find(t => t.id === selectedTier)

    if (tier.stripeUrl) {
      // Paid tiers — redirect to Stripe
      window.location.href = tier.stripeUrl
      return
    }

    // Free tier — open mailto
    const subject = encodeURIComponent(`Tool Submission: ${form.toolName || '[Tool Name]'}`)
    const body = encodeURIComponent(
      `Tool Name: ${form.toolName}\nWebsite: ${form.website}\nCategory: ${form.category}\n\nDescription:\n${form.description}\n\nAdditional Info:\n${form.additionalInfo}\n\nContact: ${form.email}`
    )
    window.location.href = `mailto:hello@pilottools.ai?subject=${subject}&body=${body}`
    setSubmitted(true)
  }

  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: 'Submit Your AI Tool — PilotTools',
    description: 'Get your AI tool listed on PilotTools. Reach 5,000+ monthly readers actively searching for AI solutions.',
    url: 'https://pilottools.ai/submit/',
  }

  return (
    <Layout
      title="Submit Your AI Tool"
      description="Get your AI tool listed on PilotTools. Reach 5,000+ monthly readers actively searching for AI solutions. Free, Featured ($49/mo), and Premium ($99/mo) tiers available."
      canonical="https://pilottools.ai/submit/"
      structuredData={structuredData}
    >
      {/* Hero */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-dark-bg via-dark-bg to-accent/5 pointer-events-none" />
        <div className="absolute top-20 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative max-w-4xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent/10 border border-accent/20 text-accent text-sm font-medium mb-6 animate-fade-in">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            5,000+ monthly readers actively evaluating AI tools
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold text-dt mb-6 animate-fade-in-up" style={{ fontFamily: "'Sora', sans-serif" }}>
            Get Your AI Tool<br />
            <span className="text-accent">In Front of Buyers</span>
          </h1>

          <p className="text-xl text-dt-muted max-w-2xl mx-auto mb-10 animate-fade-in-up stagger-2">
            PilotTools readers don't browse for fun — they arrive from Google with specific problems to solve and budgets to spend. A listing here puts your tool exactly where purchase decisions happen.
          </p>

          {/* Social proof strip */}
          <div className="flex flex-wrap justify-center gap-8 text-sm animate-fade-in-up stagger-3">
            {[
              { num: '5,000+', label: 'monthly readers' },
              { num: '200+', label: 'tools reviewed' },
              { num: '50+', label: 'categories covered' },
              { num: '#1', label: 'on 40+ AI keywords' },
            ].map(stat => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl font-extrabold text-accent" style={{ fontFamily: "'Sora', sans-serif" }}>{stat.num}</div>
                <div className="text-dt-muted">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Tiers */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-dt text-center mb-4" style={{ fontFamily: "'Sora', sans-serif" }}>
            Choose Your Listing Tier
          </h2>
          <p className="text-dt-muted text-center mb-12 max-w-xl mx-auto">
            Start free. Upgrade when you're ready to drive real traffic and conversions.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            {TIERS.map(tier => (
              <div
                key={tier.id}
                onClick={() => setSelectedTier(tier.id)}
                className={`relative card cursor-pointer transition-all duration-200 ${
                  selectedTier === tier.id
                    ? `border-2 ${tier.borderClass} shadow-glow`
                    : 'border-dark-border hover:border-accent/20'
                } ${tier.highlight ? 'gradient-border' : ''}`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-accent text-dark-bg text-xs font-bold px-3 py-1 rounded-full">
                      MOST POPULAR
                    </span>
                  </div>
                )}

                {/* Selected indicator */}
                <div className={`absolute top-4 right-4 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                  selectedTier === tier.id
                    ? 'border-accent bg-accent'
                    : 'border-dark-border bg-transparent'
                }`}>
                  {selectedTier === tier.id && (
                    <svg className="w-3 h-3 text-dark-bg" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>

                <div className="mb-4">
                  {tier.badge && (
                    <span className={`inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full mb-3 ${tier.badgeClass}`}>
                      {tier.badge}
                    </span>
                  )}
                  <h3 className="text-xl font-bold text-dt mb-1" style={{ fontFamily: "'Sora', sans-serif" }}>{tier.name}</h3>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-extrabold text-dt" style={{ fontFamily: "'Sora', sans-serif" }}>{tier.priceLabel}</span>
                    {tier.price && <span className="text-dt-muted text-sm">billed monthly</span>}
                  </div>
                  <p className="text-xs text-dt-muted mt-1">Review in {tier.reviewTime}</p>
                </div>

                <ul className="space-y-2.5 mb-6">
                  {tier.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-dt-muted">
                      <svg className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={e => { e.stopPropagation(); setSelectedTier(tier.id) }}
                  className={`${tier.ctaClass} text-sm py-2.5`}
                >
                  {tier.cta}
                </button>
              </div>
            ))}
          </div>

          {/* Submission Form */}
          <div className="max-w-2xl mx-auto">
            <div className={`card border-2 ${activeTier.borderClass}`}>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-bold text-dt" style={{ fontFamily: "'Sora', sans-serif" }}>
                    Submit — {activeTier.name}
                  </h3>
                  <p className="text-sm text-dt-muted">
                    {activeTier.price
                      ? `${activeTier.priceLabel} · You'll be redirected to Stripe to complete payment`
                      : 'Free · We\'ll review your submission within 7–14 days'}
                  </p>
                </div>
              </div>

              {submitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 rounded-full bg-green-900/30 border border-green-800/30 flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-dt mb-2">Submission sent!</h3>
                  <p className="text-dt-muted text-sm">We'll review your tool and be in touch within 7–14 business days.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-dt mb-1.5">Tool Name *</label>
                      <input
                        type="text"
                        name="toolName"
                        value={form.toolName}
                        onChange={handleChange}
                        required
                        placeholder="e.g. Writesonic"
                        className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt placeholder-dt-muted text-sm focus:outline-none focus:border-accent/50 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-dt mb-1.5">Website URL *</label>
                      <input
                        type="url"
                        name="website"
                        value={form.website}
                        onChange={handleChange}
                        required
                        placeholder="https://yourtool.com"
                        className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt placeholder-dt-muted text-sm focus:outline-none focus:border-accent/50 transition-colors"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dt mb-1.5">Category *</label>
                    <select
                      name="category"
                      value={form.category}
                      onChange={handleChange}
                      required
                      className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt text-sm focus:outline-none focus:border-accent/50 transition-colors"
                    >
                      <option value="">Select a category…</option>
                      {['Writing', 'Coding', 'Image Generation', 'Video', 'Audio', 'Marketing', 'SEO', 'Productivity', 'Research', 'Design', 'Other'].map(c => (
                        <option key={c} value={c.toLowerCase()}>{c}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dt mb-1.5">Short Description *</label>
                    <textarea
                      name="description"
                      value={form.description}
                      onChange={handleChange}
                      required
                      rows={3}
                      placeholder="What does your tool do? Who is it for? What makes it different? (2–4 sentences)"
                      className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt placeholder-dt-muted text-sm focus:outline-none focus:border-accent/50 transition-colors resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dt mb-1.5">Your Email *</label>
                    <input
                      type="email"
                      name="email"
                      value={form.email}
                      onChange={handleChange}
                      required
                      placeholder="you@yourtool.com"
                      className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt placeholder-dt-muted text-sm focus:outline-none focus:border-accent/50 transition-colors"
                    />
                  </div>

                  {activeTier.id !== 'free' && (
                    <div>
                      <label className="block text-sm font-medium text-dt mb-1.5">Additional Info <span className="text-dt-muted font-normal">(optional)</span></label>
                      <textarea
                        name="additionalInfo"
                        value={form.additionalInfo}
                        onChange={handleChange}
                        rows={2}
                        placeholder="Pricing plans, key features, target audience, anything else we should know…"
                        className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2.5 text-dt placeholder-dt-muted text-sm focus:outline-none focus:border-accent/50 transition-colors resize-none"
                      />
                    </div>
                  )}

                  <button type="submit" className={activeTier.ctaClass}>
                    {activeTier.price
                      ? `Continue to Payment (${activeTier.priceLabel}) →`
                      : 'Submit Tool for Review →'}
                  </button>

                  <p className="text-xs text-dt-muted text-center pt-1">
                    {activeTier.price
                      ? 'Secure checkout via Stripe. Cancel any time — no long-term contracts.'
                      : 'We review all free submissions manually. No guarantees of listing.'}
                  </p>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* What You Get — value props */}
      <section className="py-16 bg-dark-surface dot-grid-bg">
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-dt text-center mb-12" style={{ fontFamily: "'Sora', sans-serif" }}>
            Why List on PilotTools?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: (
                  <svg className="w-6 h-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                ),
                title: 'High-Intent Search Traffic',
                body: 'Our readers arrive from Google searches like "best AI writing tool for freelancers" — they\'re already in buying mode, not just browsing.',
              },
              {
                icon: (
                  <svg className="w-6 h-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ),
                title: 'Trusted Editorial Voice',
                body: 'We run hands-on tests of every tool we feature. That credibility transfers to tools we recommend — readers trust our shortlists.',
              },
              {
                icon: (
                  <svg className="w-6 h-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                ),
                title: 'Growing Audience',
                body: 'Traffic doubled in the last 90 days. Getting listed now means establishing visibility before this niche gets crowded with competitors.',
              },
            ].map(item => (
              <div key={item.title} className="card">
                <div className="w-12 h-12 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center mb-4">
                  {item.icon}
                </div>
                <h3 className="font-bold text-dt mb-2" style={{ fontFamily: "'Sora', sans-serif" }}>{item.title}</h3>
                <p className="text-sm text-dt-muted leading-relaxed">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-16">
        <div className="max-w-2xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-dt text-center mb-10" style={{ fontFamily: "'Sora', sans-serif" }}>
            Frequently Asked Questions
          </h2>
          <div className="space-y-3">
            {FAQS.map(faq => <FAQ key={faq.q} faq={faq} />)}
          </div>

          <div className="mt-12 text-center card">
            <p className="text-dt-muted mb-4 text-sm">Still have questions?</p>
            <a href="mailto:hello@pilottools.ai?subject=Listing Inquiry" className="btn-secondary inline-flex">
              Email hello@pilottools.ai
            </a>
          </div>
        </div>
      </section>
    </Layout>
  )
}
