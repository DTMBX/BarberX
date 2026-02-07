# Evident Backend

Privacy-first legal AI platform backend API.

**Requires:** Python >= 3.12

## Structure

```
Evident-Backend/
├── src/               # Main application source
│   ├── app.py         # Flask application entry point
│   ├── *_routes.py    # API route handlers
│   └── *_service.py   # Business logic services
├── api/               # API definitions
├── models/            # Database models
├── services/          # External service integrations
├── tests/             # Test suite
├── templates/         # Jinja2 templates (for admin/emails)
├── static/            # Static assets for backend
├── barber-cam/        # Body-worn camera analysis module
├── scripts/           # Deployment & utility scripts
└── tools/             # Development tools
```

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\Activate.ps1` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.template .env
# Edit .env with your values

# Run development server
python src/app.py
```

## Running Tests (recommended isolated venv)

We recommend running tests in an isolated virtual environment to avoid interfering with developer or CI environments.

Windows (PowerShell):

```powershell
py -3 -m venv .venv_test
.venv_test\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q backend/tests
```

Unix / macOS:

```bash
python -m venv .venv_test
source .venv_test/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q backend/tests
```

Notes:
- The backend `requirements.txt` now includes `numpy` which is required by the audio sync tests and `bwc_sync` utilities.
- If you encounter issues with the system `.venv`, create a fresh `.venv_test` as above.

## Environment Variables

See `.env.template` for required configuration.

## Deployment

- **Railway**: `railway up`
- **Render**: Push to main branch (auto-deploy)
- **Docker**: `docker-compose -f docker-compose.enterprise.yml up`

## Related Repositories

- [Evident.info](https://github.com/DTB396/Evident.info) - Marketing website
  (Jekyll/GitHub Pages)
