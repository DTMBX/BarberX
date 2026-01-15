# Docket Upload Worker Setup

This Cloudflare Worker enables PR-based docket uploads from the `/docket/submit/` form.

## Prerequisites

1. A Cloudflare account with Workers enabled
2. A GitHub Personal Access Token (PAT) with `repo` scope

## Setup Steps

### 1. Create GitHub Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "FaithFrontier Docket Worker"
4. Select scopes:
   - `repo` (Full control of private repositories)
5. Generate and save the token securely

### 2. Deploy Worker to Cloudflare

1. Install Wrangler CLI:
   ```bash
   npm install -g wrangler
   ```

2. Login to Cloudflare:
   ```bash
   wrangler login
   ```

3. Create a new worker:
   ```bash
   cd worker
   wrangler init docket-upload
   ```

4. Copy the `worker.js` content to your worker script

5. Configure the worker:
   - Create `wrangler.toml`:
     ```toml
     name = "docket-upload"
     main = "worker.js"
     compatibility_date = "2024-01-01"
     
     [env.production]
     vars = { REPO_OWNER = "XTX33", REPO_NAME = "FaithFrontier" }
     ```

6. Add the GitHub token as a secret:
   ```bash
   wrangler secret put GITHUB_PAT
   ```
   When prompted, paste your GitHub token

7. Deploy:
   ```bash
   wrangler deploy
   ```

8. Note the worker URL (e.g., `https://docket-upload.your-subdomain.workers.dev`)

### 3. Update the Submit Form

Edit `/assets/js/docket-submit.js` and replace the placeholder URL with your worker URL:

```javascript
const workerUrl = 'https://docket-upload.your-subdomain.workers.dev/docket-upload';
```

### 4. Configure CORS (if needed)

If your worker URL is different from `faithfrontier.org`, update the CORS origin in `worker.js`:

```javascript
'Access-Control-Allow-Origin': 'https://faithfrontier.org',
```

## How It Works

1. User fills out the form at `/docket/submit/`
2. JavaScript sends PDF + metadata to Cloudflare Worker
3. Worker creates a new git branch
4. Worker uploads PDF to `cases/`&lt;slug&gt;`/filings/`
5. Worker updates `_data/docket/`&lt;slug&gt;`.yml` with new entry
6. Worker creates a Pull Request for review
7. You review and merge the PR

## Security

- The GitHub token only has `repo` scope (read/write repository access)
- Token is stored as a Cloudflare secret (encrypted at rest)
- CORS restricts requests to faithfrontier.org
- All uploads go through PR review before merging

## Alternative: Manual Upload

If you prefer not to use the worker, you can manually:

1. Upload PDFs to the correct folder: `cases/`&lt;slug&gt;`/filings/`
2. Edit `_data/docket/`&lt;slug&gt;`.yml` to add the entry
3. Commit and push, or create a PR

## Troubleshooting

- **CORS errors**: Check the `Access-Control-Allow-Origin` header in worker.js
- **401 errors**: Verify the GitHub token is valid and has correct scopes
- **404 errors**: Ensure repository name and owner are correct
- **Worker not found**: Check the worker URL in docket-submit.js

## Testing

Test the worker locally:

```bash
wrangler dev
```

Then update `docket-submit.js` temporarily to use `http://localhost:8787` for testing.
