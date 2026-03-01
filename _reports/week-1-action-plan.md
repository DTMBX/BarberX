# WEEK 1 IMPLEMENTATION CHECKLIST
**Tillerstead.com - Immediate Action Items**  
**Start Date:** 2026-01-26  
**Goal:** Execute quick wins for immediate impact

---

## MONDAY: Brand Foundation (2-3 hours)

### Task 1: Logo Consolidation Plan
- [ ] **Audit current logos** (15 min)
  ```bash
  cd assets/img
  ls -la | grep logo
  # Document all logo files and their usage
  ```

- [ ] **Create logo priority list** (15 min)
  - SVG master (scalable, all uses)
  - PNG 180x180 (favicon, app icon)
  - PNG 512x512 (high-res, social)
  - WebP header variant (performance)

- [ ] **Document logo guidelines** (30 min)
  ```markdown
  # Logo Usage Guidelines
  
  ## Primary Logo
  - File: logo-master.svg
  - Use: All web applications
  - Min size: 40px height
  
  ## Favicon
  - File: logo-icon-180.png
  - Use: Browser tab icons
  
  ## Social Sharing
  - File: logo-social-512.png
  - Use: OG images, social media
  ```

- [ ] **Create color documentation** (45 min)
  - Create: `assets/css/design-tokens.css`
  - Define all brand colors
  - Document usage guidelines
  - Create accessibility matrix

### Task 2: Fix Missing Meta Descriptions
- [ ] **Add meta to test pages** (30 min)
  ```yaml
  # tile-pattern-demo.html
  meta_description: "Interactive tile pattern designer. Preview herringbone, subway, basketweave, and custom patterns before installation."
  
  # offline.html  
  meta_description: "Offline page for Tillerstead PWA. Continue browsing cached content while connection is restored."
  
  # form-detection.html
  meta_description: "Internal testing page for form validation and detection systems."
  ```

- [ ] **Set test pages to noindex** (15 min)
  ```html
  <meta name="robots" content="noindex, nofollow">
  ```

---

## TUESDAY: SEO Foundation (3-4 hours)

### Task 3: Structured Data Implementation
- [ ] **Create schema templates** (60 min)
  
  **Template 1: Service Schema**
  ```html
  <!-- _includes/schema/service.html -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Service",
    "name": "{{ include.name }}",
    "provider": {
      "@type": "LocalBusiness",
      "name": "Tillerstead LLC"
    },
    "areaServed": {
      "@type": "State",
      "name": "New Jersey"
    },
    "description": "{{ include.description }}"
  }
  </script>
  ```

  **Template 2: Review Schema**
  ```html
  <!-- _includes/schema/reviews.html -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "AggregateRating",
    "itemReviewed": {
      "@type": "LocalBusiness",
      "name": "Tillerstead LLC"
    },
    "ratingValue": "5.0",
    "reviewCount": "47"
  }
  </script>
  ```

  **Template 3: FAQ Schema**
  ```html
  <!-- _includes/schema/faq.html -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "{{ include.question }}",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "{{ include.answer }}"
        }
      }
    ]
  }
  </script>
  ```

- [ ] **Implement on key pages** (90 min)
  - services.html → Service schema
  - reviews.html → Review + AggregateRating
  - faq.html → FAQPage
  - about.html → Organization
  - contact.html → ContactPoint

- [ ] **Test with Google Rich Results Test** (15 min)
  - https://search.google.com/test/rich-results
  - Fix any validation errors

### Task 4: Google Search Console Setup
- [ ] **Verify ownership** (10 min)
- [ ] **Submit sitemap.xml** (5 min)
- [ ] **Request indexing for key pages** (10 min)
- [ ] **Set up performance monitoring** (10 min)

---

## WEDNESDAY: Content Launch (4-5 hours)

### Task 5: Write First Strategic Blog Post
- [ ] **Choose topic** (15 min)
  - Recommended: "Ultimate Guide to NJ Tile Shower Building Codes 2026"
  - Why: High search volume + establishes authority

- [ ] **Research** (45 min)
  - NJ building codes
  - TCNA standards
  - Local requirements
  - Competitor posts

- [ ] **Outline** (30 min)
  ```markdown
  # NJ Tile Shower Building Codes: Complete 2026 Guide
  
  ## Introduction
  - Why codes matter
  - What homeowners need to know
  
  ## NJ-Specific Requirements
  - HIC licensing
  - Permit requirements
  - Inspection process
  
  ## TCNA Standards
  - Waterproofing requirements
  - Substrate preparation
  - Tile installation
  
  ## Common Code Violations
  - Missing waterproofing
  - Improper slope
  - Wrong materials
  
  ## Working with Inspectors
  - What they check
  - How to pass inspection
  - Common issues
  
  ## Conclusion + CTA
  ```

- [ ] **Write** (2 hours)
  - Target: 2,000-2,500 words
  - Include images/diagrams
  - Add internal links
  - Optimize for SEO

- [ ] **Optimize** (30 min)
  - Meta title: "NJ Tile Shower Building Codes 2026 | Complete Guide"
  - Meta description: "Everything NJ homeowners need to know about tile shower codes, permits, and inspections. TCNA-compliant expert guidance."
  - Headers: H2/H3 structure
  - Alt text on all images
  - Internal links to services

- [ ] **Publish** (15 min)
  - Save to `_posts/2026-01-27-nj-tile-shower-codes-guide.md`
  - Build and deploy
  - Share on social media

---

## THURSDAY: Google Business Profile (2-3 hours)

### Task 6: Optimize GBP Listing
- [ ] **Claim/verify business** (30 min)
  - https://business.google.com

