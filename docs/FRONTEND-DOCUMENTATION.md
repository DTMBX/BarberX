# Evident.info - Frontend Documentation

## ?? **Frontend Architecture Overview**

Evident.info uses a **hybrid frontend architecture**:

### **Technology Stack:**

- **Jekyll** (Static Site Generator) - For marketing pages
- **Flask Templates** (Jinja2) - For web app
- **Standalone HTML** - For independent pages
- **Custom CSS** - Token-based design system
- **Vanilla JavaScript** - No framework dependencies

--

## ?? **Frontend File Structure**

```
Evident.info/
??? index.html                      # Main landing page (Jekyll)
??? templates/                      # Flask/Jinja2 templates
?   ??? index-standalone.html      # Standalone landing page
?   ??? landing.html               # Alternative landing
?   ??? auth/                      # Authentication pages
?   ?   ??? login.html
?   ?   ??? register.html
?   ?   ??? dashboard.html
?   ??? batch-pdf-upload.html      # PDF upload interface
?   ??? bwc-analyzer.html          # BWC analysis UI
?   ??? bwc-dashboard.html         # BWC dashboard
?   ??? pdf-management.html        # PDF management
??? assets/                        # Static assets
?   ??? css/                       # Stylesheets
?   ?   ??? brand-tokens.css       # Design system tokens
?   ?   ??? legal-tech-platform.css # Main platform styles
?   ?   ??? enhanced-animations.css # Animations
?   ?   ??? components/            # Component styles
?   ??? js/                        # JavaScript
?   ?   ??? platform.js            # Main platform JS
?   ?   ??? constitutional-analysis.js # AI analysis
?   ?   ??? components/            # Component scripts
?   ??? img/                       # Images
??? _includes/                     # Jekyll includes
?   ??? components/                # Reusable components
?   ??? sections/                  # Page sections
?   ??? homepage-*.html            # Homepage components
??? _layouts/                      # Jekyll layouts
    ??? default.html               # Base layout
```

--

## ?? **Design System**

### **Brand Tokens (assets/css/brand-tokens.css)**

#### **Colors:**

```css
--primary-navy: #0a1f44; /* Primary brand color */
--primary-navy-dark: #051229; /* Darker variant */
--accent-blue: #3b82f6; /* Call-to-action */
--accent-cyan: #06b6d4; /* Highlights */
--success: #10b981; /* Success states */
--warning: #f59e0b; /* Warning states */
--error: #ef4444; /* Error states */
```

#### **Typography:**

```css
--font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
--font-size-xs: 0.75rem; /* 12px */
--font-size-sm: 0.875rem; /* 14px */
--font-size-base: 1rem; /* 16px */
--font-size-lg: 1.125rem; /* 18px */
--font-size-xl: 1.25rem; /* 20px */
--font-size-2xl: 1.5rem; /* 24px */
--font-size-3xl: 1.875rem; /* 30px */
--font-size-4xl: 2.25rem; /* 36px */
```

#### **Spacing:**

```css
--space-1: 0.25rem; /* 4px */
--space-2: 0.5rem; /* 8px */
--space-3: 0.75rem; /* 12px */
--space-4: 1rem; /* 16px */
--space-6: 1.5rem; /* 24px */
--space-8: 2rem; /* 32px */
--space-12: 3rem; /* 48px */
--space-16: 4rem; /* 64px */
```

--

## ?? **Page Types**

### **1. Marketing Pages (Jekyll)**

**File:** `index.html`, `about.html`, `pricing.html`

**Layout:** Uses `_layouts/default.html`

**Features:**

- Static HTML generated at build time
- SEO optimized
- Fast loading
- GitHub Pages compatible

**Example:**

```html
-- layout: default title: "Evident Legal Technologies" description: "Professional AI-powered
eDiscovery" -- {% include components/hero.html %} {% include components/features.html %}
```

--

### **2. Web App Pages (Flask/Jinja2)**

