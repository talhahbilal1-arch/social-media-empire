export default function EditorsTake({ take, toolName }) {
  if (!take || !take.whyWePickedIt) return null

  const { pick, whyWePickedIt, bestFor, caveats, author = 'PilotTools Editors', dateReviewed } = take

  return (
    <section
      className="my-6 bg-dark-surface border-l-4 border-accent rounded-r-xl p-6 md:p-8"
      aria-label={`Editor's take on ${toolName}`}
    >
      <div className="flex items-center gap-2 mb-3">
        <svg
          className="w-5 h-5 text-accent flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.196-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118L2.098 10.1c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.518-4.673z" />
        </svg>
        <span className="text-xs uppercase tracking-wider font-semibold text-accent">
          Editor's Take
        </span>
        <span className="text-xs text-dt-muted ml-auto">
          By {author}{dateReviewed ? ` · Updated ${dateReviewed}` : ''}
        </span>
      </div>

      {pick && (
        <p className="text-lg md:text-xl font-bold text-dt mb-4 leading-snug">
          {pick}
        </p>
      )}

      <p className="text-dt-muted leading-relaxed mb-5">
        {whyWePickedIt}
      </p>

      <div className="grid sm:grid-cols-2 gap-4">
        {bestFor && (
          <div>
            <p className="text-xs uppercase tracking-wider font-semibold text-dt-muted mb-1">
              Best for
            </p>
            <p className="text-sm text-dt">{bestFor}</p>
          </div>
        )}
        {caveats && (
          <div>
            <p className="text-xs uppercase tracking-wider font-semibold text-dt-muted mb-1">
              Honest caveat
            </p>
            <p className="text-sm text-dt">{caveats}</p>
          </div>
        )}
      </div>
    </section>
  )
}
