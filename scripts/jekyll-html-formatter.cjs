// Jekyll-aware HTML formatter
// Skips files with Liquid tags and prettifies others
const fs = require('fs');
const path = require('path');
const prettier = require('prettier');

function hasLiquidTags(content) {
  return /{%-?\s*|{{\s*/.test(content);
}

function formatHTML(dir) {
  fs.readdirSync(dir).forEach(f => {
    const fp = path.join(dir, f);
    if (fs.statSync(fp).isDirectory()) formatHTML(fp);
    else if (fp.endsWith('.html')) {
      const src = fs.readFileSync(fp, 'utf8');
      if (!hasLiquidTags(src)) {
        const formatted = prettier.format(src, { parser: 'html' });
        fs.writeFileSync(fp, formatted);
      }
    }
  });
}

formatHTML(process.cwd());
