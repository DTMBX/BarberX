const fs = require('fs');
const path = require('path');

function copyFile(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

const filesToCopy = [
  { src: 'src/assets/css/tokens.css', dest: '_site/assets/css/tokens.css' },
  { src: 'assets/css/core.css', dest: '_site/assets/css/core.css' },
  { src: 'src/assets/img/logo/light-variant-logo.svg', dest: '_site/assets/img/logo/light-variant-logo.svg' },
  { src: 'src/assets/img/brand/evident-wordmark-light-hd.svg', dest: '_site/assets/img/brand/evident-wordmark-light-hd.svg' },
  { src: 'src/assets/img/apple-touch-icon.png', dest: '_site/assets/img/apple-touch-icon.png' },
  { src: 'src/assets/images/apple-touch-icon.png', dest: '_site/assets/images/apple-touch-icon.png' },
  { src: 'src/assets/images/logo-source.svg', dest: '_site/assets/images/logo-source.svg' },
  { src: 'src/favicon.ico', dest: '_site/favicon.ico' },
];

filesToCopy.forEach(({ src, dest }) => {
  if (fs.existsSync(src)) {
    copyFile(src, dest);
    console.log(`Copied ${src} -> ${dest}`);
  } else {
    console.warn(`Missing source file: ${src}`);
  }
});