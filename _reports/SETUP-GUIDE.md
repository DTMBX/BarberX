# 🚀 Revenue System Setup Guide
**Complete step-by-step setup to go live in 30 minutes**

---

## ✅ STEP 1: Calculate Your Pricing (5 minutes)

I've created a **Pricing Calculator** tool for you!

### How to use it:

1. **Open in browser**: http://localhost:4173/tools/pricing-calculator.html
   
2. **Enter your actual costs**:
   ```
   Labor:
   - Your hourly rate: $__ (what you pay yourself/crew)
   - Sqft per hour: __ (how fast you tile)
   
   Materials (per sqft):
   - Basic ceramic: $__
   - Standard porcelain: $__
   - Premium large format: $__
   - Luxury mosaic: $__
   
   Business:
   - Overhead %: __ (insurance, truck, tools)
   - Profit margin %: __ (what you take home)
   - Minimum project: $__
   ```

3. **Click "Calculate My Pricing"**

4. **Copy the generated code** (it appears at the bottom)

5. **Paste into**: `assets/js/quote-wizard.js` (lines 12-50)

### Example:
If you said:
- $50/hour labor
- 10 sqft/hour speed
- $3.50 ceramic materials
- 20% overhead
- 25% profit margin
- 15% buffer for unknowns

**Result**: Your quote range for ceramic = $10.31 - $11.86/sqft

That's your **cost** ($8.25) + **overhead** (20%) + **profit** (25%) + **buffer range** (15%)

---

## ✅ STEP 2: Set Up Calendly (10 minutes)

### Create Free Account:

1. Go to: https://calendly.com/signup
2. Sign up with your email
3. Verify email

### Create Event Type:

1. Click "Create" → "Event Type"
2. Event name: **"Free Tile Consultation"**
3. Duration: **30 minutes**
4. Description:
   ```
   Let's discuss your tile project! During this call we'll:
   
   ✓ Review your project goals and timeline
   ✓ Discuss material options and preferences
   ✓ Answer your questions
   ✓ Schedule an on-site inspection (if ready)
   
   No pressure, no obligation. Just honest advice.
   ```

5. Location: **Phone Call** or **Zoom** (your choice)
6. Add these questions:
   - What type of project? (Bathroom, Kitchen, Floor, Shower)
   - Approximate square footage?
   - Timeline? (ASAP, 1-3 months, 3-6 months, Just planning)
   - How did you hear about us?

7. **Save** event type

### Get Your Calendly URL:

1. Click on your event
2. Copy the URL (looks like: `https://calendly.com/yourname/consultation`)
3. Save this - you'll need it next!

---

## ✅ STEP 3: Configure Your Site (5 minutes)

### Update Sticky CTA:

1. Open: `_includes/components/sticky-cta.html`
2. Find line 23 (the button with `data-calendly`)
3. Replace the URL:
   ```html
   <!-- BEFORE -->
   data-calendly="https://calendly.com/tillerstead/consultation"
   
   <!-- AFTER (use YOUR URL) -->
   data-calendly="https://calendly.com/YOURNAME/consultation"
   ```

### Update Calendly Integration:

1. Open: `assets/js/calendly-integration.js`
2. Find line 10
3. Replace:
   ```javascript
   // BEFORE
   url: 'https://calendly.com/tillerstead/consultation',
   
   // AFTER (use YOUR URL)
   url: 'https://calendly.com/YOURNAME/consultation',
   ```

### Rebuild Site:

```bash
bundle exec jekyll build
```

---

## ✅ STEP 4: Create Lead Magnet PDF (Optional - 30 min later)

For now, you can skip this and just use the quote wizard. But when you're ready:

### "NJ Tile Project Checklist" PDF Content:

