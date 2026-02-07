#!/usr/bin/env node
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const cwd = process.cwd();
const patterns = [
  'src/assets/css/**/*.css',
  'src/**/*.css'
];

// Use git to detect tracked files matching the patterns so we avoid NoFilesFoundError
let matched = '';
try {
  const args = ['ls-files', '--'] .concat(patterns);
  const res = spawnSync('git', args, { cwd, encoding: 'utf8' });
  if (res.status === 0 && res.stdout) matched = res.stdout.trim();
} catch (err) {
  matched = '';
}

if (!matched) {
  console.log('No CSS files found for stylelint patterns — skipping stylelint.');
  process.exit(0);
}

const files = matched.split(/\r?\n/).filter(Boolean);
console.log('Running stylelint on', files.length, 'files');
const res = spawnSync('npx', ['--yes', 'stylelint', ...files], { stdio: 'inherit', cwd });
process.exit(res.status);
