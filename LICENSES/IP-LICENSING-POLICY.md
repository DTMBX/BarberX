# Evident Technologies

## Intellectual Property & Licensing Policy

**Last Updated:** 2026-02-03

---

## 1. Purpose

This policy explains how Evident Technologies licenses, protects, and deploys
its software, including the relationship between proprietary components and
third-party open-source software. It is intended to provide clarity to users,
contributors, courts, investors, and enterprise reviewers.

This document is interpretive and explanatory. It does not replace or modify any
applicable license text.

---

## 2. Proprietary Core Systems

Evident Technologies retains exclusive ownership of its proprietary systems,
including but not limited to:

- Evidence integrity and verification logic
- Chain-of-custody workflows and audit mechanisms
- Hashing, manifest generation, and tamper-evident controls
- Evidence export orchestration and verification reporting
- Internal orchestration, sequencing, and control logic

These components are **not open source**, are **not licensed for
redistribution**, and are protected as **copyrighted works and trade secrets**.

All rights not expressly granted are reserved.

---

## 3. Open-Source and Third-Party Components

Evident incorporates third-party open-source software under permissive and
compatible licenses, including but not limited to:

- MIT License
- BSD 3-Clause License
- Apache License 2.0
- LGPL 2.1 (dynamic linking only)

Each third-party dependency retains its original license and attribution. Full
license texts and attributions are maintained in the repository under
`LICENSES/` and `THIRD-PARTY-LICENSES.md`.

No third-party license grants rights to Evident’s proprietary systems.

---

## 4. FFmpeg and LGPL Compliance

Where multimedia processing is performed, Evident uses **LGPL-only FFmpeg
builds** via dynamic linking.  
No GPL-licensed FFmpeg components are included.

This architecture permits proprietary software use without triggering
source-disclosure obligations, in compliance with the LGPL.

---

## 5. Artificial Intelligence Models

Evident may execute third-party machine learning or AI models locally for
analytical assistance.

- Evident **does not claim ownership** of third-party model weights or
  architectures.
- Evident **does claim exclusive rights** to its proprietary workflows,
  integrity controls, and evidence-verification processes that coordinate and
  contextualize model output.

Model-assisted analysis does not constitute legal advice or factual
adjudication.

---

## 6. Outputs and Evidence Artifacts

Users retain ownership of:

- Uploaded source evidence
- Derived exhibits and exports generated from their data

Evident retains ownership of:

- The software platform
- The processing systems
- The integrity and verification mechanisms

Evident does not claim ownership over user data or evidence content.

---

## 7. No License by Implication

No rights are granted by implication, estoppel, or inference.  
Use of Evident software does not convey any ownership interest in proprietary
systems.

---

## 8. Questions

Licensing or IP questions may be directed to:

**legal@evident.info**
