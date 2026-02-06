Flag media placement and guidelines

1. Add the actual video file to: `src/assets/media/flag.mp4` (MP4 H.264 is recommended for broad compatibility).
2. Add a poster image for the video at: `src/assets/images/flag-poster.jpg` (use 1280×720 or similar).
3. If you have multiple variants (webm, av1), add them as additional `<source>` entries in `src/_includes/components/flag-video.njk`.
4. For production builds, prefer storing the canonical video in CI artifacts or an origin (CDN/S3) and reference the content-addressed URL.
5. When replacing the placeholder, run image optimization for the poster and consider generating multiple video renditions (adaptive bitrate) if you need performance.

Example local add:

```bash
mkdir -p src/assets/media src/assets/images
cp /path/to/flag.mp4 src/assets/media/flag.mp4
cp /path/to/flag-poster.jpg src/assets/images/flag-poster.jpg
npm run build
```
