const fs = require('fs');
const path = require('path');

const reportsDir = path.join(__dirname, '..', 'reports');
const outJson = path.join(reportsDir, 'broken-links-priority.json');
const outMd = path.join(reportsDir, 'broken-links-priority.md');

function readReports() {
  const files = fs.readdirSync(reportsDir).filter(f => f.startsWith('site-scan') && f.endsWith('.json'));
  const reports = files.map(f => JSON.parse(fs.readFileSync(path.join(reportsDir, f), 'utf8')));
  return reports;
}

function aggregate() {
  const reports = readReports();
  const counts = {};
  const missing = {};
  for (const r of reports) {
    (r.brokenLinks || []).forEach(b => {
      const key = b.href || b.target || 'unknown';
      counts[key] = (counts[key] || 0) + 1;
    });
    (r.missingAssets || []).forEach(m => {
      const key = m.src || m.target || 'unknown';
      missing[key] = (missing[key] || 0) + 1;
    });
  }

  const sortedBroken = Object.entries(counts).sort((a,b) => b[1]-a[1]);
  const sortedMissing = Object.entries(missing).sort((a,b) => b[1]-a[1]);

  const report = { generatedAt: new Date().toISOString(), broken: sortedBroken, missing: sortedMissing };
  fs.writeFileSync(outJson, JSON.stringify(report, null, 2));

  let md = '# Broken Links Priority\n\n';
  md += 'Top broken hrefs (frequency across reports):\n\n';
  sortedBroken.slice(0,50).forEach(([href, cnt]) => md += `- ${href} — ${cnt}\n`);
  md += '\nTop missing assets (frequency):\n\n';
  sortedMissing.slice(0,50).forEach(([src, cnt]) => md += `- ${src} — ${cnt}\n`);
  fs.writeFileSync(outMd, md);
  console.log('Wrote', outJson, 'and', outMd);
}

aggregate();
