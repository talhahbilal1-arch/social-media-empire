export default function QuizCard({ question, options, onSelect }) {
  return (
    <div className="card max-w-2xl mx-auto text-center">
      <h2 className="text-2xl font-bold text-dt mb-6">{question}</h2>
      <div className="grid sm:grid-cols-2 gap-3">
        {options.map(option => (
          <button
            key={option.value}
            onClick={() => onSelect(option.value)}
            className="p-4 bg-dark-surface-hover border border-dark-border rounded-xl text-dt hover:border-accent/40 hover:shadow-glow transition-all text-left"
          >
            <span className="font-medium">{option.label}</span>
            {option.description && <p className="text-sm text-dt-muted mt-1">{option.description}</p>}
          </button>
        ))}
      </div>
    </div>
  )
}
