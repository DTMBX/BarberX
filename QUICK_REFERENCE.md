# EVIDENT Repository - Quick Reference

## 🚀 Quick Start

```bash
# Setup Development Environment
./infrastructure/scripts/setup.ps1  # Windows
./infrastructure/scripts/setup.sh   # Unix

# Install Dependencies
pip install -r requirements.txt
npm install
```

## 📂 Directory Quick Links

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `src/backend/` | Python/Flask app | `app.py`, `app_config.py` |
| `src/frontend/` | Web, Windows, Mobile | `package.json`, component files |
| `src/static/` | CSS, JS, images | compiled assets |
| `src/templates/` | HTML templates | chat, legal-library |
| `tests/` | Test suites | unit, integration, e2e |
| `docs/` | Documentation | API, architecture, guides |
| `infrastructure/` | DevOps configs | Docker, K8s, Terraform |
| `.config/` | Tool configs | ESLint, pytest, etc |

## 🛠️ Common Tasks

### Backend Development
```bash
cd src/backend
python app.py
```

### Frontend Development
```bash
cd src/frontend/web
npm run dev
```

### Running Tests
```bash
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/               # All tests
```

### Build & Deploy
```bash
./infrastructure/scripts/build.ps1  # Windows
./infrastructure/scripts/setup.sh   # Unix
```

## 📖 Documentation

- **REPOSITORY_STRUCTURE.md** - Complete structure guide
- **CONTRIBUTING.md** - Development workflow
- **docs/architecture/** - Architecture decisions
- **docs/api/** - API documentation
- **docs/deployment/** - Deployment guides

## 🔧 Configuration

All tool configurations in `.config/`:
- `.config/.eslintrc.cjs` - ESLint
- `.config/.prettierrc.json` - Prettier
- `.config/.stylelintrc.cjs` - Stylelint
- `.config/pytest.ini` - Pytest
- `.env.example` → copy to `.env` for local development

## 📌 Git Workflow

```bash
# Create feature branch
git checkout -b feature/description g8-pages

# Make changes and test
pytest tests/
npm run lint

# Commit
git commit -m "type: description"

# Push and create PR
git push origin feature/description
```

## 🌐 Repository

- **GitHub**: https://github.com/DTMBX/EVIDENT
- **Main Branch**: `g8-pages`
- **Development Branch**: Feature branches from `g8-pages`

## 📞 Support

1. Check **REPOSITORY_STRUCTURE.md** for navigation
2. Read **CONTRIBUTING.md** for development guidelines
3. Review **docs/** for technical documentation
4. Open GitHub issues for bugs/features

---

**✅ Repository is professionally organized and ready for production!**
