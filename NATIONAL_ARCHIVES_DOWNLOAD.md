# Download National Anthem from National Archives (Official Version)

## Official U.S. Government Recording

Unfortunately, the National Archives and other official U.S. government sources don't provide direct download links that work with automated tools - they require interactive browser sessions.

## Manual Download from National Archives

### Method 1: National Archives Digital Vault

1. **Visit:** https://www.archives.gov/exhibits/charters/star_spangled_banner.html
2. Look for audio/media player on the page
3. Right-click on audio player → "Save audio as..."
4. Save to: `src\assets\media\audio\star-spangled-banner.mp3`

### Method 2: Library of Congress (Official Recording)

1. **Visit:** https://www.loc.gov/item/ihas.200197495/
2. This is the U.S. Marine Band official recording
3. Click "Download" button
4. Choose MP3 format
5. Save to: `src\assets\media\audio\star-spangled-banner.mp3`

### Method 3: U.S. Military Bands Official Recordings

**U.S. Marine Band ("The President's Own"):**
1. Visit: https://www.marineband.marines.mil/Audio-Resources/
2. Search for "National Anthem" or "Star-Spangled Banner"
3. Download official recording
4. Save as: `star-spangled-banner.mp3`

**U.S. Army Band ("Pershing's Own"):**
1. Visit: https://www.usarmyband.com/download-music.html
2. Find "The Star-Spangled Banner"
3. Download MP3
4. Save to project folder

### Method 4: Defense Visual Information Distribution Service (DVIDS)

1. Visit: https://www.dvidshub.net/
2. Search: "Star Spangled Banner audio"
3. Filter by: Audio files, Public Domain
4. Download official military band recording

---

## After Downloading

```powershell
# Verify the file
Get-Item "src\assets\media\audio\star-spangled-banner.mp3"

# Rebuild site
npx @11ty/eleventy

# Test
# Open http://localhost:8080
```

---

## Why Automated Download Failed

Official U.S. government websites have:
- JavaScript-based players (not direct links)
- CAPTCHA / bot protection
- Session-based authentication
- Dynamic CDN URLs that expire
- HTML access control

**Manual download from an official source ensures:**
- ✓ Authentic official recording
- ✓ Appropriate audio quality
- ✓ Legal public domain status
- ✓ Respectful presentation

---

## Quick Alternative (If Needed)

If you need to test immediately, here's a working public domain instrumental:

```powershell
curl.exe -L -o "src\assets\media\audio\star-spangled-banner.mp3" "https://www.bensound.com/bensound-music/bensound-ukulele.mp3"
```

**(This is NOT the National Anthem - just for testing the player functionality)**

Replace with official version from National Archives once downloaded.
