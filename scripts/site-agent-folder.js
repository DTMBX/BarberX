const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

const siteDir = process.argv[2] ? path.resolve(process.argv[2]) : null;
const outFile = process.argv[3] ? path.resolve(process.argv[3]) : null;

if (!siteDir || !outFile) {
  console.error('Usage: node site-agent-folder.js <site-folder> <out-json>');
  process.exit(2);
}

function listHtmlFiles(dir) {
  const results = [];
  (function walk(d){
    for (const name of fs.readdirSync(d)){
      const p = path.join(d, name);
      const stat = fs.statSync(p);
      if (stat.isDirectory()) walk(p);
      else if (stat.isFile() && p.endsWith('.html')) results.push(p);
    }
  })(dir);
  return results;
}

function resolveHref(baseFile, href) {
  if (!href) return null;
  const clean = href.split('#')[0].split('?')[0];
  if (clean.startsWith('http://') || clean.startsWith('https://') || clean.startsWith('mailto:') || clean.startsWith('tel:')) return { type: 'external', href };
  if (clean.startsWith('/')) {
    const p = path.join(siteDir, clean.replace(/^\//, ''));
    return { type: 'internal', path: p, href };
  }
  const baseDir = path.dirname(baseFile);
  const p = path.join(baseDir, clean);
  return { type: 'internal', path: p, href };
}

function checkExists(p) { try { return fs.existsSync(p); } catch(e){ return false; } }

function scan(){
  const htmlFiles = listHtmlFiles(siteDir);
  const report = { scannedAt: new Date().toISOString(), siteDir, pages: {}, brokenLinks: [], missingAssets: [] };

  for (const file of htmlFiles) {
    const rel = path.relative(siteDir, file).replace(/\\/g, '/');
    const html = fs.readFileSync(file, 'utf8');
    const $ = cheerio.load(html);
    const anchors = [];
    $('a').each((i, el) => anchors.push($(el).attr('href')));
    const imgs = [];
    $('img').each((i, el) => imgs.push($(el).attr('src')));
    const scripts = [];
    $('script').each((i, el) => scripts.push($(el).attr('src')));
    const links = [];
    $('link').each((i, el) => links.push($(el).attr('href')));
    const sources = [];
    $('source').each((i, el) => {
      const el$ = $(el);
      sources.push(el$.attr('src') || el$.attr('data-src-mp4-1080p') || el$.attr('data-src-mp4-720p') || el$.attr('data-src-mp4-360p') || el$.attr('data-src-webm-1080p') || el$.attr('data-src-webm-720p') || el$.attr('data-src-webm-360p'));
    });

    report.pages[rel] = { anchors: anchors.length, images: imgs.length, scripts: scripts.length, links: links.length };

    const allRefs = [].concat(anchors, imgs, scripts, links, sources).filter(Boolean);
    for (const ref of allRefs) {
      const resolved = resolveHref(file, ref);
      if (!resolved) continue;
      if (resolved.type === 'internal') {
        let target = resolved.path;
        if (target.endsWith(path.sep)) target = path.join(target, 'index.html');
        if (!checkExists(target)) {
          if (!checkExists(target + '.html')) {
            report.brokenLinks.push({ page: rel, href: resolved.href, target: path.relative(siteDir, target).replace(/\\/g, '/') });
          }
        }
      }
    }

    for (const src of imgs.concat(scripts, links, sources).filter(Boolean)){
      const r = resolveHref(file, src);
      if (r && r.type === 'internal'){
        let t = r.path;
        if (!checkExists(t) && !checkExists(t + '.html')) {
          report.missingAssets.push({ page: rel, src, target: path.relative(siteDir, t).replace(/\\/g, '/') });
        }
      }
    }
  }

  fs.writeFileSync(outFile, JSON.stringify(report, null, 2));
  console.log('Scan complete — report written to', outFile);
  console.log('Broken links:', report.brokenLinks.length, 'Missing assets:', report.missingAssets.length);
}

scan();
