import Layout from '../../components/Layout'

export default function SubmitTool() {
  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl font-extrabold text-dt mb-6">Submit Your AI Tool</h1>
        <p className="text-xl text-dt-muted mb-8">
          We review tools for a free listing in our directory. Please send us your tool's details.
        </p>
        <div className="card p-8 bg-dark-surface">
          <a href="mailto:talhahbilal1@gmail.com?subject=Tool Submission - [Tool Name]" className="btn-primary inline-flex">
            Email Us Your Submission
          </a>
        </div>
      </div>
    </Layout>
  )
}
