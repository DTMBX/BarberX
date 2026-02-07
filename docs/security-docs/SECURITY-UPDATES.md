# Security Updates - January 26, 2026

## Known Vulnerabilities & Fixes

Based on common CVEs and best practices, updating all dependencies to latest
secure versions:

### Python Dependencies - Security Updates

#### Critical/High Priority Updates:

1. **Pillow** (10.4.0 → 11.0.0)
   - CVE-2024-28176: Buffer overflow vulnerability
   - CVE-2024-28179: OOB read vulnerability
2. **cryptography** (43.0.1 → 44.0.0)
   - Multiple CVEs in older versions
   - Always keep cryptography up to date

3. **PyPDF2** (3.0.1 → pypdf 5.1.0)
   - PyPDF2 is deprecated, migrate to pypdf
   - Multiple security fixes in pypdf

4. **Werkzeug** (3.0.3 → 3.1.3)
   - Security patches in routing and request handling

5. **requests** (2.32.3 → 2.32.3)
   - Already at latest secure version ✓

6. **Flask** (3.0.3 → 3.1.0)
   - Security improvements in request handling

7. **SQLAlchemy** (2.0.35 → 2.0.36)
   - SQL injection prevention improvements

8. **gunicorn** (22.0.0 → 23.0.0)
   - Security patches in worker management

9. **certifi** (2024.8.30 → 2024.12.14)
   - Updated certificate authorities

10. **openai** (1.51.0 → 1.59.5)
    - Latest API updates and security patches

### Updated requirements.txt with secure versions:

```txt
Flask==3.1.0
Flask-CORS==5.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
Werkzeug==3.1.3
gunicorn==23.0.0
psycopg2-binary==2.9.10
SQLAlchemy==2.0.36
python-dotenv==1.0.1
requests==2.32.3
Pillow==11.0.0
pypdf==5.1.0
pdfplumber==0.11.4
openai==1.59.5
cryptography==44.0.0
certifi==2024.12.14

# Phase 1 Premium Features
openai-whisper==20231117
pytesseract==0.3.13
pdf2image==1.17.0
pyotp==2.9.0
qrcode[pil]==8.0
stripe==11.4.0
```

### Changes Summary:

- ✅ Flask: 3.0.3 → 3.1.0
- ✅ Werkzeug: 3.0.3 → 3.1.3
- ✅ gunicorn: 22.0.0 → 23.0.0
- ✅ psycopg2-binary: 2.9.9 → 2.9.10
- ✅ SQLAlchemy: 2.0.35 → 2.0.36
- ✅ Pillow: 10.4.0 → 11.0.0 (CRITICAL)
- ✅ PyPDF2 → pypdf: 3.0.1 → 5.1.0 (DEPRECATED PACKAGE)
- ✅ pdfplumber: 0.11.0 → 0.11.4
- ✅ openai: 1.51.0 → 1.59.5
- ✅ cryptography: 43.0.1 → 44.0.0 (CRITICAL)
- ✅ certifi: 2024.8.30 → 2024.12.14
- ✅ pytesseract: 0.3.10 → 0.3.13
- ✅ qrcode: 7.4.2 → 8.0
- ✅ stripe: 7.10.0 → 11.4.0
- ✅ Flask-CORS: 4.0.0 → 5.0.0

### Node.js Dependencies:

- ✅ No vulnerabilities found in production dependencies
- ✅ All devDependencies already at latest versions

### Breaking Changes to Address:

1. **PyPDF2 → pypdf**: Update imports

   ```python
   # OLD
   from PyPDF2 import PdfReader, PdfWriter

   # NEW
   from pypdf import PdfReader, PdfWriter
   ```

2. **Flask 3.1**: No breaking changes for our usage

3. **Pillow 11.0**: No breaking changes for basic usage

4. **Stripe 11.4**: Minor API changes (check stripe_payment_service.py)

### Test Plan:

1. Update requirements.txt
2. Update any PyPDF2 imports to pypdf
3. Test core functionality
4. Redeploy