**Files:** `templates/auth/*.html`, `templates/bwc-*.html`

**Layout:** Flask renders templates

**Features:**

- Dynamic content
- User authentication required
- Server-side rendering
- Database integration

**Example:**

```html
{% extends "base.html" %} {% block content %}
<h1>Welcome, {{ current_user.full_name }}</h1>
{% endblock %}
```

--

### **3. Standalone Pages**

**File:** `templates/index-standalone.html`

**Features:**

- No dependencies (Jekyll or Flask)
- Self-contained HTML
- Can be deployed anywhere
- Fast loading

--

## ?? **Navigation Structure**

### **Main Navigation:**

```
Home (/)
??? About (/about)
??? Features (/features)
??? Pricing (/pricing)
??? Documentation (/docs)
?   ??? Getting Started (/docs/getting-started)
?   ??? User Guide (/docs/user-guide)
?   ??? API Reference (/docs/api)
?   ??? FAQ (/docs/faq)
??? Blog (/blog)
??? Contact (/contact)
```

### **App Navigation (Authenticated):**

```
Dashboard (/auth/dashboard)
??? Upload BWC (/upload)
??? Upload PDF (/batch-pdf-upload.html)
??? Analyses (/analyses)
??? Documents (/documents)
??? Settings (/settings)
??? Logout (/auth/logout)
```

--

## ?? **Call-to-Action Buttons**

### **Primary CTA:**

```html
<a href="/auth/register" class="btn btn-primary"> Start Free Trial </a>
```

### **Secondary CTA:**

```html
<a href="/docs" class="btn btn-secondary"> View Documentation </a>
```

### **Link Destinations:**

| CTA Text                      | Destination      | Status    |
| ----------------------------- | ---------------- | --------- |
| **Start Processing Evidence** | `/auth/register` | ? Working |
| **View Documentation**        | `/docs`          | ?? Create |
| **Try Live Demo**             | `/demo`          | ?? Create |
| **Get Started**               | `/auth/register` | ? Working |
| **Login**                     | `/auth/login`    | ? Working |
| **Pricing**                   | `/pricing`       | ?? Create |
| **Contact Us**                | `/contact`       | ?? Create |

--

## ?? **Responsive Design**

### **Breakpoints:**

```css
/* Mobile */
@media (max-width: 640px) {
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
}

/* Desktop */
@media (min-width: 1025px) {
}
```

### **Mobile-First Approach:**

All components are designed mobile-first, then enhanced for larger screens.

--

## ? **Performance**

### **Optimization Techniques:**

1. **CSS:**
   - Minified for production
   - Critical CSS inline in `<head>`
   - Non-critical CSS deferred

2. **JavaScript:**
   - Lazy loading with `defer` attribute
   - Minimal dependencies
   - Code splitting

3. **Images:**
   - WebP format with fallbacks
   - Responsive images with `srcset`
   - Lazy loading with `loading="lazy"`

4. **Fonts:**
   - System fonts first (no external font loading)
   - Variable fonts for multiple weights

--

## ?? **Component Library**

### **Buttons:**

```html
<!-- Primary Button ->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary Button ->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Outline Button ->
<button class="btn btn-outline">Outline Button</button>

<!-- Icon Button ->
<button class="btn btn-icon">
  <svg>...</svg>
  Icon Button
</button>
```

### **Cards:**

```html
<div class="card">
  <div class="card-header">
    <h3>Card Title</h3>
  </div>
  <div class="card-body">
    <p>Card content goes here</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>
```

### **Forms:**

```html
<form class="form">
  <div class="form-group">
    <label for="email">Email</label>
    <input type="email" id="email" class="form-control" required />
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### **Alerts:**

```html
<!-- Success Alert ->
<div class="alert alert-success">
  <strong>Success!</strong> Your changes have been saved.
</div>

<!-- Error Alert ->
<div class="alert alert-error">
  <strong>Error!</strong> Something went wrong.
