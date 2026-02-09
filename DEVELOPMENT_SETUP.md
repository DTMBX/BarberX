# Development Environment Setup Guide

## Prerequisites

### System Requirements

- OS: macOS, Linux, or Windows (WSL2 recommended)
- Git 2.40+
- Disk space: 5GB minimum

### Tools to Install

#### 1. Node Version Manager

**macOS/Linux:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

**Windows:**
Use [nvm-windows](https://github.com/coreybutler/nvm-windows/releases)

#### 2. Ruby Version Manager

**macOS:**

```bash
brew install rbenv ruby-build
```

**Linux:**

```bash
curl -fsSL https://github.com/rbenv/rbenv-installer/raw/main/bin/rbenv-installer | bash
```

**Windows:**
Use [RubyInstaller](https://rubyinstaller.org/)

## Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/DTMBX/EVIDENT.git
cd EVIDENT
```

### 2. Install Node.js

```bash
nvm install 18
nvm use 18
node --version  # Verify: v18.x.x
```

### 3. Install Ruby

```bash
rbenv install 3.3.0
rbenv local 3.3.0
ruby --version  # Verify: ruby 3.3.0
```

### 4. Install Dependencies

#### Node dependencies:

```bash
npm ci --no-audit --no-fund
```

#### Ruby gems:

```bash
bundle install --jobs 1
```

### 5. Setup Git Hooks (Husky)

```bash
npm run prepare 2>/dev/null || npx husky install
```

This installs:

- **pre-commit hook** - Runs linting before commit
- **pre-push hook** - Prevents pushes to protected branches

## Development Workflow

### Local Development Server

```bash
npm run dev
```

This starts:

- Eleventy in watch mode
- BrowserSync on http://localhost:3000
- CSS/asset compilation with PostCSS
- Live reload on file changes

Press `Ctrl+C` to stop.

### Building for Production

```bash
ELEVENTY_ENV=production npm run build
```

Output: `_site/` directory with static files

### Code Quality Checks

#### Lint CSS:

```bash
npm run lint:css
```

#### Check formatting (Prettier):

```bash
npm run format:check:site
```

#### Format automatically:

```bash
npm run format
```

#### Lint JavaScript:

```bash
npm run lint:js
```

### Full Build Pipeline

```bash
npm run build
```

Steps:

1. Optimize images
2. Generate media renditions
3. Compile CSS (PostCSS + Tailwind)
4. Build site with Eleventy
5. Output to `_site/`

## Common Tasks

### Add a new page

1. Create `src/pages/my-page.md`
2. Add frontmatter:
   ```yaml
   ---
   title: My Page Title
   layout: layouts/default.njk
   ---
   ```
3. Write content in Markdown
4. Browse to http://localhost:3000/pages/my-page/

### Update styling

1. Edit `.src/assets/css/tailwind.css`
2. Or add Tailwind classes directly in templates
3. npm rebuild triggers on save (auto-compiled)

### Add a new layout

1. Create `src/_includes/layouts/my-layout.njk`
2. Extend default layout or create standalone
3. Reference in page frontmatter: `layout: layouts/my-layout.njk`

### Add dependencies

**npm (JavaScript):**

```bash
npm install --save package-name
npm install --save-dev package-name-dev
```

**bundle (Ruby):**

```bash
bundle add gem-name
bundle add --group development gem-name-dev
```

## Environment Variables

Create `.env.local` for local overrides:

```env
ELEVENTY_ENV=development
DEBUG=true
```

Production environment handled by GitHub Actions.

## Troubleshooting

### "npm: command not found"

```bash
nvm install 18
nvm use 18
```

### "ruby: command not found"

```bash
rbenv install 3.3.0
rbenv local 3.3.0
```

### Build fails with "Cannot find module"

```bash
rm -rf node_modules
npm ci
```

### Bundle install fails

```bash
bundle update
bundle install --jobs 1
```

### Git hooks not running

```bash
npx husky install
chmod +x .husky/*
```

### Port 3000 already in use

```bash
# Find process on port 3000
lsof -i :3000
# Kill it
kill -9 <PID>
# Or use different port:
PORT=3001 npm run dev
```

## Performance Tips

### Speed up builds

1. Use `npm ci` instead of `npm install` (deterministic)
2. Cache node_modules: `npm ci --prefer-offline`
3. Use incremental builds during development: `ELEVENTY_ENV=development npm run dev`

### Speed up tests

1. Run in parallel when possible
2. Use dedicated test databases/fixtures
3. Skip heavy operations in CI when not needed

## Git Workflow

### Create feature branch

```bash
git checkout -b feature/my-feature
```

### Before committing

```bash
npm run lint
npm run format:check:site
```

### Commit (triggers pre-commit hook)

```bash
git add .
git commit -m "feat: add my feature"
```

### Push (triggers pre-push hook)

```bash
git push origin feature/my-feature
```

### Create Pull Request

1. Go to GitHub: https://github.com/DTMBX/EVIDENT
2. Click "New Pull Request"
3. Select your branch
4. Add description
5. Submit

### After merge

```bash
git checkout main
git pull origin main
```

## Resources

- [Node.js LTS](https://nodejs.org/en/)
- [Ruby 3.3 Documentation](https://www.ruby-lang.org/en/documentation/)
- [11ty Guide](https://www.11ty.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [PostCSS Documentation](https://postcss.org/)
- [npm Commands](https://docs.npmjs.com/cli/v8/commands)

## Support

For issues:

1. Check existing GitHub issues
2. Review error messages carefully
3. Create detailed bug report with:
   - OS/Node/Ruby/npm versions
   - Reproduction steps
   - Error output
   - Environment variables
