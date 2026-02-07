# GOVERNANCE

## Purpose

This document explains repository governance: quality gates, release rules, security and dependency policy, and automation that keeps the project reproducible.

## Quick summary

- All contributions must go through pull requests and pass CI checks.
- CI gates: install, lint, format-check, test, build, dependency-audit, accessibility/perf checks where applicable.
- Dependabot keeps deps up to date. Critical/security updates must be triaged within 72 hours.

## Required checks (PRs)

1. Build: `npm ci && npm run build` must complete successfully.
2. Lint & format: `npm run lint` (includes stylelint + Prettier) must pass.
3. Python tests: `pytest` must pass for backend components.
4. Security scans: `npm audit` and `pip-audit` run in CI and alerts posted to PR (failures flagged for review).

## Branching and merging

- `main` is protected: require PRs, passing status checks, and at least one approving reviewer before merge.
- Use short-lived feature branches named `feat/*`, `chore/*`, or `fix/*` and open PRs against `main`.

## Version pinning and reproducibility

- Commit lock files (`package-lock.json`, `requirements.txt`) and pin major versions for production builds.
- CI workflows pin Node and Python versions. Local envs should use `.nvmrc` and `.python-version` when present.

## Pre-commit and developer tooling

- Use `pre-commit` and `lint-staged` to run formatting and quick linters locally before commits.
- Run `npm run format` to auto-fix Prettier issues and `npx --yes stylelint "src/**/*.css" --fix` for CSS.

## Security & dependency management

- Enable Dependabot for `npm` and `pip` updates. Review PRs and run tests before merging.
- Run supply-chain scans and SCA (e.g., `npm audit`, `pip-audit`) in CI; treat high-severity results as blockers.

## Release & deployment (summary)

- Releases are created from `main` using tags. Use a release checklist that includes: build verification, regression smoke tests, and security audit review.

## Runbook links

- CI: `.github/workflows/ci.yml`
- Dependabot: `.github/dependabot.yml`
- PR template: `.github/pull_request_template.md`

## Contact

Repository maintainers and security contacts should be listed in the project README or in `CODEOWNERS`.

## Notes

This document is intentionally concise — add project-specific policies, compliance notes, and contact lists as needed.
