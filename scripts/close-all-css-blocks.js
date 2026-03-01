#!/usr/bin/env node
/**
 * Find and close all unclosed CSS blocks
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');

console.log('🔧 Finding and closing unclosed CSS blocks\n');

let content = fs.readFileSync(BUNDLE_PATH, 'utf8');
const lines = content.split('\n');

let braceCount = 0;
const unclosedBlocks = [];

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const openBraces = (line.match(/{/g) || []).length;
  const closeBraces = (line.match(/}/g) || []).length;
  
  braceCount += openBraces - closeBraces;
  
  // Track where blocks open
  if (openBraces > 0 && line.trim().startsWith('@')) {
    unclosedBlocks.push({ line: i + 1, content: line.trim(), braceCount });
  }
}

console.log(`Final brace count: ${braceCount}`);
console.log(`${braceCount > 0 ? 'Missing closing braces!' : 'All blocks closed!'}\n`);

if (braceCount > 0) {
  console.log(`Adding ${braceCount} closing brace(s) at end of file...`);
  const closingBraces = '\n' + '}'.repeat(braceCount) + '\n';
  fs.writeFileSync(BUNDLE_PATH, content + closingBraces);
  console.log('✅ Fixed!\n');
}

// Now balance braces properly
content = fs.readFileSync(BUNDLE_PATH, 'utf8');
const fixedLines = content.split('\n');

// Find sections that should close before new sections start
const newLines = [];
braceCount = 0;
let lastSectionLine = -1;

for (let i = 0; i < fixedLines.length; i++) {
  const line = fixedLines[i];
  const trimmed = line.trim();
  
  // Check if this is a new section header
  if (trimmed.startsWith('/*') && trimmed.includes('===')) {
    // If we have unclosed braces, close them before this section
    if (braceCount > 0) {
      console.log(`Closing ${braceCount} braces before line ${i + 1}: ${trimmed.substring(0, 50)}...`);
      for (let j = 0; j < braceCount; j++) {
        newLines.push('}');
      }
      braceCount = 0;
    }
  }
  
  newLines.push(line);
  
  const openBraces = (line.match(/{/g) || []).length;
  const closeBraces = (line.match(/}/g) || []).length;
  braceCount += openBraces - closeBraces;
}

// Close any remaining braces
if (braceCount > 0) {
  console.log(`Closing ${braceCount} remaining braces at end of file`);
  for (let i = 0; i < braceCount; i++) {
    newLines.push('}');
  }
}

fs.writeFileSync(BUNDLE_PATH, newLines.join('\n'));

console.log('✅ All CSS blocks properly closed!\n');
