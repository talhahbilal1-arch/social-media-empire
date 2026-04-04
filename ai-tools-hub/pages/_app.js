import '../styles/globals.css'
import Analytics from '../components/Analytics'
import CookieConsent from '../components/CookieConsent'

export default function App({ Component, pageProps }) {
  return (
    <>
      <Analytics />
      <Component {...pageProps} />
      <CookieConsent />
    </>
  )
}
