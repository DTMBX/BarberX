const sharp = require('sharp');
const fs = require('fs');
const inPath = 'src/assets/img/apple-touch-icon.png';
const outPath = 'src/assets/images/apple-touch-icon.png';
if (!fs.existsSync(inPath)) { console.error('INPUT MISSING', inPath); process.exit(1); }
sharp(inPath).png({compressionLevel:9}).toFile(outPath).then(()=>console.log('REENCODED', outPath)).catch(e=>{ console.error('REENCODE ERROR', e && e.message); process.exit(1); });
