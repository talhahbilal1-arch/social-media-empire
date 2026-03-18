import Link from 'next/link'

export default function MobileMenu({ open, onClose, links }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-[60] md:hidden">
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/60" onClick={onClose} />

      {/* Panel */}
      <div className="fixed right-0 top-0 h-full w-72 bg-dark-surface border-l border-dark-border p-6 overflow-y-auto">
        <div className="flex items-center justify-between mb-8">
          <span className="text-xl font-bold text-accent">PilotTools</span>
          <button onClick={onClose} className="p-2 text-dt-muted hover:text-accent" aria-label="Close menu">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="space-y-1">
          {links.map(link => (
            <Link
              key={link.href}
              href={link.href}
              onClick={onClose}
              className="block px-3 py-3 text-dt-muted hover:text-accent hover:bg-dark-surface-hover rounded-lg transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="mt-6 pt-6 border-t border-dark-border">
          <Link
            href="/quiz/"
            onClick={onClose}
            className="btn-primary w-full justify-center text-sm"
          >
            Tool Finder
          </Link>
        </div>

        <div className="mt-6 pt-6 border-t border-dark-border space-y-1">
          <Link href="/about/" onClick={onClose} className="block px-3 py-2 text-sm text-dt-muted hover:text-accent">About</Link>
          <Link href="/contact/" onClick={onClose} className="block px-3 py-2 text-sm text-dt-muted hover:text-accent">Contact</Link>
          <Link href="/privacy/" onClick={onClose} className="block px-3 py-2 text-sm text-dt-muted hover:text-accent">Privacy</Link>
        </div>
      </div>
    </div>
  )
}
