# Beginner Operator Workflow

> Step 12 of the Evident Ecosystem Architecture Series
>
> Principle: **Confidence comes from knowing what you just did, what it changed,
> and what to do next.**

---

## 0. Who This Is For

The "beginner operator" is the person managing the Evident ecosystem day to day.
They may or may not write code. They use VS Code, the web-builder, Git, and
GitHub. They need to:

- make visual changes to sites and apps
- export those changes to the right repo
- review what changed before committing
- push changes through Git with discipline
- switch between repos without losing context
- onboard new satellite projects
- prepare releases

This document defines the workflow for each of those tasks. It assumes no
framework expertise. It assumes literacy with a file system, a browser, and a
terminal.

---

## 1. Daily Workflow — Working on One Repo

This is the core loop. Every other workflow is a variation of this one.

### 1.1 The Five Phases

```text
  Open → Build → Review → Commit → Verify
   │       │        │        │        │
   │       │        │        │        └─ Check live deploy or preview
   │       │        │        └─ Stage, commit with message, push
   │       │        └─ Diff in VS Code, preflight in builder
   │       └─ Edit in builder or editor, run checks
   └─ Open folder, load registry, check status
```

### 1.2 Phase by Phase

**Phase 1 — Open**

1. Open VS Code with the workspace that includes all repos.
2. In the terminal, navigate to the repo you are working on.
3. Run `git status -sb` to confirm you are on the expected branch with no
   uncommitted changes from a previous session.
4. If using the web-builder, launch it and open the repo folder. The builder
   will auto-detect the `.evident-repo.json` manifest if present.

**What you should see:** A clean working tree, the correct branch, and the
builder loaded with the repo's identity in the registry panel.

**Phase 2 — Build**

1. Make your changes. In the builder, drag components, edit properties, use
   templates. In VS Code, edit files directly.
2. If the builder is open, use the Standards Check panel to validate your work
   before moving on. Look for green checkmarks on HTML5, Accessibility, and
   Responsive.
3. If editing code files directly, save frequently. Use VS Code's Problems
   panel to catch errors as you type.

**What you should see:** Your changes visible in the builder canvas or in the
editor. No red errors in the Standards Check or Problems panel.

**Phase 3 — Review**

1. In the builder, click Export. The preflight checklist runs automatically.
   Review each item. Fix any failures before proceeding.
2. Check the stack tier notice in the export panel. If it says "Aware" or
   "Prompt," you will need to manually convert the output after export.
3. Export to the target repo folder.
4. In VS Code, open the Source Control panel (Ctrl+Shift+G). Review every
   changed file. Click each file to see the diff.
5. Read the diff. Ask: "Does this change only what I intended?"

**What you should see:** A short list of changed files that match your intent.
No unexpected deletions, no files you did not touch, no secrets or tokens in
the diff.

**Phase 4 — Commit**

1. Stage only the files you intend to commit. Do not stage everything blindly.
   In Source Control, click the `+` icon on each file you reviewed.
2. Write a commit message that describes what changed and why. Format:

```text
Short summary (50 chars or less)

- What was changed
- Why it was changed
- What it affects
```

3. Commit. If the pre-commit hook runs lint-staged, let it complete. If it
   fails, fix the issues and commit again.
4. Push to the remote. If the pre-push hook blocks you from pushing to `main`
   directly, create a feature branch first:

```text
git checkout -b feat/your-change-name
git push origin feat/your-change-name
```

Then open a pull request on GitHub.

**What you should see:** A clean commit with a clear message. The push succeeds
or the PR is created.

**Phase 5 — Verify**

1. If the repo deploys to GitHub Pages, wait for the Actions workflow to
   complete. Check the Actions tab on GitHub for green checkmarks.
2. Visit the live URL and confirm your changes appear.
3. If the repo has CI checks (tests, linting, Lighthouse), review their output
   in the PR or Actions tab.

**What you should see:** A green build, your changes live, no regressions in
the CI output.

### 1.3 Daily Checklist (Copy-Friendly)

```text
[ ] git status -sb — clean tree, correct branch
[ ] Made changes — builder or editor
[ ] Standards check — green or addressed
[ ] Preflight — all pass
[ ] Exported — correct target folder
[ ] Reviewed diff — only intended changes
[ ] Committed — clear message, scoped files
[ ] Pushed — branch or main per policy
[ ] Verified — live deploy or CI green
```

---

## 2. Switching Between Main Suite and Satellites

The ecosystem has one main suite (Evident) and multiple satellites. Switching
between them should be deliberate, not accidental.

### 2.1 Before You Switch

