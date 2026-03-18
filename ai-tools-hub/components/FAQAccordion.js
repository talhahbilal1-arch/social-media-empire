export default function FAQAccordion({ faqs }) {
  if (!faqs || faqs.length === 0) return null

  return (
    <div className="space-y-3">
      {faqs.map((faq, idx) => (
        <details key={idx} className="group bg-dark-surface border border-dark-border rounded-xl overflow-hidden">
          <summary className="flex items-center justify-between p-5 cursor-pointer text-dt font-medium hover:bg-dark-surface-hover transition-colors list-none">
            <span>{faq.question}</span>
            <svg className="w-5 h-5 text-dt-muted flex-shrink-0 ml-4 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          <div className="px-5 pb-5 text-dt-muted">
            {faq.answer}
          </div>
        </details>
      ))}
    </div>
  )
}
