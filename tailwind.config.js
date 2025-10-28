/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './users/templates/**/*.html',
    './projects/templates/**/*.html',
    './messaging/templates/**/*.html',
    './notifications/templates/**/*.html',
    './core/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1e3a8a', // Bleu foncé
          light: '#3b82f6',
          dark: '#1e40af',
        },
        secondary: {
          DEFAULT: '#059669', // Vert
          light: '#10b981',
          dark: '#047857',
        },
        accent: {
          DEFAULT: '#10b981',
          light: '#34d399',
          dark: '#059669',
        },
      },
      fontFamily: {
        sans: ['Lato', 'Open Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
