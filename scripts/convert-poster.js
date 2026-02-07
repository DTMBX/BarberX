const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const posterJpg = path.join(process.cwd(), 'src/assets/images/flag-poster.jpg');
const outWebp = path.join(process.cwd(), 'src/assets/images/flag-poster.webp');
const outJpg = path.join(process.cwd(), 'src/assets/images/flag-poster-optimized.jpg');

(async () => {
  if (!fs.existsSync(posterJpg)) {
    console.log('No poster found at', posterJpg);
    process.exit(0);
  }

  try {
    await sharp(posterJpg)
      .resize({ width: 1280 })
      .webp({ quality: 80 })
      .toFile(outWebp);

    await sharp(posterJpg)
      .resize({ width: 1280 })
      .jpeg({ quality: 82 })
      .toFile(outJpg);

    console.log('Poster optimized:', outWebp, outJpg);
  } catch (e) {
    console.error('Poster optimization failed:', e.message);
    process.exit(2);
  }
})();
