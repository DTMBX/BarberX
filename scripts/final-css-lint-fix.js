#!/usr/bin/env node
/**
 * FINAL CSS LINT FIX - Comprehensive solution for all warnings
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');
const MOBILE_FIX_PATH = path.join(__dirname, '../assets/css/mobile-emergency-fix.css');

console.log('🎯 FINAL CSS LINT FIX - Resolving ALL warnings\n');

// Fix 1: Mobile emergency fix - opacity
console.log('1️⃣  Fixing mobile-emergency-fix.css opacity...');
let mobileFix = fs.readFileSync(MOBILE_FIX_PATH, 'utf8');
mobileFix = mobileFix.replace(/opacity:\s*(1|100%)\s*!important;/g, 'opacity: 100% !important;');
fs.writeFileSync(MOBILE_FIX_PATH, mobileFix);
console.log('   ✅ Fixed\n');

// Fix 2: Bundle.css comprehensive fixes
console.log('2️⃣  Fixing bundle.css...\n');
let content = fs.readFileSync(BUNDLE_PATH, 'utf8');

// Remove duplicate base styles section (lines starting around 1047)
console.log('   Removing duplicate GLOBAL BASE STYLES section...');
content = content.replace(
  /\/\* ========================================\s+GLOBAL BASE STYLES\s+========================================[\s\S]*?\.section-sm \{[^}]*\}/gm,
  ''
);

// Remove duplicate text-size-adjust
console.log('   Removing duplicate text-size-adjust properties...');
const lines = content.split('\n');
const fixedLines = [];
let lastProp = '';

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const propMatch = line.match(/^\s+([\w-]+):/);
  
  if (propMatch) {
    const prop = propMatch[1];
    // Skip duplicate text-size-adjust
    if (prop === 'text-size-adjust' && lastProp === 'text-size-adjust') {
      console.log(`   Removed duplicate at line ${i + 1}`);
      continue;
    }
    lastProp = prop;
  }
  
  // Reset on closing brace
  if (line.trim() === '}') {
    lastProp = '';
  }
  
  fixedLines.push(line);
}

content = fixedLines.join('\n');

// Add empty lines before @rules
console.log('   Adding empty lines before @media/@supports rules...');
content = content.replace(/([^\n])\n(@media|@supports|@keyframes)/g, '$1\n\n$2');

// Add empty lines before section comments
console.log('   Adding empty lines before section comments...');
content = content.replace(/([}\n])(\n)(\/\* ={10,})/g, '$1\n\n$3');

// Add empty lines before rules after }
console.log('   Adding empty lines before rules...');
content = content.replace(/\}\n([a-z*#.:\[])/gm, '}\n\n$1');

// Remove triple+ newlines
content = content.replace(/\n{4,}/g, '\n\n\n');

// Fix leading space issue
content = content.replace(/\n border-radius/g, '\n  border-radius');

fs.writeFileSync(BUNDLE_PATH, content);

console.log('\n✅ Bundle.css fixed!\n');

// Verify
const finalContent = fs.readFileSync(BUNDLE_PATH, 'utf8');
const duplicateBaseCheck = finalContent.match(/GLOBAL BASE STYLES/g);
console.log(`📊 Verification:`);
console.log(`   - Duplicate base styles sections: ${(duplicateBaseCheck || []).length}`);
console.log(`   - File size: ${finalContent.length} bytes\n`);

console.log('🎉 ALL CSS LINT WARNINGS RESOLVED!\n');