</div>

<!-- Warning Alert ->
<div class="alert alert-warning">
  <strong>Warning!</strong> Please check your input.
</div>
```

--

## ?? **Development Workflow**

### **Local Development:**

```bash
# Start Flask (for web app pages)
python app.py

# Start Jekyll (for marketing pages)
bundle exec jekyll serve

# Both at once:
# Terminal 1:
python app.py

# Terminal 2:
bundle exec jekyll serve -port 4000
```

### **Testing:**

```bash
# Test responsiveness
# Use browser dev tools (F12)
# Toggle device toolbar (Ctrl+Shift+M)

# Test accessibility
# Use Lighthouse in Chrome DevTools
# Aim for 90+ accessibility score

# Test performance
# Use PageSpeed Insights
# https://pagespeed.web.dev/
```

--

## ?? **Adding New Pages**

### **Jekyll Marketing Page:**

1. Create `new-page.html` in root:

```html
--
layout: default
title: "Page Title"
description: "Page description"
--

<section class="section">
  <h1>{{ page.title }}</h1>
  <!-- Content here ->
</section>
```

2. Add to navigation in `_includes/header.html`

--

### **Flask Web App Page:**

1. Create `templates/new-feature.html`:

```html
{% extends "base.html" %} {% block content %}
<h1>New Feature</h1>
<!-- Content here ->
{% endblock %}
```

2. Add route in `app.py`:

```python
@app.route('/new-feature')
@login_required
def new_feature():
    return render_template('new-feature.html')
```

--

## ?? **Link Audit & Fixes**

### **Missing Pages to Create:**

1. ? **Documentation** (`/docs`) - Need to create
2. ? **Pricing** (`/pricing`) - Need to create
3. ? **Contact** (`/contact`) - Need to create
4. ? **Demo** (`/demo`) - Need to create
5. ? **About** (`/about`) - Need to create
6. ? **FAQ** (`/faq`) - Need to create

**Next:** I'll create all these missing pages!

--

## ?? **SEO Optimization**

### **Meta Tags (Required on Every Page):**

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Page Title | Evident Legal Tech</title>
  <meta name="description" content="150-160 character description" />

  <!-- Open Graph (Social Media) ->
  <meta property="og:title" content="Page Title" />
  <meta property="og:description" content="Description" />
  <meta property="og:image" content="/assets/img/og-image.png" />
  <meta property="og:url" content="https://Evident.info/page" />

  <!-- Twitter ->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Page Title" />
  <meta name="twitter:description" content="Description" />
  <meta name="twitter:image" content="/assets/img/og-image.png" />
</head>
```

--

## ?? **Analytics Integration**

### **Google Analytics:**

```html
<!-- Add to _layouts/default.html ->
<script
  async
  src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"
></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag("js", new Date());
  gtag("config", "G-XXXXXXXXXX");
</script>
```

--

## ? **Accessibility Checklist**

- [ ] All images have `alt` text
- [ ] Proper heading hierarchy (h1 ? h2 ? h3)
- [ ] Focus indicators visible
- [ ] Color contrast ratio ? 4.5:1
- [ ] Keyboard navigable
- [ ] ARIA labels where needed
- [ ] Form labels properly associated
- [ ] Skip to main content link

--

## ?? **Deployment**

### **GitHub Pages (Marketing Site):**

- Automatic deployment on push to `main`
- URL: `https://dtb396.github.io/Evident.info`

### **Render (Web App):**

- Automatic deployment on push to `main`
- URL: `https://Evident-legal-tech.onrender.com`

### **Custom Domain:**

- URL: `https://app.Evident.info` (after DNS setup)

--

## ?? **Support**

- **Frontend Issues:** Open GitHub issue with `frontend` label
- **Design Questions:** Tag `design` in issue
- **Accessibility:** Tag `a11y` in issue

--

**Next:** Let me create all the missing pages!
