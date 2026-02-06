# CourtListener API Setup - Complete Guide

**Status:** Code updated and ready. Just need API key!

--

## ✅ What I Just Did

### 1. Updated Code for API Authentication

- ✅ Modified `legal_library.py` - Added `Authorization` header support
- ✅ Modified `verified_legal_sources.py` - Added API key authentication
- ✅ Both files now read `COURTLISTENER_API_KEY` from environment
- ✅ Graceful fallback if key is missing (will warn instead of crash)

### 2. Code Changes Made

```python
# In legal_library.py (line 202-208):
headers = {}
api_key = os.getenv('COURTLISTENER_API_KEY')
if api_key:
    headers['Authorization'] = f'Token {api_key}'

response = requests.get(url, params=params, headers=headers)
```

```python
# In verified_legal_sources.py (similar pattern)
headers = {}
api_key = os.getenv('COURTLISTENER_API_KEY')
if api_key:
    headers['Authorization'] = f'Token {api_key}'
```

--

## 🚀 Setup Instructions

### Step 1: Get Your Free API Key (5 minutes)

1. **Visit:** https://www.courtlistener.com/sign-in/
2. **Create Account** (free)
3. **Get API Key:**
   - Go to: https://www.courtlistener.com/api/rest-info/
   - OR: Profile → API → "Get API Token"
4. **Copy your token** (looks like: `a1b2c3d4e5f6...`)

--

### Step 2: Add to Render (2 minutes)

**For Production (Render.com):**

1. Go to **https://dashboard.render.com**
2. Select your **Evident web service**
3. Click **"Environment"** (left sidebar)
4. Click **"Add Environment Variable"**
5. Enter:
   ```
   Key:   COURTLISTENER_API_KEY
   Value: <paste your API token here>
   ```
6. Click **"Save Changes"**
7. ✅ Render will auto-deploy in ~2 minutes

--

### Step 3: Add to Local Development (1 minute)

**For Local Testing:**

Create `.env` file in project root:

```bash
# .env
COURTLISTENER_API_KEY=your_api_token_here
```

Or set environment variable:

```powershell
# PowerShell (Windows)
$env:COURTLISTENER_API_KEY="your_api_token_here"

# Then run:
python overnight_library_builder.py -practice-area all
```

--

### Step 4: Test It! (2 minutes)

**Test locally:**

```powershell
cd C:\web-dev\github-repos\Evident.info
python overnight_library_builder.py -practice-area civil_rights -max-cases 3
```

**Expected output:**

```
[1/3] 384 U.S. 436 - Miranda v. Arizona
  [INFO] Attempting direct import anyway...
  [OK] Imported successfully (id: 1)

[2/3] 392 U.S. 1 - Terry v. Ohio
  [OK] Imported successfully (id: 2)

[3/3] 471 U.S. 1 - Tennessee v. Garner
  [OK] Imported successfully (id: 3)

SUCCESS RATE: 100%
Total cases in library: 3
```

--

## 📊 What Will Import

### Foundation Cases (27 total)

**Civil Rights (10 cases):**

- Miranda v. Arizona
- Terry v. Ohio
- Tennessee v. Garner
- Graham v. Connor
- Monell v. Dept of Social Services
- Payton v. New York
- Mapp v. Ohio
- Katz v. United States
- Chimel v. California
- United States v. Wade

**Criminal Defense (8 cases):**

- Gideon v. Wainwright
- Brady v. Maryland
- Batson v. Kentucky
- Giglio v. United States
- Kyles v. Whitley
- Strickland v. Washington
- Crawford v. Washington
- Berghuis v. Thompkins

**Employment Law (5 cases):**

- McDonnell Douglas v. Green
- Burlington Industries v. Ellerth
- Faragher v. City of Boca Raton
- Harris v. Forklift Systems
- Price Waterhouse v. Hopkins

**Constitutional Law (4 cases):**

- Brown v. Board of Education
- Roe v. Wade
- Marbury v. Madison
- McCulloch v. Maryland

--

## 🎯 Import Commands

### Test with 3 cases:

```powershell
python overnight_library_builder.py -practice-area civil_rights -max-cases 3
```

### Import all 27 foundation cases:

```powershell
python overnight_library_builder.py -practice-area all
```

### Import by practice area:

```powershell
python overnight_library_builder.py -practice-area criminal_defense
python overnight_library_builder.py -practice-area employment
python overnight_library_builder.py -practice-area constitutional
```

--

## 🔍 Verify It Worked

### Check database:

```python
from legal_library import LegalDocument
cases = LegalDocument.query.all()
print(f"Total cases: {len(cases)}")
for case in cases:
    print(f"  - {case.citation}: {case.title}")
```

### Check via API:

```bash
curl https://Evident.onrender.com/api/legal-library/search?q=Miranda
```

### Check in logs:

```
logs/overnight_import_20260127.log
logs/import_report_20260127_*.json
```

--

## ✅ Success Checklist

- [ ] Created CourtListener account
- [ ] Got API token from https://www.courtlistener.com/api/rest-info/
- [ ] Added `COURTLISTENER_API_KEY` to Render environment variables
- [ ] Saved changes in Render (triggered redeploy)
- [ ] Tested locally with 3 cases
- [ ] Ran full import of 27 cases
- [ ] Verified cases in database
- [ ] Checked API endpoint returns results

--

## 🐛 Troubleshooting

### Error: "403 Forbidden"

**Problem:** API key not set or invalid  
**Fix:** Double-check environment variable name and value

### Error: "Could not verify"

**Problem:** API key working but citations not found  
**Fix:** Normal - some citations might not be in CourtListener database

### Error: "Import failed - not found"

**Problem:** Case exists but not in CourtListener format  
**Fix:** Try alternative citation format or manual upload

### No errors but 0 imported

**Problem:** Rate limiting or network issue  
**Fix:** Add `-delay 3` flag to slow down requests

--

## 📈 Next Steps After Import

### 1. Hook Up Integrations (5 minutes)

```python
# Add to api/chatgpt.py
from chatgpt_legal_library_integration import ChatGPTLegalLibraryIntegration
```

### 2. Test ChatGPT Integration

```bash
curl -X POST https://Evident.onrender.com/api/chatgpt/assist \
  -d '{"question": "What is qualified immunity?"}'
```

### 3. Schedule Nightly Updates

```powershell
# Windows Task Scheduler
# Run: python overnight_library_builder.py -practice-area all
# Schedule: Daily at 2 AM
```

--

## 💰 CourtListener API Limits

**Free Tier:**

- ✅ Unlimited read requests
- ✅ Access to 10M+ opinions
- ✅ No credit card required
- ⚠️ Rate limit: ~100 requests/minute (plenty for your needs)

**Your Usage:**

- Initial import: 27 requests (one-time)
- Nightly updates: ~5-10 requests
- User searches: ~10-50 requests/day

**Total:** Well within free tier limits!

--

## 🎉 Result

Once you add the API key:

- ✅ 27 verified Supreme Court cases in your database
- ✅ ChatGPT can reference real case law
- ✅ Document Optimizer can auto-cite precedents
- ✅ Violation Finder can link to actual court opinions
- ✅ Full legal research library for Evident users

**Time to complete:** 10 minutes  
**Cost:** $0 (free tier)  
**Value:** Priceless (professional legal research tool!)
