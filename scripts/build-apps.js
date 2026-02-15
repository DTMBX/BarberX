#!/usr/bin/env node
/**
 * Build satellite apps and copy their dist/ output into _site/apps/.
 * Each app is a Vite/React SPA built independently.
 *
 * Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
 * PROPRIETARY — See LICENSE.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SITE_DIR = path.resolve(__dirname, '..', '_site');
const APPS_DIR = path.resolve(__dirname, '..', 'apps');
const APPS_OUTPUT = path.join(SITE_DIR, 'apps');

/** @type {Array<{dir: string, slug: string, label: string}>} */
const apps = [
  { dir: 'civics-hierarchy', slug: 'civics-hierarchy', label: 'Civics Hierarchy' },
  { dir: 'epstein-library-evid', slug: 'epstein-library', label: 'Epstein Document Library' },
  { dir: 'essential-goods-ledg', slug: 'essential-goods', label: 'Essential Goods Ledger' },
  { dir: 'geneva-bible-study-t', slug: 'geneva-bible-study', label: 'Geneva Bible Study' },
];

console.log('\n=== Building Satellite Apps ===\n');

let built = 0;
let skipped = 0;

for (const app of apps) {
  const appPath = path.join(APPS_DIR, app.dir);
  const pkgPath = path.join(appPath, 'package.json');

  if (!fs.existsSync(pkgPath)) {
    console.log(`  SKIP: ${app.label} (no package.json)`);
    skipped++;
    continue;
  }

  console.log(`  Building: ${app.label} ...`);
  const outputDir = path.join(APPS_OUTPUT, app.slug);

  try {
    // Install if node_modules doesn't exist
    const nodeModules = path.join(appPath, 'node_modules');
    if (!fs.existsSync(nodeModules)) {
      execSync('npm install --no-audit --no-fund', {
        cwd: appPath,
        stdio: 'pipe',
        timeout: 300000,
      });
    }

    // Build
    execSync('npm run build', {
      cwd: appPath,
      stdio: 'pipe',
      timeout: 300000,
    });

    // Copy dist to _site/apps/<slug>
    const distPath = path.join(appPath, 'dist');
    if (fs.existsSync(distPath)) {
      fs.mkdirSync(outputDir, { recursive: true });
      copyRecursive(distPath, outputDir);
      const fileCount = countFiles(outputDir);
      console.log(`  DONE: ${app.label} -> _site/apps/${app.slug}/ (${fileCount} files)`);
      built++;
    } else {
      console.log(`  WARN: ${app.label} built but no dist/ directory found`);
      skipped++;
    }
  } catch (err) {
    console.error(`  FAIL: ${app.label}: ${err.message}`);
    // Continue building other apps
    skipped++;
  }
}

console.log(`\n=== Done: ${built} built, ${skipped} skipped ===\n`);

/**
 * Recursively copy directory contents.
 * @param {string} src
 * @param {string} dest
 */
function copyRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Count files recursively.
 * @param {string} dir
 * @returns {number}
 */
function countFiles(dir) {
  let count = 0;
  if (!fs.existsSync(dir)) return 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      count += countFiles(path.join(dir, entry.name));
    } else {
      count++;
    }
  }
  return count;
}
