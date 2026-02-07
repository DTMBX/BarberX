const fs = require('fs');
const path = require('path');

const lhciDir = path.join(process.cwd(), 'lhci');
const outFile = path.join(lhciDir, 'lhci-summary.json');
const compactOut = path.join(lhciDir, 'lhci-compact.json');
const lhciConfigPath = path.join(process.cwd(), '.lighthouserc.json');

function readLhciConfig() {
  if (!fs.existsSync(lhciConfigPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(lhciConfigPath, 'utf8'));
  } catch (e) {
    return null;
  }
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return null;
  }
}

if (!fs.existsSync(lhciDir)) {
  console.error('No lhci directory found');
  process.exit(1);
}

const files = fs.readdirSync(lhciDir).filter(f => f.endsWith('.json'));
if (!files.length) {
  console.error('No JSON files in lhci directory');
  process.exit(1);
}

const categories = ['performance','accessibility','best-practices','seo'];
const accum = {count:0};
for (const c of categories) accum[c]=0;
const details = [];

const lhciConfig = readLhciConfig();
const assertions = (lhciConfig && lhciConfig.ci && lhciConfig.ci.assert && lhciConfig.ci.assert.assertions) || {};
function getAssertionFor(category) {
  const key = `categories:${category}`;
  const v = assertions[key];
  if (!v) return null;
  // v can be [level, {minScore: x}]
  if (Array.isArray(v)) return { level: v[0], minScore: v[1] && v[1].minScore };
  return null;
}

for (const f of files) {
  const p = path.join(lhciDir, f);
  const j = readJson(p);
  if (!j) continue;
  // find LHR object
  let lhr = j.lhr || j;
  if (lhr && lhr.categories) {
    accum.count++;
    const entry = {file: f, scores: {}};
    for (const c of categories) {
      const score = lhr.categories[c] && lhr.categories[c].score != null ? lhr.categories[c].score : null;
      if (score != null) {
        accum[c] += score;
        entry.scores[c] = score;
      }
    }
    details.push(entry);
  }
}

if (accum.count === 0) {
  console.error('No LHR category data found in lhci JSON files');
  process.exit(1);
}

const summary = {count: accum.count, averages: {}, details};
for (const c of categories) {
  summary.averages[c] = Math.round((accum[c] / accum.count) * 100) / 100;
}

// Apply assertions to determine pass/warn/fail per category
const compact = {averages: {}, status: {}};
for (const c of categories) {
  const avg = summary.averages[c];
  compact.averages[c] = avg;
  const assertion = getAssertionFor(c);
  if (!assertion || assertion.minScore == null) {
    compact.status[c] = 'unknown';
    continue;
  }
  const min = assertion.minScore;
  if (avg >= min) compact.status[c] = 'pass';
  else compact.status[c] = assertion.level === 'error' ? 'fail' : 'warn';
}

fs.writeFileSync(outFile, JSON.stringify(summary, null, 2), 'utf8');
fs.writeFileSync(compactOut, JSON.stringify(compact, null, 2), 'utf8');
console.log('LHCI summary written to', outFile);
console.log('LHCI compact summary written to', compactOut);