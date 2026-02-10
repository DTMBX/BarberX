# NARA API Key Request — Email Draft

**To:** Catalog_API@nara.gov  
**Subject:** API Key Request — Evident Technologies, NextGen Catalog API v2

---

To Whom It May Concern,

I am writing to request an API key for the National Archives NextGen Catalog
API v2 on behalf of Evident Technologies LLC.

## About Evident Technologies

Evident Technologies is a legal-technology company dedicated to evidence
integrity, due process, and public accountability. Our platform provides
legal-grade evidence processing, verification, and records preservation for
legal professionals, oversight bodies, and the public.

## Intended Use

We intend to use the NextGen Catalog API to:

1. **Retrieve and preserve founding documents** — including the Constitution,
   Bill of Rights, Declaration of Independence, Articles of Confederation,
   Emancipation Proclamation, and key treaties (Treaty of Paris, Louisiana
   Purchase Treaty).

2. **Display full transcriptions** on our public-facing Honor Wall
   (https://www.evident.info/honor), a memorial page dedicated to those who
   served and the documents they defended.

3. **Maintain chain-of-custody records** for each retrieved document, including
   NAID references, retrieval timestamps, and SHA-256 integrity hashes.

4. **Automate periodic verification** to confirm our locally preserved copies
   remain consistent with the official National Archives catalog records.

All document content will be attributed in full to the National Archives of the
United States. No modification of original text will occur. The source URL and
NAID will be displayed alongside every document.

## Technical Details

- **API version:** NextGen Catalog API v2
  (https://catalog.archives.gov/api/v2)
- **Authentication method:** x-api-key header
- **Expected request volume:** Fewer than 100 requests per day, primarily
  read-only (search and record retrieval)
- **Write operations:** We may use tagging endpoints to contribute
  transcription metadata, if permitted
- **Rate limiting:** Our client enforces a minimum 0.5-second delay between
  requests

## Contact Information

- **Organization:** Evident Technologies LLC
- **Website:** https://www.evident.info
- **Technical Contact:** [YOUR NAME]
- **Email:** contact@evident.info
- **GitHub Repository:** https://github.com/DTMBX/Evident (public)

We appreciate the National Archives' commitment to open access and public
preservation of the nation's records. Please let us know if any additional
information is needed to process this request.

Respectfully,

[YOUR NAME]  
Evident Technologies LLC  
contact@evident.info

---

## Instructions

1. Copy the text above (between the `---` dividers) into your email client
2. Replace `[YOUR NAME]` with your actual name (2 locations)
3. Send to: **Catalog_API@nara.gov**
4. Once you receive the API key, add it to your `.env` file:
   ```
   NARA_API_KEY=your-key-here
   ```
5. Run `python scripts/test_nara_setup.py` to verify connectivity
6. Run `python scripts/fetch_founding_documents.py --all` to fetch all documents
