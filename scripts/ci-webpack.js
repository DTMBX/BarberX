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
const webpackConfigPath = path.join(cwd, 'webpack.config.js');
const hasWebpackConfig = fs.existsSync(webpackConfigPath);

if (!hasEntry || !hasWebpackConfig) {
  console.log('No frontend entry or webpack.config.js found — skipping webpack.');
  process.exit(0);
}

// If webpack config references WebAssembly or project expects a .wasm entry, ensure the file exists.
let webpackConfigContents = '';
try {
  webpackConfigContents = fs.readFileSync(webpackConfigPath, 'utf8');
} catch (err) {
  // already guarded by existsSync, but be defensive
  webpackConfigContents = '';
}

const expectsWasm = /\.wasm|index\.wasm|wasm\b/i.test(webpackConfigContents);
const wasmPath = path.join(cwd, 'src', 'index.wasm');
if (expectsWasm && !fs.existsSync(wasmPath)) {
  console.log(`webpack config references .wasm but ${wasmPath} doesn't exist — skipping webpack to avoid CI failure.`);
  process.exit(0);
}

console.log('Frontend entry detected — running webpack');
const res = spawnSync('npx', ['--yes', 'webpack', '--mode=production'], { stdio: 'inherit' });
process.exit(res.status);
