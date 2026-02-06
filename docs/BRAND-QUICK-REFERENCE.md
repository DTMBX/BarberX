# Evident Brand Quick Reference

**EST. 2024 | A CUT ABOVE**  
_Like a fresh NYC fade — clean, rounded, crisp_

--

## 🎨 Colors

```css
/* The Barber Trio */
--barber-red: #c41e3a --barber-white: #ffffff --barber-blue: #1e40af
  /* Brass Accents */ --brass-gold: #ffd700 --brass-mid: #d4a574;
```

--

## 📐 Spacing (4px Grid)

```css
--space-2: 0.5rem /* 8px */ --space-4: 1rem /* 16px */ --space-6: 1.5rem
  /* 24px */ --space-8: 2rem /* 32px */ --space-12: 3rem /* 48px */;
```

--

## 🔘 Border Radius

```css
--radius-sm: 8px --radius-md: 12px --radius-lg: 16px --radius-full: 9999px
  /* Pills & circles */;
```

--

## ⚡ Transitions

```css
--transition-fast: 200ms /* Hover states */ --transition-base: 300ms
  /* Default */ --transition-slow: 500ms /* Large movements */;
```

**Easing:** `cubic-bezier(0.4, 0, 0.2, 1)` (smooth)

--

## 💈 Barber Pole Sizes

| Size     | Dimensions | Use Case           |
| -------- | ---------- | ------------------ |
| `nav`    | 18×48px    | Header navigation  |
| `small`  | 24×64px    | Footer, compact    |
| `medium` | 36×100px   | Default (corners)  |
| `large`  | 56×180px   | Prominent sections |
| `hero`   | 70×220px   | Homepage hero      |

--

## 🔧 Usage

### Include Pole Component

```liquid
{% include components/barber-pole-spinner.html
   position="static"
   size="small" %}
```

### Front Matter Options

```yaml
hide_barber_pole: true # Hide corner pole
barber_pole_size: medium # Size variant
barber_pole_position: fixed # fixed|absolute|static
```

--

## 📝 Brand Copy

**Tagline:** "Precision. Patience. Virtue. Honor."  
**Slogan:** "A CUT ABOVE"  
**Established:** "EST. 2024"  
**Location:** "Built with precision in NYC"  
**Philosophy:** "Like a fresh fade — clean, rounded, crisp"

--

## ✅ Checklist for New Pages

- [ ] Load `brand-tokens.css` first
- [ ] Include `barber-branding.css`
- [ ] Add pole to header (if custom header)
- [ ] Add pole to footer (if custom footer)
- [ ] Test with dark mode
- [ ] Test with reduced motion
- [ ] Verify mobile responsive

--

## 📚 Full Documentation

- **Brand Guide:** `docs/BRAND-GUIDE.md`
- **Implementation Summary:** `docs/BRANDING-IMPLEMENTATION-SUMMARY.md`
- **Visual Test:** Open `branding-test.html` in browser

--

**Remember:** Every pixel matters. Measure twice, code once. 💈✂️
