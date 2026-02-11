# Internal Change-Control Policy

> Evident Technologies LLC — Engineering Governance  
> Effective: Phase 7 (v0.6.0)

---

## Purpose

This policy governs how changes are proposed, reviewed, merged, and released
within the Evident platform. It exists to preserve:

- evidentiary defensibility
- audit trail integrity
- deterministic reproducibility
- operational stability

---

## 1. Phase-Locking Rule

Once a phase is declared **COMPLETE** (all tests green, morning report filed):

- Its code is **frozen**.
- No modifications to phase-frozen code are permitted unless:
  1. A regression is detected (failing test reproduces the defect).
  2. A security vulnerability is disclosed (CVE or equivalent).
  3. A court or counsel requires a correction.
- All exceptions require a written justification in the commit message referencing
  the specific test failure, CVE ID, or legal requirement.

### Phase registry

| Phase | Status   | Lock date  |
|-------|----------|------------|
| 1     | LOCKED   | 2026-01-01 |
| 2     | LOCKED   | 2026-01-15 |
| 3     | LOCKED   | 2026-01-20 |
| 4     | LOCKED   | 2026-01-25 |
| 5     | LOCKED   | 2026-02-05 |
| 6     | LOCKED   | 2026-02-10 |
| 7     | ACTIVE   | —          |

---

## 2. Branch Policy

| Branch      | Purpose                       | Merge requires          |
|-------------|-------------------------------|-------------------------|
| `main`      | Production-ready code         | PR + all tests green    |
| `phase-N`   | Active phase development      | Tests green locally     |
| `hotfix/*`  | Security / regression patches | PR + justification      |

- Direct commits to `main` are prohibited.
- Force-push to `main` is prohibited.
- All PRs must include the phase number in the title: `[Phase N] description`.

---

## 3. Commit Message Format

```
[Phase N] <scope>: <imperative description>

<body — what and why, not how>

Refs: <issue/ticket if applicable>
Tests: <which test suites validate this change>
```

Example:

```
[Phase 7] share-links: add expiring share-link model and service

Adds ShareLink model with SHA-256 token hashing, mandatory expiry,
and revocation support. Tokens are returned once at creation and
never stored in plaintext.

Tests: tests/test_share_links.py (28 tests)
```

---

## 4. Pre-Merge Checklist

Before any PR is merged, the author must verify:

- [ ] All existing test suites pass (zero regressions).
- [ ] New code has test coverage for all significant paths.
- [ ] No forensic invariant is weakened:
  - Originals remain immutable.
  - Audit logs remain append-only.
  - Hashes remain SHA-256.
  - Exports remain reproducible.
- [ ] No new dependency introduces a known CVE.
- [ ] No sensitive data (keys, tokens, PII) is committed.
- [ ] CHANGELOG.md is updated.
- [ ] VERSION file is updated (if releasing).

---

## 5. Release Process

1. Merge all phase work into `main`.
2. Update `VERSION`, `CHANGELOG.md`, `package.json`.
3. Tag: `git tag -a v<version> -m "Phase N release"`.
4. Push: `git push origin main --tags`.
5. File the morning report marking the phase COMPLETE.

---

## 6. Forensic Code Review Standards

Reviewers must specifically check:

- **Immutability**: Does this change ever overwrite an original file?
- **Audit completeness**: Are all access paths recorded?
- **Determinism**: Given the same inputs, does this always produce the same output?
- **Hash integrity**: Are SHA-256 hashes computed and verified at every boundary?
- **No inference**: Does this change draw conclusions, infer intent, or suggest guilt/liability?
- **No silent access**: Can any path serve evidence without an audit record?

If the answer to any of these is "yes", the PR must not be merged.

---

## 7. Incident Response for Code Defects

If a defect is discovered in production:

1. **Do not modify the evidence store.**
2. Create a `hotfix/*` branch from `main`.
3. Write a failing test that reproduces the defect.
4. Fix the defect.
5. Verify the fix with all test suites.
6. Merge via PR with a reference to the defect.
7. Document in CHANGELOG.md with the category **Fixed**.

---

## 8. Dependency Policy

- New dependencies require justification and CVE review.
- Dependencies must be pinned to specific versions in requirements files.
- Quarterly dependency audit: check all packages against known CVE databases.
- Prefer stdlib solutions over third-party packages when feasible.

---

## 9. Documentation Requirements

Every new feature must include:

- Docstrings on all public functions and classes.
- Test file with descriptive test names.
- Entry in CHANGELOG.md.
- If user-facing: entry in the appropriate `docs/` guide.
