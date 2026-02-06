# ⚡ COPYRIGHT COMPLIANCE - ACTION CHECKLIST

**Print this page and check off as you complete each step**

--

## 📋 TODAY - CRITICAL BLOCKERS (2-4 hours)

### ☐ Step 1: Create Database Tables (5 minutes)

```bash
cd c:\web-dev\github-repos\Evident.info
python models_data_rights.py
```

**Expected Output:**

```
✅ Data rights compliance tables created
```

**Verify in database:**

- [ ] `data_sources` table exists
- [ ] `citation_metadata` table exists
- [ ] `public_case_data` table exists
- [ ] `proprietary_source_data` table exists
- [ ] `export_manifests` table exists
- [ ] `material_inventory` table exists

--

### ☐ Step 2: Test Compliance Module (5 minutes)

```bash
python integration_example.py
```

**Expected Results:**

- [ ] ✅ BWC footage included in export
- [ ] ✅ AI transcript included in export
- [ ] ❌ Westlaw content blocked
- [ ] ❌ Police report full text blocked
- [ ] Manifest file created in `exports/` directory

--

### ☐ Step 3: Integrate into app.py (1-2 hours)

**Add imports at top of app.py:**

```python
from data_rights import RightsAwareExport, Material, RIGHTS_PROFILES, ExportViolation
from models_data_rights import (
    DataSource, CitationMetadata, PublicCaseData,
    ProprietarySourceData, ExportManifest, MaterialInventory
)
```

**Update PDF export function:**

```python
@app.route('/api/export/<analysis_id>/pdf', methods=['POST'])
@login_required
def export_pdf(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)

    # Create rights-aware export
    export = RightsAwareExport(
        case_number=analysis.case_number,
        export_type="discovery_production"
    )

    # Add BWC video
    bwc_material = Material(
        filename=analysis.filename,
        category="bwc_videos",
        rights=RIGHTS_PROFILES["opra_bwc"],
        file_path=Path(analysis.file_path),
        acquired_by=current_user.full_name
    )
    export.add_material(bwc_material)

    # Add transcript if exists
    if analysis.report_json_path:
        transcript_material = Material(
            filename=f"{analysis.case_number}_transcript.pdf",
            category="transcripts",
            rights=RIGHTS_PROFILES["our_transcript"]
        )
        export.add_material(transcript_material)

    # Finalize export
    export_path = export.finalize_export(
        certifying_attorney=current_user.full_name,
        attorney_bar_number=request.form.get('bar_number', 'Unknown'),
        export_directory=Path('./exports')
    )

    # Return PDF
    return send_file(export_path / 'export.pdf')
```

**Checklist:**

- [ ] Imports added to app.py
- [ ] Export function updated
- [ ] Test export route works
- [ ] Verify manifest generated

--

### ☐ Step 4: Update bwc_forensic_analyzer.py (30 minutes)

**Add at top of file:**

```python
from data_rights import Material, RIGHTS_PROFILES, DataRights, SourceType
from models_data_rights import MaterialInventory, DataSource
```

**Update transcript generation:**

```python
def generate_transcript(self, bwc_video_path):
    # Existing transcription code...

    # Track transcript as our work product
    transcript_material = MaterialInventory(
        id=str(uuid.uuid4()),
        filename=f"{case_number}_transcript.json",
        category="transcripts",
        data_source_id=self._get_or_create_data_source("our_transcript").id,
        owner_user_id=self.user_id,
        case_number=case_number
    )
    db.session.add(transcript_material)
    db.session.commit()
```

**Checklist:**

- [ ] Imports added
- [ ] Transcript tracking added
- [ ] Test analysis generates MaterialInventory records

--

## 📋 THIS WEEK - SECURITY (4-8 hours)

### ☐ Step 5: Configure Environment Variables (30 minutes)

**Create `.env` file:**

```bash
SECRET_KEY=generate-256-bit-random-key-here
DATABASE_URL=postgresql://user:pass@localhost/Evident_legal
STRIPE_API_KEY=sk_live_...
```

**Update app.py:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
```

**Generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Checklist:**

- [ ] `.env` file created
- [ ] SECRET_KEY generated (256-bit)
- [ ] app.py reads from environment
- [ ] Add `.env` to `.gitignore`

--

### ☐ Step 6: Migrate to PostgreSQL (2-3 hours)

**Install PostgreSQL:**

```bash
# Windows (via Chocolatey)
choco install postgresql

# Or download from: https://www.postgresql.org/download/
```

**Create database:**

```bash
psql -U postgres
CREATE DATABASE Evident_legal;
CREATE USER Evident WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE Evident_legal TO Evident;
```

**Update DATABASE_URL in `.env`:**

```
DATABASE_URL=postgresql://Evident:secure-password@localhost/Evident_legal
```

**Migrate data:**

```bash
# Export from SQLite
python migrate_to_postgres.py  # You'll need to create this script
```

**Checklist:**

- [ ] PostgreSQL installed
- [ ] Database created
- [ ] User/permissions configured
- [ ] DATABASE_URL updated
- [ ] Data migrated
- [ ] Verify app connects to PostgreSQL

--

### ☐ Step 7: Configure HTTPS/SSL (2 hours)

**For production server:**

```bash
# Install Certbot (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot -nginx -d Evident.info -d www.Evident.info
```

**For local development:**

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

**Update app.py for HTTPS:**

```python
if -name- == '-main-':
    app.run(
        host='0.0.0.0',
        port=443,
        ssl_context=('cert.pem', 'key.pem')
    )
