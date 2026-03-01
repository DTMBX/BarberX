#!/usr/bin/env node
/**
 * Fix bundle.css syntax errors - Remove orphaned closing braces and properties
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');

console.log('🔧 Fixing bundle.css Syntax Errors\n');

let content = fs.readFileSync(BUNDLE_PATH, 'utf8');
const lines = content.split('\n');

console.log(`Total lines: ${lines.length}`);

// Find orphaned closing braces (lines with only } and whitespace, preceded by another })
const fixedLines = [];
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmed = line.trim();
  
  // Skip orphaned closing braces
  if (trimmed === '}' && i > 0 && lines[i-1].trim() === '}') {
    console.log(`Removing orphaned } at line ${i+1}`);
    continue;
  }
  
  // Skip lines that are just properties without a selector (no leading spaces after a })
  if (trimmed && !trimmed.startsWith('/*') && !trimmed.startsWith('*/') &&  !trimmed.includes('{') && trimmed.includes(':') && i > 0 && lines[i-1].trim() === '}') {
    console.log(`Removing orphaned property at line ${i+1}: ${trimmed}`);
    continue;
  }
  
  fixedLines.push(line);
}

content = fixedLines.join('\n');

// Remove any duplicate empty lines
content = content.replace(/\n{3,}/g, '\n\n');

fs.writeFileSync(BUNDLE_PATH, content);

console.log(`\nFixed lines: ${lines.length} → ${fixedLines.length}`);
console.log('✅ Syntax errors fixed!\n');
