# 🔒 Verified Sources - Quality Assurance

## Source Verification System

**Purpose:** Ensure only legitimate, verified, and respected legal sources are used.

--

## ✅ Verified Source Registry

### Tier 1: Official Government Sources (10/10 Credibility)

#### 1. Supreme Court of the United States

- **URL:** https://www.supremecourt.gov
- **API:** PDF downloads available
- **Coverage:** All SCOTUS opinions (1790-present)
- **Verification:** Official U.S. Government website (.gov)
- **Status:** ✅ Verified
- **Justification:**
  - Highest court in the United States
  - Primary source for Supreme Court law
  - Definitive legal authority
  - No higher source exists

#### 2. GovInfo.gov (U.S. Government Publishing Office)

- **URL:** https://www.govinfo.gov
- **API:** https://api.govinfo.gov
- **Coverage:** Federal statutes, regulations, Congressional documents
- **Verification:** Official U.S. Government (.gov)
- **Status:** ✅ Verified
- **Justification:**
  - Official government publishing office
  - Authoritative legal documents
  - Primary source for federal law

#### 3. Cornell Legal Information Institute (LII)

- **URL:** https://www.law.cornell.edu
- **Coverage:** U.S. Code, Supreme Court, CFR
- **Verification:** Official Cornell Law School (.edu)
- **Status:** ✅ Verified
- **Justification:**
  - Academic institution (Cornell Law School)
  - Established 1992
  - Primary source for legal research
  - Cited by courts and scholars

--

### Tier 2: Verified Non-Profit Sources (9-9.5/10 Credibility)

#### 4. CourtListener

- **URL:** https://www.courtlistener.com
- **API:** https://www.courtlistener.com/api/rest/v3/
- **Coverage:** 10M+ legal opinions (federal, state, Supreme Court)
- **Organization:** Free Law Project (501(c)(3) non-profit)
- **Established:** 2010
- **Status:** ✅ Verified
- **Justification:**
  - Non-profit legal database
  - Used by legal professionals nationwide
  - Comprehensive collection
  - Regular updates and verification
  - Open-source transparency
- **Rating:** 9.5/10
- **PRIMARY SOURCE FOR AUTOMATED IMPORTS**

--

### Tier 3: Verified Commercial Sources (8.5-9/10 Credibility)

#### 5. Justia

- **URL:** https://www.justia.com
- **Coverage:** Federal and state case law, statutes
- **Established:** 2003
- **Status:** ✅ Verified
- **Justification:**
  - Well-established legal database
  - Used by legal professionals
  - Free access to verified cases
  - Regular updates
- **Rating:** 9.0/10

#### 6. Google Scholar (Legal)

- **URL:** https://scholar.google.com
- **Coverage:** Legal opinions indexed from verified sources
- **Status:** ✅ Verified
- **Justification:**
  - Academic search engine
  - Indexes verified legal opinions
  - Cross-referenced with official sources
  - Wide coverage
- **Rating:** 8.5/10

--

## ❌ Non-Verified Sources (Rejected)

### Why Some Sources Are NOT Used

**Commercial Paid Databases:**

- Westlaw - ❌ Proprietary, requires subscription
- Lexis - ❌ Proprietary, requires subscription
- Bloomberg Law - ❌ Proprietary, requires subscription

**Unverified Websites:**

- Random law blogs - ❌ Not authoritative
- Wikipedia - ❌ Not primary source
- Unknown case law sites - ❌ Cannot verify accuracy

**Social Media / Forums:**

- Reddit legal advice - ❌ Not authoritative
- Law forums - ❌ Not verified
- Social media posts - ❌ Not reliable

--

## 🔍 Verification Process

### Multi-Stage Verification

#### Stage 1: Source Credibility Check

```python
source_info = {
    'official': True/False,      # .gov or .edu
    'verified': True/False,      # Known legitimate source
    'credibility_rating': 0-10,  # Quality score
    'established_year': int,     # How long in operation
    'peer_reviewed': True/False, # Academic review
    'non_profit': True/False     # 501(c)(3) status
}
```

#### Stage 2: Citation Validation

```python
citation_check = {
    'format_valid': True/False,        # Bluebook compliant
    'year_valid': True/False,          # 1789-present
    'reporter_valid': True/False,      # Recognized reporter
    'quality_score': 0-100             # Overall quality
}
```

#### Stage 3: Cross-Verification

```python
cross_verify = {
    'verified_in': ['courtlistener', 'cornell_lii'],
    'not_found_in': [],
    'confidence': 'HIGH' | 'MEDIUM' | 'LOW'
}

# Confidence levels:
# HIGH   = verified in 2+ sources
# MEDIUM = verified in 1 source
# LOW    = not verified
```

#### Stage 4: Content Validation

```python
content_check = {
    'has_full_text': True/False,
    'has_citation': True/False,
    'has_court': True/False,
    'has_date': True/False,
    'metadata_complete': True/False
}
```

--

## 📊 Quality Scoring System

### Document Quality Score (0-100)

**Citation (30 points):**

- Valid format: 20 points
- Bluebook compliant: 10 points

**Source (25 points):**

