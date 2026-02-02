---
layout: page
title: "Layout Example: Full-Featured Page"
description: "This page demonstrates all available layout features and conditionals. Use this as a reference when creating new pages."
category: "Documentation"
type: "Example"
author: "Devon Tyler"
date: 2026-01-19
last_updated: 2026-01-19
reading_time: "8 min"
permalink: /layout-example/

# Navigation
show_breadcrumbs: true
toc: true

# Tags
tags:
  - Documentation
  - Examples
  - Reference
  - Guide

# Alert Banner
alert: "This is an example page showing all layout features. You can copy and modify this for your own pages!"
alert_title: "Example Page"
alert_type: "info"

# Call to Action
cta_title: "Ready to Create Your Own Page?"
cta_description: "Use this template as a starting point for your content"
cta_text: "View Documentation"
cta_link: /docs/

# Related Pages
related_pages:
  - title: "Layout Documentation"
    url: /layouts/README/
    description: "Complete reference for all layout options"
  - title: "Quick Reference"
    url: /layouts/QUICK_REFERENCE/
    description: "Cheat sheet for common patterns"
  - title: "Component Guide"
    url: /_includes/README/
    description: "Reusable components documentation"

# External Resources
resources:
  - title: "Jekyll Documentation"
    url: https://jekyllrb.com/docs/
    description: "Official Jekyll documentation"
  - title: "Liquid Template Language"
    url: https://shopify.github.io/liquid/
    description: "Template syntax reference"
  - title: "Markdown Guide"
    url: https://www.markdownguide.org/
    description: "Learn Markdown syntax"

# Footer Metadata
source: "Evident.info Layout System"
license: "CC BY-SA 4.0"
version: "2.0.0"
changelog_url: /changelog/

# Custom Styling
page_class: "example-page"
---

## Introduction

This page showcases all the features available in the enhanced **page.html** layout. Each section below demonstrates a different capability you can use when creating content.

## Features Demonstrated

### 1. Alert Banners

You can see an alert banner at the top of this page. These are perfect for:

- Important notices
- Time-sensitive information
- Warnings or cautions
- Success messages

Available types: `info`, `warning`, `error`, `success`

### 2. Rich Page Header

The header includes:

- **Category/Type Label** - "Documentation" shown above the title
- **Title** - Large, prominent heading
- **Description** - Subtitle/summary text
- **Metadata** - Author, dates, reading time
- **Tags** - Visual tags for categorization

### 3. Breadcrumb Navigation

Look above the page header to see the breadcrumb trail showing your location in the site hierarchy.

### 4. Table of Contents

The TOC appears before the main content (if `toc: true` is set) and lists all headings for easy navigation.

### 5. Auto-Calculated Reading Time

The system automatically calculates reading time based on word count (~200 words per minute). You can override this with a manual `reading_time` value.

## Content Organization

### Headings Structure

Use proper heading hierarchy for accessibility and SEO:

```markdown
## Main Section (H2)

### Subsection (H3)

#### Detail Section (H4)
```

### Lists and Formatting

**Unordered Lists:**

- First item
- Second item
  - Nested item
  - Another nested item

**Ordered Lists:**

1. First step
2. Second step
3. Third step

**Emphasis:**

- _Italic text_ with single asterisks
- **Bold text** with double asterisks
- **_Bold italic_** with triple asterisks

### Code Blocks

Inline code: `const example = "code"`

Block code:

```javascript
function greet(name) {
  return `Hello, ${name}!`;
}

console.log(greet("World"));
```

### Blockquotes

> "This is a blockquote. Use it for testimonials, important quotes, or to emphasize key points."
>
> — Source Attribution

## Call to Action

Scroll down to see the call-to-action section (configured in front matter). This is great for:

- Directing users to next steps
- Promoting important resources
- Encouraging engagement

## Related Content

The "Related Pages" section at the bottom helps users discover connected content and continue their journey through your site.

## External Resources

The "Additional Resources" section links to external references, tools, or documentation that complements your content.

## Print Optimization

This layout includes print-specific CSS that:

- Removes decorative elements
- Optimizes for black and white printing
- Ensures good page breaks
- Maintains readability

Try printing this page to see the difference!

## Advanced Features

### Conditional Content

The layout intelligently shows/hides sections based on what you configure:

- No breadcrumbs? They won't appear
- No CTA? The section is hidden
- No related pages? Section omitted
- No tags? Tag section removed

This means you only see what you need!

### Accessibility

Built-in accessibility features:

- Semantic HTML5 structure
- Proper heading hierarchy
- ARIA labels where needed
- Skip-to-main-content link
- High contrast ratios
- Focus indicators

### SEO Optimization

- Structured metadata
- Schema.org markup (when configured)
- Proper heading structure
- Meta descriptions
- Canonical URLs
- Open Graph tags

## Customization

### Custom Classes

Add custom CSS classes via front matter:

```yaml
body_class: "custom-body"
page_class: "special-page"
main_class: "wide-container"
```

### Custom Assets

Load additional CSS or JavaScript:

```yaml
extra_css:
  - /assets/css/custom.css
extra_js:
  - /assets/js/custom.js
```

### Inline Scripts

Add page-specific JavaScript:

```yaml
custom_js: "console.log('Page loaded!');"
```

## Best Practices

1. **Always set a title** - It's required and crucial for UX
2. **Write clear descriptions** - Helps users and search engines
3. **Use tags consistently** - Makes content discoverable
4. **Enable TOC for long pages** - Improves navigation
5. **Add related pages** - Keeps users engaged
6. **Use alerts sparingly** - Only for important messages
7. **Test on mobile** - Ensure responsive design works
8. **Check print preview** - Verify print styles

## Conclusion

This layout system provides everything you need to create professional, accessible, and user-friendly pages. Copy this template and modify it to create your own content!

For more information, see:

- `_layouts/README.md` - Complete documentation
- `_layouts/QUICK_REFERENCE.md` - Quick reference guide

---

**Questions or Feedback?**  
If you have suggestions for improving this layout system, please share them!
