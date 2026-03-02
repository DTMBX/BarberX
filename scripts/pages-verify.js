#!/usr/bin/env node
/**
 * @fileoverview GitHub Pages build verification script.
 * Ensures build output meets deployment requirements.
 * Run after build, before deploy. Exit code 0 = pass, 1 = fail.
 *
 * Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
 * PROPRIETARY — See LICENSE.
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = '_site';
const EXPECTED_DOMAIN = 'www.evident.icu';

const errors = [];
const warnings = [];

/**
 * Log verification result.
 * @param {'pass'|'fail'|'warn'} status
 * @param {string} message
 */
function log(status, message) {
  const symbols = { pass: '✓', fail: '✗', warn: '⚠' };
  const colors = { pass: '\x1b[32m', fail: '\x1b[31m', warn: '\x1b[33m' };
  const reset = '\x1b[0m';
  console.log(`${colors[status]}${symbols[status]}${reset} ${message}`);
}

/**
 * Recursively get all files in directory.
 * @param {string} dir
 * @returns {string[]}
 */
function getAllFiles(dir) {
  const files = [];
  if (!fs.existsSync(dir)) return files;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...getAllFiles(fullPath));
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

// 1. Check output directory exists and is non-empty
console.log('\n=== GitHub Pages Build Verification ===\n');

if (!fs.existsSync(OUTPUT_DIR)) {
  log('fail', `Output directory "${OUTPUT_DIR}" does not exist`);
  errors.push('Missing output directory');
} else {
  const files = getAllFiles(OUTPUT_DIR);
  if (files.length === 0) {
    log('fail', `Output directory "${OUTPUT_DIR}" is empty`);
    errors.push('Empty output directory');
  } else {
    log('pass', `Output directory exists with ${files.length} files`);
  }
}

// 2. Check index.html exists
const indexPath = path.join(OUTPUT_DIR, 'index.html');
if (!fs.existsSync(indexPath)) {
  log('fail', 'index.html not found in output');
  errors.push('Missing index.html');
} else {
  log('pass', 'index.html exists');
}

// 3. Check CNAME file
const cnamePath = path.join(OUTPUT_DIR, 'CNAME');
if (!fs.existsSync(cnamePath)) {
  log('fail', 'CNAME file not found in output');
  errors.push('Missing CNAME file');
} else {
  const cnameContent = fs.readFileSync(cnamePath, 'utf8').trim();
  if (cnameContent === EXPECTED_DOMAIN) {
    log('pass', `CNAME contains "${EXPECTED_DOMAIN}"`);
  } else {
    log('fail', `CNAME contains "${cnameContent}" but expected "${EXPECTED_DOMAIN}"`);
    errors.push('CNAME domain mismatch');
  }
}

// 4. Check for localhost references in HTML (only in href/src attributes, not documentation)
const htmlFiles = getAllFiles(OUTPUT_DIR).filter((f) => f.endsWith('.html'));
let localhostCount = 0;
const localhostAttrPattern = /(href|src|action)=["'](https?:\/\/localhost[^\s"']*)/gi;

for (const file of htmlFiles) {
  const content = fs.readFileSync(file, 'utf8');
  let match;
  while ((match = localhostAttrPattern.exec(content)) !== null) {
    localhostCount++;
    log('fail', `Found localhost in ${match[1]} attribute: ${path.relative(OUTPUT_DIR, file)}`);
  }
}

if (localhostCount === 0) {
  log('pass', `No localhost references in ${htmlFiles.length} HTML files`);
} else {
  errors.push(`Found ${localhostCount} localhost references`);
}

// 5. Check for broken asset references (href/src starting with /)
let brokenAssetCount = 0;
const assetPattern = /(href|src)=["'](\/[^"']+)["']/gi;

for (const file of htmlFiles) {
  const content = fs.readFileSync(file, 'utf8');
  let match;
  while ((match = assetPattern.exec(content)) !== null) {
    const assetPath = match[2];
    // Skip external links, anchors, and common valid roots
    if (
      assetPath.startsWith('//') ||
      assetPath.startsWith('/#') ||
      assetPath.includes('#') ||
      assetPath === '/'
    ) {
      continue;
    }
    // Check if the referenced file exists
    const resolvedPath = path.join(OUTPUT_DIR, assetPath);
    if (!fs.existsSync(resolvedPath) && !fs.existsSync(resolvedPath + '.html')) {
      // Check without trailing slash for directories
      const dirIndex = path.join(resolvedPath, 'index.html');
      if (!fs.existsSync(dirIndex)) {
        brokenAssetCount++;
        if (brokenAssetCount <= 5) {
          log('warn', `Possibly missing asset: ${assetPath} (in ${path.relative(OUTPUT_DIR, file)})`);
        }
      }
    }
  }
}

if (brokenAssetCount === 0) {
  log('pass', 'No obviously broken asset references found');
} else if (brokenAssetCount <= 5) {
  warnings.push(`${brokenAssetCount} potentially missing assets`);
} else {
  log('warn', `${brokenAssetCount} potentially missing assets (showing first 5)`);
  warnings.push(`${brokenAssetCount} potentially missing assets`);
}

// 6. Check total output size
const totalSize = getAllFiles(OUTPUT_DIR).reduce((sum, file) => {
  return sum + fs.statSync(file).size;
}, 0);
const sizeMB = (totalSize / (1024 * 1024)).toFixed(2);
if (totalSize > 500 * 1024 * 1024) {
  log('warn', `Output size is ${sizeMB}MB (consider optimization)`);
  warnings.push('Large output size');
} else {
  log('pass', `Output size: ${sizeMB}MB`);
}

// Summary
console.log('\n=== Verification Summary ===\n');
console.log(`HTML pages: ${htmlFiles.length}`);
console.log(`Total files: ${getAllFiles(OUTPUT_DIR).length}`);
console.log(`Output size: ${sizeMB}MB`);
console.log(`Errors: ${errors.length}`);
console.log(`Warnings: ${warnings.length}`);

if (errors.length > 0) {
  console.log('\n\x1b[31mVerification FAILED\x1b[0m');
  errors.forEach((e) => console.log(`  - ${e}`));
  process.exit(1);
} else if (warnings.length > 0) {
  console.log('\n\x1b[33mVerification PASSED with warnings\x1b[0m');
  warnings.forEach((w) => console.log(`  - ${w}`));
  process.exit(0);
} else {
  console.log('\n\x1b[32mVerification PASSED\x1b[0m');
  process.exit(0);
}
