#!/usr/bin/env node
// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

"use strict";

const fs = require("fs").promises;
const path = require("path");

const DEFAULT_ROOT = path.resolve(__dirname, "..", "site");
const TARGET_EXTS = new Set([
  ".html",
  ".htm",
  ".md",
  ".js",
  ".jsx",
  ".ts",
  ".tsx",
  ".njk",
  ".jinja",
  ".jinja2",
  ".txt",
]);
const IGNORE_DIRS = new Set([
  ".git",
  ".jekyll-cache",
  "_site",
  "node_modules",
  "dist",
  "build",
  "out",
]);

const CLI_ARGS = process.argv.slice(2);
const FLAGS = new Set(CLI_ARGS.filter((arg) => arg.startsWith("-")));
const ROOT_ARG = CLI_ARGS.find((arg) => !arg.startsWith("-"));
const ROOT = ROOT_ARG ? path.resolve(process.cwd(), ROOT_ARG) : DEFAULT_ROOT;
const DRY_RUN = FLAGS.has("--dry-run");

const BEM_SEPARATORS = /(__|--)/g;
const CLASS_ATTR_RE = /(class(Name)?\s*=\s*['"][^'"]*['"])/g;
const CLASSLIST_CALL_RE =
  /(classList\.(?:add|remove|toggle)\s*\(\s*['"][^'"]*['"]\s*\))/g;
const TEMPLATE_BEM_RE = /(__|--)\$\{/g;
const TOKEN_RE =
  /(^|['"`\s>])([A-Za-z0-9][A-Za-z0-9_-]*(?:__|--)[A-Za-z0-9_-]*)(?=[\s'"`<>\)])/g;

function hasBemTokens(value) {
  return value.includes("__") || value.includes("--");
}

function normalizeBemToken(token) {
  return token.replace(BEM_SEPARATORS, "-");
}

/**
 * Recursively walk directories, skipping known generated/vendor folders.
 * @param {string} dir
 */
async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.has(entry.name)) continue;
      await walk(path.join(dir, entry.name));
      continue;
    }

    if (!entry.isFile()) continue;

    const ext = path.extname(entry.name).toLowerCase();
    if (!TARGET_EXTS.has(ext)) continue;

    await processFile(path.join(dir, entry.name));
  }
}

/**
 * Replace BEM tokens (block__element--modifier) with kebab tokens.
 * @param {string} filePath
 */
async function processFile(filePath) {
  const contents = await fs.readFile(filePath, "utf8");
  if (!hasBemTokens(contents)) return;

  let updated = contents;

  // 1) Replace in class/className attribute values.
  updated = updated.replace(CLASS_ATTR_RE, (match) =>
    match.replace(BEM_SEPARATORS, "-"),
  );

  // 2) Replace in classList.add/remove/toggle calls.
  updated = updated.replace(CLASSLIST_CALL_RE, (match) =>
    match.replace(BEM_SEPARATORS, "-"),
  );

  // 3) Replace template literals: --${} or __${} -> -${}
  updated = updated.replace(TEMPLATE_BEM_RE, "-${");

  // 4) Replace standalone BEM-like tokens near common delimiters.
  updated = updated.replace(TOKEN_RE, (match, prefix, token) =>
    `${prefix}${normalizeBemToken(token)}`,
  );

  if (updated === contents) return;

  if (DRY_RUN) {
    console.log("[dry-run] Would update:", path.relative(process.cwd(), filePath));
    return;
  }

  await fs.writeFile(filePath, updated, "utf8");
  console.log("Updated:", path.relative(process.cwd(), filePath));
}

(async () => {
  try {
    console.log(`Scanning ${ROOT}${DRY_RUN ? " (dry-run)" : ""}`);
    await walk(ROOT);
    console.log("Done. Review changes and run stylelint.");
  } catch (err) {
    console.error("bem-to-kebab failed:", err);
    process.exit(1);
  }
})();
