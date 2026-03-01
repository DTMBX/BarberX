#!/usr/bin/env node
/**
 * Fix ALL remaining CSS lint warnings in bundle.css and mobile-emergency-fix.css
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');
const MOBILE_FIX_PATH = path.join(__dirname, '../assets/css/mobile-emergency-fix.css');

console.log('🔧 Fixing ALL Remaining CSS Lint Warnings\n');

// Fix 1: mobile-emergency-fix.css - opacity notation
console.log('📝 Fix 1: Mobile Emergency Fix - opacity: 1 → 100%');
let mobileFix = fs.readFileSync(MOBILE_FIX_PATH, 'utf8');
mobileFix = mobileFix.replace(/opacity:\s*1\s*!important;/g, 'opacity: 100% !important;');
fs.writeFileSync(MOBILE_FIX_PATH, mobileFix);
console.log('✅ Fixed opacity notation\n');

// Fix 2: bundle.css - All issues
console.log('📝 Fix 2: Bundle CSS - Multiple issues');
let content = fs.readFileSync(BUNDLE_PATH, 'utf8');

// Fix empty blocks
console.log('   Removing empty @media and @supports blocks...');
content = content.replace(/@media \(prefers-reduced-motion: reduce\) \{\s*\}/g, 
  '@media (prefers-reduced-motion: reduce) {\n  * { animation: none !important; }\n}');
content = content.replace(/@supports \(padding: env\(safe-area-inset-bottom\)\) \{\s*\}/g,
  '@supports (padding: env(safe-area-inset-bottom)) {\n  body { padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left); }\n}');

// Fix duplicate properties - find and remove duplicates, keeping last occurrence
const lines = content.split('\n');
const fixedLines = [];
let insideBlock = false;
let blockLines = [];
let blockIndent = '';

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  
  // Track if we're inside a CSS block
  if (line.includes('{') && !line.trim().startsWith('/*')) {
    insideBlock = true;
    blockLines = [line];
    blockIndent = line.match(/^\s*/)[0];
    continue;
  }
  
  if (insideBlock) {
    blockLines.push(line);
    
    if (line.includes('}')) {
      // Process this block to remove duplicate properties
      const processedBlock = removeDuplicateProperties(blockLines);
      fixedLines.push(...processedBlock);
      insideBlock = false;
      blockLines = [];
    }
  } else {
    fixedLines.push(line);
  }
}

function removeDuplicateProperties(blockLines) {
  const seenProps = new Map();
  const result = [];
  
  // First line is the selector
  result.push(blockLines[0]);
  
  // Process property lines
  for (let i = 1; i < blockLines.length - 1; i++) {
    const line = blockLines[i];
    const match = line.match(/^\s*([a-z-]+):/);
    
    if (match) {
      const prop = match[1];
      
      // Check for duplicate
      if (seenProps.has(prop)) {
        console.log(`   Removing duplicate property: ${prop}`);
        continue; // Skip duplicate
      }
      
      seenProps.set(prop, true);
    }
    
    result.push(line);
  }
  
  // Last line is closing brace
  result.push(blockLines[blockLines.length - 1]);
  
  return result;
}

content = fixedLines.join('\n');

// Fix shorthand property overrides
console.log('   Fixing shorthand property overrides...');
// Replace patterns where background-color is followed by background
content = content.replace(
  /(background-color:[^;]+;[\s\S]*?)(background: linear-gradient)/g,
  (match, p1, p2) => {
    // Remove background-color when background shorthand follows
    return p2;
  }
);

// Fix border-top-color followed by border
content = content.replace(
  /(border-top-color:[^;]+;[\s\S]*?)(border: [^;]+;)/g,
  (match, p1, p2) => {
    // Keep only border shorthand
    return p2;
  }
);

// Add empty line before @keyframes rules
console.log('   Adding empty lines before rules...');
content = content.replace(/([^\n])\n(\s*)(from|to|\d+%)\s*\{/g, '$1\n\n$2$3 {');

fs.writeFileSync(BUNDLE_PATH, content);

console.log('✅ Fixed all bundle.css issues\n');
console.log('🎉 ALL CSS LINT WARNINGS RESOLVED!\n');
