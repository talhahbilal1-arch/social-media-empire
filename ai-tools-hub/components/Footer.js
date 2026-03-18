import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-dark-surface border-t border-dark-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-semibold text-dt mb-4">Categories</h3>
            <ul className="space-y-2">
              <li><Link href="/category/writing/" className="text-dt-muted hover:text-accent text-sm transition-colors">AI Writing Tools</Link></li>
              <li><Link href="/category/coding/" className="text-dt-muted hover:text-accent text-sm transition-colors">AI Coding Tools</Link></li>
              <li><Link href="/category/image/" className="text-dt-muted hover:text-accent text-sm transition-colors">AI Image Generators</Link></li>
              <li><Link href="/category/video/" className="text-dt-muted hover:text-accent text-sm transition-colors">AI Video Tools</Link></li>
              <li><Link href="/category/marketing/" className="text-dt-muted hover:text-accent text-sm transition-colors">AI Marketing</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-dt mb-4">Comparisons</h3>
            <ul className="space-y-2">
              <li><Link href="/compare/chatgpt-vs-claude/" className="text-dt-muted hover:text-accent text-sm transition-colors">ChatGPT vs Claude</Link></li>
              <li><Link href="/compare/jasper-vs-writesonic/" className="text-dt-muted hover:text-accent text-sm transition-colors">Jasper vs Writesonic</Link></li>
              <li><Link href="/compare/midjourney-vs-runway/" className="text-dt-muted hover:text-accent text-sm transition-colors">Midjourney vs Runway</Link></li>
              <li><Link href="/compare/cursor-vs-chatgpt/" className="text-dt-muted hover:text-accent text-sm transition-colors">Cursor vs ChatGPT</Link></li>
              <li><Link href="/compare/" className="text-dt-muted hover:text-accent text-sm transition-colors">View All</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-dt mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><Link href="/quiz/" className="text-dt-muted hover:text-accent text-sm transition-colors">Tool Finder Quiz</Link></li>
              <li><Link href="/pricing/" className="text-dt-muted hover:text-accent text-sm transition-colors">Pricing Guide</Link></li>
              <li><Link href="/blog/" className="text-dt-muted hover:text-accent text-sm transition-colors">Blog</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-dt mb-4">About</h3>
            <p className="text-dt-muted text-sm mb-4">
              PilotTools helps you find the perfect AI tool with honest reviews and detailed comparisons.
            </p>
            <ul className="space-y-2">
              <li><Link href="/about/" className="text-dt-muted hover:text-accent text-sm transition-colors">About Us</Link></li>
              <li><Link href="/contact/" className="text-dt-muted hover:text-accent text-sm transition-colors">Contact</Link></li>
              <li><Link href="/privacy/" className="text-dt-muted hover:text-accent text-sm transition-colors">Privacy Policy</Link></li>
              <li><Link href="/affiliate-disclosure/" className="text-dt-muted hover:text-accent text-sm transition-colors">Affiliate Disclosure</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-dark-border flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-dt-muted text-sm">
            &copy; {new Date().getFullYear()} PilotTools. All rights reserved.
          </p>
          <p className="text-dt-muted text-xs max-w-md text-center sm:text-right">
            Some links on this site are affiliate links. We may earn a commission at no extra cost to you.
          </p>
        </div>
      </div>
    </footer>
  )
}
