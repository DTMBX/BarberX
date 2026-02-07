const fs = require('fs').promises;
const path = require('path');
const sharp = require('sharp');

const srcDir = path.join(__dirname, '..', 'src', 'assets', 'images');
const outDir = path.join(__dirname, '..', '_site', 'assets', 'images');

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function optimizeFile(file) {
  const ext = path.extname(file).toLowerCase();
  if (!['.jpg', '.jpeg', '.png', '.webp', '.svg'].includes(ext)) return;
  const infile = path.join(srcDir, file);
  const outBase = path.join(outDir, path.basename(file, ext));
  await ensureDir(outDir);
  try {
    if (ext === '.svg') {
      // copy svg as-is
      await fs.copyFile(infile, outBase + '.svg');
      return;
    }
    const image = sharp(infile);
    // create multiple sizes and webp
    const sizes = [320, 640, 1024];
    for (const w of sizes) {
      await image
        .resize({ width: w })
        .toFile(`${outBase}-${w}.jpg`);
      await image
        .resize({ width: w })
        .webp()
        .toFile(`${outBase}-${w}.webp`);
    }
  } catch (err) {
    console.warn('Skipping image due to error:', infile, err.message);
    return;
  }
}

async function run() {
  try {
    const files = await fs.readdir(srcDir);
    await Promise.all(files.map(optimizeFile));
    console.log('Images optimized to', outDir);
  } catch (err) {
    console.error('Image optimization failed:', err.message);
    process.exit(1);
  }
}

run();
