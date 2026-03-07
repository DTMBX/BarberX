# Build Federation Spec

**Document:** Federation build protocol for canonical-standalone satellites  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident monorepo — satellite app integration builds  
**Revision:** Phase 3C — release determinism hardening

---

## Purpose

This document specifies how the Evident monorepo integrates satellite
apps from their canonical standalone repos into the monorepo build
output (`_site/apps/`) without maintaining duplicate source copies
inside `apps/`.

The current `scripts/build-apps.js` reads directly from `apps/`
workspace copies. This spec defines a federation pipeline that replaces
those copies with deterministic fetches from canonical sources.

---

## Terminology

| Term | Definition |
| ---- | ---------- |
| **Canonical repo** | The standalone GitHub repo that is the source of truth |
| **Federation target** | A satellite app that the monorepo build integrates |
| **Version lock** | A branch + optional commit SHA that pins the fetch |
| **Federation cache** | Local directory holding fetched repos between builds |
| **Build manifest** | JSON log recording what was fetched, built, and deployed |

---

## Federation Targets

| App | Canonical repo | Slug in `_site/apps/` |
| --- | -------------- | --------------------- |
| Civics Hierarchy | `DTMBX/civics-hierarchy` | `civics-hierarchy` |
| DOJ Document Library | `DTMBX/epstein-library-evid` | `epstein-library` |
| Essential Goods Ledger | `DTMBX/essential-goods-ledg` | `essential-goods` |
| Geneva Bible Study | `DTMBX/geneva-bible-study-t` | `geneva-bible-study` |

---

## Version Lock Schema

Each federation target has a `versionLock` entry in
`workspace-registry.json`. The schema supports two operational modes:
**dev** (latest on branch) and **release** (pinned to tag or SHA).

### Full schema

```json
{
  "versionLock": {
    "branch": "main",
    "pin": "HEAD",
    "tag": null,
    "releaseChannel": "dev"
  }
}
```

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `branch` | string | Yes | Git branch to fetch from |
| `pin` | string | Yes | `"HEAD"` for latest, or a 7+ char commit SHA for deterministic pin |
| `tag` | string\|null | No | Git tag (e.g., `"v1.0.0"`) — overrides `pin` when set |
| `releaseChannel` | string | Yes | `"dev"` or `"release"` — controls which mode the build enforces |

### Mode semantics

| Mode | `releaseChannel` | `pin` | `tag` | Behavior |
| ---- | ---------------- | ----- | ----- | -------- |
| **Dev** | `"dev"` | `"HEAD"` | `null` | Fetch latest commit on branch. Fast iteration. |
| **Release (tag)** | `"release"` | ignored | `"v1.0.0"` | Fetch the tagged commit. Build fails if tag missing. |
| **Release (SHA)** | `"release"` | `"abc1234..."` | `null` | Fetch exact commit. Build fails if SHA missing on branch. |

### Pin resolution order

1. If `tag` is set and non-null → resolve tag to SHA, use that commit.
2. Else if `pin` is not `"HEAD"` → use the explicit SHA.
3. Else → fetch `HEAD` of the specified branch.

### Dev mode example

```json
{
  "versionLock": {
    "branch": "main",
    "pin": "HEAD",
    "tag": null,
    "releaseChannel": "dev"
  }
}
```

### Release mode example (tag)

```json
{
  "versionLock": {
    "branch": "main",
    "pin": "HEAD",
    "tag": "v1.0.0",
    "releaseChannel": "release"
  }
}
```

### Release mode example (SHA)

```json
{
  "versionLock": {
    "branch": "main",
    "pin": "a1b2c3d4e5f6789",
    "tag": null,
    "releaseChannel": "release"
  }
}
```

### Upgrading a pin

To bump a satellite to a newer version:

1. Verify the target commit or tag in the canonical repo.
2. Update the `pin`, `tag`, and/or `releaseChannel` fields in
   `workspace-registry.json`.
3. Run the federation build to confirm it succeeds.
4. Commit the registry change with message:
   `chore(federation): pin {app} to {tag or sha}`

### Switching channels

To promote from dev to release:

1. Set `releaseChannel` to `"release"`.
2. Set `tag` to the release tag, or set `pin` to the target SHA.
3. Run the federation build. It will enforce exact-match verification.
4. Commit with: `chore(federation): promote {app} to release @ {ref}`

To revert to dev for iteration:

1. Set `releaseChannel` to `"dev"`.
2. Set `tag` to `null`, `pin` to `"HEAD"`.
3. Commit with: `chore(federation): {app} back to dev channel`

See RELEASE-PINNING-RULES.md for the complete pinning policy.

---

## Fetch Protocol

### Step 1 — Resolve version

Read `workspace-registry.json` and extract `versionLock` for each
federated app (entries with `hasWorkspaceCopy` set).

### Step 2 — Clone or update cache

```text
.federation-cache/
  civics-hierarchy/          ← shallow clone of DTMBX/civics-hierarchy
  epstein-library-evid/      ← shallow clone of DTMBX/epstein-library-evid
  essential-goods-ledg/      ← shallow clone of DTMBX/essential-goods-ledg
  geneva-bible-study-t/      ← shallow clone of DTMBX/geneva-bible-study-t
```

For each target:

- If cache directory does not exist: `git clone --depth 1 --branch {branch} {url} {cache-dir}`
- If cache directory exists: `git -C {cache-dir} fetch origin {branch} && git -C {cache-dir} checkout {resolved-sha}`

