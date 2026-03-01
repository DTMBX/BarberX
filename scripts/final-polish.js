#!/usr/bin/env node
/**
 * FINAL POLISH - Fix last remaining CSS lint warnings
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');

console.log('✨ Final Polish - Fixing last CSS warnings\n');

let content = fs.readFileSync(BUNDLE_PATH, 'utf8');

// Fix: Add empty lines before specific declarations that need them
console.log('Adding empty lines before declarations...');
content = content.replace(
  /(max-width:[^\n]+;\n)(  width: min)/g,
  '$1\n$2'
);
content = content.replace(
  /(text-align: center;\n)(  padding-inline:)/g,
  '$1\n$2'
);
content = content.replace(
  /(\}\n)(\s+border-radius: var\(--tiller-input-border-radius\);)/g,
  '$1\n$2'
);

// Fix: Add empty lines before nested rules inside @media
console.log('Adding empty lines before rules in @media blocks...');
const lines = content.split('\n');
const fixedLines = [];
let inMediaBlock = false;
let lastLineWasRule = false;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmed = line.trim();
  
  // Track if we're in a @media block
  if (trimmed.startsWith('@media')) {
    inMediaBlock = true;
  }
  
  // Check if this line starts a new rule (selector)
  const isRule = !trimmed.startsWith('/*') && 
                 !trimmed.startsWith('*/') &&
                 !trimmed.startsWith('@') &&
                 (trimmed.match(/^[.#a-z*:][\w-]*.*\{/) || 
                  (trimmed.match(/^[.#a-z*:]/) && !trimmed.includes(':')));
  
  // Check if previous line was closing brace
  const prevLine = i > 0 ? lines[i - 1].trim() : '';
  const prevWasCloseBrace = prevLine === '}';
  
  // Add empty line before rule if needed
  if (inMediaBlock && isRule && prevWasCloseBrace && !lines[i - 1].match(/^\s*$/)) {
    fixedLines.push('');
  }
  
  fixedLines.push(line);
  
  // Exit media block
  if (inMediaBlock && trimmed === '}' && line.match(/^}/)) {
    inMediaBlock = false;
  }
}

content = fixedLines.join('\n');

// Fix: Simplify selector to reduce type count
console.log('Simplifying complex selectors...');
content = content.replace(
  /main\.light-theme tr:nth-child\(even\) td \{/g,
  '.light-theme tbody tr:nth-child(even) td {'
);

// Remove triple+ newlines again
content = content.replace(/\n{4,}/g, '\n\n\n');

fs.writeFileSync(BUNDLE_PATH, content);

console.log('\n✅ Final polish complete!\n');
console.log('🎉 All CSS lint warnings should now be resolved!\n');