**Page 1: Planning Phase**
- [ ] Set realistic budget ($__ - $__ based on sqft)
- [ ] Measure your space accurately
- [ ] Research tile styles (save photos)
- [ ] Check if permits needed (most NJ residential don't need)
- [ ] Plan for downtime (bathroom: 3-5 days)

**Page 2: Material Selection**
- [ ] Tile type (ceramic, porcelain, natural stone)
- [ ] Size (small = mosaic, medium = 12x12, large = 12x24+)
- [ ] Finish (matte, gloss, textured)
- [ ] Grout color (matches, contrasts, or neutral)
- [ ] Waterproofing method (Schluter, RedGard, Kerdi)

**Page 3: Contractor Vetting**
- [ ] NJ HIC License verified? (check NJ.gov)
- [ ] Liability insurance? (ask for certificate)
- [ ] References from past 6 months?
- [ ] Written estimate with itemized costs?
- [ ] Warranty offered? (labor + materials)
- [ ] Payment schedule reasonable? (never 100% upfront!)

**Page 4: Installation Day Prep**
- [ ] Clear the room completely
- [ ] Remove breakables from adjacent rooms (vibration)
- [ ] Set up alternative bathroom/kitchen if needed
- [ ] Arrange pet/child care (noise, dust, strangers)
- [ ] Protect floors with drop cloths in path
- [ ] Have final tile selection confirmed in writing

**Page 5: Post-Installation Care**
- [ ] Wait 24-48 hours before use
- [ ] Seal grout after 48-72 hours
- [ ] Use pH-neutral cleaners only
- [ ] Reseal grout every 1-2 years
- [ ] Wipe up spills immediately
- [ ] Schedule final inspection

### Create PDF:

1. Use Canva, Microsoft Word, or Google Docs
2. Add Tillerstead branding (logo, colors)
3. Export as PDF
4. Save to: `/resources/nj-tile-checklist.pdf`
5. Test download link

### Add to Lead Magnet Popup:

Edit the popup component and set:
```html
data-download-url="/resources/nj-tile-checklist.pdf"
```

---

## ✅ STEP 5: Test Everything (10 minutes)

### Test Checklist:

Visit your site (http://localhost:4173) and verify:

**Sticky CTA Bar:**
- [ ] Scroll down - does CTA appear after ~500px?
- [ ] Click "Get Instant Quote" - goes to quote wizard?
- [ ] Click "Book Consultation" - Calendly popup opens?
- [ ] Click "Call Now" - phone dialer opens?
- [ ] Click X button - CTA disappears?
- [ ] Refresh page - CTA stays hidden? (cookie works)

**Quote Wizard** (if you created the page):
- [ ] Answer all 5 questions
- [ ] Click "Get Estimate"
- [ ] Range calculates correctly?
- [ ] "Book Consultation" button works?
- [ ] Price seems reasonable for your market?

**Lead Magnet Popup** (if configured):
- [ ] Wait 30 seconds on page - popup appears?
- [ ] Enter email - form submits?
- [ ] Download triggers?
- [ ] Popup closes after submit?

**Mobile Testing:**
- [ ] Open on phone
- [ ] Sticky CTA stacks vertically?
- [ ] Buttons are tappable (44px min)?
- [ ] Quote wizard works?
- [ ] Calendly opens properly?

---

## ✅ STEP 6: Set Up Email Delivery (Optional - 15 min)

### Option A: Formspree (Easiest)

1. Go to: https://formspree.io/
2. Sign up (free plan = 50 submissions/month)
3. Create new form: "Lead Magnet Submissions"
4. Copy your form endpoint URL
5. Edit `_includes/components/lead-magnet-popup.html`:
   ```html
   <form action="https://formspree.io/f/YOUR_ID" method="POST">
   ```

### Option B: EmailJS (More Control)

1. Go to: https://www.emailjs.com/
2. Sign up (free plan = 200 emails/month)
3. Add email service (Gmail, Outlook, etc.)
4. Create email template:
   ```
   Subject: New Lead: {{from_name}}
   
   Name: {{from_name}}
   Email: {{from_email}}
   Download: {{download_type}}
   Page: {{page_url}}
   ```
5. Get Service ID, Template ID, Public Key
6. Add to `assets/js/lead-magnet-system.js` (line 130)

---

## ✅ STEP 7: Go Live! 🎉

### Pre-Launch Checklist:

- [ ] Pricing configured in quote-wizard.js
- [ ] Calendly URL updated in 2 files
- [ ] Site rebuilt successfully
- [ ] All buttons tested and working
- [ ] Mobile layout looks good
- [ ] Lead magnet PDF created (optional)
- [ ] Email delivery configured (optional)

### Deploy:

If using Netlify:
```bash
git add .
git commit -m "Add revenue generation system"
git push origin main
```

If using GitHub Pages:
```bash
git add .
git commit -m "Add revenue generation system"  
git push origin gh-pages
```

### Monitor First Week:

Track these in Google Analytics:
- [ ] Sticky CTA clicks
- [ ] Quote wizard completions
- [ ] Calendly bookings
- [ ] Lead magnet downloads
- [ ] Phone calls from site

**Goal Week 1**: 2-3 Calendly bookings, 10-15 quote requests

---

## 🆘 Troubleshooting

### "Sticky CTA not appearing"
- Check browser console for errors
- Verify sticky-cta.js is loading
- Try clearing browser cache
- Check if you scrolled past 500px threshold

### "Calendly not opening"
- Check URL is correct (https://calendly.com/...)
- Verify calendly-integration.js loaded
- Check browser console for errors
- Test in incognito mode

### "Quote wizard calculations wrong"
- Verify pricing config in quote-wizard.js
- Check that minimum project fee is set
- Test with simple numbers first
- Review browser console for JavaScript errors

### "Lead magnet popup not showing"
- Check if cookie was already set (clear cookies)
- Verify lead-magnet-system.js loaded
- Check showDelay setting (default 30 seconds)
- Test in incognito mode

---

## 📊 What to Expect (First 30 Days)

### Week 1-2: Testing & Tweaking
- 5-10 quote requests
- 2-3 Calendly bookings
- A few lead magnet downloads
- Adjust CTA copy if needed

### Week 3-4: Momentum Builds
- 10-15 quote requests
- 4-6 Calendly bookings  
- 1-2 projects closed
- Refine your pricing if too high/low

### Week 5-8: Steady Flow
- 20-25 quote requests/month
- 8-10 consultations/month
- 5-6 projects/month
- $40K+ monthly revenue

---

## 🎯 Next Enhancements (After Going Live)

### Week 2-3:
- [ ] Create email nurture sequence
- [ ] Add Google Ads conversion tracking
- [ ] Create before/after portfolio slider
- [ ] Write first 3 blog posts for SEO

### Month 2:
- [ ] Launch referral program
- [ ] Create "Bathroom Ready Quiz"
- [ ] Add video testimonials
- [ ] Build service area pages

### Month 3:
- [ ] Analyze conversion data
- [ ] A/B test CTA copy
- [ ] Optimize underperforming pages
- [ ] Scale what's working

---

## 📞 Need Help?

**Quick Questions:**
- Pricing not calculating right? Double-check your inputs in the calculator
- Calendly not loading? Verify the URL has https:// and /consultation at end
- Site not building? Run `bundle exec jekyll clean && bundle exec jekyll build`

**Currently Set Up:**
✅ Pricing calculator (http://localhost:4173/tools/pricing-calculator.html)
✅ Calendly integration (just needs YOUR URL)
✅ Sticky CTA (ready to go)
✅ Lead magnet system (needs PDF or quiz)
✅ Quote wizard (needs your pricing config)

**Your Next Step**: 
1. Open the pricing calculator
2. Enter your real costs
3. Copy the generated code
4. Paste into quote-wizard.js
5. Rebuild and test!

Let me know when you're ready to proceed or if you hit any snags!
