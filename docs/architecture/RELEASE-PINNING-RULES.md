# Release Pinning Rules

**Document:** Federation version pinning policy  
**Date:** 2026-03-06  
**Status:** Active  
**Scope:** Evident monorepo — satellite app federation builds  
**Phase:** 3C — Release Determinism Hardening

---

## Purpose

This document defines when and how federation targets must be pinned
to specific commits or tags, and when `HEAD` tracking is permitted.
All rules apply to the `versionLock` fields in `workspace-registry.json`.

See BUILD-FEDERATION-SPEC.md for the version lock schema and fetch
protocol. See FEDERATION-STRATEGY.md for the architectural rationale.

---

## Release Channels

| Channel | `releaseChannel` | Meaning |
| ------- | ---------------- | ------- |
| **Dev** | `"dev"` | Active development. Latest commit on branch. |
| **Release** | `"release"` | Frozen source. Tag or SHA required. |

Every federation target must declare exactly one channel at any time.

---

## When HEAD Is Allowed

`pin: "HEAD"` with `releaseChannel: "dev"` is permitted when:

1. The monorepo is on a development or feature branch.
2. The build is for local preview or CI preview (not production deploy).
3. No release tag has been cut for the current development cycle.
4. The target satellite has no current release obligations.

`pin: "HEAD"` is **forbidden** when:

1. `releaseChannel` is `"release"`.
2. The monorepo build is tagged for production release.
3. The build output will be deployed to a production URL.
4. The federation-manifest.json is being committed as a release artifact.

---

## When a Tag Is Required

A `tag` must be set (and `releaseChannel` set to `"release"`) when:

1. The monorepo is preparing a versioned release.
2. The satellite app has reached a stability milestone.
3. The build must be reproducible for audit or legal review.
4. The federation-manifest.json will be committed alongside a release.

Tags take precedence over SHA pins. When a tag is set, the build
resolves it to a SHA and verifies the resolved commit exists.

---

## Tag Naming Convention

All federation tags must follow semantic versioning with a `v` prefix:

```text
v{major}.{minor}.{patch}
```

Examples:

- `v1.0.0` — first stable release
- `v1.1.0` — minor feature addition
- `v1.0.1` — patch fix
- `v0.1.0` — pre-release (experimental)

### Rules

1. Tags must be annotated (`git tag -a`), not lightweight.
2. Tags must exist on the declared `branch` (usually `main`).
3. Tags must not be moved or deleted after a federation build uses them.
4. Pre-release versions (0.x.y) are permitted for experimental apps.

### Tag creation command

```bash
git tag -a v1.0.0 -m "Release v1.0.0 — stable federation target"
git push origin v1.0.0
```

---

## Commit SHA Overrides

A direct SHA pin (without a tag) is permitted when:

1. A hotfix must be deployed before a formal tag is cut.
2. A specific commit has been verified but tagging is deferred.
3. Debugging requires pinning to an exact historical commit.

### SHA override rules

1. The SHA must be at least 7 characters (short form) or 40 characters
   (full form). The build script normalizes to full SHA internally.
2. The SHA must exist on the declared `branch`.
3. The `releaseChannel` must be `"release"` (SHA overrides are not
   meaningful in dev mode since HEAD already fetches latest).
4. The override must be documented in the commit message:
   `chore(federation): pin {app} to SHA {sha} — {reason}`

---

## Provenance Logging

Every federation build produces a `federation-manifest.json` that
records provenance for each target:

| Field | Purpose |
| ----- | ------- |
| `resolvedSha` | Short SHA of the commit that was actually checked out |
| `resolvedShaFull` | Full 40-character SHA for exact reproducibility |
| `tag` | The tag used to resolve the commit (null if SHA or HEAD) |
| `branch` | The branch fetched from |
| `releaseChannel` | dev or release — indicates build intent |
| `business` | LLC attribution — verifies boundary enforcement |
| `builtAt` | ISO 8601 timestamp of the build |

### Provenance chain

```text
workspace-registry.json  (input: declared intent)
       ↓
build-federate.ps1       (process: fetch + build)
       ↓
federation-manifest.json (output: recorded provenance)
```

For release builds, the manifest must be committed alongside the
registry change so that the provenance chain is preserved in git
history.

---

## Channel Transition Procedures

### Dev → Release

1. Identify the target commit or tag in the canonical repo.
2. Update `workspace-registry.json`:
   - Set `releaseChannel` to `"release"`
   - Set `tag` to the release tag, OR set `pin` to the target SHA
3. Run `build-federate.ps1` (non-dry-run).
4. Verify `federation-manifest.json` shows correct resolved SHA.
5. Run `test-federation-reproducibility.ps1` to confirm determinism.
6. Commit both `workspace-registry.json` and `federation-manifest.json`
   with: `chore(federation): promote {app} to release @ {ref}`

### Release → Dev

1. Update `workspace-registry.json`:
   - Set `releaseChannel` to `"dev"`
   - Set `tag` to `null`
   - Set `pin` to `"HEAD"`
2. Commit with: `chore(federation): {app} back to dev channel`

### SHA Hotfix

1. Identify the hotfix commit SHA.
2. Update `workspace-registry.json`:
   - Set `pin` to the SHA
   - Set `releaseChannel` to `"release"`
   - Set `tag` to `null`
3. Run build and reproducibility test.
4. Commit with: `chore(federation): hotfix {app} to {sha} — {reason}`

---

## Enforcement

### Build-time enforcement

The build script (`build-federate.ps1`) enforces:

1. If `releaseChannel` is `"release"` and both `tag` and `pin` are
   `"HEAD"` or null → **build fails** with clear error message.
2. If `tag` is set but does not exist in the canonical repo →
   **build fails**.
3. If `pin` is a SHA but does not exist on the declared branch →
   **build fails**.

### Commit-time enforcement (future CI)

When CI is configured (Phase 3E):

1. Warn if any federation target uses `releaseChannel: "dev"` on the
   `main` branch.
2. Block release tags on the monorepo if any target uses `pin: "HEAD"`.
3. Require `federation-manifest.json` to be committed and up-to-date
   for release branches.

---

## Decision Record

| Decision | Date | Rationale |
| -------- | ---- | --------- |
| Dual-mode versionLock (dev/release) | 2026-03-06 | Separates fast iteration from audit-grade reproducibility |
| Tag takes precedence over SHA | 2026-03-06 | Tags are human-readable and conventional for releases |
| SHA override permitted for hotfixes | 2026-03-06 | Pragmatic escape hatch without forcing premature tagging |
| Annotated tags required | 2026-03-06 | Provides author, date, and message for audit trail |
| Manifest committed for releases | 2026-03-06 | Preserves provenance chain in git history |
