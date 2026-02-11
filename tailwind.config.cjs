const forms = require('@tailwindcss/forms');
const typography = require('@tailwindcss/typography');

module.exports = {
  content: [
    './src/**/*.{njk,md,html,js,css}',
    './_site/**/*.html',
    './_layouts/**/*.html',
    './_includes/**/*.html',
    './*.html',
  ],
  theme: {
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },
    fontFamily: {
      sans: [
        'Inter',
        'system-ui',
        '-apple-system',
        'Segoe UI',
        'Roboto',
        'Helvetica Neue',
        'Arial',
        'sans-serif',
      ],
    },
    container: {
      center: true,
      padding: '1rem',
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1200px',
      },
    },
    extend: {
      colors: {
        primary: '#2f5d9f',
        accent: '#e07a5f',
        neutral: '#f6f3ed',
        muted: '#6b7280',
        ink: '#0b0d10',
        paper: '#f6f3ed',
      },
      spacing: {
        18: '4.5rem',
        28: '7rem',
      },
      fontSize: {
        '2xl': ['1.5rem', { lineHeight: '1.25' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.15' }],
      },
    },
  },
  plugins: [forms, typography],
};
