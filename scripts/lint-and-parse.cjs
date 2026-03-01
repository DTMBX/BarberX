// lint-and-parse.js
// Repo-wide linting and parsing tool

const { ESLint } = require('eslint');
const stylelint = require('stylelint');
const fs = require('fs');
const path = require('path');
const { HTMLHint } = require('htmlhint');

async function lintJS() {
  const eslint = new ESLint({ fix: false });
  const results = await eslint.lintFiles(['**/*.js', '**/*.ts']);
  return ESLint.getErrorResults(results);
}

async function lintCSS() {
  return await stylelint.lint({ files: ['**/*.{css,scss}'] });
}

function lintHTML() {
  const htmlFiles = [];
  function walk(dir) {
    fs.readdirSync(dir).forEach(f => {
      const fp = path.join(dir, f);
      if (fs.statSync(fp).isDirectory()) walk(fp);
      else if (fp.endsWith('.html')) htmlFiles.push(fp);
    });
  }
  walk(process.cwd());
  return htmlFiles.map(file => ({
    file,
    result: HTMLHint.verify(fs.readFileSync(file, 'utf8'))
  }));
}

function parseYAMLFrontMatter(file) {
  const content = fs.readFileSync(file, 'utf8');
  const match = content.match(/^---[\s\S]*?---/);
  if (!match) return null;
  try {
    return require('js-yaml').load(match[0].replace(/---/g, ''));
  } catch (e) {
    return { error: e.message };
  }
}

async function main() {
  console.log('Linting JS...');
  const jsResults = await lintJS();
  console.log('Linting CSS/SCSS...');
  const cssResults = await lintCSS();
  console.log('Linting HTML...');
  const htmlResults = lintHTML();
  console.log('Parsing YAML front matter...');
  const htmlFiles = htmlResults.map(r => r.file);
  const yamlResults = htmlFiles.map(f => ({ file: f, yaml: parseYAMLFrontMatter(f) }));

  // Output summary
  console.log('JS Lint:', jsResults);
  console.log('CSS Lint:', cssResults.results);
  console.log('HTML Lint:', htmlResults);
  console.log('YAML Parse:', yamlResults);
}

main().catch(e => { console.error(e); process.exit(1); });
