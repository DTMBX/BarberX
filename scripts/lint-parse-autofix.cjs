// lint-parse-autofix.js
// Repo-wide linting, parsing, and auto-fix tool using modern web dev standards

const { ESLint } = require('eslint');
const stylelint = require('stylelint');
const prettier = require('prettier');
const fs = require('fs');
const path = require('path');
const _htmlhint = require('htmlhint').HTMLHint;
const jsYaml = require('js-yaml');

async function fixJS() {
  const eslint = new ESLint({ fix: true });
  await eslint.lintFiles(['**/*.js', '**/*.ts']);
  await ESLint.outputFixes(await eslint.lintFiles(['**/*.js', '**/*.ts']));
}

async function fixCSS() {
  await stylelint.lint({ files: ['**/*.{css,scss}'], fix: true });
}

async function _fixHTML() {
  // HTMLHint does not auto-fix, but we can prettify HTML
  async function walk(dir) {
    for (const f of fs.readdirSync(dir)) {
      const fp = path.join(dir, f);
      if (fs.statSync(fp).isDirectory()) await walk(fp);
      else if (fp.endsWith('.html')) {
        const src = fs.readFileSync(fp, 'utf8');
        const formatted = await prettier.format(src, { parser: 'html' });
        fs.writeFileSync(fp, formatted);
      }
    }
  }
  await walk(process.cwd());
}

function fixYAMLFrontMatter(file) {
  const content = fs.readFileSync(file, 'utf8');
  const match = content.match(/^---[\s\S]*?---/);
  if (!match) return;
  try {
    const yaml = jsYaml.load(match[0].replace(/---/g, ''));
    const fixedYaml = '---\n' + jsYaml.dump(yaml) + '---\n';
    const rest = content.replace(/^---[\s\S]*?---/, '');
    fs.writeFileSync(file, fixedYaml + rest);
  } catch (e) {
    // If YAML is invalid, comment it out
    fs.writeFileSync(file, '<!-- Invalid YAML front matter: ' + e.message + ' -->\n' + content);
  }
}

function fixAllYAML() {
  function walk(dir) {
    fs.readdirSync(dir).forEach(f => {
      const fp = path.join(dir, f);
      if (fs.statSync(fp).isDirectory()) walk(fp);
      else if (fp.endsWith('.html')) fixYAMLFrontMatter(fp);
    });
  }
  walk(process.cwd());
}

async function main() {
  console.log('Auto-fixing JS...');
  await fixJS();
  console.log('Auto-fixing CSS/SCSS...');
  await fixCSS();
  console.log('Auto-fixing YAML front matter in HTML files...');
  fixAllYAML();
  console.log('Repo-wide lint, parse, and auto-fix complete.');
}

main().catch(e => { console.error(e); process.exit(1); });
