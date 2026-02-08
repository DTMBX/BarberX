# Security Scan Results - 2026-02-07

## Summary

**Scan Date**: 2026-02-07  
**Dependencies Scanned**: 30+ Python packages  
**Vulnerabilities Found**: 13 known vulnerabilities in 3 packages  
**Risk Level**: 🔴 **HIGH** - Action required

---

## Vulnerable Packages

### 1. pypdf 5.1.0 → **7 vulnerabilities**

| ID | Severity | Fix Version | Impact |
|----|----------|-------------|---------|
| GHSA-7hfw-26vp-jp8m (CVE-2025-55197) | HIGH | 6.0.0 | RAM exhaustion via malicious FlateDecode filters |
| GHSA-vr63-x8vc-m265 (CVE-2025-62707) | MEDIUM | 6.1.3 | Infinite loop via DCTDecode inline image |
| GHSA-jfx9-29x2-rv3j (CVE-2025-62708) | MEDIUM | 6.1.3 | Large memory usage via LZWDecode |
| GHSA-m449-cwjh-6pw7 (CVE-2025-66019) | MEDIUM | 6.4.0 | Memory usage up to 1GB per stream (LZWDecode) |
| GHSA-4xc4-762w-m6cg (CVE-2026-22690) | MEDIUM | 6.6.0 | Long runtimes for invalid /Root entry |
| GHSA-4f6g-68pf-7vhv (CVE-2026-22691) | MEDIUM | 6.6.0 | Long runtimes for invalid startxref |
| GHSA-2q4j-m29v-hq73 (CVE-2026-24688) | MEDIUM | 6.6.2 | Infinite loop accessing outlines/bookmarks |

**Recommendation**: Upgrade to pypdf >= 6.6.2

**Workaround** (if cannot upgrade immediately):
```python
# Use strict mode to mitigate some attacks
reader = PdfReader("file.pdf", strict=True)
```

---

### 2. pdfminer-six 20231228 → **2 vulnerabilities**

| ID | Severity | Fix Version | Impact |
|----|----------|-------------|---------|
| GHSA-wf5f-4jwr-ppcp (CVE-2025-64512) | 🔴 **CRITICAL** | 20251107 | RCE via malicious pickle deserialization |
| GHSA-f83h-ghpp-7wcc (CVE-2025-70559) | 🔴 **CRITICAL** | 20251230 | Privilege escalation via unsafe pickle |

**Recommendation**: Upgrade to pdfminer-six >= 20251230

**Severity**: **CRITICAL** - Allows arbitrary code execution

**Impact**: 
- Attacker can execute arbitrary Python code by providing malicious PDF
- Possible privilege escalation from low-privileged user to root
- **CVSS Score**: 7.8 (High) for CVE-2025-70559

**Workaround**: None effective; upgrade immediately

---

### 3. torch 2.3.1 → **4 vulnerabilities**

| ID | Severity | Fix Version | Impact |
|----|----------|-------------|---------|
| PYSEC-2025-41 (CVE-2025-32434) | HIGH | 2.6.0 | RCE when loading model with torch.load(weights_only=True) |
| PYSEC-2024-259 (CVE-2024-48063) | MEDIUM | 2.5.0 | Deserialization RCE in RemoteModule |
| GHSA-3749-ghw9-m3mg (CVE-2025-2953) | LOW | 2.7.1rc1 | DoS in torch.mkldnn_max_pool2d |
| GHSA-887c-mr87-cxwp (CVE-2025-3730) | LOW | 2.8.0 | DoS in torch.nn.functional.ctc_loss |

**Recommendation**: Upgrade to torch >= 2.6.0 (or 2.8.0 for all fixes)

**Workaround**: Avoid loading untrusted models

---

## Priority Actions

### 🔴 **CRITICAL** - Immediate Action Required

1. **Upgrade pdfminer-six** to >= 20251230
   - Fixes RCE and privilege escalation vulnerabilities
   - **DO NOT** process untrusted PDFs with current version

2. **Upgrade pypdf** to >= 6.6.2
   - Fixes DoS attacks (infinite loops, memory exhaustion)
   - Use strict mode as temporary mitigation

### ⚠️ **HIGH** - Action Within 7 Days

3. **Upgrade torch** to >= 2.6.0
   - Fixes RCE when loading models
   - Only affects AI/ML features (Whisper transcription)

---

## Upgrade Plan

### Phase 1: Critical Security Patches (Immediate)

```bash
# Update requirements.txt
pypdf==6.6.2           # Was: 5.1.0
pdfminer-six==20251230 # Was: 20231228
```

### Phase 2: AI/ML Dependencies (Within 7 days)

```bash
# Update requirements.txt
torch==2.6.0  # Was: 2.3.1 (or wait for 2.8.0 for all DoS fixes)
```

### Testing Checklist

After upgrading:
- [ ] PDF upload and processing works
- [ ] PDF text extraction works (pdfplumber uses pdfminer-six)
- [ ] OCR processing works (pdf2image)
- [ ] Whisper transcription works (torch dependency)
- [ ] No breaking changes in pypdf API
- [ ] Run full test suite

---

## Supply-Chain Hardening (Next Steps)

Based on these findings, implement:

1. **Automated Vulnerability Scanning**
   - ✅ GitHub Actions workflow created (`.github/workflows/security-scan.yml`)
   - ⏳ Enable weekly scheduled scans
   - ⏳ Fail CI on HIGH/CRITICAL vulnerabilities

2. **SBOM Generation**
   - ⏳ Install cyclonedx-bom: `pip install cyclonedx-bom==4.6.4`
   - ⏳ Generate: `cyclonedx-py requirements backend/requirements.txt --output governance/sbom-backend.json`

3. **Dependency Pinning with Hashes**
   - ⏳ Install pip-tools: `pip install pip-tools==7.4.1`
   - ⏳ Generate hashes: `pip-compile --generate-hashes backend/requirements.txt`

4. **Update governance/DEPENDENCIES.md**
   - ⏳ Document new versions
   - ⏳ Note security fixes in "Security" field

---

## False Positives / Disputed CVEs

### CVE-2024-48063 (torch RemoteModule)

- **Status**: Disputed by multiple parties
- **Reason**: "Intended behavior in PyTorch distributed computing"
- **Action**: Review if using RemoteModule (likely not in Evident)

---

## References

- PyPDF GitHub: https://github.com/py-pdf/pypdf
- pdfminer.six GitHub: https://github.com/pdfminer/pdfminer.six
- PyTorch Security: https://github.com/pytorch/pytorch/security
- pip-audit GitHub: https://github.com/pypa/pip-audit
- OSV Database: https://osv.dev/

---

## Approval Required

Before upgrading:
- [ ] Engineering lead review (API compatibility)
- [ ] QA testing (PDF processing, OCR, transcription)
- [ ] Security team approval (if applicable)

**Recommended approval process**: Create separate PR for critical pdfminer-six/pypdf upgrades (Phase 1) for fast-track approval.

---

**Last Updated**: 2026-02-07  
**Next Scan**: Weekly (automated via GitHub Actions)  
**Scan Tool**: pip-audit 2.7.3