1. **Finish or stash.** If you have uncommitted changes in the current repo,
   either commit them or stash them:

```text
git stash push -m "WIP: description of what I was doing"
```

2. **Note where you stopped.** Write a one-line note in the terminal or in a
   scratch file: what you were working on, what remains.

### 2.2 The Switch

1. In VS Code, use the file explorer to navigate to the new repo folder.
2. Open a new terminal in that repo's directory (`cd path/to/repo`).
3. Run `git status -sb` to confirm the state of the new repo.
4. If using the web-builder, close the current folder and open the new one. The
   registry panel will update to show the new repo's identity.

### 2.3 Context Cues

The builder's registry shows every repo with its role badge and stack tier
badge. Use these to orient yourself:

| Badge | Meaning |
| --- | --- |
| `main-suite-core` | You are in the Evident platform. Changes touch the product. |
| `ops` | You are in Founder-Hub. Changes touch operations tooling. |
| `satellite-app` | You are in a venture app. Changes are scoped to that product. |
| `site` | You are in a marketing or content site. Changes are presentation. |
| `experiment` | You are in a prototype. Lower standards, higher freedom. |

### 2.4 After You Switch Back

1. Run `git stash list` to check if you left work in progress.
2. If yes, run `git stash pop` to restore it.
3. Run `git status -sb` to confirm the restored state.

### 2.5 Rules

- Never have uncommitted changes in two repos at once. Finish one before
  starting the other.
- Never export from the builder to a repo you are not actively working in.
  The export target must match your terminal context.
- If you forget which repo you are in, check the terminal prompt, the builder's
  header, and `git remote -v`.

---

## 3. Adding a New Satellite

This is a structured workflow for onboarding a new project into the ecosystem.
It does not require coding expertise. It requires discipline.

### 3.1 Prerequisite Decisions

Before creating anything, answer these questions:

| Question | Options |
| --- | --- |
| What family does this belong to? | Evident, Tillerstead, Personal, or new family |
| What is the satellite tier? | Companion, Venture, or Independent |
| What stack will it use? | HTML/CSS, React+Vite, Python+FastAPI, Jekyll, etc. |
| Where will it deploy? | GitHub Pages, Netlify, Render, Railway, none yet |
| What is the output type? | web-app, api, static-site, pwa, docs, scripts |

### 3.2 Steps

**Step 1 — Create the GitHub repo.**

Go to GitHub. Click "New repository." Name it following the ecosystem
convention:

```text
{family}-{product-name}
```

Examples: `evident-consent-companion`, `tillerstead-toolkit`,
`evident-civics-hierarchy`.

Initialize with a README. Choose a license. Do not add a template.

**Step 2 — Clone locally.**

```text
git clone https://github.com/DTMBX/{repo-name}.git
```

Place it in the appropriate directory:
- Evident-family satellites: `Desktop/ventures/` or `Desktop/Evident/apps/`
  (if it will be a workspace member)
- Tillerstead-family satellites: `Desktop/ventures/`
- Independent: wherever is logical

**Step 3 — Create the manifest.**

Create `.evident-repo.json` at the repo root. Use this template:

```json
{
  "_manifest": "evident-repo",
  "_version": 1,
  "name": "Your Project Name",
  "description": "One-sentence purpose.",
  "role": "satellite-app",
  "family": "Evident",
  "stack": "React 19 + TypeScript + Vite",
  "outputType": "web-app",
  "exportTargets": ["GitHub Pages"],
  "brand": "evident",
  "satelliteTier": "venture",
  "catalogVisibility": "draft",
  "tokenFamily": "evident",
  "releaseStatus": "draft",
  "packagingStatus": "not-started",
  "sharedStandardsVersion": "1.0",
  "owner": "DTMBX"
}
```

Adjust every field to match your answers from Step 3.1.

**Step 4 — Register in the builder.**

1. Open the web-builder.
2. Go to the Projects tab.
3. Click "Add."
4. Fill in the fields. If you open the repo folder, the builder will
   auto-detect the manifest and pre-fill the form.
5. Save.

The repo now appears in the registry with its role badge and stack tier badge.

**Step 5 — Apply foundation tokens (if applicable).**

If the satellite uses the `evident` or `tillerstead` token family, copy the
appropriate foundation CSS file from `tokens/` into the new repo:

```text
tokens/evident.foundation.css    → for evident-family repos
tokens/tillerstead.foundation.css → for tillerstead-family repos
```

Link it in the repo's HTML or import it in the CSS.

**Step 6 — Set up CI (optional, by tier).**

