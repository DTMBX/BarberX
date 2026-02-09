/\*\*

- DESIGN TOKENS PACKAGE CONFIGURATION
- Modern, Open-Source Frontend Stack
- Evident Technologies
-
- CORE TECHNOLOGIES:
- - Tailwind CSS v4: Utility-first CSS framework (MIT License)
- - Inter Font: Open-source typeface optimized for screens
- - CSS-in-JS Variables: CSS Custom Properties for theming
- - Vanilla JavaScript: Zero dependency interactive components
- - HTML5 Semantic: Modern, accessible markup standards
-
- DESIGN PRINCIPLES:
- 1.  Accessibility First: WCAG 2.1 AA compliant
- 2.  Mobile-First: Progressive enhancement from mobile to desktop
- 3.  Performance: Minimal CSS, optimized fonts, lazy loading
- 4.  Maintainability: Design tokens as single source of truth
- 5.  Flexibility: CSS variables enable theme switching
-
- NPM DEPENDENCIES (Modern & Open Source):
- - tailwindcss@4+: https://tailwindcss.com (MIT)
- - postcss@8+: CSS transformation (MIT)
- - autoprefixer@10+: CSS vendor prefixes (MIT)
- - @tailwindcss/typography@0.5+: Prose styling (MIT)
- - @tailwindcss/forms@0.5+: Form styling (MIT)
- - @tailwindcss/aspect-ratio@0.4+: Media aspect ratios (MIT)
-
- FILE STRUCTURE:
- \_layouts/
- └─ default.html Modern semantic HTML template with native forms
- assets/
- ├─ css/
- │ ├─ design-tokens.css CSS variables for colors, spacing, typography
- │ ├─ components.css Reusable component styles (buttons, cards, forms)
- │ ├─ styles.css Page-specific styles
- │ └─ tailwind.css Tailwind directives
- └─ js/
-       ├─ navigation.js        Mobile menu, keyboard navigation
-       └─ theme.js            Light/dark mode toggle with system preference
-
- DESIGN TOKENS:
-
- COLOR PALETTE:
- --color-primary-500: #0b73d2 (Evident Blue)
- --color-accent-500: #e07a5f (Accent Orange)
- --color-neutral-\*: Grays 50-900 (UI elements)
- --color-text-\*: Semantic text colors
- --color-bg: Background colors
-
- TYPOGRAPHY:
- Font Family: Inter (open-source)
- Sizes: xs (12px) to 5xl (48px)
- Weights: Regular (400) to Extrabold (800)
- Line Heights: Tight (1.25) to Loose (2)
-
- SPACING SCALE:
- --spacing-\*: 0.25rem to 6rem (4px to 96px)
- Based on 4px baseline for pixel-perfect layouts
-
- SHADOW SYSTEM:
- --shadow-sm: 1px subtle elevation
- --shadow-md: 4px medium elevation
- --shadow-lg: 10px large elevation
- --shadow-xl: 20px extra large elevation
- --shadow-focus: Blue ring for focus states (accessibility)
-
- COMPONENTS PROVIDED:
-
- .btn (buttons):
- - .btn-primary Branded call-to-action
- - .btn-secondary Secondary action
- - .btn-outline Outlined variant
- - .btn-ghost Minimal, text-only
- - .btn-sm / .btn-lg Size variants
- - .btn-icon Icon-only buttons
-
- .card (containers):
- - Default card with shadow and border
- - .card-elevated Higher elevation
- - .card-border-accent Colored left border
-
- .form-\*:
- - .form-group Input wrapper
- - input, textarea Styled form inputs
- - :focus Blue ring focus indicator
-
- .alert:
- - .alert-info Information message
- - .alert-success Success confirmation
- - .alert-warning Warning message
- - .alert-error Error message
-
- .badge:
- - Small status indicators
- - Semantic color variants
-
- ACCESSIBILITY FEATURES:
- - Semantic HTML5 (header, nav, main, footer, article, section)
- - ARIA labels and roles
- - Keyboard navigation (Tab, Enter, Escape)
- - Focus indicators (3px blue ring)
- - Color contrast ratios: WCAG AA+ compliant
- - Screen reader friendly with .sr-only and .visually-hidden
- - Skip-to-content link
- - Proper form labels and error messages
- - High contrast mode support
-
- RESPONSIVE DESIGN:
- - Mobile-first approach
- - Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- - Flexible grid system
- - Touch-friendly targets (min 44px)
- - Fluid typography scaling
-
- PERFORMANCE OPTIMIZATIONS:
- - CSS variables reduce duplicate styling
- - Minimal CSS bundle (utility classes only when used)
- - System fonts as fallback (fast initial render)
- - Lazy-loaded fonts (Google Fonts with display=swap)
- - Vanilla JS (no jQuery or heavy frameworks)
- - Intersection Observer for lazy loading
- - Modern image formats (WebP with PNG fallback)
-
- BROWSER SUPPORT:
- - Chrome/Edge 90+
- - Firefox 88+
- - Safari 14+
- - Mobile browsers (iOS Safari 14+, Chrome Android)
- - Graceful degradation for older browsers
-
- BUILD COMMANDS:
- npm run build Build entire site (CSS + HTML)
- npm run build:css Compile Tailwind + PostCSS
- npm run dev Watch mode with live reload
- npm run lint:css Validate CSS
- npm run format Auto-format code
-
- CUSTOMIZATION:
- 1.  Update colors in design-tokens.css root variables
- 2.  Modify spacing scale in design-tokens.css
- 3.  Add new components in components.css
- 4.  Extend Tailwind config in tailwind.config.js
- 5.  Toggle dark mode in theme.js
-
- LICENSES:
- - All components: MIT License
- - Tailwind CSS: MIT
- - Inter Font: OFL 1.1
- - This design system: MIT
-
- OPEN SOURCE PHILOSOPHY:
- - No proprietary libraries
- - Standards-based (CSS3, HTML5, Web Platform APIs)
- - Framework-agnostic
- - Forks and extends the best open-source tools
- - Contributes improvements back to community
    \*/

/\*\*

- FRONTEND DEPENDENCIES
- Install with: npm install --save-dev [package]
  \*/
  {
  "devDependencies": {
  "tailwindcss": "^4.1.0", // CSS utility framework
  "postcss": "^8.4.0", // CSS transformation
  "autoprefixer": "^10.4.0", // Vendor prefixes
  "@tailwindcss/typography": "^0.5.0",
  "@tailwindcss/forms": "^0.5.0",
  "@tailwindcss/aspect-ratio": "^0.4.0",
  "cssnano": "^7.0.0", // CSS minification
  "prettier": "^3.0.0", // Code formatter
  "stylelint": "^16.0.0", // CSS linter
  "eslint": "^8.0.0" // JS linter
  },
  "dependencies": {
  // NO runtime dependencies!
  // This design system uses vanilla JavaScript and standard web APIs
  }
  }

/\*\*

- QUICK START:
-
- 1.  Install dependencies:
- npm install
-
- 2.  Create page with layout:
- ***
- layout: default
- title: My Page
- ***
- <section class="container py-12">
-      <h1>Welcome</h1>
-      <p>Your content here</p>
- </section>
-
- 3.  Use components:
- <button class="btn btn-primary">Click me</button>
- <div class="card">Content</div>
- <div class="alert alert-info">Info message</div>
-
- 4.  Customize colors:
- Edit design-tokens.css root variables
-
- 5.  Build and deploy:
- npm run build
- Deploy \_site/ to GitHub Pages
  \*/
