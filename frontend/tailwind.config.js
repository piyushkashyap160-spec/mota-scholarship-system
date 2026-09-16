/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#0B3B60',
          blue: '#13548A',
          dark: '#07233B',
          light: '#F4F7FA',
          saffron: '#FF9933',
          green: '#138808',
          gold: '#D97706',
        }
      }
    },
  },
  plugins: [],
}
