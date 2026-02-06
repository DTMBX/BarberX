const fs = require('fs');
const path = require('path');

const media = [
  { file: 'src/assets/media/flag.mp4', minBytes: 1024 * 10 }, // at least 10KB
  { file: 'src/assets/images/flag-poster.jpg', minBytes: 1024 }
];

let failed = false;
media.forEach(item => {
  const p = path.join(process.cwd(), item.file);
  if (!fs.existsSync(p)) {
    console.error('MISSING:', item.file);
    failed = true;
    return;
  }
  const stat = fs.statSync(p);
  if (item.minBytes && stat.size < item.minBytes) {
    console.error(`TOO_SMALL: ${item.file} (${stat.size} bytes)`);
    failed = true;
  }
});

if (failed) {
  console.error('Media validation failed. Ensure production assets are present and non-empty.');
  process.exit(2);
}

console.log('Media validation passed.');
