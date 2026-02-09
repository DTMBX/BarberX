# Contributing to EVIDENT

Thank you for your interest in contributing to EVIDENT! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to a Code of Conduct to ensure a welcoming and inclusive environment. Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

## Getting Started

### Prerequisites

- Git
- Python 3.12+
- Node.js 20+
- Ruby 2.7+
- Docker (optional)

### Setup Development Environment

**Windows:**

```powershell
.\infrastructure\scripts\setup.ps1
```

**macOS/Linux:**

```bash
./infrastructure/scripts/setup.sh
```

### Repository Structure

The project is organized as follows:

- **`src/backend/`** - Flask backend application
- **`src/frontend/`** - Frontend applications (web, windows, mobile)
- **`src/static/`** - Static assets (CSS, JS, images)
- **`src/templates/`** - HTML templates
- **`tests/`** - Test suites (unit, integration, e2e)
- **`docs/`** - Project documentation
- **`infrastructure/`** - DevOps and deployment files
- **`.config/`** - Tool configurations

See [REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) for detailed structure information.

## Development Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name g8-pages
```

Branch naming conventions:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code cleanup
- `test/` - Test improvements
- `chore/` - Build, deps, automation

### 2. Make Your Changes

**Backend changes:**

```bash
cd src/backend
# Edit files, add tests
pytest tests/unit/backend/
```

**Frontend changes:**

```bash
cd src/frontend/web
# Edit files, add tests
npm test
```

**Documentation:**

```bash
# Edit docs in docs/ directory
# Use markdown format
```

### 3. Follow Code Standards

#### Python (Backend)

```bash
# Run linting
pylint src/backend/**/*.py

# Format code
black src/backend/

# Type checking
mypy src/backend/
```

#### JavaScript/TypeScript (Frontend)

```bash
# Run linting
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

#### Configuration Files

All tool configurations are in `.config/`:

- `.config/.eslintrc.cjs` - ESLint rules
- `.config/.prettierrc.json` - Formatting
- `.config/.stylelintrc.cjs` - CSS linting
- `.config/pytest.ini` - Python testing

### 4. Write Tests

Place tests in appropriate `tests/` subdirectories:

```bash
# Unit tests for backend
tests/unit/backend/test_models.py
tests/unit/backend/test_services.py

# Integration tests
tests/integration/test_api_endpoints.py

# E2E tests
tests/e2e/test_workflows.py
```

Run all tests:

```bash
pytest tests/ -v
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "type(scope): description

- Detailed explanation
- Multiple bullet points if needed
"
```

**Commit types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting, no code changes
- `refactor:` - Code restructuring
- `test:` - Test additions
- `chore:` - Build, dependencies, automation

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- Clear title describing the change
- Description of what was changed and why
- Reference to related issues (#123)
- Screenshots/demos if applicable
- Checklist items completed

## Pull Request Guidelines

Your PR should:

- [ ] Have a descriptive title
- [ ] Reference related issues
- [ ] Include description of changes
- [ ] Pass all CI/CD checks
- [ ] Have tests with 80%+ coverage
- [ ] Update documentation if needed
- [ ] Follow code style guidelines
- [ ] Have clear, logical commit history

**Example PR Template:**

```markdown
## Description

Brief description of changes

## Related Issues

Fixes #123

## Changes

- Change 1
- Change 2
- Change 3

## Testing

How to test these changes:

1. Step 1
2. Step 2

## Screenshots (if applicable)

[Add screenshots if UI changes]

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] All CI checks passing
```

## Code Review Process

1. **Automated Checks** - CI/CD pipeline runs automatically
2. **Manual Review** - Core team reviews code
3. **Feedback** - Changes may be requested
4. **Approval** - PR is approved after feedback is addressed
5. **Merge** - PR is merged into main branch

## Performance Guidelines

### Backend (Python)

- Optimize database queries
- Cache frequently accessed data
- Use async patterns for I/O operations
- Profile code for bottlenecks

### Frontend (JavaScript)

- Minimize bundle size
- Optimize images
- Lazy load components
- Use performance budgets

### General

- Monitor build time impact
- Test on target hardware
- Document performance implications

## Security Guidelines

1. **Never commit secrets** - Use `.env` files, never commit keys
2. **Validate input** - Sanitize all user input
3. **Use HTTPS** - Always use secure connections
4. **Dependencies** - Keep dependencies up to date
5. **Report vulnerabilities** - See [SECURITY.md](SECURITY.md)

## Documentation

When adding features:

- Add docstrings to functions/classes
- Update relevant documentation files
- Add examples if applicable
- Document API changes
- Update CHANGELOG.md

## Getting Help

- **Questions?** Open a Discussion on GitHub
- **Found a bug?** Open an Issue with details
- **Need guidance?** Check existing documentation
- **Community Discord** - [Link if available]

## Recognition

Contributors are recognized in:

- CONTRIBUTORS.md
- Release notes for significant contributions
- GitHub contributors page

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for contributing to EVIDENT! 🙏

For questions, please open a GitHub issue or discussion.
