# Evident Platform - Getting Started Today

## Quick Start (5 minutes)

### 1. Start the Application

```powershell
# In PowerShell, navigate to the project directory
cd C:\web-dev\github-repos\Evident.info

# Run the startup script
.\START.ps1
```

**OR use this one-liner:**

```powershell
cd C:\web-dev\github-repos\Evident.info; python app.py
```

The app will start at: **http://localhost:5000**

### 2. Login Credentials

**Admin Account (Full Access):**

- Email: `admin@Evident.info`
- Password: `Admin123!`

**Test User Account (Free Tier):**

- Email: `test@Evident.info`
- Password: `Password123!`

### 3. Access the Platform

Open your browser and go to:

- **Login Page:** http://localhost:5000/auth/login
- **Dashboard:** http://localhost:5000/dashboard (after login)
- **Home:** http://localhost:5000

## What You Can Do Today

### ✅ Authentication System

- Login/logout with test credentials
- Session management working
- Password authentication verified

### ✅ Dashboard Access

- BWC Dashboard at `/bwc-dashboard`
- Main Dashboard at `/dashboard`
- Evidence Dashboard at `/evidence/dashboard`

### ✅ Legal Retrieval System (NEW!)

**Ingest a legal document:**

```python
# In Python console or script
from legal_library_adapter import LegalLibraryAdapter

adapter = LegalLibraryAdapter()
doc_id = adapter.ingest_text_document(
    text="""
    The Fourth Amendment protects against unreasonable searches and seizures.
    A warrant must be supported by probable cause.
    """,
    filename="fourth_amendment.txt",
    source_system="legal_library",
    document_type="statute"
)
print(f"✓ Ingested: {doc_id}")
```

**Search for legal passages:**

```python
from retrieval_service import RetrievalService

service = RetrievalService()
passages = service.retrieve(query="search warrant", top_k=5)

for p in passages:
    print(f"Document: {p.filename}")
    print(f"Page: {p.page_number}")
    print(f"Snippet: {p.snippet[:100]}...")
```

**Use the CLI:**

```bash
# Retrieve passages
python -m pipeline.cli retrieve "search warrant" -top 3
```

> Note: The CLI currently supports `retrieve` only.

## Frontend Interface Actions (Quick Wins)

### Core UI Pages

- Login: http://localhost:5000/auth/login
- Dashboard: http://localhost:5000/dashboard
- BWC Dashboard: http://localhost:5000/bwc-dashboard
- Evidence Dashboard: http://localhost:5000/evidence/dashboard
- Enhanced Chat UI: http://localhost:5000/chat

### Frontend Checks

- Hard refresh (clear cache): Ctrl + Shift + R
- Open DevTools console: F12
- Network tab: confirm no 404s for CSS/JS assets
- Responsive view: toggle device toolbar in DevTools

## Testing the Full Stack

### Test Login Flow

1. Go to http://localhost:5000/auth/login
2. Login with `test@Evident.info` / `Password123!`
3. You should be redirected to the dashboard
4. Check browser console (F12) - should be no JavaScript errors

### Test Retrieval System

```python
# Run this to ingest sample data
python -c "
from legal_library_adapter import LegalLibraryAdapter

adapter = LegalLibraryAdapter()

# Sample legal text
legal_text = '''
Miranda v. Arizona established that suspects must be informed of their rights.
These include the right to remain silent and the right to an attorney.

Terry v. Ohio allows brief investigatory stops based on reasonable suspicion.
The officer may conduct a limited search for weapons if they believe the
person is armed and dangerous.

Probable cause is required for a search warrant. It must be based on facts
and circumstances that would lead a reasonable person to believe evidence
of a crime will be found.
'''

doc_id = adapter.ingest_text_document(
    text=legal_text,
    filename='criminal_law_basics.txt',
    source_system='legal_library',
    document_type='case_law',
    metadata={'topic': 'Criminal Procedure'}
)

print(f'✓ Sample document ingested: {doc_id}')
"

# Now test retrieval
python -m pipeline.cli retrieve "Miranda rights attorney" -top 2
```

### Test Municipal Codes

```python
from municipal_code_service import MunicipalCodeService

service = MunicipalCodeService()

# Seed Atlantic County
service.seed_core_counties({
    "Atlantic": ["Atlantic City", "Galloway", "Egg Harbor Township"]
})

# Add a test ordinance
source = service.ensure_source("Atlantic", "Atlantic City")
service.upsert_section(
    source_id=source.id,
    section_citation="§ 222-36",
    title="Body-worn cameras required",
    text="All law enforcement officers shall wear body-worn cameras during public interactions."
)

# Search
results = service.search("body camera", county="Atlantic")
print(f"Found {len(results)} ordinances")
```

## Troubleshooting

### App won't start

```powershell
# Check if port 5000 is in use
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

# Kill any Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Try again
python app.py
```

### Can't login

```powershell
# Reset passwords
python -c "
from app import app
from models_auth import db, User

with app.app_context():
    admin = User.query.filter_by(email='admin@Evident.info').first()
    admin.set_password('Admin123!')

    test = User.query.filter_by(email='test@Evident.info').first()
    test.set_password('Password123!')

    db.session.commit()
    print('✓ Passwords reset')
"
```

## 🔐 Required Security Step (Daily)

Before commits/pushes:

```powershell
# Ensure hooks are active
python scripts/security/validate_encryption.py

# Generate local key if missing
python scripts/security/generate_key.py
```

### JavaScript errors in browser

- Hard refresh: Ctrl + Shift + R (clears cached JS files)
- Check browser console (F12) for specific errors
- All three JS files should load:
  - `/static/js/toast-notifications.js`
  - `/static/js/loading-states.js`
  - `/static/js/form-validation.js`

### Database issues

```powershell
# Check database exists
Test-Path instance\Evident_FRESH.db

# Recreate if needed
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Check legal retrieval DB
Test-Path instance\Evident_legal.db

# Initialize if missing
python scripts\db\init_db.py
```

## Available Endpoints

After logging in, you can access:

- `/dashboard` - Main dashboard
- `/bwc-dashboard` - BWC forensic analysis
- `/evidence/dashboard` - Evidence processing
- `/pricing` - View pricing tiers
- `/api/legal-library/documents` - Legal library API (if implemented)

## Next Steps After Login

1. **Explore the Dashboard**
   - Check what features are available
   - Test navigation

2. **Upload Test Data**
   - Use BWC dashboard to upload video files
   - Use legal library to ingest documents

3. **Test Retrieval**
   - Run queries against ingested documents
   - Verify citation tracking works

4. **Check Integration**
   - Test if ChatGPT integration can access retrieved passages
   - Verify SOURCES block appears in prompts

## Production Checklist

Before deploying:

- [ ] Set `SECRET_KEY` environment variable
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper logging
- [ ] Set up backup strategy

## Quick Commands Reference

```powershell
# Start app
python app.py

# Run tests
python -m pytest tests\test_unified_retrieval.py -v

# Check login flow
python test_login_integration.py

# Reset passwords
python -c "from app import app; from models_auth import db, User; ..."

# CLI retrieval
python -m pipeline.cli retrieve "query" -top 5

# Initialize databases
python scripts\db\init_db.py
```

## Support Files

- `LOGIN-FIXES-COMPLETE.md` - Login system documentation
- `UNIFIED-RETRIEVAL-COMPLETE.md` - Retrieval system details
- `RETRIEVAL-QUICK-START.md` - Retrieval API reference
- `START.ps1` - Quick startup script

--

**You're ready to use Evident today!** 🚀

Start with: `.\START.ps1` or `python app.py` Then login at:
http://localhost:5000/auth/login
