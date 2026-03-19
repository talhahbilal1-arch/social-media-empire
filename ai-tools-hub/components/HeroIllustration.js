export default function HeroIllustration() {
  return (
    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[500px] h-[500px] opacity-20 hidden lg:block pointer-events-none">
      <svg viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* Central node */}
        <circle cx="250" cy="250" r="40" stroke="#00d4ff" strokeWidth="2" opacity="0.6">
          <animate attributeName="r" values="38;42;38" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx="250" cy="250" r="8" fill="#00d4ff" opacity="0.8" />

        {/* Orbiting nodes */}
        <circle cx="140" cy="160" r="20" stroke="#7c3aed" strokeWidth="1.5" opacity="0.5" />
        <circle cx="140" cy="160" r="5" fill="#7c3aed" opacity="0.6" />

        <circle cx="360" cy="140" r="24" stroke="#00d4ff" strokeWidth="1.5" opacity="0.4" />
        <circle cx="360" cy="140" r="6" fill="#00d4ff" opacity="0.5" />

        <circle cx="380" cy="320" r="18" stroke="#7c3aed" strokeWidth="1.5" opacity="0.5" />
        <circle cx="380" cy="320" r="5" fill="#7c3aed" opacity="0.6" />

        <circle cx="120" cy="350" r="22" stroke="#00d4ff" strokeWidth="1.5" opacity="0.4" />
        <circle cx="120" cy="350" r="5" fill="#00d4ff" opacity="0.5" />

        <circle cx="300" cy="420" r="16" stroke="#7c3aed" strokeWidth="1.5" opacity="0.3" />
        <circle cx="300" cy="420" r="4" fill="#7c3aed" opacity="0.4" />

        <circle cx="180" cy="80" r="14" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />
        <circle cx="180" cy="80" r="4" fill="#00d4ff" opacity="0.4" />

        <circle cx="420" cy="230" r="16" stroke="#00d4ff" strokeWidth="1" opacity="0.3" />
        <circle cx="420" cy="230" r="4" fill="#00d4ff" opacity="0.4" />

        {/* Connection lines */}
        <line x1="250" y1="250" x2="140" y2="160" stroke="#00d4ff" strokeWidth="1" opacity="0.15" />
        <line x1="250" y1="250" x2="360" y2="140" stroke="#7c3aed" strokeWidth="1" opacity="0.15" />
        <line x1="250" y1="250" x2="380" y2="320" stroke="#00d4ff" strokeWidth="1" opacity="0.15" />
        <line x1="250" y1="250" x2="120" y2="350" stroke="#7c3aed" strokeWidth="1" opacity="0.15" />
        <line x1="250" y1="250" x2="300" y2="420" stroke="#00d4ff" strokeWidth="1" opacity="0.1" />
        <line x1="250" y1="250" x2="180" y2="80" stroke="#7c3aed" strokeWidth="1" opacity="0.1" />
        <line x1="250" y1="250" x2="420" y2="230" stroke="#00d4ff" strokeWidth="1" opacity="0.1" />

        {/* Cross-connections */}
        <line x1="140" y1="160" x2="360" y2="140" stroke="#00d4ff" strokeWidth="0.5" opacity="0.08" strokeDasharray="4 4" />
        <line x1="360" y1="140" x2="380" y2="320" stroke="#7c3aed" strokeWidth="0.5" opacity="0.08" strokeDasharray="4 4" />
        <line x1="120" y1="350" x2="300" y2="420" stroke="#00d4ff" strokeWidth="0.5" opacity="0.08" strokeDasharray="4 4" />
        <line x1="140" y1="160" x2="180" y2="80" stroke="#7c3aed" strokeWidth="0.5" opacity="0.08" strokeDasharray="4 4" />

        {/* Outer ring */}
        <circle cx="250" cy="250" r="180" stroke="#00d4ff" strokeWidth="0.5" opacity="0.08" strokeDasharray="8 8">
          <animateTransform attributeName="transform" type="rotate" from="0 250 250" to="360 250 250" dur="60s" repeatCount="indefinite" />
        </circle>
        <circle cx="250" cy="250" r="130" stroke="#7c3aed" strokeWidth="0.5" opacity="0.06" strokeDasharray="6 6">
          <animateTransform attributeName="transform" type="rotate" from="360 250 250" to="0 250 250" dur="45s" repeatCount="indefinite" />
        </circle>

        {/* Tiny floating particles */}
        <circle cx="200" cy="180" r="2" fill="#00d4ff" opacity="0.4">
          <animate attributeName="cy" values="180;170;180" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="320" cy="280" r="2" fill="#7c3aed" opacity="0.4">
          <animate attributeName="cy" values="280;290;280" dur="5s" repeatCount="indefinite" />
        </circle>
        <circle cx="280" cy="150" r="1.5" fill="#00d4ff" opacity="0.3">
          <animate attributeName="cx" values="280;290;280" dur="6s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  )
}

export function WaveDivider({ flip = false, color = '#111118' }) {
  return (
    <div className={`w-full overflow-hidden leading-none ${flip ? 'rotate-180' : ''}`}>
      <svg viewBox="0 0 1440 60" preserveAspectRatio="none" className="w-full h-[40px] md:h-[60px]">
        <path
          d="M0,30 C360,60 720,0 1080,30 C1260,45 1380,20 1440,30 L1440,60 L0,60 Z"
          fill={color}
        />
      </svg>
    </div>
  )
}
