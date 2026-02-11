# National Anthem Audio File Required

## Status: Audio File Missing

The anthem player is configured but the audio file needs to be manually downloaded.

## Download Instructions

### Option 1: Internet Archive (U.S. Military Academy Band)

1. Visit: https://archive.org/details/USMA_Band
2. Find: "The Star Spangled Banner"
3. Right-click → "Save Link As"
4. Save to: `src/assets/media/audio/star-spangled-banner.mp3`

### Option 2: Wikimedia Commons (Public Domain)

1. Visit: https://commons.wikimedia.org/wiki/File:Star_Spangled_Banner_instrumental.ogg
2. Click "Download" → Choose MP3 if available, or OGG
3. Save as: `src/assets/media/audio/star-spangled-banner.mp3` (or `.ogg`)

### Option 3: MusicBrainz

1. Visit: https://musicbrainz.org/
2. Search: "Star Spangled Banner instrumental public domain"
3. Download MP3 version
4. Save to: `src/assets/media/audio/star-spangled-banner.mp3`

## File Requirements

- **Format:** MP3 or OGG
- **Filename:** `star-spangled-banner.mp3` (or `.ogg`)
- **Location:** `src/assets/media/audio/`
- **Size:** Recommended < 5MB
- **Quality:** 128-192 kbps is sufficient

## After Downloading

1. Place file in `src/assets/media/audio/`
2. Rebuild: `npx @11ty/eleventy`
3. Test at: http://localhost:8080

## Current Behavior Without Audio

- Player will show "Audio unavailable" message
- Play button will be visible but non-functional
- No errors will appear to end users
- Site remains fully functional

---

**Note:** The automated download failed due to anti-scraping protection on source websites. Manual download required.
