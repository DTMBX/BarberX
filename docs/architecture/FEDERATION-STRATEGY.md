# Federation Strategy

**Document:** Submodule vs clone vs tarball — tradeoff analysis and chosen approach  
**Date:** 2026-03-06  
**Status:** Approved  
**Scope:** Evident monorepo — satellite app source integration

---

## Problem

The Evident monorepo currently maintains full source copies of four
satellite apps inside `apps/`. These copies have diverged from their
canonical standalone repos (see SOURCE-OF-TRUTH-DIAGNOSIS.md). A
federation mechanism is needed to replace these copies with a
repeatable, auditable fetch-and-build pipeline.

Three approaches were evaluated:

1. Git submodules
2. Shallow clone at build time
3. Tarball download at build time

---

## Tradeoff Analysis

### Option 1 — Git Submodules

| Aspect | Assessment |
| ------ | ---------- |
| **Mechanism** | `.gitmodules` points to canonical repos; git manages checkouts |
| **Version pinning** | Submodule commit SHA recorded in parent repo's tree |
| **Determinism** | Exact commit pinned — fully deterministic |
| **Developer UX** | Requires `git submodule update --init` after clone |
| **CI complexity** | Most CI systems support submodules natively |
| **Monorepo fit** | Replaces `apps/` directories with submodule checkouts |
| **npm workspace compat** | Submodule directories can still be workspace members |
| **Offline builds** | Works after initial fetch; cached in `.git/modules/` |

**Pros:**

- Git-native version pinning — commit SHA in the repo tree.
- Tooling is mature and well-understood.
- `git diff` shows submodule pointer changes clearly.
- CI/CD pipelines handle submodules with one flag (`--recurse-submodules`).

**Cons:**

- Submodule UX is notoriously confusing for developers unfamiliar with it.
- Detached HEAD state in submodule directories can cause accidental commits.
- Requires explicit `git submodule update` — easy to forget.
- `.gitmodules` must be maintained alongside `workspace-registry.json`.
- Submodule directories appear as full repos, blurring the
  "these are not editable here" boundary.

### Option 2 — Shallow Clone at Build Time

| Aspect | Assessment |
| ------ | ---------- |
| **Mechanism** | Build script clones canonical repos to `.federation-cache/` |
| **Version pinning** | `versionLock` in `workspace-registry.json` |
| **Determinism** | SHA pin = deterministic; HEAD pin = latest |
| **Developer UX** | Run one script; no git submodule knowledge needed |
| **CI complexity** | Standard git + npm; no special CI flags |
| **Monorepo fit** | Cache directory is gitignored; `apps/` can be removed later |
| **npm workspace compat** | Not workspace members; built independently |
| **Offline builds** | Works if cache is populated; fails on cold start without network |

**Pros:**

- Clean separation: fetched repos live in a gitignored cache, not in the
  repo tree.
- No developer confusion about whether a directory is editable.
- Version lock is explicit in `workspace-registry.json` — single source
  of version truth.
- No `.gitmodules` to maintain.
- Works with any hosting (GitHub, GitLab, self-hosted).
- Cache can be pre-populated in CI for speed.

**Cons:**

- Requires network access for cold builds.
- Build script must handle clone, fetch, checkout, and error recovery.
- Cache invalidation is manual (delete directory).
- Slightly slower cold builds (clone + install + build per app).

### Option 3 — Tarball Download at Build Time

| Aspect | Assessment |
| ------ | ---------- |
| **Mechanism** | Download release tarball from GitHub Releases or archive API |
| **Version pinning** | Release tag or commit SHA in URL |
| **Determinism** | Fixed tag = deterministic; `latest` = not |
| **Developer UX** | Simplest — download and unpack |
| **CI complexity** | Requires `curl`/`Invoke-WebRequest` + tar/Expand-Archive |
| **Monorepo fit** | No git dependency for fetch; cache is files only |
| **npm workspace compat** | Not workspace members; no lock file available |
| **Offline builds** | Must pre-download; no local update mechanism |

**Pros:**

- No git required for fetch (useful in constrained CI environments).
- Smallest download size (no `.git` history).
- Simple caching (keep the tarball file).

**Cons:**

- No lock file in tarball unless repo includes `package-lock.json`.
- GitHub archive API tarballs do not include `.git` — cannot verify SHA
  after download without separate API call.
- Release management overhead — must create GitHub Releases for each
  satellite app.
- No incremental updates; must re-download entire tarball on change.
- Least mature option for this ecosystem's current state (no releases
  exist yet).

---

## Decision Matrix

