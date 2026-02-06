# COPYRIGHT COMPLIANCE QUICK START

**Protect Your Law Firm from Copyright Lawsuits**

## 🚨 CRITICAL: THREE RULES TO AVOID LAWSUITS

### ⚖️ RULE 1: POINTER, DON'T REPUBLISH

**NEVER copy full copyrighted content from Westlaw, LexisNexis, Bloomberg Law,
or police reports.**

✅ **ALLOWED:**

```python
# Store citation metadata only
case = {
    "citation": "Smith v. Jones, 123 F.3d 456 (3d Cir. 2024)",
    "westlaw_cite": "2024 WL 123456",  # Citation only
    "fair_use_excerpt": "The court held that...[max 200 words]",
    "courtlistener_url": "https://...",  # Link to public source
    "our_analysis": "This supports our motion because..."
}
```

❌ **PROHIBITED:**

```python
# DO NOT DO THIS - Copyright infringement
case = {
    "full_opinion_text": "...[20 pages from Westlaw]...",  # ILLEGAL
    "westlaw_headnotes": "...",  # PROPRIETARY - lawsuit risk
    "lexis_shepards": "..."  # PROPRIETARY - lawsuit risk
}
```

**Why?** Westlaw and LexisNexis own copyrights to their editorial enhancements.
Copying their content violates terms of service and copyright law.

**Consequences:** Up to $150,000 per violation + attorney fees + license
termination

--

### 🔒 RULE 2: KEEP PROPRIETARY LAYERS SEPARATE

**Store Westlaw/Lexis data in separate, non-exportable database tables.**

✅ **SAFE ARCHITECTURE:**

```python
# Public domain table (EXPORTABLE)
public_case_data:
    - citation
    - court, date, docket
    - public_domain_text (from CourtListener)
    - our_analysis

# Proprietary table (NEVER EXPORT)
proprietary_source_data:
    - westlaw_keycite  # Internal use only
    - lexis_shepards   # Internal use only
    - export_allowed = False  # Forced
```

❌ **DANGEROUS:** Mixing proprietary and public data in same table → Risk of
accidental export

--

### 📋 RULE 3: RIGHTS-AWARE EXPORTS

**Every export MUST include attribution and exclude restricted materials.**

✅ **COMPLIANT EXPORT:**

```json
{
  "materials_included": [
    {
      "filename": "BWC_video.mp4",
      "source": "Atlantic County Sheriff OPRA Request #2025-001",
      "rights": "Public record - NJ OPRA",
      "sha256": "abc123..."
    },
    {
      "filename": "case_law_excerpt.pdf",
      "source": "CourtListener (public domain)",
      "excerpt_length": "150 words",
      "fair_use_purpose": "Legal argument in brief"
    }
  ],
  "excluded_materials": [
    {
      "filename": "westlaw_keycite.pdf",
      "reason": "Proprietary database content - internal use only"
    }
  ],
  "attribution": [
    "Whisper AI (OpenAI) - MIT License",
    "CourtListener - CC0 Public Domain"
  ]
}
```

--

## 📊 DATA SOURCE CLASSIFICATION

| Source                 | Type             | Can Export?      | Max Excerpt       |
| ---------------------- | ---------------- | ---------------- | ----------------- |
| **CourtListener**      | Public domain    | ✅ Yes           | Full text         |
| **Justia**             | Public domain    | ✅ Yes           | Full text         |
| **OPRA BWC footage**   | Public record    | ✅ Yes           | Full video        |
| **Our AI transcripts** | Our work product | ✅ Yes           | Full text         |
| **Westlaw KeyCite**    | Proprietary      | ❌ NO            | Internal use only |
| **Lexis Shepard's**    | Proprietary      | ❌ NO            | Internal use only |
| **Police reports**     | Copyrighted      | ⚠️ Excerpts only | 200 words max     |

--

## 🛠️ IMPLEMENTATION CHECKLIST

### Before Launch:

- [ ] **Install data_rights.py module** (Pattern 1-3 enforcement)
- [ ] **Create database tables** (public vs proprietary separation)
- [ ] **Update export functions** to validate rights
- [ ] **Add attribution generation** to PDF/DOCX exports
- [ ] **Test export blocking** for Westlaw/Lexis content

### Code Integration:

```python
# 1. Import compliance module
from data_rights import RightsAwareExport, RIGHTS_PROFILES, Material

# 2. Create export with validation
export = RightsAwareExport(case_number="ATL-L-002794-25")

# 3. Add materials (auto-validates)
bwc = Material(
    filename="BWC_video.mp4",
    category="bwc_videos",
    rights=RIGHTS_PROFILES["opra_bwc"]  # Pre-configured rights
)
export.add_material(bwc)  # ✅ Allowed

westlaw = Material(
    filename="keycite.pdf",
    category="research",
    rights=RIGHTS_PROFILES["westlaw"]  # Marked as non-exportable
)
export.add_material(westlaw)  # ❌ Auto-excluded

# 4. Finalize with attorney certification
export.finalize_export(
    certifying_attorney="John Doe, Esq.",
    attorney_bar_number="NJ12345",
    export_directory=Path("./exports")
)
# → Generates RIGHTS_MANIFEST.json + ATTRIBUTION.txt
```

### Database Setup:

```bash
# Run once to create compliance tables
python models_data_rights.py
```

--

## ⚠️ RED FLAGS - IMMEDIATE LEGAL RISK

**Stop immediately if you're doing ANY of these:**

1. **Copying full Westlaw opinions** into your database
2. **Exporting Westlaw headnotes** in court filings
3. **Republishing Lexis Shepard's data** in discovery
4. **Storing police reports without excerpt limits**
5. **Missing attribution** for third-party content
6. **No export validation** before PDF generation

**Each violation = Potential $150,000 lawsuit**

--

## 📧 GET HELP

**Legal Compliance Questions:**  
legal@Evident.info  
legal@Evident.info

**Copyright Concerns:**  
Report immediately: compliance@Evident.info

**Full Documentation:**  
See [DATA-RIGHTS-COMPLIANCE.md](DATA-RIGHTS-COMPLIANCE.md) for complete
framework

--

## ✅ SAFE HARBOR CHECKLIST

Before ANY court filing or discovery production:

- [ ] All case law from **public domain sources** (CourtListener, Justia)
- [ ] Westlaw/Lexis data **excluded** from exports
- [ ] Fair use excerpts **under 200 words** with attribution
- [ ] BWC footage from **OPRA requests** (documented)
- [ ] Our AI transcripts marked as **work product**
- [ ] **Attribution file** included in export package
- [ ] **Rights manifest** generated and signed by attorney
- [ ] **No proprietary database content** in export

--

**REMEMBER:** When in doubt, **EXCLUDE IT**. Better to be over-cautious than
face a $150,000 copyright lawsuit.

**Last Updated:** January 22, 2026
