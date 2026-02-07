# 🔑 GET YOUR COURTLISTENER API KEY - VISUAL GUIDE

**You're close! You're at the API root, but you need a different page to get
your key.**

--

## 📍 STEP-BY-STEP: Get Your API Token

### **Step 1: Make sure you're signed in**

If you see your username in the top-right corner of CourtListener, you're signed
in ✅

If not:

1. Go to: **https://www.courtlistener.com/sign-in/**
2. Enter your email and password
3. Click "Sign In"

--

### **Step 2: Go to the API Info Page (NOT the API Root)**

**🔗 Click this link:** **https://www.courtlistener.com/help/api/rest/**

**Or manually navigate:**

1. At the top of CourtListener, click **"Help"**
2. In the dropdown, click **"APIs & Bulk Data"**
3. Click **"REST API"**
4. Scroll down to **"Authentication"** section

--

### **Step 3: Find Your API Token**

On the API help page, you'll see a section called **"Authentication"**.

Look for text that says:

```
Your API token is: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**This is your API key!** Copy it.

--

## 🚨 ALTERNATIVE METHOD: Direct Token Page

**If you don't see your token on the help page, try this:**

**Method 1: Profile Settings**

1. Go to: **https://www.courtlistener.com/profile/settings/**
2. Look for "API Token" or "API Key" section
3. Copy your token

**Method 2: API Rest Info**

1. Try: **https://www.courtlistener.com/api/rest-info/**
2. If this page exists, your token should be displayed

**Method 3: Contact Support** If neither works, email: **info@free.law**
Subject: "Need my API token" They respond within 24 hours.

--

## ✅ WHAT YOUR API TOKEN LOOKS LIKE

**Format:**

- Long string of letters and numbers
- Usually 40-64 characters
- Example: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

**NOT your password** **NOT the API root URL**

--

## 📝 ONCE YOU HAVE YOUR TOKEN

### **Test it works:**

**In your browser, try this URL:**

```
https://www.courtlistener.com/api/rest/v4/courts/?format=json
```

**You should see:**

- Without authentication: `403 Forbidden` or limited results
- With authentication: Full JSON data

**To authenticate in browser:**

1. Install browser extension: "ModHeader" (Chrome) or "Modify Header Value"
   (Firefox)
2. Add header:
   - Name: `Authorization`
   - Value: `Token YOUR_API_KEY_HERE` (note the word "Token" before your key)
3. Refresh the API page

--

### **Test with curl (command line):**

```bash
curl "https://www.courtlistener.com/api/rest/v4/courts/" \
  -H "Authorization: Token YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with your actual token.

**Expected result:** JSON data with list of courts

--

## 🔧 ADD TO RENDER (After You Have Token)

### **Step 1: Go to Render Dashboard**

🔗 **https://dashboard.render.com**

### **Step 2: Select Your Service**

- Click on your **Evident** web service
- (Not blueprints, not databases - the main web service)

### **Step 3: Click Environment**

- In the left sidebar, click **"Environment"**
- You'll see a list of environment variables

### **Step 4: Add New Variable**

- Click **"Add Environment Variable"** button
- Fill in:
  - **Key:** `COURTLISTENER_API_KEY`
  - **Value:** `<paste your token here>`
  - ✅ **Check the "Secret" checkbox** (IMPORTANT - this hides the value)
- Click **"Save Changes"**

### **Step 5: Wait for Deploy**

- Render will automatically redeploy your app (takes 2-3 minutes)
- You'll see a progress indicator
- When it says "Live", you're ready to test

--

## 🧪 TEST YOUR INTEGRATION

### **Method 1: Run Library Builder**

```bash
cd C:\web-dev\github-repos\Evident.info
python overnight_library_builder.py -practice-area all
```

**Expected output:**

```
[OK] Building legal library for practice area: all
[OK] Importing foundation cases...
[OK] Importing: Brown v. Board of Education (347 U.S. 483)
[OK] Successfully imported 27 cases
```

### **Method 2: Test Direct Import**

