# Demo Assets & Templates - Setup Guide

## 📁 Required Assets

### Demo Case Thumbnails (static/demos/)

Create these placeholder images (or use screenshots from actual cases):

1. **traffic_stop_preview.jpg** (800x600px)
   - Screenshot from traffic stop BWC footage
   - Show police interaction with vehicle
   - Blur faces for privacy

2. **wellness_check_preview.jpg** (800x600px)
   - Screenshot from wellness check footage
   - Show officer at residence
   - Professional, respectful framing

3. **warrant_affidavit_preview.jpg** (800x600px)
   - First page of search warrant affidavit
   - Redact sensitive info
   - Show official court header

**Quick Creation:**

```bash
# If you don't have real screenshots, create colored placeholders:
# Use any image editing tool or online placeholder generator
# Recommended: placeholder.com or via-placeholder.com

# Example URLs (download and save locally):
https://via.placeholder.com/800x600/667eea/ffffff?text=Traffic+Stop+BWC
https://via.placeholder.com/800x600/764ba2/ffffff?text=Wellness+Check
https://via.placeholder.com/800x600/10b981/ffffff?text=Search+Warrant
```

--

### Template Files (static/templates/)

Create these downloadable legal templates:

#### 1. motion_suppress_evidence.docx

```
MOTION TO SUPPRESS EVIDENCE

[Your Firm Name]
[Address]
[Phone]

SUPERIOR COURT OF [STATE]
COUNTY OF [COUNTY]

THE PEOPLE OF THE STATE OF [STATE],
    Plaintiff,
v.
[DEFENDANT NAME],
    Defendant.

Case No: [CASE NUMBER]

MOTION TO SUPPRESS EVIDENCE

COMES NOW the Defendant, [NAME], by and through undersigned counsel, and hereby moves this Honorable Court to suppress all evidence obtained as a result of the unlawful search and seizure conducted on [DATE].

GROUNDS FOR MOTION:

1. Fourth Amendment Violation
   - [Detail violation]

2. Miranda Violation
   - [Detail violation]

SUPPORTING FACTS:

[Insert facts from your BWC analysis]

CONCLUSION:

For the foregoing reasons, Defendant respectfully requests this Court grant this Motion to Suppress Evidence.

Respectfully submitted,

-----------_
[Attorney Name]
[Bar Number]
Attorney for Defendant
```

#### 2. use_of_force_report.docx

```
USE OF FORCE ANALYSIS REPORT

Case: [CASE NAME]
Date of Incident: [DATE]
Prepared by: [NAME]
Date Prepared: [DATE]

EXECUTIVE SUMMARY:
[Summary of incident]

TIMELINE OF EVENTS:
[Insert timeline from Evident analysis]

CONSTITUTIONAL ANALYSIS:
Graham v. Connor Analysis:
- Severity of crime: [Analysis]
- Immediate threat: [Analysis]
- Resistance/evasion: [Analysis]

POLICY COMPLIANCE:
[Department policy review]

RECOMMENDATIONS:
[Expert recommendations]

CASE LAW CITATIONS:
[Relevant precedents from Evident search]
```

#### 3. discovery_request.docx

```
DISCOVERY REQUEST

TO: [Prosecutor Name]
    [Office Address]

RE: People v. [Defendant Name]
    Case No: [CASE NUMBER]

Dear [Prosecutor]:

Pursuant to [State Rules], Defendant hereby requests the following:

1. BODY-WORN CAMERA FOOTAGE
   - All BWC footage from incident date [DATE]
   - All BWC from involved officers
   - Metadata and timestamps

2. CAD/RMS RECORDS
   - Computer-aided dispatch logs
   - Records management system entries

3. OFFICER PERSONNEL FILES
   - Disciplinary records (Pitchess/Brady material)
   - Training records
   - Prior use of force incidents

4. DISPATCH RECORDINGS
   - All audio recordings related to incident

Please provide in digital format (MP4 for video, PDF for documents).

Respectfully,

[Attorney Name]
```

#### 4. bwc_timeline_worksheet.xlsx

Create Excel file with columns:

- Timestamp (HH:MM:SS)
- Event Description
- Severity (Low/Medium/High)
- Officer Statement
- Notes
- Evidence Link

#### 5. case_intake_form.pdf

Create PDF form with fields:

- Client Information
- Incident Details
- Charges Filed
- Evidence Available
- Witness Information
- Discovery Checklist

**Quick Creation:**
Use Google Docs or Microsoft Word, then export to PDF/DOCX.

--

### Educational Content (static/education/)

Create simple HTML pages:

#### bwc_best_practices.html

```html
<!DOCTYPE html>
<html>
  <head>
    <title>BWC Best Practices</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
  </head>
  <body class="p-5">
    <div class="container">
      <h1>Body-Worn Camera Analysis Best Practices</h1>

      <h2>1. Identifying Critical Timestamps</h2>
      <p>Look for key moments:</p>
      <ul>
        <li>Initial contact</li>
        <li>Rights advisement</li>
        <li>Use of force</li>
        <li>Witness statements</li>
      </ul>

      <h2>2. Audio Analysis Techniques</h2>
      <p>Pay attention to:</p>
      <ul>
        <li>Officer tone and demeanor</li>
        <li>Subject responses</li>
        <li>Background conversations</li>
        <li>Time gaps in recording</li>
      </ul>

      <h2>3. Fourth Amendment Considerations</h2>
      <ul>
        <li>Was there probable cause?</li>
        <li>Was consent voluntary?</li>
        <li>Were Miranda rights given?</li>
      </ul>

      <a href="/free-dashboard" class="btn btn-primary mt-4"
        >Back to Dashboard</a
      >
    </div>
  </body>
</html>
```

Create similar pages for:

- pdf_evidence_guide.html
- case_law_search.html
- constitutional_issues.html

--

## 🚀 Quick Setup (5 minutes)

### Option 1: Use Placeholders

```bash
cd static/demos
# Download placeholder images
curl "https://via.placeholder.com/800x600/667eea/ffffff?text=Traffic+Stop+BWC" -o traffic_stop_preview.jpg
curl "https://via.placeholder.com/800x600/764ba2/ffffff?text=Wellness+Check" -o wellness_check_preview.jpg
curl "https://via.placeholder.com/800x600/10b981/ffffff?text=Search+Warrant" -o warrant_affidavit_preview.jpg
```

### Option 2: Create Basic Templates

```bash
cd static/templates
# Create placeholder text files (you can convert to DOCX/PDF later)
echo "Motion to Suppress Evidence Template - Coming Soon" > motion_suppress_evidence.txt
echo "Use of Force Report Template - Coming Soon" > use_of_force_report.txt
echo "Discovery Request Template - Coming Soon" > discovery_request.txt
```

### Option 3: Skip for Now

Templates are optional for initial testing. You can add real files later when you have them ready.

--

## ✅ Checklist

- [ ] Create demo thumbnails (or use placeholders)
- [ ] Create template documents (or use placeholders)
- [ ] Create educational HTML pages (or use placeholders)
- [ ] Test FREE tier dashboard to verify assets load
- [ ] Update download links to point to real files

--

## 📝 Notes

- Assets are NOT required for launch
- FREE tier works without them (just won't display images/downloads)
- Can add real files after launch
- Focus on Stripe configuration first

**Priority: LOW** - These enhance UX but aren't blocking
