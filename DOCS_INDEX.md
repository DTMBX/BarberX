# 📚 Documentation Index

Complete documentation for the Geneva Bible Study Platform.

## 🚀 Getting Started

New to the project? Start here:

1. **[README.md](./README.md)** - Project overview, quick start, and key features
2. **[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** - ⚡ 5-minute deployment guide
3. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - How to deploy to various platforms
4. **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Guidelines for contributing code

## 📦 Deployment Documentation

### Quick Start
- **[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** - Fast deployment in 5 minutes ⚡
- **[GITHUB_PAGES_DEPLOYMENT.md](./GITHUB_PAGES_DEPLOYMENT.md)** - Complete GitHub Pages guide
- **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Comprehensive checklist

### Setup Scripts
- `setup-github-pages.sh` - Automated setup (Linux/Mac)
- `setup-github-pages.bat` - Automated setup (Windows)

## 📖 Core Documentation

### User Documentation

- **[PRD.md](./PRD.md)** - Complete product requirements document
  - Feature specifications
  - Design direction and rationale
  - User experience flows
  - Component selections

### Technical Documentation

- **[BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md)** - Bible API integration guide
  - API endpoints and usage
  - React hooks documentation
  - Caching strategy
  - Code examples

- **[THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md)** - License information
  - All dependency licenses
  - Compliance checklist
  - Attribution requirements
  - License verification methods

### Development Documentation

- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Developer guide
  - Code standards and conventions
  - Component guidelines
  - Testing procedures
  - Pull request process

- **[CHANGELOG.md](./CHANGELOG.md)** - Version history
  - Release notes
  - Feature additions
  - Breaking changes
  - Migration guides

- **[LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md)** - Performance testing guide
  - Automated performance audits
  - CI/CD integration
  - Score interpretation
  - Optimization recommendations

- **[LIGHTHOUSE_QUICK_REF.md](./LIGHTHOUSE_QUICK_REF.md)** - Quick reference
  - Common commands
  - Score thresholds
  - Troubleshooting guide
  - Quick wins

### Deployment Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Comprehensive deployment guide
  - GitHub Pages (automated)
  - Vercel, Netlify, Firebase
  - AWS S3 + CloudFront
  - Docker deployment
  - Self-hosted options

### Security Documentation

- **[SECURITY_POLICY.md](./SECURITY_POLICY.md)** - Security guidelines
  - Vulnerability reporting
  - Security measures
  - Best practices
  - Deployment checklist

## 🎯 Quick Reference

### Common Tasks

| Task | Documentation | Location |
|------|---------------|----------|
| Install and run locally | [README.md](./README.md) | Quick Start section |
| Deploy to GitHub Pages | [DEPLOYMENT.md](./DEPLOYMENT.md) | GitHub Pages section |
| Run performance tests | [LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md) | Usage section |
| Use Bible API | [BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md) | Usage Examples section |
| Add new feature | [CONTRIBUTING.md](./CONTRIBUTING.md) | Development Workflow section |
| Check licenses | [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) | Summary section |
| Report security issue | [SECURITY_POLICY.md](./SECURITY_POLICY.md) | Reporting section |

### Key Commands

```bash
# Development
npm install          # Install dependencies
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Quality
npm run lint         # Run linter
npm audit            # Check for vulnerabilities

# Performance Testing
lhci autorun         # Run Lighthouse CI locally
npm run preview      # Required for Lighthouse tests

# Deployment
git push origin main # Trigger GitHub Actions deployment
```

## 📂 Repository Structure

```
.
├── src/                      # Source code
│   ├── components/          # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── reader/         # Bible reader components
│   │   ├── social/         # Social features
│   │   ├── timeline/       # Timeline components
│   │   └── views/          # Main view components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities and data
│   │   ├── bibleApi.ts    # API integration
│   │   ├── data.ts        # Static data
│   │   ├── types.ts       # TypeScript types
│   │   └── utils.ts       # Helper functions
│   ├── styles/             # CSS and themes
│   ├── App.tsx             # Main application
│   ├── index.css           # Global styles
│   └── main.tsx            # Entry point
├── .github/
│   └── workflows/          # GitHub Actions
│       ├── deploy.yml      # Deployment workflow
│       ├── lighthouse-ci.yml      # Performance testing (PR)
│       └── lighthouse-full.yml    # Full audit (weekly)
├── public/                 # Static assets
├── Documentation files:
│   ├── README.md           # Project overview
│   ├── PRD.md              # Product requirements
│   ├── BIBLE_API_INTEGRATION.md  # API docs
│   ├── DEPLOYMENT.md       # Deployment guide
│   ├── CONTRIBUTING.md     # Developer guide
│   ├── LIGHTHOUSE_CI.md    # Performance testing
│   ├── LIGHTHOUSE_QUICK_REF.md   # Quick reference
│   ├── THIRD_PARTY_LICENSES.md   # License info
│   ├── SECURITY_POLICY.md  # Security guidelines
│   ├── CHANGELOG.md        # Version history
│   └── DOCS_INDEX.md       # This file
├── Configuration files:
│   ├── package.json        # Dependencies
│   ├── tsconfig.json       # TypeScript config
│   ├── vite.config.ts      # Vite config
│   ├── tailwind.config.js  # Tailwind config
│   ├── lighthouserc.json   # Lighthouse desktop config
│   ├── lighthouserc.mobile.json  # Lighthouse mobile config
│   ├── performance-budget.json   # Performance budgets
│   └── .gitignore          # Git ignore rules
└── LICENSE                 # MIT License

```

## 🔍 Finding Information

### By Topic

**Setup & Installation**
- Local development → [README.md](./README.md)
- Production build → [DEPLOYMENT.md](./DEPLOYMENT.md)
- Environment configuration → [DEPLOYMENT.md](./DEPLOYMENT.md)

**Features & Functionality**
- Feature list → [README.md](./README.md) or [PRD.md](./PRD.md)
- User flows → [PRD.md](./PRD.md)
- API integration → [BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md)

**Development**
- Code standards → [CONTRIBUTING.md](./CONTRIBUTING.md)
- Component structure → [CONTRIBUTING.md](./CONTRIBUTING.md)
- Pull requests → [CONTRIBUTING.md](./CONTRIBUTING.md)
- TypeScript types → `src/lib/types.ts`
- Performance testing → [LIGHTHOUSE_CI.md](./LIGHTHOUSE_CI.md)
- Quick commands → [LIGHTHOUSE_QUICK_REF.md](./LIGHTHOUSE_QUICK_REF.md)

**Deployment**
- GitHub Pages → [DEPLOYMENT.md](./DEPLOYMENT.md)
- Other platforms → [DEPLOYMENT.md](./DEPLOYMENT.md)
- Docker → [DEPLOYMENT.md](./DEPLOYMENT.md)

**Legal & Compliance**
- Project license → [LICENSE](./LICENSE)
- Dependency licenses → [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md)
- Security policy → [SECURITY_POLICY.md](./SECURITY_POLICY.md)

**Updates & Changes**
- Version history → [CHANGELOG.md](./CHANGELOG.md)
- Breaking changes → [CHANGELOG.md](./CHANGELOG.md)
- Planned features → [CHANGELOG.md](./CHANGELOG.md)

## 💡 Tips

### For New Users

1. Read [README.md](./README.md) for project overview
2. Review [PRD.md](./PRD.md) to understand features
3. Follow [DEPLOYMENT.md](./DEPLOYMENT.md) to deploy

### For Developers

1. Start with [CONTRIBUTING.md](./CONTRIBUTING.md)
2. Review code in `src/` directory
3. Check [BIBLE_API_INTEGRATION.md](./BIBLE_API_INTEGRATION.md) for API usage
4. Run `npm run dev` and explore

### For Administrators

1. Review [SECURITY_POLICY.md](./SECURITY_POLICY.md)
2. Read [DEPLOYMENT.md](./DEPLOYMENT.md) deployment checklist
3. Check [THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) for compliance
4. Monitor [CHANGELOG.md](./CHANGELOG.md) for updates

## 🆘 Getting Help

### Documentation Issues

If documentation is unclear or incomplete:
1. Open an issue on GitHub with `documentation` label
2. Suggest improvements via pull request
3. Ask in GitHub Discussions

### Technical Support

- **Bug reports:** GitHub Issues
- **Feature requests:** GitHub Discussions
- **Security issues:** See [SECURITY_POLICY.md](./SECURITY_POLICY.md)
- **General questions:** GitHub Discussions

## 📝 Contributing to Documentation

Documentation improvements are welcome! When updating docs:

1. Keep language clear and concise
2. Include code examples where helpful
3. Update this index if adding new docs
4. Follow existing formatting conventions
5. Test all commands and instructions

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📅 Documentation Updates

Documentation is updated with each release. Check:

- **CHANGELOG.md** for version-specific changes
- **README.md** for feature updates
- **PRD.md** for design decisions
- **BIBLE_API_INTEGRATION.md** for API changes

Last updated: January 2025

---

**Need something not listed here?** Open an issue or discussion on GitHub!
