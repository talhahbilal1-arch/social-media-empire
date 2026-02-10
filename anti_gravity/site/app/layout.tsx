import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Anti-Gravity Blog',
  description: 'Expert reviews and guides for the best products and tools',
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
            <nav className="text-sm text-gray-400">
              Expert Reviews & Guides
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t border-gray-800 mt-16">
          <div className="max-w-4xl mx-auto px-4 py-8 text-center text-sm text-gray-500">
            <p>Affiliate Disclosure: Some links may earn us a commission at no extra cost to you.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
