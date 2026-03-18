import Layout from '../../components/Layout'
import Breadcrumbs from '../../components/Breadcrumbs'

export default function ContactPage() {
  return (
    <Layout
      title="Contact Us"
      description="Get in touch with the PilotTools team. Questions about reviews, partnerships, or advertising."
      canonical="https://pilottools.ai/contact/"
    >
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Contact' }]} />

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-dt mb-8 text-center">Contact Us</h1>

        <div className="card space-y-6">
          <div>
            <h2 className="text-xl font-bold text-dt mb-2">General Inquiries</h2>
            <p className="text-dt-muted mb-2">Questions about our reviews, tool recommendations, or anything else.</p>
            <a href="mailto:hello@pilottools.ai" className="text-accent hover:text-cyan-300 font-medium transition-colors">
              hello@pilottools.ai
            </a>
          </div>

          <div className="border-t border-dark-border pt-6">
            <h2 className="text-xl font-bold text-dt mb-2">Partnerships & Advertising</h2>
            <p className="text-dt-muted mb-2">Interested in listing your AI tool or advertising on PilotTools?</p>
            <a href="mailto:hello@pilottools.ai" className="text-accent hover:text-cyan-300 font-medium transition-colors">
              hello@pilottools.ai
            </a>
          </div>

          <div className="border-t border-dark-border pt-6">
            <h2 className="text-xl font-bold text-dt mb-2">Corrections</h2>
            <p className="text-dt-muted">
              Found incorrect pricing, features, or other information in our reviews? Let us know and we will update it promptly.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
