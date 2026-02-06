# ?? Live Deployment & Testing Guide

## ? **Current Status**

**GitHub:** All code pushed to `main` branch  
**Render:** Auto-deploying from GitHub  
**Features:** Unified batch upload ready

--

## ?? **Your Live URLs**

### **Production App (Render):**

```
https://Evident-legal-tech.onrender.com
```

### **Key Pages:**

- **Login:** https://Evident-legal-tech.onrender.com/auth/login
- **Dashboard:** https://Evident-legal-tech.onrender.com/auth/dashboard
- **Unified Batch Upload:** https://Evident-legal-tech.onrender.com/batch-upload
- **Docs:** https://Evident-legal-tech.onrender.com/docs
- **Pricing:** https://Evident-legal-tech.onrender.com/pricing

--

## ?? **Login Credentials**

**Admin Account:**

- Email: `admin@Evident.info`
- Password: `Evident2026!`

**Test Accounts:**

- Free User: `free@Evident.test` / `test123`
- Enterprise User: `enterprise@Evident.test` / `test123`

--

## ?? **Deployment Steps (Auto-Running)**

Render is currently:

1. ? **Detected Push:** Your latest commit
2. ?? **Building:** Installing dependencies (Python 3.11.9)
3. ?? **Deploying:** Starting gunicorn
4. ? **ETA:** 5-7 minutes

### **Monitor Deployment:**

**Go to Render Dashboard:**
https://dashboard.render.com

**Check:**

1. Click your service: **Evident-legal-tech**
2. Watch **"Events"** tab for real-time logs
3. Look for **"Live"** status (green)

--

## ?? **Testing Plan**

### **Test 1: Unified Batch Upload (PRIMARY)**

**Objective:** Upload your 26 discovery files in one batch

**Steps:**

1. Login: https://Evident-legal-tech.onrender.com/auth/login
   - Email: `admin@Evident.info`
   - Password: `Evident2026!`

2. Go to batch upload:
   - https://Evident-legal-tech.onrender.com/batch-upload

3. Upload test files:
   - **Option A:** Upload 2-3 sample files (1 PDF + 1 video)
   - **Option B:** Upload all 26 discovery files (RECOMMENDED for full test)

4. Expected results:
   - Files automatically separated (Videos vs PDFs)
   - Real-time progress bar
   - Success message per file type
   - Database records created

**Expected Output:**

```json
{
  "success": true,
  "results": {
    "total": 26,
    "categorized": {
      "videos": 24,
      "pdfs": 2
    },
    "successful": {
      "video": [...24 items...],
      "pdf": [...2 items...]
    },
    "failed": []
  },
  "summary": {
    "total_successful": 26,
    "total_failed": 0
  }
}
```

--

### **Test 2: Frontend Pages**

**Test all new pages:**

? **Documentation:** https://Evident-legal-tech.onrender.com/docs

- Should show 6 documentation categories
- Quick start guide
- Links to existing docs

? **Pricing:** https://Evident-legal-tech.onrender.com/pricing

- 4 pricing tiers (Free, Pro, Premium, Enterprise)
- Feature comparison table
- FAQ section

? **Contact:** https://Evident-legal-tech.onrender.com/contact

- Contact form
- Email addresses
- Support hours

--

### **Test 3: BWC Analysis (If AI Enabled)**

**If you have API keys set:**

1. Upload a BWC video
2. Check for:
   - ? Audio transcription (Whisper)
   - ? Speaker diarization
   - ? Timeline analysis
   - ? Constitutional violation detection

**Note:** AI features require:

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `HUGGINGFACE_TOKEN`

Set these in Render ? Environment variables

--

## ?? **Troubleshooting**

### **Issue: "Service Unavailable"**

**Cause:** Render is still deploying or sleeping (free tier)  
**Fix:** Wait 30 seconds, refresh page

### **Issue: "Build Failed"**

**Check:** Render dashboard ? Logs  
**Common:** Missing dependency (already fixed with openai added)

### **Issue: "Cannot login"**

**Cause:** Database not initialized  
**Fix:** First deployment creates fresh DB, wait for completion

### **Issue: "Batch upload fails"**

**Check:**

