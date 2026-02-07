# Layout Quick Reference Card

## 📋 Choose Your Layout

### Content Types

```yaml
layout: article      # Biographies, narratives, long-form stories
layout: essay        # Thought pieces, opinion, philosophy
layout: post         # Blog posts, news, updates
layout: case         # Legal cases with docket integration
layout: case-enhanced # Advanced legal cases with timeline
layout: page         # Standard informational pages
layout: doc          # Technical documentation
layout: listing      # Index/archive pages
layout: cases        # Case directory with filters
layout: record       # OPRA public records requests
layout: record-notes # OPRA commentary & notes
layout: trust_document # Ecclesiastical/spiritual documents
```

--

## ⚡ Common Front Matter

### Every Page Should Have:

```yaml
--
layout: [type]
title: "Page Title"
description: "SEO description (160 chars max)"
--
```

### Optional Enhancements:

```yaml
# Metadata
author: "Evident"
date: 2024-01-15
last_updated: 2024-01-20
tags: [tag1, tag2, tag3]
category: "Main Category"

# Features
show_breadcrumbs: true
show_toc: true
show_newsletter: true
hide_social_share: false
hide_progress_bar: false
hide_back_to_top: false
comments: true

# SEO Override
og_image: "/assets/images/custom-og.jpg"
twitter_card: "summary_large_image"
robots: "index, follow"
```

--

## 🎨 Layout-Specific Options

### Article

```yaml
layout: article
subcategory: "Constitutional Narrative" # Default: Constitutional Narrative
```

### Essay

```yaml
layout: essay
show_toc: true
related_essays:
  - title: "Related Essay"
    url: /path/
    description: "Brief description"
```

### Post

```yaml
layout: post
categories: [News, Updates]
show_toc: true
related_posts:
  - title: "Related Post"
    url: /path/
```

### Case

```yaml
layout: case
court: "U.S. District Court"
venue: "Trenton"
primary_docket: "3:23-cv-12345"
case_type: "Civil Rights"
status: "active" # or "closed"
filed_date: 2023-06-15
forum_level: "Federal District Court"
role: "Pro Se Plaintiff"
judge: "Hon. Jane Doe"
overview: "Brief case summary..."
```

### Doc

```yaml
layout: doc
version: "1.0.0"
has_sidebar: true
sidebar_items:
  - title: "Section 1"
    url: "#section-1"
show_edit_link: true
github_path: "docs/filename.md"
```

### OPRA Record

```yaml
layout: record
request_date: 2024-01-10
agency: "Department Name"
status: "completed" # or "pending"
request_number: "2024-001"
documents:
  - title: "Document Name"
    url: "/path/to/doc.pdf"
    size: "1.2 MB"
```

### Trust Document

```yaml
layout: trust_document
doc_type: "ecclesiastical_declaration"
status: "active"
access_level: "public"
pdf_path: "/trust/doc.pdf"
signature_date: 2024-01-01
witness: "Witness Name"
```

--

## 🔧 Feature Flags Quick Reference

| Flag                | Default | Description                 |
| ------------------- | ------- | --------------------------- |
| `show_breadcrumbs`  | `false` | Navigation breadcrumb trail |
| `show_toc`          | `false` | Auto table of contents      |
| `show_newsletter`   | `false` | Newsletter signup CTA       |
| `hide_social_share` | `false` | Social sharing buttons      |
| `hide_progress_bar` | `false` | Reading progress bar        |
| `hide_back_to_top`  | `false` | Scroll-to-top button        |
| `comments`          | `true`  | Comments section            |
| `track_analytics`   | `true`  | Analytics tracking          |

--

## 📱 Component Includes

### Manual Component Usage

```liquid
{%- comment -%} Search Bar {%- endcomment -%}
{% include components/search.html
   placeholder="Search..."
   max_width="600px" %}

{%- comment -%} Newsletter {%- endcomment -%}
{% include components/newsletter-signup.html
   title="Stay Updated"
   description="Custom description" %}

{%- comment -%} Social Share {%- endcomment -%}
{% include components/social-share.html
   background="rgba(0,0,0,0.5)" %}

{%- comment -%} Breadcrumbs {%- endcomment -%}
{% include components/navigation/breadcrumbs.html %}

{%- comment -%} Comments {%- endcomment -%}
{% include components/comments.html margin="5rem 0" %}

{%- comment -%} Back to Top {%- endcomment -%}
{% include components/back-to-top.html %}

{%- comment -%} Reading Progress {%- endcomment -%}
{% include components/reading-progress.html %}
```

--

## 🎯 Content Examples

### Minimal Page

```yaml
--
layout: page
title: "Simple Page"
--
Your content here...
```

### Full-Featured Article

```yaml
--
layout: article
title: "My Constitutional Journey"
description: "A story of faith and advocacy"
author: "Evident"
date: 2024-01-15
last_updated: 2024-01-20
category: Biography
tags: [faith, constitution, advocacy]
show_breadcrumbs: true
show_newsletter: true
og_image: "/assets/images/journey-og.jpg"
--
Content...
```

### Legal Case

```yaml
--
layout: case
title: "Barber v. State"
court: "Superior Court of New Jersey"
primary_docket: "L-001234-24"
case_type: "Civil Rights - First Amendment"
status: "active"
filed_date: 2024-01-10
role: "Pro Se Plaintiff"
tags: [constitutional, religious-freedom]
overview: "Challenge to state regulation..."
--
Case details...
```

--

## 🚀 Performance Checklist

- [ ] Use appropriate layout for content type
- [ ] Add SEO metadata (title, description, image)
- [ ] Set proper date fields
- [ ] Add relevant tags
- [ ] Enable breadcrumbs for deep pages
- [ ] Add table of contents for long content
- [ ] Include newsletter CTA on key pages
- [ ] Test mobile responsiveness
- [ ] Verify accessibility
- [ ] Check social sharing preview

--

## 📞 Need Help?

1. **Layout Guide**: `LAYOUT-OPTIMIZATION-SUMMARY.md`
2. **Components Guide**: `PROFESSIONAL-COMPONENTS-GUIDE.md`
3. **Full Docs**: `_layouts/README.md`

--

**Pro Tip**: Start with minimal front matter and add features as needed. Every
layout works great out of the box!
