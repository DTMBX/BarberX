# Video Setup Instructions for Flag Hero

## Required Asset

**File Location:** `src/assets/media/flag.mp4`

## Video Specifications

### Recommended Settings

- **Resolution:** 1920×1080 (HD) or 3840×2160 (4K)
- **Codec:** H.264 (MP4)
- **Duration:** 10-30 seconds (will loop seamlessly)
- **Framerate:** 24fps or 30fps
- **File Size:** Under 5MB for HD, under 15MB for 4K
- **Audio:** None (video will be muted)

### Content Guidelines

- Gentle waving flag motion (subtle, dignified)
- American flag or abstract patriotic motion graphics
- Professional, restrained aesthetic
- Avoid: rapid motion, aggressive cuts, flashy effects

### Style Reference

Inspired by **AmericaByDesign.gov** flag video aesthetic:

- Slow, elegant wave
- High contrast for text legibility
- Suitable for professional/government context

## How to Add Your Video

1. Obtain or create a flag video matching the specifications above
2. Name it exactly: `flag.mp4`
3. Place it at: `src/assets/media/flag.mp4`
4. Run `npm run build` to process video renditions
5. Build system will automatically generate optimized versions

## Fallback Behavior

If no video is present:

- Hero section displays gradient background with static flag SVG
- All text remains fully legible
- Design degrades gracefully
- No broken elements or missing content

## Testing

After adding video:

```bash
npm run build
npm run serve
```

Visit `http://localhost:8080` to see the flag hero in action.

## Legal Compliance

Ensure flag video usage complies with:

- U.S. Flag Code (4 USC §1-10)
- Copyright/licensing requirements
- Evident's content standards (see copilot-instructions.md)

Video should be used respectfully and within proper context for legal-technology
platform.
