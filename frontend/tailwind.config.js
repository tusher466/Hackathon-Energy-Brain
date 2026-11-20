/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0D1210',
          900: '#131A17',
          800: '#1B2420',
          700: '#26322C',
        },
        bone: {
          50: '#F6F3EC',
          100: '#EDE8DC',
          200: '#DDD6C6',
        },
        fg: {
          strong: 'var(--fg-strong)',
          muted: '#8E9A92',
        },
        amber: {
          signal: '#E0A73A',
          hover: '#F0BB55',
          deep: '#9A6F16',
        },
        moss: {
          DEFAULT: '#5F8F6B',
          soft: '#A9C7B0',
        },
        teal: {
          slate: '#3E7C86',
        },
        brick: '#C2503A',
        ochre: '#C98A2B',
      },
      fontFamily: {
        serif: ['Fraunces', 'Newsreader', 'serif'],
        sans: ['Instrument Sans', 'Geist', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'control': '10px',
      },
      animation: {
        'countup': 'countup 0.6s ease-out',
      }
    },
  },
  plugins: [],
}
