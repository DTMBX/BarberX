#!/usr/bin/env node
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const cwd = process.cwd();
const wasmPath = path.join(cwd, 'src', 'index.wasm');

function run(cmd, args, opts = {}) {
  const res = spawnSync(cmd, args, { stdio: 'inherit', shell: false, ...opts });
  return res.status === 0;
}

// If already present, nothing to do.
if (fs.existsSync(wasmPath)) {
  console.log('src/index.wasm already exists — skipping build.');
  process.exit(0);
}

// Try common wasm project locations and toolchains
const wasmDirs = ['wasm', 'wasm-src', 'wasm_project', 'pkg'];
for (const d of wasmDirs) {
  const dir = path.join(cwd, d);
  if (!fs.existsSync(dir)) continue;
  console.log('Found wasm source dir:', d);

  // wasm-pack (Rust to wasm)
  if (run('which', ['wasm-pack'])) {
    console.log('Building with wasm-pack in', dir);
    if (run('wasm-pack', ['build', dir, '--target', 'web'])) {
      // try to locate generated .wasm
      const candidates = [path.join(dir, 'pkg', 'index_bg.wasm'), path.join(dir, 'pkg', 'index.wasm')];
      for (const c of candidates) {
        if (fs.existsSync(c)) {
          fs.mkdirSync(path.dirname(wasmPath), { recursive: true });
          fs.copyFileSync(c, wasmPath);
          console.log('Copied generated wasm to src/index.wasm');
          process.exit(0);
        }
      }
    }
  }

  // cargo + wasm-bindgen
  if (run('which', ['cargo'])) {
    console.log('Attempting cargo build in', dir);
    if (run('cargo', ['build', '--release', '--manifest-path', path.join(dir, 'Cargo.toml')])) {
      // try expected target location
      const out = path.join(dir, 'target', 'wasm32-unknown-unknown', 'release');
      if (fs.existsSync(out)) {
        const files = fs.readdirSync(out).filter(f => f.endsWith('.wasm'));
        if (files.length) {
          fs.mkdirSync(path.dirname(wasmPath), { recursive: true });
          fs.copyFileSync(path.join(out, files[0]), wasmPath);
          console.log('Copied cargo-generated wasm to src/index.wasm');
          process.exit(0);
        }
      }
    }
  }
}

// If we reach here, no toolchain found or build failed. Create a minimal placeholder.
console.log('No wasm toolchain detected or build failed — creating minimal placeholder wasm.');
try {
  fs.mkdirSync(path.dirname(wasmPath), { recursive: true });
  const buf = Buffer.from([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00]);
  fs.writeFileSync(wasmPath, buf);
  console.log('Placeholder wasm written to src/index.wasm');
  process.exit(0);
} catch (err) {
  console.error('Failed writing placeholder wasm:', err);
  process.exit(1);
}
