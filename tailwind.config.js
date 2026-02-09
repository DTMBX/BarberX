/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./**/*.html', './_layouts/**/*.html', './_includes/**/*.html', './index.html'],
  theme: {
    extend: {
      colors: {
        // Evident brand palette
        primary: {
          50: '#f0f7fc',
          100: '#e0eef8',
          200: '#c1def2',
          300: '#a2cde9',
          400: '#5ea9d8',
          500: '#0b73d2', // Brand blue
          600: '#0a5fb2',
          700: '#084a92',
          800: '#063774',
          900: '#042555',
        },
        accent: {
          50: '#fef5f1',
          100: '#fce9dd',
          200: '#f8d3bb',
          300: '#f5bd99',
          400: '#ed8855',
          500: '#e07a5f', // Accent orange
          600: '#c76551',
          700: '#ad5043',
          800: '#933b35',
          900: '#792627',
        },
        neutral: {
          50: '#fafbfc',
          100: '#f6f7f9', // Light gray
          200: '#e8ebed',
          300: '#d5d8dd',
          400: '#a8adb3',
          500: '#7a7f87',
          600: '#525961',
          700: '#3a3f47',
          800: '#252a30',
          900: '#0d0f12',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        info: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#0d0f12',
            maxWidth: 'none',
          },
        },
      },
      spacing: {
        13: '3.25rem',
        15: '3.75rem',
        17: '4.25rem',
      },
      borderRadius: {
        '3xl': '1.5rem',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.1)',
        inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
        focus: '0 0 0 3px rgba(11, 115, 210, 0.1)',
      },
      transitionDuration: {
        250: '250ms',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Georgia', 'Cambria', 'serif'],
        mono: ['Consolas', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
};
