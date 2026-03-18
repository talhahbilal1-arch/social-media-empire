import Head from 'next/head'
import Navigation from './Navigation'
import Footer from './Footer'
import googleConfig from '../config/google.json'

const SITE_NAME = 'PilotTools'
const SITE_TAGLINE = 'Find the Perfect AI Tool'
const SITE_URL = 'https://pilottools.ai'

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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
        {hasGA4 && (
          <>
            <script async src={`https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`} />
            {/* GA4 inline config - safe: uses only our own config constant, no user input */}
            <script dangerouslySetInnerHTML={{ __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA4_ID}');` }} />
          </>
        )}
      </Head>
      {/* Structured data from build-time props only - no user input */}
      {structuredData && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
      )}

      <div className="min-h-screen flex flex-col" style={{ fontFamily: "'Inter', sans-serif" }}>
        <Navigation />

        <main className="flex-1">
          {children}
        </main>

        <Footer />
      </div>
    </>
  )
}
