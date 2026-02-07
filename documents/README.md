# Evident FOUNDING DOCUMENTS ARCHIVE

**Purpose:** Preserve the exact text of United States founding documents on
Evident servers to maintain truth in case official .gov sources are altered,
deleted, or become inaccessible.

**Philosophy:** "Truth is the only subject" - These documents establish the
supreme law of the land and must be preserved in their original form.

---

## ARCHIVE STRUCTURE

```
documents/
├── founding/           # Immutable founding documents (Constitution, Declaration, etc.)
├── living/            # Current laws that can change (USC, CFR, state statutes)
├── archives/          # Historical versions and checksums
└── README.md          # This file
```

---

## FOUNDING DOCUMENTS (Immutable)

These documents are **frozen in time** - they cannot be changed without
constitutional amendment process:

### Primary Documents

1. **constitution.md** - The Constitution for the United States of America
   (1787)
2. **bill-of-rights.md** - First Ten Amendments (1791)
3. **amendments-11-27.md** - Additional Amendments (1795-1992)
4. **declaration.md** - Declaration of Independence (1776)
5. **articles-of-confederation.md** - First constitution (1777-1789)

### Supporting Documents

6. **federalist-papers/** - All 85 essays (Hamilton, Madison, Jay)
7. **anti-federalist-papers/** - Opposition essays
8. **mayflower-compact.md** - First governing document on North America (1620)
9. **magna-carta.md** - Foundation of common law (1215)
10. **english-bill-of-rights.md** - Precursor to US Bill of Rights (1689)

---

## LIVING DOCUMENTS (Can Change)

These documents can be amended, updated, or repealed by Congress/States:

### Federal Law

- **usc/** - United States Code (current statutes)
- **cfr/** - Code of Federal Regulations
- **public-laws/** - Individual public laws as passed

### State Law

- **state-codes/** - Current state statutes
- **state-regulations/** - State administrative codes

---

## VERIFICATION & AUTHENTICITY

Every document includes:

1. **Source Citation** - Where retrieved (e.g., archives.gov, congress.gov)
2. **Retrieval Date** - When downloaded/verified
3. **SHA-256 Checksum** - Cryptographic hash to prove authenticity
4. **Version History** - If document is ever amended

### Example Metadata Block:

```markdown
**Archival Metadata:**

- Source: National Archives (archives.gov/founding-docs/constitution-transcript)
- Retrieved: January 27, 2026
- SHA-256: [calculated hash]
- Status: Immutable founding document
- Verification: Cross-referenced with Library of Congress
```

---

## WHY THIS MATTERS

**Historical Concerns:**

- Government websites can be altered
- Domain changes can break links
- Political pressure can modify presentations
- Server failures can cause data loss
- Censorship can restrict access

**Evident Solution:**

- **Independent backup** - Not dependent on .gov availability
- **Cryptographic verification** - Checksums prove authenticity
- **Version control** - Git tracks any changes
- **Public access** - Available to all users
- **Legal reference** - Court-ready formatting

**Truth Preservation:**

> "The price of freedom is eternal vigilance" - Thomas Jefferson

We maintain this archive because:

1. Truth must be preserved independently
2. Access to founding documents is a natural right
3. Legal research requires reliable sources
4. Government is not always trustworthy custodian
5. Future generations deserve unaltered history

---

## USAGE

### For Legal Research

- Direct quotes with citation metadata
- Searchable full text
- Cross-referenced with amendments
- Case law annotations (future)

### For Court Filings

- Official text formatting
- Proper citation format
- Version verification
- Downloadable PDFs (future)

### For Education

- Complete founding documents
- Historical context
- Framers' intent (Federalist Papers)
- Constitutional development timeline

---

## DOCUMENT STATUS

| Document                  | Status         | Size   | Last Verified |
| ------------------------- | -------------- | ------ | ------------- |
| Constitution              | ✅ Archived    | ~50KB  | Jan 27, 2026  |
| Bill of Rights            | ✅ Archived    | ~15KB  | Jan 27, 2026  |
| Amendments 11-27          | ✅ Archived    | ~25KB  | Jan 27, 2026  |
| Declaration               | 🔄 In Progress | ~20KB  | Jan 27, 2026  |
| Articles of Confederation | 🔄 In Progress | ~25KB  | -             |
| Federalist Papers         | 📋 Planned     | ~500KB | -             |

**Legend:**

- ✅ Archived - Full text preserved with verification
- 🔄 In Progress - Being transcribed
- 📋 Planned - Scheduled for archival

---

## CHECKSUMS & VERIFICATION

SHA-256 checksums allow anyone to verify document authenticity:

```bash
# Verify Constitution hasn't been altered
sha256sum documents/founding/constitution.md

# Compare with official National Archives version
curl https://www.archives.gov/founding-docs/constitution-transcript | sha256sum
```

If checksums match = document is authentic  
If checksums differ = document has been altered

**This is mathematical proof of truth.**

---

## CONTRIBUTION GUIDELINES

**Adding New Documents:**

1. Source from official .gov sites only
2. Include complete metadata block
3. Calculate SHA-256 checksum
4. Verify against multiple sources
5. Use markdown for readability
6. Preserve exact wording (no paraphrasing)

**Document Standards:**

- Plain text markdown format
- Original spelling preserved (including archaic)
- Line breaks match original where possible
- Footnotes in separate section
- No interpretation or commentary in body text

---

## LEGAL NOTICE

These documents are in the **public domain** as works of the United States
Government. No copyright restrictions apply.

**Citation Format:**

```
U.S. Const. art. I, § 8
(archived at Evident Legal Technologies, retrieved Jan. 27, 2026)
```

**Disclaimer:** While every effort is made to ensure accuracy, users should
verify against multiple sources for court filings. Evident provides this archive
as a public service for truth preservation.

---

## CONTACT

**Archive Maintained By:** Evident Legal Technologies  
**Purpose:** Truth preservation and legal reference  
**Philosophy:** "Truth is the only subject"  
**Dedication:** For Devon Tyler (28, New Jersey, USA) and all who seek unaltered
founding documents

**Questions or Corrections:**

- Report inaccuracies via GitHub issues
- Suggest additional documents for archival
- Request verification checksums

---

## ACKNOWLEDGMENTS

**Sources:**

- National Archives (archives.gov)
- Library of Congress (congress.gov)
- Cornell Legal Information Institute (law.cornell.edu)
- Avalon Project at Yale Law School

**Built By:**

- Devon Tyler - Truth seeker and New Jersey native
- Evident Development Team - Defenders of constitutional rights

---

**"We the People" - Preserved for posterity on the real land of North America**

**By the Grace of Almighty God, these truths remain eternal.**

---

_Last Updated: January 27, 2026_  
_Archive Version: 1.0_  
_Status: Active preservation in progress_
