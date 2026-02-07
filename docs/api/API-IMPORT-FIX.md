# 🔧 API IMPORT FIX - Quick Guide

## Issue Found

Your overnight library builder is failing because:

1. **Wrong API version**: Code was using v3, but CourtListener now requires v4
2. **Missing local API key**: The API key is in Render, but not in your local
   environment

## ✅ Fixes Applied

### 1. Updated API Endpoint (DONE)

Changed in `legal_library.py`:

```python
# OLD:
self.courtlistener_api = "https://www.courtlistener.com/api/rest/v3/"

# NEW:
self.courtlistener_api = "https://www.courtlistener.com/api/rest/v4/"
```

### 2. Added CourtListener Attribution (DONE)

Updated `templates/components/footer.html` with:

- CourtListener & Free Law Project links
- Explanation of value-add vs free data
- Professional styling with blue accent

--

## 🚀 To Test Locally (2 Options)

### Option 1: Set API Key Locally

```bash
# Windows PowerShell
$env:COURTLISTENER_API_KEY = "YOUR_API_KEY_HERE"
cd C:\web-dev\github-repos\Evident.info
python overnight_library_builder.py -practice-area all
```

### Option 2: Wait for Render Deploy

The code fix will work automatically on Render since the API key is already
there as a SECRET.

After you push:

```bash
git add legal_library.py templates/components/footer.html
git commit -m "Fix CourtListener API v4 endpoint and add attribution"
git push
```

Then on Render, run:

```bash
# Via Render shell
python overnight_library_builder.py -practice-area all
```

--

## 📋 What Was Fixed

**legal_library.py:**

- Line 137: Changed API endpoint from v3 → v4

**templates/components/footer.html:**

- Added CourtListener attribution section
- Links to CourtListener.com and Free.law
- Explains value-add (AI, mobile, support)
- Professional styling with blue accent

--

## ✅ Next Steps

1. **Commit changes:**

```bash
git add legal_library.py templates/components/footer.html
git commit -m "Fix CourtListener v4 API and add proper attribution"
git push
```

2. **Verify on website:**

- Visit your site footer
- Should see "Legal Data Powered By: CourtListener | Free Law Project"
- Links should work

3. **Test import on Render:**

- Once deployed, test foundation case import
- Should successfully import 27 cases

--

## 🧪 Test Single Case Import (Locally)

If you want to test locally first:

```bash
# Set API key
$env:COURTLISTENER_API_KEY = "YOUR_KEY"

# Test single case
cd C:\web-dev\github-repos\Evident.info
python -c "from legal_library import LegalLibrary; ll = LegalLibrary(); print(ll.ingest_from_courtlistener('410 U.S. 113'))"
```

Should return Roe v. Wade case data.

--

## 📊 What You'll Have After Import

- **27 Foundation Cases** (Miranda, Brown, Roe, Terry, etc.)
- **Citation Network** (relationships between cases)
- **Judge Data** (Warren, Marshall, Burger courts)
- **Full Opinions** (searchable text)
- **Metadata** (dates, courts, citations)

--

**The fixes are ready. Commit and push to deploy!** ✅