If `pin` is not `"HEAD"`, verify the checked-out commit matches the pin
exactly. Abort on mismatch.

### Step 3 — Install dependencies

```text
cd {cache-dir}
npm ci --no-audit --no-fund
```

Use `npm ci` (not `npm install`) for deterministic installs from the
lock file.

### Step 4 — Build

```text
cd {cache-dir}
npm run build
```

Expect output in `{cache-dir}/dist/`.

### Step 5 — Copy output

```text
cp -r {cache-dir}/dist/* _site/apps/{slug}/
```

### Step 6 — Write build manifest

After all targets are built, write two manifest files:

**Primary manifest:** `federation-manifest.json` (project root, committed)

```json
{
  "_schema": "evident-federation-manifest",
  "_version": 2,
  "builtAt": "2026-03-06T14:30:00.000Z",
  "registryVersion": 5,
  "buildMode": "release",
  "targets": [
    {
      "app": "civics-hierarchy",
      "slug": "civics-hierarchy",
      "repo": "DTMBX/civics-hierarchy",
      "business": "Evident Technologies LLC",
      "role": "product-satellite",
      "branch": "main",
      "tag": "v1.0.0",
      "pin": "HEAD",
      "releaseChannel": "release",
      "resolvedSha": "a1b2c3d4e5f6789",
      "resolvedShaFull": "a1b2c3d4e5f6789012345678901234567890abc",
      "buildSuccess": true,
      "fileCount": 42
    }
  ],
  "summary": {
    "totalTargets": 4,
    "succeeded": 4,
    "failed": 0,
    "channel": "release"
  }
}
```

**Cache manifest:** `.federation-cache/build-manifest.json` (gitignored)
— same content, for local reference when federation-manifest.json has
not yet been committed.

The primary manifest:

- Is committed to the repo for audit trail and reproducibility.
- Records the `resolvedSha` (short) and `resolvedShaFull` (full 40-char)
  for every target.
- Includes `business` and `role` for LLC boundary verification.
- Includes `tag` and `releaseChannel` for release provenance.
- Includes a `summary` block for quick machine-readable status checks.

Previously this was written only to `.federation-cache/`. Phase 3C
elevates it to a committed, auditable artifact.

---

## Deterministic Build Guarantees

| Guarantee | Mechanism |
| --------- | --------- |
| Same source | Commit SHA recorded in federation-manifest.json |
| Same dependencies | `npm ci` uses lock file from canonical repo |
| Same build output | Vite deterministic builds (no source maps with timestamps) |
| Reproducible | Re-running with same pin/tag produces identical output |
| Auditable | Manifest logs timestamp, SHA, branch, tag, channel, file count |
| Verifiable | `test-federation-reproducibility.ps1` confirms manifest match |

### What breaks determinism

| Risk | Mitigation |
| ---- | ---------- |
| `pin: "HEAD"` fetches different commits | Use tag or SHA pin for release builds |
| `releaseChannel: "dev"` in production | Build script warns; gate check blocks release |
| npm registry changes | Lock files in canonical repos pin exact versions |
| Build tooling version drift | Pin Node.js version in `.nvmrc` or CI config |
| Network failure mid-fetch | Build aborts cleanly; no partial output written |

---

## Cache Management

| Operation | Command |
| --------- | ------- |
| Clear all caches | `Remove-Item -Recurse .federation-cache/` |
| Clear one app | `Remove-Item -Recurse .federation-cache/{dir}/` |
| Force fresh fetch | Delete cache, then run federation build |

The `.federation-cache/` directory must be added to `.gitignore`.

---

## Integration with Existing Build

The current build pipeline is:

```text
npm run build
  ├── prepare:media
  ├── build:images
  ├── build:css
  ├── build:eleventy
  └── build:apps  ← currently reads from apps/
```

### Migration path

1. **Phase 3B (complete):** Created `build-federate.ps1` as a standalone
   script. Documentation and skeleton delivered.
2. **Phase 3C (current):** Release determinism hardening. Dual-mode
   versionLock, hardened manifest, reproducibility test, pinning policy.
3. **Phase 3D (future):** Replace `build:apps` with federation pipeline.
   Remove `apps/` workspace copies.
4. **Phase 3E (future):** Pin all version locks to SHAs/tags for first
   release. CI enforcement of manifest commits.

During the transition, both paths coexist:

- `npm run build:apps` — builds from `apps/` (legacy, deprecated)
- `./scripts/build-federate.ps1` — builds from canonical repos (new)

---

## LLC Boundary Enforcement

The federation pipeline only fetches repos attributed to
Evident Technologies LLC or Personal projects. Tillerstead LLC repos
are never fetched into the Evident monorepo build.

| Repo | Business | Federated? |
| ---- | -------- | ---------- |
| `civics-hierarchy` | Evident LLC | Yes |
| `epstein-library-evid` | Evident LLC | Yes |
| `essential-goods-ledg` | Evident LLC | Yes |
| `geneva-bible-study-t` | Personal | Yes |
| `Tillerstead` | Tillerstead LLC | **No** |
| `tillerstead-toolkit` | Tillerstead LLC | **No** |
| `contractor-command-center` | Tillerstead LLC | **No** |
| `sweat-equity-insurance` | Tillerstead Ventures LLC | **No** |

This boundary is enforced by reading the `business` field from
`workspace-registry.json` and skipping any entry where `business`
contains "Tillerstead".
