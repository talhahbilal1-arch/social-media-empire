import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import Fuse from 'fuse.js'

const fuseOptions = {
  keys: ['name', 'category', 'tagline', 'best_for'],
  threshold: 0.3,
  includeScore: true,
}

export default function Search({ tools, placeholder = 'Search AI tools...' }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const fuseRef = useRef(null)
  const wrapperRef = useRef(null)
  const timerRef = useRef(null)

  useEffect(() => {
    if (tools) {
      fuseRef.current = new Fuse(tools, fuseOptions)
    }
  }, [tools])

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)

    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      if (val.length >= 2 && fuseRef.current) {
        const res = fuseRef.current.search(val).slice(0, 6)
        setResults(res)
        setOpen(true)
      } else {
        setResults([])
        setOpen(false)
      }
    }, 300)
  }

  return (
    <div ref={wrapperRef} className="relative w-full">
      <div className="relative">
        <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dt-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder}
          className="w-full pl-12 pr-4 py-3 bg-dark-surface border border-dark-border rounded-xl text-dt placeholder-dt-muted focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all"
        />
      </div>

      {open && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-dark-surface border border-dark-border rounded-xl shadow-glow-lg overflow-hidden z-50">
          {results.map(({ item }) => (
            <Link
              key={item.slug}
              href={`/tools/${item.slug}/`}
              onClick={() => { setOpen(false); setQuery('') }}
              className="flex items-center justify-between px-4 py-3 hover:bg-dark-surface-hover transition-colors border-b border-dark-border last:border-0"
            >
              <div>
                <p className="text-dt font-medium">{item.name}</p>
                <p className="text-xs text-dt-muted">{item.category}</p>
              </div>
              <span className="text-sm text-star font-medium">{item.rating}/5</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
