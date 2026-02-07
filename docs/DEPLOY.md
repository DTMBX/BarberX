**Deploying the Eleventy site to GitHub Pages**

- Workflow: `.github/workflows/deploy-eleventy-pages.yml` builds the site and deploys `_site` using GitHub Actions Pages support.
- Requirements:
  - Ensure the repository's default branch is `main` (or update the workflow branch filter).
  - `package.json` must include `build` that outputs to `_site` (current setup: `npm run build`).

Repository Settings (recommended):

- In GitHub > Settings > Pages, ensure the site is configured to be served from GitHub Pages (the Actions deployment will manage this automatically). If you use a custom domain, add it in the Pages settings and add the DNS records as instructed.
- Enable `Enforce HTTPS` after DNS propagation.

Recommended for a monorepo

- Use the modern Pages Actions workflow (`deploy-eleventy-pages.yml`) as the primary deployment because it provides atomic, permission-scoped deploys and integrates with Pages preview and branch protection.
- Keep the classic `gh-pages` branch workflow available only as `workflow_dispatch` (manual) for legacy needs; avoid running both automatically to prevent conflicting updates.
- Add branch protection on `main` requiring the Site CI checks (lint/build/LHCI) before merges.
- Use `workflow_dispatch` or tag-based deployments for release staging if you need reproducible releases.

Best practices:

- Use the Pages Actions (`configure-pages`, `upload-pages-artifact`, `deploy-pages`) as implemented; they run under the repository's `GITHUB_TOKEN` and are robust for atomic updates.
- Keep builds idempotent: avoid writing secrets into built files. Use runtime environment variables for client-side feature flags only when safe.
- Use `concurrency` in the workflow to avoid overlapping deploys.
- Use a CDN (Cloudflare, Fastly, Netlify) in front of Pages for more advanced caching and edge rules if needed.

To trigger deployment manually:

```
git checkout main
git merge chore/repo-layout
git push origin main
```
