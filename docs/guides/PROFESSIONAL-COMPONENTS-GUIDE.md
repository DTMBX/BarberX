# Professional Components Configuration Guide

This guide explains how to configure and use all the new professional components
added to your site.

## 🎯 Quick Setup

Add these configuration options to your `_config.yml` file:

```yaml
# ========================================
# PROFESSIONAL FEATURES CONFIGURATION
# ========================================

# Analytics & Performance
analytics_provider: 'google' # Options: 'google', 'ga4', 'plausible', 'custom'
analytics_id: 'G-XXXXXXXXXX' # Your Google Analytics 4 ID
analytics_anonymize_ip: true
enable_performance_monitoring: true

# SEO & Social Media
title: 'Evident.info - Faith-Driven Legal Advocacy'
description: 'Legal advocacy rooted in constitutional principles and faith'
keywords:
  - legal advocacy
  - constitutional rights
  - faith freedom
author: 'Evident'
og_image: '/assets/images/og-default.jpg'
logo: '/assets/images/logo.png'
theme_color: '#dc2626'
twitter_username: 'your_twitter'

# Cookie Consent
enable_cookie_consent: true
privacy_policy_url: '/privacy-policy/'
cookie_settings_url: '/privacy-policy/#cookies'

# Newsletter
newsletter_enabled: true
newsletter_provider: 'mailchimp' # Options: 'mailchimp', 'convertkit', 'custom'
newsletter_action_url: 'https://yoursite.us1.list-manage.com/subscribe/post?u=xxx&id=xxx'
newsletter_title: 'Stay Updated'
newsletter_description:
  'Get the latest updates, insights, and case analysis delivered straight to
  your inbox.'
newsletter_honeypot_field: 'b_xxx_xxx' # For Mailchimp bot protection
page_newsletter_enabled: false # Set to true to show on all pages

# Comments System
comments_enabled: true
comments_provider: 'utterances' # Options: 'disqus', 'utterances', 'giscus', 'custom'

# For Disqus:
disqus_shortname: 'your-disqus-shortname'

# For Utterances (GitHub Issues):
utterances_repo: 'your-username/your-repo'
utterances_issue_term: 'pathname' # Options: 'pathname', 'url', 'title'
utterances_label: 'comment'
utterances_theme: 'github-dark'

# For Giscus (GitHub Discussions):
giscus_repo: 'your-username/your-repo'
giscus_repo_id: 'R_xxxxx'
giscus_category: 'General'
giscus_category_id: 'DIC_xxxxx'
giscus_mapping: 'pathname'
giscus_theme: 'dark'

show_comment_guidelines: true
```

## 📦 Component Usage

### 1. Analytics (`analytics.html`)

Automatically loaded in `default.html` layout. Supports:

- Google Analytics 4
- Plausible Analytics
- Custom tracking code
- Performance monitoring

**Disable on specific pages:**

```yaml
--
track_analytics: false
--
```

### 2. SEO Meta Tags (`seo-meta.html`)

Automatically included in `<head>`. Override per page:

```yaml
--
title: "Custom Page Title"
description: "Custom page description for SEO"
og_image: "/assets/images/custom-og.jpg"
og_type: "article"
twitter_card: "summary_large_image"
keywords: [custom, keywords, here]
robots: "index, follow"
--
```

### 3. Cookie Consent (`cookie-consent.html`)

Automatically appears for first-time visitors. Features:

- GDPR/CCPA compliant
- LocalStorage persistence (365 days)
- Accept/Reject/Customize options

**Disable sitewide:**

```yaml
enable_cookie_consent: false
```

### 4. Newsletter Signup (`newsletter-signup.html`)

Include anywhere in your content:

```liquid
{% include components/newsletter-signup.html %}
```

**Custom parameters:**

```liquid
{% include components/newsletter-signup.html
   title="Join Our Community"
   description="Custom description here"
   margin="2rem 0"
%}
```

**Show on all pages automatically:**

```yaml
page_newsletter_enabled: true
```

### 5. Social Share Buttons (`social-share.html`)

Include in layouts or pages:

```liquid
{% include components/social-share.html %}
```

**Disable on specific pages:**

```yaml
--
hide_social_share: true
--
```

**Custom styling:**

```liquid
{% include components/social-share.html
   background="rgba(0,0,0,0.5)"
   padding="2rem"
   margin="3rem 0"
%}
```

### 6. Back to Top Button (`back-to-top.html`)

Automatically loaded in `default.html`. Features:

- Circular progress indicator
- Smooth scroll animation
- Appears after scrolling 300px

**Disable on specific pages:**

```yaml
--
hide_back_to_top: true
--
```

### 7. Reading Progress Bar (`reading-progress.html`)

Automatically loaded in `default.html`. Shows scroll progress at top of page.

**Disable on specific pages:**

```yaml
--
hide_progress_bar: true
--
```

### 8. Search Component (`search.html`)

Add to your header or any page:

```liquid
{% include components/search.html %}
```

**Custom configuration:**

```liquid
{% include components/search.html
   placeholder="Search cases and articles..."
   max_width="500px"
   margin="2rem auto"
%}
```

**Note:** Requires `search.json` to be generated (already created).

**Exclude pages from search:**

```yaml
--
exclude_from_search: true
--
```

### 9. Comments System (`comments.html`)

Automatically included in `page.html` layout.

**Disable on specific pages:**

```yaml
--
comments: false
--
```

**Manual inclusion:**

```liquid
{% include components/comments.html margin="5rem 0" %}
```

## 🎨 Component Locations

All components are in: `_includes/components/`

- `analytics.html` - Analytics tracking
- `seo-meta.html` - SEO meta tags
- `cookie-consent.html` - Cookie consent banner
- `newsletter-signup.html` - Newsletter subscription form
- `social-share.html` - Social media sharing buttons
- `back-to-top.html` - Scroll to top button
- `reading-progress.html` - Reading progress bar
- `search.html` - Site-wide search
- `comments.html` - Comments integration

## 🚀 Testing

1. **Analytics**: Check browser console and network tab for tracking calls
2. **SEO**: Use
   [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) and
   [Twitter Card Validator](https://cards-dev.twitter.com/validator)
3. **Cookie Consent**: Clear localStorage and refresh to see banner again
4. **Search**: Visit `/search.json` to ensure index is generating
5. **Comments**: Test in production (most providers require live URLs)

## 📝 Page Layout Examples

### Article with all features:

```yaml
--
layout: page
title: "My Article"
description: "Article description"
show_breadcrumbs: true
show_newsletter: true
tags: [legal, advocacy]
--
Content here...
```

### Minimal page (no extras):

```yaml
--
layout: page
title: "Simple Page"
hide_social_share: true
hide_back_to_top: true
hide_progress_bar: true
comments: false
--
Content here...
```

## 🎯 Next Steps

1. **Add your analytics ID** to `_config.yml`
2. **Set up newsletter** (Mailchimp/ConvertKit)
3. **Configure comments** (choose Utterances for easiest GitHub integration)
4. **Customize colors** in CSS variables if needed
5. **Test all components** in development
6. **Add Open Graph image** at `/assets/images/og-default.jpg`

--

All components are production-ready and follow accessibility best practices!
