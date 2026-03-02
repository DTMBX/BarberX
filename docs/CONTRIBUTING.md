# Contributing to Evident Technologies

## Branching Strategy

### Long-lived Branches

| Branch       | Purpose                                               |
|-------------|-------------------------------------------------------|
| `main`       | Production-ready code. All PRs merge here.            |
| `gh-pages`   | Auto-deployed GitHub Pages site.                      |
| `release/*`  | Release stabilization (e.g., `release/1.0`).          |
| `hotfix/*`   | Critical production fixes (branched from `main`).     |

### Short-lived Branches

| Pattern           | Purpose                                          |
|-------------------|--------------------------------------------------|
| `feat/*`          | New features.                                    |
| `fix/*`           | Bug fixes.                                       |
| `refactor/*`      | Code restructuring (no behavior change).         |
| `chore/*`         | Maintenance, deps, CI.                           |
| `test/*`          | Test improvements.                               |
| `docs/*`          | Documentation changes only.                      |

Short-lived branches are deleted after merge.

### Rules

1. **One PR = one axis of change.** Do not mix features with refactors.
2. **All PRs target `main`** unless they are hotfixes for a release branch.
3. **Rebase before merge** (squash acceptable for single-commit fixes).
4. **Branch protection on `main`**: requires CI pass + 1 review.
5. **No force-push to `main` or `release/*`**.

---

## Code Standards

- Python 3.11+, PEP 8 compliant (Black formatter)
- Type hints required
- Docstrings for all public functions
- ES2022+ JavaScript, CommonJS modules
- WCAG 2.1 AA accessibility minimum

---

## Pull Request Requirements

- [ ] All Tier 1 Playwright tests pass.
- [ ] No new lint errors.
- [ ] Build succeeds.
- [ ] Security audit shows no new critical/high vulnerabilities.
- [ ] If touching auth/evidence/export: manual review required.
- [ ] If touching audit logging: **flag for security review**.

---

## Commit Message Format

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `refactor`, `chore`, `test`, `docs`, `perf`, `ci`

---

## Development Setup

```bash
# Install dependencies
npm install --legacy-peer-deps

# Run lint
npm run lint:css
npm run lint:js

# Run Playwright tests (Tier 1 — PR gate)
npx playwright test tests/tier1/ --project=chromium-desktop

# Run full suite (Tier 1 + 2)
npx playwright test tests/tier1/ tests/tier2/ --project=chromium-desktop

# Python tests
pytest
```

---

## Architecture Principles

1. **Immutable evidence.** Originals are never modified after ingest.
2. **Append-only audit.** Audit records cannot be edited or deleted.
3. **Server-side role enforcement.** Client-side checks are cosmetic.
4. **Deterministic processing.** Same input always produces same output.
5. **Traceable AI actions.** Every assistant action produces an audit receipt.

---

## Security

- Report vulnerabilities to security@evident.icu (not GitHub Issues).
- Do not commit secrets, tokens, or credentials.
- All evidence access must include a stated purpose.

---

## Stale Branch Cleanup

After each release:
1. Delete merged `feat/*`, `fix/*`, `refactor/*`, `chore/*` branches.
2. Keep `main`, `gh-pages`, and active `release/*` / `hotfix/*` branches.
3. Document deletions in the release notes.

