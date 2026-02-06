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
if (!hasEntry) {
  console.log('No frontend entry found under ./src — skipping webpack.');
  process.exit(0);
}

console.log('Frontend entry detected — running webpack');
const res = spawnSync('npx', ['--yes', 'webpack', '--mode=production'], { stdio: 'inherit' });
process.exit(res.status);
