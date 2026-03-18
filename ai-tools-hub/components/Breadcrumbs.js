import Link from 'next/link'

const SITE_URL = 'https://pilottools.ai'

export default function Breadcrumbs({ items }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, idx) => ({
      "@type": "ListItem",
      "position": idx + 1,
      "name": item.label,
      ...(item.href ? { "item": item.href.startsWith('http') ? item.href : `${SITE_URL}${item.href}` } : {})
    }))
  }

  return (
    <>
      {/* BreadcrumbList JSON-LD - safe: build-time static data from getStaticProps only, no user input */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <ol className="flex items-center space-x-2 text-sm text-dt-muted">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-center space-x-2">
              {idx > 0 && <span className="text-dark-border">&gt;</span>}
              {item.href ? (
                <Link href={item.href} className="hover:text-accent transition-colors">{item.label}</Link>
              ) : (
                <span className="text-dt font-medium">{item.label}</span>
              )}
            </li>
          ))}
        </ol>
      </nav>
    </>
  )
}
