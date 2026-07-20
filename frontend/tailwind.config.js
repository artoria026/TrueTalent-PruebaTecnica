/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        surface: 'var(--surface)',
        'surface-alt': 'var(--surface-alt)',
        line: 'var(--line)',
        ink: 'var(--ink)',
        'ink-muted': 'var(--ink-muted)',
        'ink-faint': 'var(--ink-faint)',
        accent: 'var(--accent)',
        'accent-ink': 'var(--accent-ink)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        'mod-transactions': 'var(--mod-transactions)',
        'mod-assistant': 'var(--mod-assistant)',
        'mod-rpa': 'var(--mod-rpa)',
        'mod-transactions-soft': 'var(--mod-transactions-soft)',
        'mod-assistant-soft': 'var(--mod-assistant-soft)',
        'mod-rpa-soft': 'var(--mod-rpa-soft)',
        'danger-soft': 'var(--danger-soft)',
        'danger-wash': 'var(--danger-wash)',
        'danger-line': 'var(--danger-line)',
      },
      fontFamily: {
        sans: ['"Work Sans"', 'system-ui', 'sans-serif'],
        display: ['Manrope', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        ping: {
          '0%': { opacity: '0.8', transform: 'scale(0.6)' },
          '100%': { opacity: '0', transform: 'scale(1.8)' },
        },
        'dot-pulse': {
          '0%, 80%, 100%': { opacity: '0.35', transform: 'scale(0.75)' },
          '40%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'led-ping': 'ping 2s ease-out infinite',
        'dot-pulse': 'dot-pulse 1.1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
