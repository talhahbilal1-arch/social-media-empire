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

          <div className="border-t border-dark-border pt-6">
            <h2 className="text-xl font-bold text-dt mb-4">Quick Contact Form</h2>
            <form action="mailto:hello@pilottools.ai" method="POST" encType="text/plain" className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-dt mb-2">Name</label>
                <input
                  type="text"
                  id="name"
                  name="Name"
                  required
                  className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-dt focus:outline-none focus:border-accent transition-colors"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-dt mb-2">Email</label>
                <input
                  type="email"
                  id="email"
                  name="Email"
                  required
                  className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-dt focus:outline-none focus:border-accent transition-colors"
                  placeholder="your@email.com"
                />
              </div>
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-dt mb-2">Message</label>
                <textarea
                  id="message"
                  name="Message"
                  required
                  rows={6}
                  className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-dt focus:outline-none focus:border-accent transition-colors"
                  placeholder="Your message..."
                />
              </div>
              <button
                type="submit"
                className="w-full px-6 py-2 bg-accent text-dt font-semibold rounded-lg hover:bg-cyan-300 transition-colors"
              >
                Send Message
              </button>
            </form>
            <p className="mt-4 text-sm text-dt-muted">
              Can&apos;t use the form? Email us directly at <a href="mailto:hello@pilottools.ai" className="text-accent hover:text-cyan-300">hello@pilottools.ai</a> or <a href="mailto:talhahbilal1+pilottools@gmail.com" className="text-accent hover:text-cyan-300">talhahbilal1+pilottools@gmail.com</a>.
            </p>
            <p className="mt-2 text-sm text-dt-muted">
              <strong>Typical response time:</strong> 1-2 business days.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
