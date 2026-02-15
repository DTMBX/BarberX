# 🎵 National Anthem Player - Setup Required

## Quick Start

The National Anthem audio player is **fully implemented** but needs an audio file to function.

### What's Complete ✅

- Glass-effect player controls (beautiful UI in bottom-right of hero)
- 3-second gentle fade-in (respectful, not startling)
- Autoplay with browser policy compliance
- Mute toggle with localStorage preference
- Replay button functionality
- Reduced-motion support
- Full accessibility (ARIA labels, keyboard navigation)
- Error handling and graceful degradation

### What You Need to Do 📥

**Download an MP3 of The Star-Spangled Banner and place it at:**

```
src/assets/media/audio/star-spangled-banner.mp3
```

### Recommended Sources

**Easiest Options:**
1. **YouTube Audio Library** - https://www.youtube.com/audiolibrary (search "Star Spangled Banner")
2. **Pixabay Music** - https://pixabay.com/music/ (search "anthem")
3. **Internet Archive** - https://archive.org/details/audio (filter "Public Domain")

**Requirements:**
- Format: MP3 (or OGG)
- Size: Preferably < 5MB
- Quality: 128-192 kbps recommended
- License: Public domain or free to use

### After Adding the File

```powershell
# Rebuild the site
npx @11ty/eleventy

# If dev server is running, it will auto-reload
# Otherwise start it:
npx @11ty/eleventy --serve
```

Visit http://localhost:8080 and the anthem will autoplay with a gentle fade-in!

---

## Detailed Instructions

See: [src/assets/media/audio/DOWNLOAD_ANTHEM.md](src/assets/media/audio/DOWNLOAD_ANTHEM.md)

## Current Status

- ✅ Player UI visible and beautiful
- ✅ All JavaScript logic implemented
- ✅ CSS styling complete
- ⏳ Audio file needs to be manually added
- ✅ Gracefully handles missing audio (no errors shown to users)

---

**Why Manual Download?**

Automated downloads failed due to anti-scraping protection on free music sites. Manual download gives you control over the audio source and quality.

**Delete this file** once you've added the audio file and confirmed it works.
