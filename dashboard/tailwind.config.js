/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        appBg: '#0a0a0a',         // Pure black background
        tileBg: '#111113',        // Dark card surface
        tileBorder: '#1e1e22',    // Subtle card border
        cream: '#faf6ef',         // Warm cream for light cards
        creamDark: '#f0ead6',     // Deeper cream
        creamText: '#111111',     // Dark text on cream
        skyAccent: '#60a5fa',     // Light blue accent
        skyDark: '#3b82f6',       // Blue-500
        skyPale: '#dbeafe',       // Blue-100 for light bg
        skyBg: '#eff6ff',         // Blue-50 container
        textMuted: '#94a3b8',     // Slate muted text
        accent: '#3b82f6',        // Primary accent (blue)
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}