| Criterion | Weight | Submodules | Shallow Clone | Tarball |
| --------- | ------ | ---------- | ------------- | ------- |
| Determinism | 5 | 5 | 4 | 3 |
| Developer UX | 4 | 2 | 4 | 5 |
| Auditability | 5 | 5 | 4 | 2 |
| Monorepo separation | 4 | 3 | 5 | 5 |
| CI simplicity | 3 | 3 | 4 | 3 |
| Offline capability | 2 | 4 | 3 | 2 |
| Maintenance burden | 4 | 2 | 4 | 3 |
| **Weighted total** | — | **90** | **110** | **89** |

---

## Chosen Approach: Shallow Clone at Build Time

**Rationale:**

1. **Clearest separation.** Federated repos live in `.federation-cache/`
   (gitignored), not in the repo tree. Developers cannot accidentally
   edit them thinking they are canonical.

2. **Single source of version truth.** `workspace-registry.json` already
   exists and is maintained. Adding `versionLock` there avoids a second
   version tracking mechanism (`.gitmodules`).

3. **No submodule UX tax.** Contributors do not need to learn
   `git submodule update`, `--recurse-submodules`, or detached HEAD
   recovery. One script handles everything.

4. **Audit-grade builds when needed.** Setting `pin` to a specific SHA
   produces byte-identical output. Setting `pin` to `"HEAD"` gives
   fast iteration during development.

5. **Smooth migration path.** The `apps/` workspace copies remain in
   place during transition. The federation script runs beside them. Once
   parity is confirmed, `apps/` can be removed.

---

## Migration Timeline

### Phase 3B — Complete (Documentation + Skeleton)

- `BUILD-FEDERATION-SPEC.md` — fetch protocol and manifest format
- `FEDERATION-STRATEGY.md` — this document
- `build-federate.ps1` — skeleton script (reads registry, clones, builds)
- `workspace-registry.json` v4 — `versionLock` fields added
- `WORKSPACE-LINKING-RULES.md` — marks `apps/` copies as deprecated

**Deliverable:** Documentation and a runnable skeleton script that
demonstrates the pipeline. Does not replace the production build yet.

### Phase 3C — Current (Release Determinism Hardening)

- Dual-mode `versionLock` schema: dev (HEAD) and release (tag/SHA)
- `releaseChannel` field added to registry (v5)
- `tag` field added to versionLock
- `build-federate.ps1` hardened: tag resolution, release enforcement,
  v2 manifest with business/role/tag/channel, full SHA recording
- `federation-manifest.json` committed to repo root (audit trail)
- `RELEASE-PINNING-RULES.md` — complete pinning policy
- `test-federation-reproducibility.ps1` — determinism verifier
- Migration gates defined for Phase 3D entry

**Deliverable:** Audit-grade federation pipeline. Release builds are
deterministic and reproducible. Manifest is a committed artifact.

### Phase 3D — Cutover (requires gates)

- Replace `build:apps` in `package.json` with federation pipeline.
- Remove `apps/` workspace copies from the monorepo.
- Remove `"apps/*"` from the `workspaces` array in `package.json`.
- Update CI workflows to use the federation pipeline.

**Migration gates (all must pass to enter Phase 3D):**

1. At least one tagged release built with tag-based federation
   (`releaseChannel: "release"` + `tag` set for at least one target).
2. `test-federation-reproducibility.ps1` passes on the tagged build.
3. `federation-manifest.json` committed and reviewed (manifest audit).
4. Federation build output diffed against legacy `build:apps` output
   with no functional divergence.
5. No `pin: "HEAD"` entries in the release manifest.

**Deliverable:** `apps/` directory removed. Federation pipeline is the
sole build path for satellite apps.

### Phase 3E — Hardening

- Pin all version locks to specific SHAs for the first release build.
- Add CI check that verifies build manifests are committed.
- Add CI check that warns if `pin: "HEAD"` is used in release branches.
- Document SHA rotation cadence (e.g., monthly review of pins).

**Deliverable:** Release-grade federation with full audit trail.

---

## Risks and Mitigations

| Risk | Severity | Mitigation |
| ---- | -------- | ---------- |
| Network outage during CI build | Medium | Pre-populate cache in CI; fail fast with clear error |
| Canonical repo force-pushed | Low | SHA pin rejects unknown commits; branch protection on main |
| Developer runs old `build:apps` | Low | Deprecation warning in `build-apps.js` during Phase 3C |
| Cache corruption | Low | Delete cache and re-clone; script handles missing cache |
| Tillerstead repo accidentally federated | High | Business field check in script; LLC boundary enforced |

---

## What This Strategy Does NOT Do

- Does not delete `apps/` workspace copies (deferred to Phase 3D).
- Does not merge any repos.
- Does not change deployment targets or domains.
- Does not alter the Tillerstead LLC boundary.
- Does not publish packages to npm.
