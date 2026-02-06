#!/usr/bin/env node
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const cwd = process.cwd();
const candidates = [
  path.join(cwd, 'src', 'index.js'),
  path.join(cwd, 'src', 'index.ts'),
  path.join(cwd, 'src', 'index.tsx'),
  path.join(cwd, 'src', 'main.js')
];

const hasEntry = candidates.some(p => fs.existsSync(p));
const webpackConfig = path.join(cwd, 'webpack.config.js');
const hasWebpackConfig = fs.existsSync(webpackConfig);
if (!hasEntry || !hasWebpackConfig) {
  console.log('No frontend entry or webpack.config.js found — skipping webpack.');
  process.exit(0);
}

console.log('Frontend entry detected — running webpack');
const res = spawnSync('npx', ['--yes', 'webpack', '--mode=production'], { stdio: 'inherit' });
process.exit(res.status);
