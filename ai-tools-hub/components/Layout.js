import Head from 'next/head'
import Link from 'next/link'
import googleConfig from '../config/google.json'

const SITE_NAME = 'ToolPilot'
const SITE_TAGLINE = 'Find the Perfect AI Tool'
const SITE_URL = 'https://toolpilot-hub.netlify.app'

// Google config — auto-activates when real values are pasted into config/google.json
const GSC_TAG = googleConfig.search_console.verification_tag
const GA4_ID = googleConfig.analytics.ga4_measurement_id
const hasGSC = GSC_TAG && !GSC_TAG.startsWith('PASTE')
const hasGA4 = GA4_ID && !GA4_ID.startsWith('PASTE')

export default function Layout({ children, title, description, canonical, ogType, structuredData }) {
  const fullTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} - ${SITE_TAGLINE}`
  const metaDesc = description || 'Compare the best AI tools in 2026. Honest reviews, pricing comparisons, and expert recommendations for AI writing, coding, image, video, and marketing tools.'
  const canonicalUrl = canonical || SITE_URL

  return (
    <>
      <Head>
        <title>{fullTitle}</title>
        <meta name="description" content={metaDesc} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="canonical" href={canonicalUrl} />
        {hasGSC && <meta name="google-site-verification" content={GSC_TAG} />}
        <meta property="og:title" content={fullTitle} />
        <meta property="og:description" content={metaDesc} />
        <meta property="og:type" content={ogType || 'website'} />
        <meta property="og:url" content={canonicalUrl} />
        <meta property="og:site_name" content={SITE_NAME} />
        <meta property="og:image" content={`${SITE_URL}/og-image.png`} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={fullTitle} />
        <meta name="twitter:description" content={metaDesc} />
        <meta name="twitter:image" content={`${SITE_URL}/og-image.png`} />
        <meta name="robots" content="index, follow" />
        {hasGA4 && (
          <>
            <script async src={`https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`} />
            <script dangerouslySetInnerHTML={{ __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA4_ID}');` }} />
          </>
        )}
      </Head>
      {structuredData && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      )}

      <div className="min-h-screen flex flex-col">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-2xl font-bold text-primary-600">ToolPilot</span>
                <span className="text-sm text-gray-500 hidden sm:inline">{SITE_TAGLINE}</span>
              </Link>

              <div className="hidden md:flex items-center space-x-6">
                <Link href="/category/writing/" className="text-gray-600 hover:text-primary-600 transition-colors">Writing</Link>
                <Link href="/category/coding/" className="text-gray-600 hover:text-primary-600 transition-colors">Coding</Link>
                <Link href="/category/image/" className="text-gray-600 hover:text-primary-600 transition-colors">Image</Link>
                <Link href="/category/video/" className="text-gray-600 hover:text-primary-600 transition-colors">Video</Link>
                <Link href="/category/marketing/" className="text-gray-600 hover:text-primary-600 transition-colors">Marketing</Link>
                <Link href="/compare/" className="text-gray-600 hover:text-primary-600 transition-colors">Compare</Link>
              </div>
            </div>
          </nav>
        </header>

        <main className="flex-1">
          {children}
        </main>

        <footer className="bg-gray-50 border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Categories</h3>
                <ul className="space-y-2">
                  <li><Link href="/category/writing/" className="text-gray-600 hover:text-primary-600 text-sm">AI Writing Tools</Link></li>
                  <li><Link href="/category/coding/" className="text-gray-600 hover:text-primary-600 text-sm">AI Coding Tools</Link></li>
                  <li><Link href="/category/image/" className="text-gray-600 hover:text-primary-600 text-sm">AI Image Generators</Link></li>
                  <li><Link href="/category/video/" className="text-gray-600 hover:text-primary-600 text-sm">AI Video Tools</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">More Categories</h3>
                <ul className="space-y-2">
                  <li><Link href="/category/marketing/" className="text-gray-600 hover:text-primary-600 text-sm">AI Marketing Tools</Link></li>
                  <li><Link href="/category/productivity/" className="text-gray-600 hover:text-primary-600 text-sm">AI Productivity</Link></li>
                  <li><Link href="/category/audio/" className="text-gray-600 hover:text-primary-600 text-sm">AI Audio & Voice</Link></li>
                  <li><Link href="/category/seo/" className="text-gray-600 hover:text-primary-600 text-sm">AI SEO Tools</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">Popular Comparisons</h3>
                <ul className="space-y-2">
                  <li><Link href="/compare/chatgpt-vs-claude/" className="text-gray-600 hover:text-primary-600 text-sm">ChatGPT vs Claude</Link></li>
                  <li><Link href="/compare/jasper-vs-writesonic/" className="text-gray-600 hover:text-primary-600 text-sm">Jasper vs Writesonic</Link></li>
                  <li><Link href="/compare/midjourney-vs-runway/" className="text-gray-600 hover:text-primary-600 text-sm">Midjourney vs Runway</Link></li>
                  <li><Link href="/compare/cursor-vs-chatgpt/" className="text-gray-600 hover:text-primary-600 text-sm">Cursor vs ChatGPT</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-4">About</h3>
                <p className="text-gray-600 text-sm mb-4">
                  ToolPilot helps you find the perfect AI tool for your needs with honest reviews and detailed comparisons.
                </p>
                <p className="text-gray-500 text-xs">
                  Affiliate disclosure: Some links on this site are affiliate links. If you purchase through these links, we may earn a commission at no additional cost to you. This does not influence our reviews or recommendations.
                </p>
              </div>
            </div>
            <div className="mt-8 pt-8 border-t border-gray-200 text-center text-gray-500 text-sm">
              &copy; {new Date().getFullYear()} ToolPilot. All rights reserved.
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}
