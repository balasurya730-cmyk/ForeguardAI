/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        base: {
          950: '#0A0D11',
          900: '#0F1318',
          800: '#151A21',
          700: '#1D232C',
          600: '#2A313C',
          500: '#3D4552',
        },
        ink: {
          900: '#E9ECF1',
          700: '#B8C0CC',
          500: '#7C8797',
          300: '#4E5866',
        },
        signal: {
          amber: '#F5A623',
          amberDim: '#8A5E17',
          cyan: '#2DD4C8',
          cyanDim: '#155F58',
          red: '#EF4444',
          redDim: '#7A1F1F',
          green: '#3DDC84',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        panel: '0 0 0 1px rgba(255,255,255,0.04), 0 8px 24px rgba(0,0,0,0.35)',
      },
      backgroundImage: {
        'grid-overlay':
          'linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '28px 28px',
      },
    },
  },
  plugins: [],
}
