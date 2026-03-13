/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'space-grotesk': ['Space Grotesk', 'sans-serif'],
        'jetbrains-mono': ['JetBrains Mono', 'monospace'],
      },
      colors: {
        'bg-deep': '#050510',
        'bg-primary': '#0a0a1a',
        'bg-secondary': '#0f0f24',
        'bg-card': 'rgba(15, 15, 40, 0.7)',
        'accent': '#00d4aa',
        'text-primary': '#e8e8f0',
        'text-secondary': '#8888a0',
      },
    },
  },
  plugins: [],
}