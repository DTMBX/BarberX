# Project Structure Guide

## Quick Navigation

### For Backend Development

- **Main App**: `src/backend/app.py`
- **Configuration**: `src/backend/app_config.py`
- **Routes**: `src/backend/routes/`
- **Services**: `src/backend/services/`
- **Models**: `src/backend/models/`
- **Tests**: `tests/unit/backend/`

### For Frontend Development

- **Web App**: `src/frontend/web/`
- **Windows App**: `src/frontend/windows/`
- **Mobile App**: `src/frontend/mobile/`
- **Static Assets**: `src/static/`
- **Templates**: `src/templates/`

### For Infrastructure

- **Docker**: `infrastructure/docker/`
- **Kubernetes**: `infrastructure/kubernetes/`
- **Terraform**: `infrastructure/terraform/`
- **Deploy Scripts**: `infrastructure/scripts/`
- **Configs**: `infrastructure/config/`

### For Documentation

- **Architecture**: `docs/architecture/`
- **API Docs**: `docs/api/`
- **Deployment Guide**: `docs/deployment/`
- **Development Guide**: `docs/development/`
- **User Guide**: `docs/user-guide/`

### Configuration Files

All config files organized in `.config/`:

- 💅 `.config/.eslintrc.cjs` - JavaScript linting
- 🎨 `.config/.prettierrc.json` - Code formatting
- 📋 `.config/.stylelintrc.cjs` - CSS linting
- ⚙️ `.config/pytest.ini` - Python testing

## Directory Structure Detail

```
src/
├── backend/                  # Python/Flask backend
│   ├── app.py               # Flask application entry
│   ├── app_config.py        # Configuration management
│   ├── auth/                # Authentication & authorization
│   ├── api/                 # RESTful API endpoints
│   ├── routes/              # Route blueprints
│   ├── services/            # Business logic layer
│   ├── models/              # Data models
│   ├── utils/               # Utility functions
│   └── __init__.py
│
├── frontend/
│   ├── web/                 # Next.js/React web app
│   ├── windows/             # .NET Windows client
│   ├── mobile/              # React Native/Flutter
│   └── components/          # Shared UI components
│
├── static/                  # Static web assets
│   ├── css/                 # Styles & compiled CSS
│   ├── js/                  # Client-side JavaScript
│   ├── images/              # Images & artwork
│   └── fonts/               # Custom fonts
│
└── templates/               # HTML templates
    ├── chat/                # Chat interface templates
    ├── legal-library/       # Legal document templates
    └── shared/              # Shared template components

tests/
├── unit/                    # Unit test suites
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
├── fixtures/                # Test data & fixtures
└── conftest.py              # Pytest configuration

docs/
├── api/                     # API documentation
│   ├── endpoints.md         # API endpoints
│   └── schemas.md           # Data schemas
├── architecture/            # Architecture docs
│   ├── overview.md
│   └── deployment.md
├── deployment/              # Deployment guides
├── development/             # Developer guides
└── user-guide/              # End-user documentation

infrastructure/
├── docker/                  # Docker configurations
│   ├── Dockerfile
│   └── docker-compose.yml
├── kubernetes/              # K8s manifests
├── terraform/               # Infrastructure as Code
├── scripts/                 # Setup & deployment scripts
└── config/                  # Environment configs

.config/                    # All tool configurations
├── .eslintrc.cjs
├── .prettierrc.json
├── .stylelintrc.cjs
├── pytest.ini
├── .env.example
└── ... (15+ config files)
```

## Development Workflow

1. **Clone Repository**

   ```bash
   git clone https://github.com/DTMBX/EVIDENT.git
   cd EVIDENT
   ```

2. **Setup Environment**

   ```bash
   # Windows
   .\infrastructure\scripts\setup.ps1

   # Unix
   ./infrastructure/scripts/setup.sh
   ```

3. **Backend Development**

   ```bash
   cd src/backend
   pip install -r ../../requirements.txt
   python app.py
   ```

4. **Frontend Development**

   ```bash
   cd src/frontend/web
   npm install
   npm run dev
   ```

5. **Running Tests**

   ```bash
   # Unit tests
   pytest tests/unit/

   # Integration tests
   pytest tests/integration/

   # All tests
   pytest tests/
   ```

6. **Building**

   ```bash
   # Using provided script
   .\infrastructure\scripts\build.ps1

   # Or manually
   npm run build
   ```

## Important Files at Root

- **README.md** - Project overview
- **LICENSE** - License file
- **CONTRIBUTING.md** - Contribution guidelines
- **SECURITY.md** - Security policy
- **CODE_OF_CONDUCT.md** - Code of conduct
- **CHANGELOG.md** - Version history
- **package.json** - Node dependencies
- **requirements.txt** - Python dependencies
- **pyproject.toml** - Python project config
- **Gemfile** - Ruby dependencies
- **tailwind.config.cjs** - Tailwind configuration
- **postcss.config.cjs** - PostCSS configuration

## Git Workflow

1. **Create feature branch**

   ```bash
   git checkout -b feature/description g8-pages
   ```

2. **Make changes**
   - Follow structure guidelines
   - Add tests in corresponding `tests/` directory
   - Update documentation in `docs/`

3. **Commit and push**

   ```bash
   git add .
   git commit -m "type: description"
   git push origin feature/description
   ```

4. **Create Pull Request**
   - Reference issue numbers
   - Include description of changes
   - Ensure all tests pass

## Configuration Management

All configuration files are now centralized in `.config/`:

```bash
# Update tool configs
.config/.eslintrc.cjs          # Edit ESLint rules
.config/.prettierrc.json       # Edit formatting
.config/.stylelintrc.cjs       # Edit CSS rules
.config/pytest.ini             # Edit test config

# Copy templates for local development
.config/.env.example → .env    # Create local .env
```

## Next Steps

1. Update CI/CD workflows to reference new paths
2. Update import statements in code files
3. Create `.gitignore` entries for new structure
4. Document any path changes in CHANGELOG
5. Update deployment documentation

---

**Last Updated**: Feb 9, 2026
**Repository**: https://github.com/DTMBX/EVIDENT
