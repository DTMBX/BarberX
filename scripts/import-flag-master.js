const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

if (process.argv.length < 3) {
  console.error('Usage: node import-flag-master.js /path/to/master.mp4');
  process.exit(2);
}

const src = path.resolve(process.argv[2]);
const repoRoot = path.resolve(__dirname, '..');
const destDir = path.join(repoRoot, 'src', 'assets', 'media');
const dest = path.join(destDir, 'flag.mp4');

if (!fs.existsSync(src)) {
  console.error('Source file does not exist:', src);
  process.exit(2);
}

fs.mkdirSync(destDir, { recursive: true });
fs.copyFileSync(src, dest);
console.log('Copied master to', dest);

// Run the existing renditions generator
console.log('Running renditions generator...');
const res = spawnSync(process.execPath, [path.join(__dirname, 'generate-flag-renditions.js')], { stdio: 'inherit' });
if (res.status !== 0) process.exit(res.status);
console.log('Renditions generation complete.');