| Tier | Minimum CI |
| --- | --- |
| Companion | Full CI: lint, test, build, deploy |
| Venture | Basic CI: build + deploy on push to main |
| Independent | Optional: deploy only |
| Experiment | None required |

Use the workflow templates from BUILD-RELEASE-WORKFLOW.md §6.

**Step 7 — First commit and push.**

```text
git add .
git commit -m "Initialize {project-name} with manifest and foundation tokens"
git push origin main
```

**Step 8 — Update the workspace registry export.**

In the builder, use Projects → Export Registry to save an updated
`workspace-registry.json`. Commit this update to the Evident repo.

### 3.3 Checklist (Copy-Friendly)

```text
[ ] Prerequisite decisions answered
[ ] GitHub repo created with correct name
[ ] Cloned to correct local directory
[ ] .evident-repo.json created with all fields
[ ] Registered in web-builder
[ ] Foundation tokens applied (if applicable)
[ ] CI workflow added (if applicable)
[ ] First commit pushed
[ ] Workspace registry export updated
```

---

## 4. Packaging a Release Candidate

This workflow applies to any repo that has reached a point where it should be
reviewed, tagged, and optionally deployed as a named version.

### 4.1 Prerequisites

- All changes are committed and pushed.
- CI is green.
- The manifest's `releaseStatus` is at least `alpha`.

### 4.2 Steps

**Step 1 — Create a release branch.**

```text
git checkout main
git pull origin main
git checkout -b release/v{MAJOR}.{MINOR}.{PATCH}
```

Example: `release/v0.9.0`.

**Step 2 — Update version markers.**

For the main suite (Evident):

```text
VERSION file      → 0.9.0
package.json      → "version": "0.9.0"
```

For satellites, update `package.json` only (if it exists).

Commit:

```text
git add VERSION package.json
git commit -m "Bump version to 0.9.0"
```

**Step 3 — Run the full validation suite.**

```text
npm run build        # Confirm the build succeeds
npm test             # Confirm tests pass (if tests exist)
npm run lint:css     # Confirm CSS is clean
```

If any step fails, fix it on the release branch before proceeding.

**Step 4 — Update the manifest.**

Set `releaseStatus` to `rc` in `.evident-repo.json`:

```json
"releaseStatus": "rc"
```

Commit:

```text
git add .evident-repo.json
git commit -m "Mark release candidate"
```

**Step 5 — Push and open PR.**

```text
git push origin release/v0.9.0
```

Open a pull request on GitHub targeting `main`. Title it:

```text
Release: v0.9.0
```

In the PR description, include:
- What changed since the last release
- What was tested
- Any known issues
- Link to the live preview (if applicable)

**Step 6 — Review the PR.**

Review every file in the GitHub diff. Confirm:
- No secrets, tokens, or credentials in the diff
- No unintended file changes
- Version markers are correct
- Manifest is correct

**Step 7 — Merge and tag.**

After review, merge the PR. Then tag the release:

```text
git checkout main
git pull origin main
git tag -a v0.9.0 -m "Release v0.9.0"
git push origin v0.9.0
```

**Step 8 — Post-release.**

1. Update `releaseStatus` to `stable` in the manifest.
2. Commit: `git commit -am "Post-release: mark stable"`.
3. Push.
4. Verify the deployment.

### 4.3 Checklist (Copy-Friendly)

```text
[ ] All changes committed and pushed
[ ] CI green on main
[ ] Release branch created
[ ] Version markers updated
[ ] Build, test, lint all pass
[ ] Manifest set to rc
[ ] PR opened with changelog
[ ] PR reviewed — no secrets, no drift
[ ] PR merged
[ ] Tag created and pushed
[ ] Manifest set to stable
[ ] Deployment verified
```

---

## 5. How the Web-Builder Should Teach the Workflow

The builder is not a tutorial app. It should not pop up wizards or interrupt
work with tips. Instead, it should make the right next action visible at the
right time.

### 5.1 Contextual Guidance Moments

| Moment | What the User Sees | Guidance Method |
| --- | --- | --- |
| **Empty canvas** | No components on the page | Hint text: "Start by dragging a component from the left panel, or choose a template." |
| **First export** | User clicks Export with no target selected | Notice: "Select a target repo from the picker. The stack tier badge shows what the builder can export for that repo." |
| **Stack mismatch** | Target repo is Tier 2 (Aware) or Tier 3 (Prompt) | Stack notice in export panel with specific guidance |
| **Preflight failure** | One or more preflight checks fail | Failure item shows description + action: "Fix this before exporting." |
| **Post-export** | Export completes successfully | Toast: "Exported to {repo}. Review the diff in VS Code before committing." |
| **Registry empty** | Projects tab has no items | Hint: "No repos registered. Click Add to register your first project, or import a workspace-registry.json file." |

