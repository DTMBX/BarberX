# National Anthem Audio Setup

The Star-Spangled Banner audio player requires a public domain audio file.

## Required File

Place your audio file at:
```
src/assets/media/audio/star-spangled-banner.mp3
```

Supported formats (in order of preference):
- `.mp3` (best compatibility)
- `.ogg` (open format)

## Recommended Sources (Public Domain)

1. **U.S. Navy Band** (Recommended)
   - Source: Wikimedia Commons
   - File: `United_States_Navy_Band_-_The_Star-Spangled_Banner.ogg`
   - URL: https://commons.wikimedia.org/wiki/File:United_States_Navy_Band_-_The_Star-Spangled_Banner.ogg
   - License: Public Domain (U.S. Government work)

2. **U.S. Marine Band**
   - Source: Library of Congress / Marine Band
   - License: Public Domain (U.S. Government work)

3. **U.S. Army Band "Pershing's Own"**
   - Source: usarmyband.com
   - License: Public Domain (U.S. Government work)

## Download Instructions

### Option 1: Manual Download
1. Go to the Wikimedia Commons link above
2. Click "Download" or right-click and "Save As"
3. Save as `star-spangled-banner.ogg` in `src/assets/media/audio/`
4. Optionally convert to MP3 for better compatibility

### Option 2: Command Line (PowerShell)
```powershell
# Download from Wikimedia Commons
$url = "https://upload.wikimedia.org/wikipedia/commons/8/86/United_States_Navy_Band_-_The_Star-Spangled_Banner.ogg"
Invoke-WebRequest -Uri $url -OutFile "src/assets/media/audio/star-spangled-banner.ogg"
```

### Option 3: Using curl
```bash
curl -L "https://upload.wikimedia.org/wikipedia/commons/8/86/United_States_Navy_Band_-_The_Star-Spangled_Banner.ogg" -o src/assets/media/audio/star-spangled-banner.ogg
```

## Player Behavior

Without the audio file:
- The anthem player UI will be hidden (`is-unavailable` class)
- No errors will appear to the user
- The flag video hero continues to function normally

With the audio file:
- Gentle 3-second fade-in on page load
- Plays at 40% volume (respectful level)
- Graceful fade-out when song ends
- Replay button appears after completion
- User can mute (preference is saved)
- Respects `prefers-reduced-motion` (no autoplay)

## Legal Notes

All U.S. military band recordings are in the public domain as works of the 
U.S. federal government (17 U.S.C. § 105).

The Star-Spangled Banner itself is a public domain national anthem with 
lyrics by Francis Scott Key (1814) and music by John Stafford Smith (c. 1773).
