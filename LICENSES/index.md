---
title: 'Licensing & IP Index'
description:
  'Single entry point for proprietary IP notices, third-party licenses, and
  governance documents for Evident.'
permalink: /licenses/
---

# Evident Technologies — Licensing & IP Index

This page is the **single entry point** for licensing, attribution, and
IP-governance materials for the Evident platform.

It is designed for **enterprise counsel, courts, investors, auditors, and
technical reviewers** who need an accurate, navigable view of:

- what is proprietary,
- what is third-party,
- which licenses apply,
- and what governance documents control usage and exports.

> This index is informational and does not modify any license text.

---

## 1) Quick Start (What to Read First)

### If you are conducting a license compliance review

1. **IP & Licensing Policy** → `IP-LICENSING-POLICY.md`
2. **Third-party license texts** → `MIT-LICENSE.txt`,
   `BSD-3-CLAUSE-LICENSE.txt`, `APACHE-2.0-LICENSE.txt`
3. **FFmpeg licensing posture** → `FFMPEG-GPL-WARNING.md`

### If you are reviewing evidentiary handling and export boundaries

1. **Evidence Ownership & Liability Boundary** →
   `EVIDENCE-OWNERSHIP-AND-LIABILITY.md`
2. **Export footer notice** → `EXPORT-FOOTER-LANGUAGE.md`
3. **About the Technology (court-ready)** → `ABOUT-THE-TECHNOLOGY-AFFIDAVIT.md`

### If you are contributing code

1. **Contributor Policy (No CLA)** → `CONTRIBUTOR-POLICY.md`

### If you are performing diligence / investment review

1. **Investor IP Summary (1 page)** → `INVESTOR-IP-SUMMARY.md`
2. **Trade Secret Declaration (internal governance)** →
   `TRADE-SECRET-DECLARATION.md`

---

## 2) Proprietary vs. Third-Party: Scope and Boundaries

### Proprietary (All Rights Reserved)

Evident’s proprietary systems (including evidence integrity controls,
chain-of-custody workflows, audit mechanisms, and export verification processes)
are **not open source** and are protected as proprietary intellectual property
and trade secrets.

Authoritative policy document:

- `IP-LICENSING-POLICY.md`

Trade secret governance record:

- `TRADE-SECRET-DECLARATION.md`

### Third-Party Open Source

Evident incorporates third-party software governed by the licenses listed below.
All third-party components retain their original license terms. Full license
texts are provided in this directory.

---

## 3) Third-Party License Texts (Canonical Copies)

These files contain full license texts used by third-party dependencies.

- **MIT License** → `MIT-LICENSE.txt`
- **BSD 3-Clause License** → `BSD-3-CLAUSE-LICENSE.txt`
- **Apache License 2.0** → `APACHE-2.0-LICENSE.txt`

Repository-level licensing inventory and process notes:

- `README.md`

---

## 4) FFmpeg: LGPL-Only Posture (Media Processing)

Evident uses **LGPL-only FFmpeg builds** (no GPL components) to avoid copyleft
conflicts with proprietary software distribution models.

Documentation and verification notes:

- `FFMPEG-GPL-WARNING.md`
- `FFMPEG-GPL-WARNING.txt`

---

## 5) Governance Documents (Non-License, High-Authority)

These documents govern how the system is positioned, used, and relied upon. They
do not replace license texts; they define **boundaries, representations, and
risk posture**.

- **IP & Licensing Policy** → `IP-LICENSING-POLICY.md`
- **Evidence Ownership & Liability Boundary** →
  `EVIDENCE-OWNERSHIP-AND-LIABILITY.md`
- **Contributor Policy (No CLA)** → `CONTRIBUTOR-POLICY.md`
- **Export Footer Language** → `EXPORT-FOOTER-LANGUAGE.md`
- **About the Technology (Court-Ready Statement)** →
  `ABOUT-THE-TECHNOLOGY-AFFIDAVIT.md`
- **Investor IP Summary (1 Page)** → `INVESTOR-IP-SUMMARY.md`

---

## 6) Attribution & Additional Materials (If Present Elsewhere)

If your repository also contains:

- `THIRD-PARTY-LICENSES.md`
- `ATTRIBUTION.md`

those documents typically provide dependency-by-dependency listings and
acknowledgments. This directory contains the **canonical full license texts**.

---

## 7) Operational Guidance for Releases

For each public release or customer delivery, recommended minimum checks:

- Confirm third-party license texts remain current for your pinned dependency
  versions
- Confirm FFmpeg remains LGPL-only (no `--enable-gpl` in the build
  configuration)
- Ensure exports include the current footer notice and any manifest integrity
  fields
- Retain this `LICENSES/` directory in distributed packages where required by
  third-party licenses

---

## 8) Contact

Licensing / IP inquiries: **legal@evident.info**