```

**Checklist:**

- [ ] SSL certificate obtained
- [ ] HTTPS configured
- [ ] HTTP → HTTPS redirect
- [ ] Test HTTPS works
- [ ] Verify certificate valid

--

## 📋 BEFORE LAUNCH - TESTING (4-6 hours)

### ☐ Step 8: End-to-End Testing (2-3 hours)

**Test scenarios:**

- [ ] User registration works
- [ ] Login/logout works
- [ ] Upload BWC video (500MB test file)
- [ ] Upload BWC video (2GB test file) - Professional tier
- [ ] AI transcription completes successfully
- [ ] Entity extraction works
- [ ] Discrepancy detection finds issues
- [ ] Timeline generation creates JSON
- [ ] Export PDF includes only permitted materials
- [ ] Export PDF excludes Westlaw/Lexis content
- [ ] Manifest file generated correctly
- [ ] Attribution file readable

--

### ☐ Step 9: Copyright Compliance Testing (1 hour)

**Create test materials:**

```python
# Test 1: Verify Westlaw blocking
westlaw_test = Material(
    filename="westlaw_keycite.pdf",
    category="research",
    rights=RIGHTS_PROFILES["westlaw"]
)
# Expected: AUTO-EXCLUDED

# Test 2: Verify fair use limit
long_excerpt = Material(
    filename="police_report.pdf",
    category="documents",
    rights=RIGHTS_PROFILES["police_report"],
    content=" ".join(["word"] * 250),  # 250 words - exceeds limit
    is_excerpt=True
)
# Expected: ExportViolation raised

# Test 3: Verify OPRA allows export
bwc_test = Material(
    filename="bwc.mp4",
    category="bwc_videos",
    rights=RIGHTS_PROFILES["opra_bwc"]
)
# Expected: INCLUDED in export
```

**Checklist:**

- [ ] Westlaw content blocked
- [ ] Lexis content blocked
- [ ] 250-word excerpt blocked
- [ ] 200-word excerpt allowed
- [ ] OPRA BWC footage allowed
- [ ] Our transcripts allowed

--

### ☐ Step 10: Security Audit (1-2 hours)

**Run security checks:**

```bash
# Check for hardcoded secrets
grep -r "SECRET_KEY\|API_KEY\|PASSWORD" *.py

# Verify HTTPS enforced
curl -I http://Evident.info  # Should redirect to HTTPS

# Check file permissions
ls -la uploads/  # Should be 700 or 750

# Verify database encryption
psql -U Evident -c "SHOW ssl;"
```

**Checklist:**

- [ ] No hardcoded secrets in code
- [ ] HTTPS enforced (HTTP redirects)
- [ ] File permissions secure (not world-readable)
- [ ] Database uses SSL
- [ ] Session cookies marked secure
- [ ] CORS configured properly

--

## 📋 LAUNCH DAY - FINAL CHECKS (1 hour)

### ☐ Step 11: Pre-Launch Verification (30 minutes)

**Final checklist:**

- [ ] All database tables created
- [ ] Copyright compliance integrated
- [ ] Export blocking tested
- [ ] HTTPS working
- [ ] PostgreSQL configured
- [ ] Environment variables set
- [ ] Backup system configured
- [ ] Error logging working
- [ ] User registration tested
- [ ] Payment processing tested (if applicable)

--

### ☐ Step 12: Go Live (30 minutes)

**Deployment steps:**

1. [ ] Deploy to production server
2. [ ] Verify HTTPS certificate
3. [ ] Test user registration
4. [ ] Test BWC upload
5. [ ] Test export generation
6. [ ] Verify manifest creation
7. [ ] Check error logs
8. [ ] Monitor for 1 hour

**Post-launch monitoring:**

- [ ] Hour 1: Check logs every 15 minutes
- [ ] Day 1: Check logs every 2 hours
- [ ] Week 1: Daily log review
- [ ] Month 1: Weekly security audit

--

## ✅ SUCCESS CRITERIA

**You're production-ready when:**

- [x] Legal documents complete
- [x] Compliance code implemented
- [ ] Database tables created
- [ ] Export functions integrated
- [ ] SSL configured
- [ ] PostgreSQL migrated
- [ ] End-to-end tests passing
- [ ] Security audit clean

**Current Status:** \_\_\_% complete (check items above)

**Target Launch Date:** **\*\***\_\_\_\_**\*\***

**Launched Successfully:** ☐ YES ☐ NO

--

## 📞 EMERGENCY CONTACTS

**Copyright Violation Detected:**  
compliance@Evident.info (24-hour response)

**Security Incident:**  
security@Evident.info (immediate escalation)

**Technical Issues:**  
support@Evident.info (24-hour support)

**Legal Questions:**  
legal@Evident.info  
support@Evident.info

--

**Print Date:** **\*\***\_\_\_\_**\*\***  
**Completed By:** **\*\***\_\_\_\_**\*\***  
**Completion Date:** **\*\***\_\_\_\_**\*\***  
**Signature:** **\*\***\_\_\_\_**\*\***

--

**REMEMBER:** When in doubt about copyright, EXCLUDE IT.  
Better safe than a $150,000 lawsuit.