```bash
cd C:\web-dev\github-repos\Evident.info
python -c "from legal_library import LegalLibrary; ll = LegalLibrary(); result = ll.ingest_from_courtlistener('410 U.S. 113'); print(result)"
```

**Expected:** Should print case data for Roe v. Wade

### **Method 3: Check Logs**

```bash
# Check for any errors
cat logs/Evident.log | tail -n 50
```

Look for:

- ✅ `Successfully authenticated with CourtListener`
- ✅ `Imported case: ...`
- ❌ `403 Forbidden` = API key not working
- ❌ `Invalid token` = Wrong API key format

--

## 🚨 TROUBLESHOOTING

### **Problem: "I don't see my API token anywhere"**

**Solution:**

1. Make sure you're signed in to CourtListener
2. Try this direct link: **https://www.courtlistener.com/help/api/rest/**
3. Scroll down to "Authentication" section
4. If still nothing, email **info@free.law** with:
   - Subject: "Need my API token"
   - Body: "I'm signed into CourtListener but can't find my API token. My
     username is [your username]. Can you help?"

### **Problem: "403 Forbidden when testing API"**

**Solution:**

1. Check your token is correct (no extra spaces)
2. Verify header format: `Authorization: Token YOUR_KEY` (note "Token" with
   capital T)
3. Make sure token is added to Render as SECRET
4. Wait 2-3 minutes after adding to Render for deploy to complete

### **Problem: "Import script fails"**

**Solution:**

1. Check `COURTLISTENER_API_KEY` is in Render environment variables
2. Verify it's marked as SECRET
3. Check logs: `cat logs/Evident.log`
4. Try importing one case manually (Method 2 above)
5. If still fails, check rate limit (100 requests/minute - wait 1 minute and
   retry)

--

## 📞 COURTLISTENER SUPPORT

**If you still can't find your API token:**

**Email:** info@free.law  
**Subject:** Need my API token  
**Body:**

```
Hi,

I'm signed into CourtListener (username: YOUR_USERNAME) but I can't
find my API token on the help page or in my profile settings.

Can you please send me my token or tell me where to find it?

I'm building a legal research platform and need API access.

Thank you!
```

**Response time:** Usually within 24 hours (they're very helpful!)

--

## 🎯 QUICK REFERENCE

### **Where to Find Token:**

1. **Best:** https://www.courtlistener.com/help/api/rest/ (scroll to
   "Authentication")
2. **Alternative:** https://www.courtlistener.com/profile/settings/
3. **Last resort:** Email info@free.law

### **How to Use Token:**

- **Header format:** `Authorization: Token YOUR_KEY_HERE`
- **In Python:** Already configured in `legal_library.py` (just add to Render)
- **In curl:** `curl -H "Authorization: Token YOUR_KEY" URL`

### **Where to Add Token:**

- **Render:** Dashboard → Evident service → Environment → Add Variable
- **Key:** `COURTLISTENER_API_KEY`
- **Value:** Your token
- **Secret:** ✅ Checked

### **How to Test:**

```bash
# Quick test
curl "https://www.courtlistener.com/api/rest/v4/courts/" \
  -H "Authorization: Token YOUR_API_KEY"

# Full test
python overnight_library_builder.py -practice-area all
```

--

## 🚀 NEXT STEPS (After You Have Token)

**Immediate (today):**

1. ✅ Get token from https://www.courtlistener.com/help/api/rest/
2. ✅ Add to Render as SECRET
3. ✅ Test: `python overnight_library_builder.py -practice-area all`
4. ✅ Verify: 27 foundation cases imported

**This week:**

1. Import 1,000 top cases
2. Deploy mission pages (`git push`)
3. Email 5 law schools
4. Get first 10 users

**This month:**

1. 50 law school partnerships
2. 1,000 active users
3. $25K MRR

--

**TL;DR:**

1. Go to: **https://www.courtlistener.com/help/api/rest/**
2. Scroll to "Authentication" section
3. Copy your API token
4. Add to Render: `COURTLISTENER_API_KEY` (as SECRET)
5. Done! 🎉

**Need help?** Email info@free.law - they respond quickly!