- File size limits (20 GB Enterprise, 1 GB Pro, 100 MB Free)
- File type (must be .mp4, .mov, .pdf, .jpg, etc.)
- Network timeout on large uploads

### **Issue: "404 Not Found" on new pages**

**Cause:** Flask route not registered  
**Check:** app.py has `@app.route('/batch-upload')` and `@app.route('/docs')`

--

## ?? **Mobile Testing**

**Test on mobile:**

1. Open on phone: https://Evident-legal-tech.onrender.com
2. Check responsive design
3. Test batch upload from phone camera/files

--

## ? **Performance Testing**

### **Upload Speed Test:**

| File Type      | Size   | Expected Time  |
| -------------- | ------ | -------------- |
| 1 PDF          | 5 MB   | 2-5 seconds    |
| 1 BWC Video    | 100 MB | 10-20 seconds  |
| 1 BWC Video    | 1 GB   | 60-120 seconds |
| 26 Mixed Files | 22 GB  | 15-30 minutes  |

**Note:** Free tier has slower disk I/O. Upgrade to paid tier for faster uploads.

--

## ?? **Security Verification**

**Test security features:**

? **Login required:**

- Try accessing `/batch-upload` without login ? Redirects to login

? **Tier limits:**

- Free user: Try uploading 3 videos (should fail after 2)
- Enterprise: Upload unlimited

? **File validation:**

- Try uploading `.exe` file ? Should reject
- Try oversized file ? Should enforce tier limit

? **SHA-256 hashing:**

- Upload same file twice ? Different upload IDs, same hash

--

## ?? **Expected Metrics**

After testing, verify:

**Database:**

- ? 26 records in `Analysis` table (for videos)
- ? 2 records in `PDFUpload` table
- ? Audit logs created
- ? User storage_used_mb updated

**Files:**

- ? Videos in: `/uploads/bwc_videos/`
- ? PDFs in: `/uploads/pdfs/`
- ? Hashes match

**Performance:**

- ? Parallel processing (check timestamps)
- ? All 26 files uploaded in <30 min

--

## ? **Deployment Checklist**

Before testing:

- [x] Code pushed to GitHub
- [x] Render auto-deploying
- [x] Python 3.11.9 forced
- [x] openai dependency added
- [x] Batch upload blueprint registered
- [x] Frontend pages created
- [x] Documentation complete

During deployment:

- [ ] Check Render logs for errors
- [ ] Wait for "Live" status
- [ ] Verify health check passes

After deployment:

- [ ] Test login
- [ ] Test batch upload (2-3 files)
- [ ] Test new frontend pages
- [ ] Test responsive design
- [ ] Test API endpoints

--

## ?? **Success Criteria**

? **Deployment successful if:**

1. App loads at https://Evident-legal-tech.onrender.com
2. Login works
3. Can access `/batch-upload` page
4. Can upload 1 PDF + 1 video in same batch
5. Files are separated and processed
6. Results show correct categorization
7. New pages load (docs, pricing, contact)

--

## ?? **Next Steps After Testing**

1. **Custom Domain:**
   - Follow: `CUSTOM-DOMAIN-SETUP.md`
   - Point `app.Evident.info` to Render

2. **API Keys (Optional):**
   - Add in Render ? Environment:
     - `OPENAI_API_KEY`
     - `HUGGINGFACE_TOKEN`
   - Enables AI features

3. **Upgrade Tier (Optional):**
   - Render Starter: $7/month (no cold starts)
   - PostgreSQL Starter: $7/month (more storage)

4. **Production Optimizations:**
   - Enable Redis caching
   - Set up CDN for static files
   - Configure monitoring (Sentry)

--

## ?? **Support**

**If deployment fails:**

1. Check Render logs (dashboard ? Events)
2. Copy last 30 lines of error
3. Send to: security@Evident.info
4. Or open GitHub issue

**If testing finds bugs:**

1. Document steps to reproduce
2. Include screenshots
3. Note browser/device
4. Open GitHub issue with `bug` label

--

## ?? **You're Ready!**

**Your unified batch upload system is deploying NOW!**

**Check status:**

```
https://dashboard.render.com
```

**Test when live (5-7 min):**

```
https://Evident-legal-tech.onrender.com/batch-upload
```

**Upload your 26 discovery files and watch the magic! ??**
