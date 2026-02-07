const sharp = require('sharp');
const fs = require('fs');
const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180'>
  <rect width='100%' height='100%' fill='#0b5f73'/>
  <text x='50%' y='50%' dy='0.35em' fill='#fff' font-family='Arial' font-size='48' text-anchor='middle'>E</text>
</svg>`;
const buffer = Buffer.from(svg);
const out1 = 'src/assets/img/apple-touch-icon.png';
const out2 = 'src/assets/images/apple-touch-icon.png';
(async function(){
  await sharp(buffer).png({compressionLevel:9}).toFile(out1);
  await sharp(buffer).png({compressionLevel:9}).toFile(out2);
  console.log('WROTE', out1, out2);
})();
