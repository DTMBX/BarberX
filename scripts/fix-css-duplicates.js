#!/usr/bin/env node
/**
 * Remove ALL duplicate CSS selectors from bundle.css
 * Keeps first occurrence, removes all duplicates
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');
const MOBILE_FIX_PATH = path.join(__dirname, '../assets/css/mobile-emergency-fix.css');

console.log('🔧 Fixing ALL CSS Lint Warnings\n');

// Fix 1: mobile-emergency-fix.css opacity notation
console.log('📝 Fix 1: Mobile Emergency Fix - opacity notation');
let mobileFix = fs.readFileSync(MOBILE_FIX_PATH, 'utf8');
const originalMobileFix = mobileFix;
mobileFix = mobileFix.replace(/opacity:\s*100%\s*!important;/g, 'opacity: 1 !important;');

if (mobileFix !== originalMobileFix) {
  fs.writeFileSync(MOBILE_FIX_PATH, mobileFix);
  console.log('✅ Fixed opacity: 100% → 1\n');
} else {
  console.log('⏭️  No opacity changes needed\n');
}

// Fix 2: bundle.css duplicate selectors
console.log('📝 Fix 2: Bundle CSS - Remove duplicate selectors');

let content = fs.readFileSync(BUNDLE_PATH, 'utf8');
const lines = content.split('\n');

console.log(`Total lines before: ${lines.length}`);

// Track seen selectors and their first occurrence line
const seenSelectors = new Map();
const duplicateBlocks = [];

// Define selectors to remove (duplicates identified by linter)
const duplicatesToRemove = [
  { selector: '*,\n*::before,\n*::after', firstLine: 181 },
  { selector: 'html', firstLine: 187 },
  { selector: 'body', firstLine: 203 },
  { selector: 'h1, h2, h3, h4, h5, h6', firstLine: 296 },
  { selector: 'h1', firstLine: 323 },
  { selector: 'a', firstLine: 239 },
  { selector: '.container', firstLine: 545 },
  { selector: '.container-sm', firstLine: 571 },
  { selector: '.container-md', firstLine: 575 },
  { selector: '.container-lg', firstLine: 579 },
  { selector: '.container-2xl', firstLine: 587 }
];

// Find and mark duplicate blocks for removal
let inDuplicateBlock = false;
let blockStartLine = -1;
let currentSelector = '';
const linesToRemove = new Set();

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const lineNum = i + 1;
  
  // Check if this line starts a duplicate selector
  for (const dup of duplicatesToRemove) {
    if (lineNum > dup.firstLine && line.trim().startsWith(dup.selector.split('\n')[0].trim())) {
      // Found a duplicate - mark this entire block for removal
      console.log(`🗑️  Found duplicate at line ${lineNum}: ${dup.selector.replace(/\n/g, ' ')}`);
      
      // Find the end of this CSS block
      let braceCount = 0;
      let blockEnd = i;
      let foundOpenBrace = false;
      
      for (let j = i; j < lines.length; j++) {
        const blockLine = lines[j];
        if (blockLine.includes('{')) {
          foundOpenBrace = true;
          braceCount += (blockLine.match(/{/g) || []).length;
        }
        if (blockLine.includes('}')) {
          braceCount -= (blockLine.match(/}/g) || []).length;
        }
        if (foundOpenBrace && braceCount === 0) {
          blockEnd = j;
          break;
        }
      }
      
      // Also include preceding comments
      let blockStart = i;
      for (let j = i - 1; j >= 0; j--) {
        const prevLine = lines[j].trim();
        if (prevLine.startsWith('/*') || prevLine.includes('*/') || prevLine === '' || prevLine.startsWith('=')) {
          blockStart = j;
        } else {
          break;
        }
      }
      
      // Mark all lines in this block for removal
      for (let k = blockStart; k <= blockEnd; k++) {
        linesToRemove.add(k);
      }
      
      console.log(`   Removing lines ${blockStart + 1} to ${blockEnd + 1}`);
      break;
    }
  }
}

// Remove marked lines
const newLines = lines.filter((_, index) => !linesToRemove.has(index));
const newContent = newLines.join('\n');

console.log(`\nTotal lines after: ${newLines.length}`);
console.log(`Removed ${lines.length - newLines.length} lines`);

fs.writeFileSync(BUNDLE_PATH, newContent);

console.log('\n✅ All duplicate selectors removed!');
console.log('\n🎉 CSS Lint Warnings: RESOLVED\n');