- Official source (.gov/.edu): 25 points
- Verified non-profit: 20 points
- Verified commercial: 15 points
- Unverified: 0 points

**Metadata (25 points):**

- Complete metadata: 25 points
- Partial metadata: 10-20 points
- Missing metadata: 0 points

**Cross-Verification (20 points):**

- Verified in 3+ sources: 20 points
- Verified in 2 sources: 15 points
- Verified in 1 source: 10 points
- Not verified: 0 points

**Thresholds:**

- 90-100: Excellent - Auto-import
- 70-89: Good - Auto-import
- 50-69: Fair - Manual review
- 0-49: Poor - Reject

--

## 🛡️ Security Measures

### API Rate Limiting

```python
RATE_LIMITS = {
    'courtlistener': 2,  # 2 seconds between requests
    'cornell_lii': 3,    # 3 seconds (more conservative)
    'govinfo': 2,        # 2 seconds
}
```

### Request Headers

```python
HEADERS = {
    'User-Agent': 'Evident Legal Library Builder/1.0 (Educational; Non-commercial)',
    'From': 'admin@Evident.info',
    'Accept': 'application/json'
}
```

### robots.txt Compliance

- ✅ All sources checked for robots.txt
- ✅ Crawl-delay respected
- ✅ Disallowed paths avoided
- ✅ Terms of service reviewed

--

## 📈 Source Comparison

```
Source            Coverage    Speed    Cost    Verification  Rating
─────────────────────────────────────────────────────────────────
SCOTUS Official   SCOTUS      Slow     Free    Official      10.0
GovInfo.gov       Federal     Medium   Free    Official      10.0
Cornell LII       All         Medium   Free    Official      10.0
CourtListener     10M+ cases  Fast     Free    High          9.5
Justia            High        Fast     Free    High          9.0
Google Scholar    Very High   Fast     Free    Medium        8.5
─────────────────────────────────────────────────────────────────
Westlaw           Highest     Fastest  $$$     Highest       N/A*
Lexis             Highest     Fastest  $$$     Highest       N/A*

* Not used due to cost/licensing restrictions
```

--

## ✅ Verification Checklist

Before importing any case:

- [ ] Source is in verified registry
- [ ] Source credibility rating ≥ 8.5
- [ ] Citation format validated
- [ ] Cross-verified in 2+ sources (preferred)
- [ ] Metadata complete
- [ ] Quality score ≥ 70
- [ ] Rate limiting respected
- [ ] Terms of service compliant

--

## 🎯 Best Practices

### 1. Always Cross-Verify

```python
# Don't trust single source
citation = "384 U.S. 436"

# Verify in multiple sources
courtlistener_result = verify_in_courtlistener(citation)
cornell_result = verify_in_cornell(citation)

if courtlistener_result and cornell_result:
    # High confidence - import
    import_case(citation)
```

### 2. Prefer Official Sources

```python
# Priority order:
1. Supreme Court official (.gov) - Use for SCOTUS cases
2. GovInfo.gov - Use for federal statutes/regs
3. Cornell LII - Use for U.S. Code
4. CourtListener - Use for general case law
5. Justia - Use as fallback
```

### 3. Validate Before Import

```python
# Never import without validation
def import_case(citation):
    # Step 1: Validate citation format
    if not validate_citation_format(citation):
        return False

    # Step 2: Verify source credibility
    if not is_verified_source(source):
        return False

    # Step 3: Cross-verify
    if not cross_verify(citation, min_sources=2):
        return False

    # Step 4: Import
    return do_import(citation)
```

--

## 📚 Source Documentation

### CourtListener API Usage

```python
# Example: Search for case
import requests

API_URL = "https://www.courtlistener.com/api/rest/v3/search/"

response = requests.get(API_URL, params={
    'q': '384 U.S. 436',
    'type': 'o',  # Opinions
    'format': 'json'
})

if response.status_code == 200:
    data = response.json()
    # Process results
```

### Cornell LII Access

```python
# Example: Get Supreme Court case
case_url = f"https://www.law.cornell.edu/supremecourt/text/{volume}/{page}"

# Miranda v. Arizona
# https://www.law.cornell.edu/supremecourt/text/384/436
```

--

## 🔐 Legal & Ethical Compliance

### Terms of Service

- ✅ All sources reviewed for TOS compliance
- ✅ Non-commercial educational use
- ✅ Attribution provided
- ✅ Rate limits respected

### Copyright

- ✅ Court opinions are public domain (U.S.)
- ✅ Government documents are public domain
- ✅ No proprietary content copied

### Attribution

```python
# Every imported document includes:
doc.source = 'courtlistener'  # Source attribution
doc.url = 'https://...'       # Original URL
doc.verified = True           # Verification status
```

--

## 📊 Verification Statistics

**Expected Results:**

```
Total cases attempted:     30
Successfully verified:     28 (93%)
Cross-verified (2+ sources): 25 (83%)
Single-source only:        3 (10%)
Failed verification:       2 (7%)

Average quality score:     92.3/100
Average credibility:       9.2/10
```

--

**Summary:** Only legitimate, verified, and respected sources used. Multi-stage verification ensures quality and authenticity.

**Status:** ✅ Production-ready with comprehensive verification
