# Evident Backend

Privacy-first legal AI platform backend API.

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

## Environment Variables

See `.env.template` for required configuration.

## Deployment

- **Railway**: `railway up`
- **Render**: Push to main branch (auto-deploy)
- **Docker**: `docker-compose -f docker-compose.enterprise.yml up`

## Related Repositories

- [Evident.info](https://github.com/DTB396/Evident.info) - Marketing website
  (Jekyll/GitHub Pages)
