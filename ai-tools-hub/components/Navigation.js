import Link from 'next/link'
import { useState } from 'react'
import MobileMenu from './MobileMenu'

const NAV_LINKS = [
  { href: '/category/writing/', label: 'Writing' },
  { href: '/category/coding/', label: 'Coding' },
  { href: '/category/image/', label: 'Image' },
  { href: '/category/video/', label: 'Video' },
  { href: '/category/marketing/', label: 'Marketing' },
  { href: '/compare/', label: 'Compare' },
  { href: '/prompt-packs/', label: 'Prompt Packs' },
  { href: '/blog/', label: 'Blog' },
]

export default function Navigation() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <>
      <header className="bg-dark-surface/80 backdrop-blur-md border-b border-dark-border sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-accent">PilotTools</span>
              <span className="text-sm text-dt-muted hidden sm:inline">Find the Perfect AI Tool</span>
            </Link>

            <div className="hidden md:flex items-center space-x-6">
              {NAV_LINKS.map(link => (
                <Link key={link.href} href={link.href} className="text-dt-muted hover:text-accent transition-colors text-sm">
                  {link.label}
                </Link>
              ))}
              <Link href="/quiz/" className="btn-primary text-sm py-2 px-4">
                Tool Finder
              </Link>
            </div>

            <button
              onClick={() => setMobileOpen(true)}
              className="md:hidden p-2 text-dt-muted hover:text-accent transition-colors"
              aria-label="Open menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </nav>
      </header>

      <MobileMenu open={mobileOpen} onClose={() => setMobileOpen(false)} links={NAV_LINKS} />
    </>
  )
}

export { NAV_LINKS }
