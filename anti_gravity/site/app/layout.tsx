import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Anti-Gravity — Home Office Optimization Guides',
  description: 'Expert reviews and guides for building a healthier, more productive home office workspace.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b border-gray-800">
          <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-white hover:text-emerald-400 transition-colors">
              Anti-Gravity
            </a>
            <nav className="flex items-center gap-6 text-sm text-gray-400">
              <a href="/" className="hover:text-white transition-colors">Home</a>
              <a href="/about" className="hover:text-white transition-colors">About</a>
              <a href="/privacy" className="hover:text-white transition-colors">Privacy</a>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t border-gray-800 mt-16">
          <div className="max-w-4xl mx-auto px-4 py-8 text-center text-sm text-gray-500">
            <div className="flex justify-center gap-6 mb-4">
              <a href="/about" className="hover:text-gray-300 transition-colors">About</a>
              <a href="/privacy" className="hover:text-gray-300 transition-colors">Privacy</a>
              <a href="/terms" className="hover:text-gray-300 transition-colors">Terms</a>
            </div>
            <p className="mb-2">&copy; 2026 Anti-Gravity. All rights reserved.</p>
            <p>Affiliate Disclosure: Some links may earn us a commission at no extra cost to you.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
