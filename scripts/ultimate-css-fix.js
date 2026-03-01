#!/usr/bin/env node
/**
 * ULTIMATE CSS FIX - Final comprehensive cleanup
 */

const fs = require('fs');
const path = require('path');

const BUNDLE_PATH = path.join(__dirname, '../assets/css/bundle.css');

console.log('🎯 ULTIMATE CSS FIX - Final cleanup\n');

let content = fs.readFileSync(BUNDLE_PATH, 'utf8');

// 1. Fix empty blocks
console.log('1. Filling empty @media/@supports blocks...');
content = content.replace(
  /@media \(prefers-reduced-motion: reduce\) \{\s*\}/g,
  '@media (prefers-reduced-motion: reduce) {\n  * { animation: none !important; transition: none !important; }\n}'
);
content = content.replace(
  /@supports \(padding: env\(safe-area-inset-bottom\)\) \{\s*\}/g,
  '@supports (padding: env(safe-area-inset-bottom)) {\n  body { padding-bottom: env(safe-area-inset-bottom); }\n}'
);

// 2. Add empty lines before section comments
console.log('2. Adding empty lines before section comments...');
content = content.replace(/([^}\n])\n(\/\* ={10,})/g, '$1\n\n$2');

// 3. Fix duplicate properties
console.log('3. Removing duplicate properties...');
const lines = content.split('\n');
const fixed = [];
let inBlock = false;
let blockProps = new Map();

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  const trimmed = line.trim();
  
  if (trimmed.includes('{') && !trimmed.startsWith('/*')) {
    inBlock = true;
    blockProps.clear();
  }
  
  if (inBlock && trimmed.match(/^\w[\w-]*:/)) {
    const prop = trimmed.split(':')[0];
    if (blockProps.has(prop)) {
      console.log(`   Removed duplicate ${prop} at line ${i + 1}`);
      continue;
    }
    blockProps.set(prop, true);
  }
  
  if (trimmed === '}') {
    inBlock = false;
    blockProps.clear();
  }
  
  fixed.push(line);
}

content = fixed.join('\n');

// 4. Fix specific declarations needing empty lines
console.log('4. Adding empty lines before specific declarations...');
content = content.replace(
  /(--container-max:[^;]+;\n)(  width: min)/g,
  '$1\n$2'
);
content = content.replace(
  /(--container-max:[^;]+;\n)(  padding-inline:)/g,
  '$1\n$2'
);
content = content.replace(
  /(\})\n(input, select, textarea \{\n  border:)/g,
  '$1\n\n$2'
);

// 5. Fix rules needing empty lines
console.log('5. Adding empty lines before rules...');
content = content.replace(
  /(\})\n(\.ts-footer::after \{)/g,
  '$1\n\n$2'
);
content = content.replace(
  /@keyframes slide-in-right \{[\s\S]*?from \{/g,
  (match) => match.replace(/from \{/, '\n  from {')
);

// 6. Simplify complex selectors
console.log('6. Simplifying complex selectors...');
content = content.replace(/\.light-theme tbody tr:nth-child/g, '.light-theme tr:nth-child');
content = content.replace(/main\.light-theme tr:hover/g, '.light-theme tr:hover');

// 7. Fix shorthand property overrides
console.log('7. Fixing shorthand property overrides...');
content = content.replace(
  /(background-color:[^;]+;[\s\n]*)(background: linear-gradient)/g,
  '$2'
);
content = content.replace(
  /(border-top-color:[^;]+;[\s\n]*)(border: [^;]+;)/g,
  '$2'
);

// Clean up triple+ newlines
content = content.replace(/\n{4,}/g, '\n\n\n');

fs.writeFileSync(BUNDLE_PATH, content);

console.log('\n✅ Ultimate CSS fix complete!\n');
console.log('📊 Final size: ' + content.length + ' bytes\n');
