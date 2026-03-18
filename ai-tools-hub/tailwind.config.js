/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        dark: {
          bg: '#0a0a0f',
          surface: '#111118',
          'surface-hover': '#1a1a24',
          border: '#23232f',
        },
        accent: {
          DEFAULT: '#00d4ff',
          purple: '#7c3aed',
        },
        dt: {
          DEFAULT: '#eaeaef',
          muted: '#8a8a9a',
        },
        star: '#f59e0b',
      },
      boxShadow: {
        glow: '0 0 20px rgba(0,212,255,0.2)',
        'glow-lg': '0 0 30px rgba(0,212,255,0.3)',
      },
      backgroundImage: {
        'gradient-mesh': 'radial-gradient(at 20% 80%, rgba(0,212,255,0.08) 0%, transparent 50%), radial-gradient(at 80% 20%, rgba(124,58,237,0.08) 0%, transparent 50%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
