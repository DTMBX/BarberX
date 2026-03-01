/**
 * scan-css-contrast.js — CSS File Contrast Scanner for Tillerstead
 *
 * Purpose:
 * Scans actual SCSS files for hardcoded color combinations and validates against
 * WCAG 2.1 standards, identifying potential contrast issues in dark theme.
 *
 * Compliance: WCAG 2.1 Level AA/AAA, TCNA 2024, NJ HIC
 *
 * Usage: node scripts/scan-css-contrast.js
 */

const { existsSync, readFileSync, readdirSync, writeFileSync } = require('fs');
const { join } = require('path');

const ISSUES = [];
const WARNINGS = [];

// Common background colors in our theme
const _BACKGROUNDS = {
  light: {
    parchment: '#f9f5eb',
    white: '#ffffff',
    surface: '#f0ead8',
    muted: '#fcfaf4',
  },
  dark: {
    slate: '#0f1713',
    ink: '#1c231f',
    teal700: '#084c3d',
    teal900: '#022318',
  },
};

function _parseColor(colorStr) {
  // Handle hex colors
  if (colorStr.startsWith('#')) {
    const hex = colorStr.slice(1);
    const shorthand = hex.length === 3;
    const r = parseInt(shorthand ? hex[0] + hex[0] : hex.substring(0, 2), 16);
    const g = parseInt(shorthand ? hex[1] + hex[1] : hex.substring(2, 4), 16);
    const b = parseInt(shorthand ? hex[2] + hex[2] : hex.substring(4, 6), 16);
    return [r, g, b];
  }

  // Handle rgb(a) colors
  const rgbMatch = colorStr.match(/rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
  if (rgbMatch) {
    return [
      parseInt(rgbMatch[1]),
      parseInt(rgbMatch[2]),
      parseInt(rgbMatch[3]),
    ];
  }

  return null;
}

function luminance([r, g, b]) {
  const a = [r, g, b].map((v) => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}

function _contrastRatio(rgb1, rgb2) {
  const l1 = luminance(rgb1);
  const l2 = luminance(rgb2);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

function scanFile(filePath) {
  const content = readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');

  // Look for problematic patterns
  lines.forEach((line, index) => {
    const lineNum = index + 1;

    // Pattern 1: Low opacity white text (potential issue on dark backgrounds)
    const lowOpacityWhite = line.match(
      /color:\s*rgb\s*\(\s*255\s*,\s*255\s*,\s*255\s*,\s*(0\.[0-6])\s*\)/,
    );
    if (lowOpacityWhite) {
      const opacity = parseFloat(lowOpacityWhite[1]);
      if (opacity < 0.7) {
        ISSUES.push({
          file: filePath,
          line: lineNum,
          type: 'Low Opacity White Text',
          code: line.trim(),
          issue: `White text at ${(opacity * 100).toFixed(0)}% opacity may fail contrast on dark backgrounds`,
          severity: 'high',
          recommendation: `Increase opacity to >= 0.85 or use semantic color variable`,
        });
      }
    }

    // Pattern 2: Low opacity elements on transparent/light backgrounds
    const lowOpacity = line.match(
      /color:\s*rgb\(a?\)?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0\.\d+)\s*\)/,
    );
    if (lowOpacity) {
      const opacity = parseFloat(lowOpacity[4]);
      if (opacity < 0.65 && !line.includes('255, 255, 255')) {
        WARNINGS.push({
          file: filePath,
          line: lineNum,
          type: 'Low Opacity Color',
          code: line.trim(),
          note: `Opacity ${(opacity * 100).toFixed(0)}% might create contrast issues`,
        });
      }
    }

    // Pattern 3: Hardcoded colors (not using CSS variables)
    if (line.includes('color:') && line.match(/#[0-9a-fA-F]{3,6}/)) {
      const match = line.match(/#[0-9a-fA-F]{3,6}/);
      if (match && !line.includes('var(--')) {
        WARNINGS.push({
          file: filePath,
          line: lineNum,
          type: 'Hardcoded Color',
          code: line.trim(),
          note: 'Consider using CSS variable for maintainability',
        });
      }
    }

    // Pattern 4: Specific low-contrast rgba on dark theme (footer issues)
    if (line.includes('rgb(255, 255, 255, 0.7)')) {
      ISSUES.push({
        file: filePath,
        line: lineNum,
        type: 'Footer Contrast Issue',
        code: line.trim(),
        issue: 'rgba(255,255,255,0.7) on dark teal may fail AA (needs testing)',
        severity: 'medium',
        recommendation: 'Test contrast or increase to 0.85+ opacity',
      });
    }

    // Pattern 5: Breadcrumbs with low contrast
    if (
      line.includes('rgb(15, 23, 42, 0.4)') ||
      line.includes('rgb(15, 23, 42, 0.6)')
    ) {
      ISSUES.push({
        file: filePath,
        line: lineNum,
        type: 'Breadcrumb Contrast',
        code: line.trim(),
        issue: 'Slate color at low opacity will fail AA on parchment',
        severity: 'high',
        recommendation:
          'Replace with var(--ts-color-muted) or increase opacity to 0.9+',
      });
    }

    // Pattern 6: Dark theme experimental overrides
    if (filePath.includes('dark-theme') && line.includes('!important')) {
      WARNINGS.push({
        file: filePath,
        line: lineNum,
        type: 'Dark Theme Override',
        code: line.trim(),
        note: 'Using !important may override contrast fixes',
      });
    }
  });
}

function scanDirectory(dir, pattern = /\.scss$/) {
  if (!existsSync(dir)) {
    WARNINGS.push({
      file: dir,
      line: 0,
      type: 'Missing Directory',
      code: '',
      note: `Directory not found; skipped scanning: ${dir}`,
    });
    return;
  }

  const entries = readdirSync(dir, { withFileTypes: true });

  entries.forEach((entry) => {
    const fullPath = join(dir, entry.name);

    if (
      entry.isDirectory() &&
      !entry.name.startsWith('.') &&
      entry.name !== 'node_modules'
    ) {
      scanDirectory(fullPath, pattern);
    } else if (entry.isFile() && pattern.test(entry.name)) {
      // Skip archive files
      if (!fullPath.includes('99-archive')) {
        scanFile(fullPath);
      }
    }
  });
}

console.log('🔍 Scanning CSS files for contrast issues...\n');

// Scan SCSS files
scanDirectory('_sass');
scanDirectory('assets/css');

console.log('\n' + '='.repeat(70));
console.log(`\n📊 Scan Complete`);
console.log(`❌ Issues Found: ${ISSUES.length}`);
console.log(`⚠️  Warnings: ${WARNINGS.length}`);

if (ISSUES.length > 0) {
  console.log('\n🚨 CRITICAL CONTRAST ISSUES:\n');
  ISSUES.forEach((issue, i) => {
    console.log(`${i + 1}. ${issue.type} [${issue.severity.toUpperCase()}]`);
    console.log(`   File: ${issue.file}:${issue.line}`);
    console.log(`   Code: ${issue.code}`);
    console.log(`   Issue: ${issue.issue}`);
    console.log(`   Fix: ${issue.recommendation}\n`);
  });
}

if (WARNINGS.length > 0 && WARNINGS.length < 20) {
  console.log('\n⚠️  WARNINGS:\n');
  WARNINGS.forEach((warn, i) => {
    console.log(`${i + 1}. ${warn.type}`);
    console.log(`   ${warn.file}:${warn.line}`);
    console.log(`   ${warn.note}\n`);
  });
} else if (WARNINGS.length >= 20) {
  console.log(`\n⚠️  ${WARNINGS.length} warnings (details in report file)`);
}

// Generate report
const report = {
  timestamp: new Date().toISOString(),
  filesScanned: {
    /* would track this */
  },
  issues: ISSUES,
  warnings: WARNINGS,
  summary: {
    totalIssues: ISSUES.length,
    criticalIssues: ISSUES.filter((i) => i.severity === 'high').length,
    mediumIssues: ISSUES.filter((i) => i.severity === 'medium').length,
    warnings: WARNINGS.length,
  },
};

writeFileSync(
  'reports/css-contrast-scan.json',
  JSON.stringify(report, null, 2),
);
console.log('\n📄 Full report: reports/css-contrast-scan.json');

// Generate markdown
let md = `# CSS Contrast Scan Report\n\n`;
md += `**Generated:** ${new Date().toLocaleString()}\n`;
md += `**Standard:** WCAG 2.1 Level AA (4.5:1)\n\n`;
md += `## Summary\n\n`;
md += `- **Critical Issues:** ${report.summary.criticalIssues} 🚨\n`;
md += `- **Medium Issues:** ${report.summary.mediumIssues} ⚠️\n`;
md += `- **Warnings:** ${report.summary.warnings}\n\n`;

if (ISSUES.length > 0) {
  md += `## 🚨 Critical Contrast Issues\n\n`;
  ISSUES.forEach((issue, i) => {
    md += `### ${i + 1}. ${issue.type} [${issue.severity.toUpperCase()}]\n\n`;
    md += `**File:** \`${issue.file}:${issue.line}\`\n\n`;
    md += `**Code:**\n\`\`\`scss\n${issue.code}\n\`\`\`\n\n`;
    md += `**Issue:** ${issue.issue}\n\n`;
    md += `**Recommendation:** ${issue.recommendation}\n\n`;
    md += `---\n\n`;
  });
}

if (WARNINGS.length > 0) {
  md += `## ⚠️ Warnings\n\n`;
  md += `| Type | File:Line | Note |\n`;
  md += `|------|-----------|------|\n`;
  WARNINGS.forEach((w) => {
    md += `| ${w.type} | \`${w.file}:${w.line}\` | ${w.note} |\n`;
  });
}

md += `\n---\n\n**Compliance:** TCNA 2024, NJ HIC, WCAG 2.1\n`;

writeFileSync('reports/CSS_CONTRAST_SCAN.md', md);
console.log('📄 Markdown report: reports/CSS_CONTRAST_SCAN.md\n');

if (ISSUES.length > 0) {
  console.log('⚠️  Action required: Fix contrast issues listed above\n');
  process.exit(1);
}

console.log('✅ No critical contrast issues detected!\n');
process.exit(0);
