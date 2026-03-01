import imagemin from 'imagemin';
import mozjpeg from 'imagemin-mozjpeg';
import pngquant from 'imagemin-pngquant';
import svgo from 'imagemin-svgo';

const files = await imagemin(['assets/img/**/*.{jpg,jpeg,png,svg}'], {
  destination: 'assets/img/',
  plugins: [
    mozjpeg({ quality: 75 }),
    pngquant({ quality: [0.6, 0.8] }),
    svgo()
  ]
});
console.log(`Compressed ${files.length} images.`);
