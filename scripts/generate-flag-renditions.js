const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const sharp = require('sharp');

const repoRoot = path.resolve(__dirname, '..');
const srcMediaDir = path.join(repoRoot, 'src', 'assets', 'media');
const renditionsDir = path.join(srcMediaDir, 'renditions');
const sourceVideo = path.join(srcMediaDir, 'flag.mp4');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function hasFFmpeg() {
  const which = process.platform === 'win32' ? 'where' : 'which';
  try {
    const res = spawnSync(which, ['ffmpeg'], { stdio: 'ignore' });
    return res.status === 0;
  } catch (e) {
    return false;
  }
}

function runFF(args) {
  const res = spawnSync('ffmpeg', args, { stdio: 'inherit' });
  return res.status === 0;
}

async function generatePosterFromSVG(outPath) {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='720'>\n  <rect width='100%' height='100%' fill='#0b5f73'/>\n  <text x='50%' y='50%' dy='0.35em' fill='#fff' font-family='Arial, Helvetica, sans-serif' font-size='48' text-anchor='middle'>Evident — Flag Poster</text>\n</svg>`;
  const buffer = Buffer.from(svg);
  await sharp(buffer).jpeg({ quality: 80 }).toFile(outPath);
}

(async function main(){
  console.log('prepare:media — generating flag renditions');
  ensureDir(renditionsDir);

  if (!fs.existsSync(sourceVideo)) {
    console.log('No source video found at', sourceVideo);
    console.log('Place your master video at src/assets/media/flag.mp4 to generate renditions.');
    // still create a poster placeholder
    const posterPath = path.join(renditionsDir, 'flag-poster.jpg');
    if (!fs.existsSync(posterPath)) {
      await generatePosterFromSVG(posterPath);
      console.log('Generated placeholder poster at', posterPath);
    }
    return;
  }

  const ff = hasFFmpeg();
  if (!ff) console.log('ffmpeg not found in PATH — falling back to copy-only renditions where possible');

  const tasks = [];
  const mp4_1080 = path.join(renditionsDir, 'flag-1080p.mp4');
  const mp4_720 = path.join(renditionsDir, 'flag-720p.mp4');
  const mp4_360 = path.join(renditionsDir, 'flag-360p.mp4');
  const webm_1080 = path.join(renditionsDir, 'flag-1080p.webm');
  const webm_720 = path.join(renditionsDir, 'flag-720p.webm');
  const webm_360 = path.join(renditionsDir, 'flag-360p.webm');
  const poster = path.join(renditionsDir, 'flag-poster.jpg');

  if (ff) {
    // Create MP4 renditions
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libx264','-preset','veryfast','-crf','23','-vf','scale=1920:-2','-c:a','aac','-b:a','128k', mp4_1080]));
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libx264','-preset','veryfast','-crf','23','-vf','scale=1280:-2','-c:a','aac','-b:a','128k', mp4_720]));
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libx264','-preset','veryfast','-crf','28','-vf','scale=640:-2','-c:a','aac','-b:a','96k', mp4_360]));
    // Create WebM renditions (VP9)
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libvpx-vp9','-b:v','2M','-vf','scale=1920:-2', webm_1080]));
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libvpx-vp9','-b:v','1M','-vf','scale=1280:-2', webm_720]));
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-c:v','libvpx-vp9','-b:v','512k','-vf','scale=640:-2', webm_360]));
    // Poster
    tasks.push(() => runFF(['-y','-i', sourceVideo,'-ss','00:00:01.000','-vframes','1', poster]));

    for (const t of tasks) {
      try {
        const ok = t();
        if (!ok) console.warn('A task failed.');
      } catch (e) {
        console.warn('Task error', e && e.message);
      }
    }
    console.log('ffmpeg renditions finished (if ffmpeg available).');
  } else {
    // Fallback: copy source as 1080p and generate poster via sharp
    try {
      fs.copyFileSync(sourceVideo, mp4_1080);
      console.log('Copied source to', mp4_1080);
      await generatePosterFromSVG(poster);
      console.log('Generated placeholder poster at', poster);
    } catch (e) {
      console.error('Fallback tasks failed:', e.message);
    }
  }

  console.log('prepare:media — done. Renditions are in', renditionsDir);
})();
