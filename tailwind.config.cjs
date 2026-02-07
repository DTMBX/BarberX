const forms = require('@tailwindcss/forms');
const typography = require('@tailwindcss/typography');

module.exports = {
  content: [
    './src/**/*.{njk,md,html,js,css}',
    './_site/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        'ad-navy': '#002e5d',
        'ad-blue': '#0b5f73',
        'ad-red': '#b22234',
        'ad-accent': '#e07a5f',
        'ad-neutral': '#f6f7f9'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif']
      },
      container: {
        center: true,
        padding: '1rem'
      }
    }
  },
  plugins: [forms, typography]
};
module.exports = {
  content: ["./src/**/*.{html,njk,md}", "./_site/**/*.html"],
  theme: {
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px'
    },
    fontFamily: {
      sans: ['Inter','system-ui','-apple-system','Segoe UI','Roboto','Helvetica','Arial','sans-serif']
    },
    container: {
      center: true,
      padding: '1rem',
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1200px'
      }
    },
    extend: {
      colors: {
        primary: '#0b5f73',
        accent: '#e07a5f',
        neutral: '#f6f7f9',
        muted: '#6b7280'
      },
      spacing: {
        18: '4.5rem',
        28: '7rem'
      },
      fontSize: {
        '2xl': ['1.5rem', { lineHeight: '1.25' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.15' }]
      }
    }
  },
  plugins: []
};
