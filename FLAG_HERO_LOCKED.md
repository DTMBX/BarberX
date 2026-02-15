# FLAG HERO — LOCKED CANONICAL

## Status: PROTECTED

**Date Locked:** February 11, 2026  
**Version:** 1.0.0  
**Git Tag:** `flag-hero-v1.0.0-canonical`

---

## Protected Files

| File | Purpose |
|------|---------|
| `src/_includes/components/flag-hero.njk` | Hero component template |
| `src/_includes/components/flag-hero.njk.CANONICAL` | Reference backup |
| `assets/css/components/flag-hero.css` | Hero styling |
| `src/_includes/components/anthem-player.njk` | National Anthem player |
| `assets/css/components/anthem-player.css` | Player styling |
| `src/assets/js/anthem-player.js` | Player behavior |
| `src/assets/media/audio/star-spangled-banner.mp3` | Audio file |

---

## National Anthem Player Specifications

### Audio Behavior
- **Autoplay:** 1.5 seconds after page load
- **Fade-in:** 3 seconds (respectful, non-startling)
- **Fade-out:** 2 seconds (when paused or ending)
- **Initial Volume:** 40%
- **Maximum Volume:** 50%

### User Experience
- Glass-effect control panel, bottom-right of hero
- Play/Pause toggle with visual feedback
- Mute toggle (preference saved to localStorage)
- Replay button appears when song ends
- Pulsing music note indicator during playback
- Respects `prefers-reduced-motion` setting

### Accessibility
- ARIA labels on all controls
- Keyboard navigable
- Reduced-motion support disables animations
- Screen reader announcements for state changes

---

## Restoration Procedure

If hero is accidentally modified, restore from canonical backup:

```powershell
Copy-Item src/_includes/components/flag-hero.njk.CANONICAL src/_includes/components/flag-hero.njk
git checkout flag-hero-v1.0.0-canonical -- assets/css/components/flag-hero.css
git checkout flag-hero-v1.0.0-canonical -- src/_includes/components/anthem-player.njk
git checkout flag-hero-v1.0.0-canonical -- assets/css/components/anthem-player.css
git checkout flag-hero-v1.0.0-canonical -- src/assets/js/anthem-player.js
```

---

## Certification

This hero component and National Anthem player honor:
- The American flag
- All who have served
- Truth, integrity, and due process

Modifications to this component require explicit approval and documentation.

---

*Evident Technologies — Truth. Preserved. Justice. Served.*
