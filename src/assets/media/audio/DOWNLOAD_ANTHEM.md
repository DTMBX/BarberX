# National Anthem Audio File - Manual Download Required

## Status: Audio File Missing (Manual Download Required)

The automated download failed due to network restrictions. The audio file must
be manually downloaded.

## Quick Steps

1. **Download the audio file** from one of the sources below
2. **Save it as:** `star-spangled-banner.mp3`
3. **Place it in:** `src/assets/media/audio/`
4. **Rebuild:** `npx @11ty/eleventy`

---

## Recommended Sources (Public Domain)

### Option 1: YouTube Audio Library (Free, No Attribution Required)

1. Visit: https://www.youtube.com/audiolibrary
2. Search: "Star Spangled Banner"
3. Download MP3
4. Rename to: `star-spangled-banner.mp3`

### Option 2: Free Music Archive

1. Visit: https://freemusicarchive.org/
2. Search: "Star Spangled Banner instrumental"
3. Filter by: "Public Domain" or "CC0"
4. Download MP3

### Option 3: Pixabay (Free Music)

1. Visit: https://pixabay.com/music/
2. Search: "National Anthem" or "Star Spangled Banner"
3. Download MP3 (free account required)

### Option 4: Internet Archive

1. Visit: https://archive.org/details/audio
2. Search: "Star Spangled Banner instrumental"
3. Filter: "Public Domain"
4. Download MP3 version

### Option 5: Use Your Own Recording

- Any MP3 file works
- Instrumental version recommended (respectful, no distractions)
- Recommended specs:
  - Format: MP3
  - Size: < 5MB
  - Bitrate: 128-192 kbps
  - Duration: 1-2 minutes

---

## Manual Download Steps

**Windows PowerShell:**

```powershell
# After manually downloading the file:
Move-Item "Downloads\your-anthem-file.mp3" "src\assets\media\audio\star-spangled-banner.mp3"
npx @11ty/eleventy
```

**Or simply:**

1. Download any Star-Spangled Banner MP3
2. Rename it to: `star-spangled-banner.mp3`
3. Copy to: `c:\web-dev\github-repos\Evident\src\assets\media\audio\`
4. Rebuild site

---

## After Adding the File

The anthem will automatically:

- ✓ Autoplay with 3-second gentle fade-in
- ✓ Start at 40% volume (not startling)
- ✓ Show glass-effect controls (bottom-right of hero)
- ✓ Provide replay button when finished
- ✓ Remember user's mute preference
- ✓ Respect reduced-motion settings

---

## Current Behavior (Without Audio)

- Player controls are visible
- Clicking play shows error in console
- System remains fully functional
- No user-facing errors displayed

---

**Why Manual Download?**

Automated downloads failed due to:

- Anti-scraping protection on source sites
- Network timeouts
- 404 errors on direct file URLs
- CORS restrictions

Manual download is more reliable and gives you control over the audio source
quality.