- [ ] **Complete all fields 100%** (90 min)
  - Business name: Tillerstead LLC
  - Category: Tile Contractor (primary)
  - Additional: Bathroom Remodeler, Waterproofing Service
  - Service area: Atlantic, Ocean, Cape May Counties
  - Hours: Update accurately
  - Phone: +1 (609) 862-8808
  - Website: https://tillerstead.com
  - Description: 750-char optimized description
  - Attributes: Licensed, Insured, Free Estimates, etc.

- [ ] **Add photos** (30 min)
  - Logo (high-res)
  - Cover photo (best project)
  - 10+ project photos
  - Team photos (if available)
  - Before/afters

- [ ] **Create first post** (15 min)
  - "Just published: NJ Tile Shower Code Guide [link]"

- [ ] **Enable messaging** (5 min)

- [ ] **Set up Q&A** (15 min)
  - Pre-populate with 5 common questions

---

## FRIDAY: Analytics & Tracking (2-3 hours)

### Task 7: Google Analytics Setup
- [ ] **Create GA4 property** (15 min)

- [ ] **Set up goals** (45 min)
  - Goal 1: Contact form submission
  - Goal 2: Phone click
  - Goal 3: Calendly booking
  - Goal 4: Email signup
  - Goal 5: Download (guides/PDFs)

- [ ] **Install tracking code** (15 min)
  - Add to `_includes/layout/head.html`
  - Test with GA debugger

- [ ] **Create custom events** (30 min)
  ```javascript
  // Quote calculator completion
  gtag('event', 'quote_completed', {
    'project_type': 'shower',
    'estimated_cost': '$5000'
  });
  
  // Blog post read
  gtag('event', 'content_engagement', {
    'content_type': 'blog',
    'scroll_depth': '75%'
  });
  ```

- [ ] **Set up conversion tracking** (30 min)
  - Link to Google Ads (if running)
  - Facebook pixel (if running)

### Task 8: Create Content Calendar
- [ ] **Set up spreadsheet** (45 min)
  - Columns: Date, Title, Status, Keywords, Author
  - Pre-populate 12 weeks (24 posts)
  - Assign deadlines
  - Track progress

- [ ] **Define content buckets** (15 min)
  - 60% Educational (how-to guides)
  - 20% Local SEO (city/county pages)
  - 10% Case studies
  - 10% Industry news

---

## WEEKEND: Quick Optimizations (1-2 hours)

### Task 9: Performance Tweaks
- [ ] **Enable Netlify optimizations** (15 min)
  ```toml
  # netlify.toml
  [build.processing.css]
    bundle = true
    minify = true

  [build.processing.js]
    bundle = true
    minify = true

  [build.processing.html]
    pretty_urls = true

  [build.processing.images]
    compress = true
  ```

- [ ] **Add preconnect hints** (15 min)
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://www.googletagmanager.com">
  <link rel="dns-prefetch" href="https://calendly.com">
  ```

- [ ] **Compress images** (30 min)
  - Run existing optimize scripts
  - Convert remaining JPGs to WebP/AVIF

### Task 10: Social Proof Collection
- [ ] **Email 5 recent customers** (30 min)
  - Request Google review
  - Ask for testimonial
  - Request before/after photos
  - Offer incentive (10% off next project?)

---

## SUCCESS METRICS (Week 1)

### Goals:
- ✅ Logo files reduced from 35 → 4
- ✅ Color system documented
- ✅ 9 meta descriptions added
- ✅ 5 structured data schemas live
- ✅ Google Search Console configured
- ✅ 1 high-quality blog post published
- ✅ Google Business Profile 100% complete
- ✅ Analytics goals tracking
- ✅ Content calendar created
- ✅ 5 review requests sent

### Time Investment:
- Monday: 2-3 hours
- Tuesday: 3-4 hours
- Wednesday: 4-5 hours
- Thursday: 2-3 hours
- Friday: 2-3 hours
- Weekend: 1-2 hours
**Total: 14-20 hours**

### Expected Outcomes:
- 📈 SEO foundation strengthened
- 📝 Content machine started
- 🎯 Tracking/analytics in place
- 🌟 Review collection initiated
- 🎨 Brand consistency improved

---

## NEXT WEEK PREVIEW (Week 2)

### Monday-Wednesday:
- Publish 2nd blog post
- Create 2 case studies
- Film first project video

### Thursday-Friday:
- Build email signup form
- Set up welcome email sequence
- Create lead magnet (downloadable guide)

---

## TOOLS NEEDED

### Free:
- ✅ Google Search Console
- ✅ Google Analytics
- ✅ Google Business Profile
- ✅ Google Rich Results Test
- ✅ Netlify (already have)

### Paid (Optional but Recommended):
- **Grammarly** ($12/mo) - Writing quality
- **Canva Pro** ($13/mo) - Graphics
- **Mailchimp** (Free < 500 subscribers) - Email
- **CallRail** ($45/mo) - Call tracking

---

## TROUBLESHOOTING

### Issue: Don't have time for 14-20 hours this week
**Solution:** Prioritize tasks 1, 2, 3, 6 (8-10 hours)

### Issue: Don't know how to write 2,000-word post
**Solution:** Use ChatGPT/Claude to create outline + first draft, then edit

### Issue: No recent projects to photograph
**Solution:** Use stock photos (attribution) or create diagrams/infographics

### Issue: Can't access Google Business Profile
**Solution:** Verify ownership via postcard (takes 5-7 days)

---

**START NOW. This week sets the foundation for market dominance.**

Print this checklist. Check boxes as you complete tasks. Update progress daily.

---

*Created: 2026-01-26*  
*Implementation Week: 1 of 52*  
*Next Review: 2026-02-02*