### 5.2 Git Command Reference

The Projects tab already shows three compact git commands (add+commit+push,
status, pull). Extend this section with context-aware commands based on the
workflow phase.

**Current state (3 commands):**

```text
git add . && git commit -m 'Update' && git push
git status
git pull origin main
```

**Recommended state (6 commands, phased):**

| Phase | Command | Label |
| --- | --- | --- |
| Before work | `git status -sb` | Check status |
| Before work | `git pull origin main` | Pull latest |
| After export | `git diff --stat` | Review changes |
| Commit | `git add -p` | Stage interactively |
| Commit | `git commit` | Commit (opens editor) |
| Push | `git push origin HEAD` | Push current branch |

Each command has a copy button. The label tells the user when to use it.

### 5.3 Workflow Strip

Add a minimal progress indicator to the builder header that shows where the
user is in the daily workflow. This is not a wizard. It is a passive status
bar.

```text
┌─────────────────────────────────────────────────────┐
│  Open  →  Build  →  Review  →  Commit  →  Verify   │
│   ●        ○         ○          ○          ○        │
└─────────────────────────────────────────────────────┘
```

**Rules:**
- "Open" lights up when a folder is loaded.
- "Build" lights up when the canvas has components.
- "Review" lights up when the user opens the export panel.
- "Commit" and "Verify" are always dim (the builder cannot observe Git state).
- The strip is small (24px tall), muted, and non-interactive. It reminds, it
  does not enforce.

### 5.4 Export Toast with Next Step

When an export succeeds, the toast message should include the next step in the
workflow:

| Export Target Tier | Toast Message |
| --- | --- |
| Native | "Exported to {repo}. Review the diff in VS Code, then commit." |
| Aware | "Exported HTML/CSS to {repo}. Convert to {stack} format, review the diff, then commit." |
| Prompt | "Exported HTML/CSS to {repo}. Copy the Stack Conversion prompt from the AI panel to convert to {stack}." |

### 5.5 What the Builder Should Not Do

- **No auto-commit.** The builder must never run git commands. Git is the
  user's responsibility. The builder only copies commands to the clipboard.
- **No auto-deploy.** The builder must never trigger a deployment. Deployment
  is the CI/CD pipeline's job.
- **No file deletion.** The builder creates and overwrites files in the target
  folder. It never deletes files it did not create.
- **No framework transpilation.** The builder exports HTML/CSS. Stack
  conversion is the user's job, assisted by prompts.
- **No hidden state.** Everything the builder stores (registry, profiles,
  history) is in localStorage and is inspectable via the browser DevTools.

---

## 6. Reference Card

A single-page summary for printing or pinning next to the monitor.

```text
╔══════════════════════════════════════════════════════╗
║            EVIDENT OPERATOR QUICK REFERENCE          ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  DAILY LOOP                                          ║
║  1. git status -sb          (clean tree?)            ║
║  2. Open builder or editor  (make changes)           ║
║  3. Run Standards Check     (green?)                 ║
║  4. Export → Preflight      (all pass?)              ║
║  5. VS Code diff            (only intended changes?) ║
║  6. git add → commit → push (clear message?)         ║
║  7. Check deploy            (live and correct?)      ║
║                                                      ║
║  SWITCHING REPOS                                     ║
║  • Commit or stash current work first                ║
║  • cd to new repo; git status -sb                    ║
║  • Open new folder in builder                        ║
║  • Never export to a repo you are not working in     ║
║                                                      ║
║  NEW SATELLITE                                       ║
║  • Create GitHub repo (family-name convention)       ║
║  • Clone locally; create .evident-repo.json          ║
║  • Register in builder; apply foundation tokens      ║
║  • Add CI by tier; push first commit                 ║
║                                                      ║
║  RELEASE                                             ║
║  • Branch: release/vX.Y.Z                            ║
║  • Bump VERSION + package.json                       ║
║  • Build, test, lint — all green                     ║
║  • PR → review → merge → tag → deploy               ║
║                                                      ║
║  STACK TIERS                                         ║
║  ● Native   — Builder exports directly               ║
║  ● Aware    — HTML/CSS + integration notes           ║
║  ● Prompt   — HTML/CSS + AI conversion prompt        ║
║  ● Metadata — Info only, no export                   ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

*This document completes the 12-step Evident Ecosystem Architecture Series.
It does not introduce new systems. It teaches the operator how to use the
systems already built in Steps 1 through 11.*
