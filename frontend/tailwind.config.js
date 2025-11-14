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
        primary: {
          DEFAULT: '#2563EB',
          dark: '#3B82F6',
        },
        secondary: {
          DEFAULT: '#10B981',
        },
        rise: {
          DEFAULT: '#EF4444',
          dark: '#F87171',
        },
        fall: {
          DEFAULT: '#3B82F6',
          dark: '#60A5FA',
        },
      },
    },
  },
  plugins: [],
}

