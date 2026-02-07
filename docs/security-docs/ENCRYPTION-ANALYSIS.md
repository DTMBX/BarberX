# 🔐 Encryption Analysis for Evident Jekyll/GitHub Pages Site

**Date:** January 30, 2026  
**Status:** Analysis Complete

--

## ⚠️ Critical Understanding: Jekyll + GitHub Pages

**GitHub Pages is a STATIC site hosting service.** All files deployed must be
readable by the server to serve them to browsers. This means:

- ❌ **Cannot encrypt:** Any file that browsers need to render (HTML, CSS, JS,
  images, fonts)
- ❌ **Cannot encrypt:** Jekyll source files (\_config.yml, \_layouts,
  \_includes, Markdown pages)
- ❌ **Cannot encrypt:** Build configuration (Gemfile, package.json,
  netlify.toml)

--

## 📋 File Classification

### 🔴 CANNOT BE ENCRYPTED (Must remain readable)

| Category           | Files                                     | Reason                            |
| ------------------ | ----------------------------------------- | --------------------------------- |
| **Jekyll Config**  | `_config.yml`                             | Jekyll needs to read during build |
| **Templates**      | `_layouts/*.html`, `_includes/*.html`     | Compiled at build time            |
| **Pages**          | `_pages/*.md`, `*.html`                   | Converted to static HTML          |
| **Styles**         | `assets/css/**`                           | Served to browsers                |
| **Scripts**        | `assets/js/**`, `static/js/**`            | Executed in browser               |
| **Images**         | `assets/images/**`, `static/images/**`    | Displayed to users                |
| **Build Files**    | `Gemfile`, `package.json`, `netlify.toml` | Required for deployment           |
| **GitHub Actions** | `.github/workflows/**`                    | CI/CD configuration               |

### 🟢 CAN BE ENCRYPTED / SHOULD BE PROTECTED

| File               | Contains                     | Protection Method          |
| ------------------ | ---------------------------- | -------------------------- |
| `.env`             | API keys, passwords, secrets | **git-crypt** + .gitignore |
| `.env-temp`        | Temporary secrets            | **git-crypt** + .gitignore |
| `.env.local`       | Local development secrets    | .gitignore (never commit)  |
| `*.key`            | Private keys                 | **git-crypt** + .gitignore |
| `*.pem`            | Certificates                 | **git-crypt** + .gitignore |
| `instance/`        | Flask instance data          | .gitignore                 |
| `secure/`          | Encrypted outputs            | .gitignore                 |
| `backups/**/.env*` | Backup secrets               | Delete or encrypt          |

### 🟡 RECOMMENDED: Remove from Repository

| Files                               | Action                             |
| ----------------------------------- | ---------------------------------- |
| `backups/` folder with `.env` files | Delete from git history            |
| Any hardcoded credentials in code   | Replace with environment variables |
| `instance/*.db`                     | Already gitignored                 |

--

## 🛡️ Implemented Protection Strategy

### 1. **Strong .gitignore Protection** (Primary Defense)

Files that should NEVER be committed are gitignored.

### 2. **git-crypt Encryption** (For files that MUST be in repo)

Some files need to be in the repo but encrypted at rest.

### 3. **GitHub Secrets** (For CI/CD)

Production secrets stored in GitHub repository secrets.

### 4. **Environment Variables** (For Deployment)

Production credentials in Render/Netlify environment settings.

--

## 🔑 Files Protected by git-crypt

```
.env
.env-temp
.env.local
.env.production
*.key
*.pem
scripts/security/*.key
secure/**
```

--

## ✅ Action Items Completed

1. [x] Analyzed all files for encryption eligibility
2. [x] Verified .gitignore covers sensitive files
3. [x] Created .gitattributes for git-crypt
4. [x] Generated encryption key
5. [x] Encrypted eligible files
6. [x] Documented protection strategy

--

## 📝 How to Access Encrypted Files

### For Developers with Access:

```bash
# Install git-crypt
# Windows: choco install git-crypt
# Mac: brew install git-crypt

# Unlock repository (requires key file)
git-crypt unlock /path/to/Evident-git-crypt.key
```

### For CI/CD:

Store the base64-encoded key in GitHub Secrets as `GIT_CRYPT_KEY`

--

## 🚫 Files That Should NOT Be Encrypted

The following files are sometimes mistakenly encrypted - **DO NOT encrypt
these:**

- `_config.yml` - Jekyll will fail to build
- `Gemfile` / `Gemfile.lock` - Dependency installation fails
- `package.json` / `package-lock.json` - npm install fails
- `.github/workflows/*.yml` - CI/CD breaks
- `netlify.toml` / `render.yaml` - Deployment fails
- Any `*.html`, `*.css`, `*.js` - Site won't load
