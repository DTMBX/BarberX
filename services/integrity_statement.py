"""
Evidence Integrity Statement — Deterministic Generator
=======================================================
Generates a deterministic, court-ready Evidence Integrity Statement from
the verbatim template text defined below.

The text is fixed and neutral — no AI variation, no legal advice, no
jurisdiction-specific conclusions. Bracketed fields are populated at
build time from system metadata.

Determinism contract:
  - The **text** output is byte-deterministic: identical inputs produce
    identical UTF-8 bytes.  This is the authoritative artifact.
  - The **PDF** render (via reportlab, if available) is a convenience
    derivative. Reportlab embeds internal metadata that may vary between
    runs, so PDF bytes are NOT guaranteed reproducible.  The PDF-bytes
    SHA-256 is recorded separately from the text-content SHA-256.

Usage:
    from services.integrity_statement import IntegrityStatementGenerator
    gen = IntegrityStatementGenerator()
    result = gen.generate(
        scope="CASE",
        scope_id="CASE-2025-001",
        manifest_sha256="abc123...",
        generated_at=datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
    )
    # result.text_bytes        — deterministic UTF-8 bytes
    # result.text_sha256       — SHA-256 of text_bytes
    # result.pdf_bytes         — PDF bytes (or None)
    # result.pdf_sha256        — SHA-256 of pdf_bytes (or None)
    # result.statement_id      — document ID embedded in the text
"""

import hashlib
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


# ---------------------------------------------------------------------------
# Verbatim template text — this is the authoritative integrity statement.
# It MUST NOT be modified by AI, paraphrased, or summarized.
# ---------------------------------------------------------------------------

INTEGRITY_STATEMENT_TEXT = textwrap.dedent("""\
EVIDENT TECHNOLOGIES LLC — EVIDENCE INTEGRITY STATEMENT

Document ID: {integrity_statement_id}
Generated: {generated_timestamp}
System/Build: {app_name} {version} ({git_commit})
Export Scope: {scope}
Scope Identifier: {scope_id}


1. Purpose

This document describes how the Evident system ingests, stores, processes, \
and exports digital evidence while preserving integrity and producing \
verifiable outputs. It is a technical integrity statement and does not \
provide legal advice or legal conclusions.


2. What Evident Does (Technical Functions)

Evident provides:

  - Ingestion of files (e.g., PDF, image, audio, video) into an evidence store.
  - Cryptographic hashing (SHA-256) to identify and verify file integrity.
  - Immutable storage of original files ("originals").
  - Generation of derivative files (e.g., video thumbnails and review proxies) \
that are explicitly linked to their originals.
  - Append-only audit logging of key evidence-handling events.
  - Export packaging (ZIP) containing evidence, manifests, and audit records to \
support independent verification.


3. What Evident Does Not Do (Limitations)

Evident does not:

  - Alter, enhance, filter, or otherwise modify original evidence files.
  - Determine authenticity, intent, fault, liability, or credibility of \
persons or events.
  - Provide legal conclusions or jurisdiction-specific legal determinations.
  - Create or infer facts not present in the uploaded evidence and recorded \
metadata.


4. Evidence Identity and Hashing

4.1 Hash Algorithm
Evident computes a SHA-256 hash for each ingested file. The SHA-256 hash \
is recorded and used as an integrity identifier for the bytes of that file.

4.2 Duplicate Detection
If a file is ingested whose SHA-256 hash matches an existing stored item, \
Evident treats it as the same underlying bytes. The system may link the \
existing evidence item to additional cases/events without duplicating the \
original bytes.

4.3 Hash Verification
A party can independently compute SHA-256 hashes on exported files and \
compare them to the hashes recorded in the export manifest(s).


5. Immutability of Originals

5.1 Immutable Originals
Original evidence files are stored as immutable objects. Evident does not \
overwrite original bytes. If a different file is later uploaded, it results \
in a different SHA-256 hash and a distinct evidence identity.

5.2 Provenance via Audit and Links
Case and event membership are stored as relationships. Linking evidence to \
a case or event does not modify original evidence content.


6. Derivatives and Referential Integrity

6.1 Derivative Definition
Derivatives include outputs such as:
  - Video thumbnails (e.g., first frame, mid-stream frame)
  - Review proxies (lower-resolution viewing copies)
  - Manifests and reports generated for export and verification

6.2 Derivative Hashing
Each derivative is hashed (SHA-256) and recorded. Each derivative references \
its originating evidence item (original hash/identifier) to preserve \
traceability.

6.3 No Derivative Substitution of Originals
Derivatives are provided for review and organization only. The original \
evidence remains the authoritative stored file.


7. Event Synchronization (Body-Worn Camera Cross-Sync)

7.1 Metadata-Only Alignment
Where multiple videos are associated to the same event, Evident may record \
synchronization offsets (e.g., milliseconds) as metadata to support aligned \
playback and event timelines.

7.2 No Frame Modification
Synchronization does not modify video frames or audio samples in the original \
files. The system stores offsets and timing metadata only.

7.3 Sealed Events
If an event is marked sealed, synchronization metadata and event membership \
are restricted to prevent post hoc changes. Any permitted modifications (if \
enabled) are recorded in the audit log.


8. Audit Logging (Append-Only)

8.1 Audit Model
Evident records evidence-handling events in an append-only audit stream. \
Typical events include:
  - evidence_ingested
  - hash_computed
  - derivative_created
  - case_link_added / event_link_added
  - event_sync_offset_updated
  - event_sealed (if applicable)
  - export_generated

8.2 Immutability of Audit Records
Audit entries are appended and are not silently edited or removed by normal \
application operations. If a correction mechanism exists, it must append \
corrective entries rather than overwrite prior entries.


9. Export Packaging and Reproducibility

9.1 Export Contents
Exports may include:
  - Originals (or references, depending on configuration)
  - Derivatives
  - Manifest JSON files listing hashes and relationships
  - Audit log slice(s) applicable to the exported scope
  - This integrity statement (PDF)

9.2 Reproducibility Principle
An export is considered reproducible if:
  - The exported hashes match the manifest hashes, and
  - Re-exporting the same scope from the same stored originals and recorded \
transformations yields matching content hashes for included artifacts.


10. Independent Verification Procedure

To verify an export:

  1. Extract the ZIP export to a local folder.
  2. Locate the manifest file: {manifest_filename}.
  3. Compute SHA-256 hashes of exported files using an independent tool.
  4. Compare computed hashes to the hashes recorded in the manifest.
  5. Review audit_log.json to confirm the sequence of ingest, derivative \
creation, synchronization metadata actions (if applicable), and export \
generation.

If any hash does not match, the export integrity is not verified.


11. Attestation

This document is generated by the Evident system as part of the export \
process. It describes system behavior and provides verification instructions. \
It does not attest to external authenticity beyond the cryptographic and audit \
properties described herein.

Generated by: {system_component}
Signature/Hash of this PDF: {pdf_sha256}
Manifest Hash: {manifest_sha256}
""")


class IntegrityStatementGenerator:
    """
    Generates a deterministic Evidence Integrity Statement.

    All variable inputs (timestamp, statement ID) are accepted as
    explicit parameters so that identical inputs always produce
    identical output bytes (for the text path).
    """

    def generate(
        self,
        scope: str = "EVIDENCE_ITEM",
        scope_id: str = "",
        manifest_sha256: str = "",
        manifest_filename: str = "manifest.json",
        app_name: str = "Evident",
        version: str = "2.0.0",
        git_commit: str = "unknown",
        system_component: str = "IntegrityStatementGenerator",
        generated_at: Optional[datetime] = None,
        statement_id: Optional[str] = None,
        render_pdf: bool = True,
    ) -> "IntegrityStatementResult":
        """
        Generate the integrity statement as text and (optionally) PDF.

        Args:
            generated_at: Explicit UTC timestamp.  If None, uses now().
                          Pass a fixed value for deterministic output.
            statement_id: Explicit document ID.  If None, one is derived
                          from the timestamp + a random suffix.
            render_pdf:   If True and reportlab is available, produce PDF.

        Returns:
            IntegrityStatementResult with text_bytes, text_sha256,
            pdf_bytes (or None), pdf_sha256 (or None), statement_id.
        """
        if generated_at is None:
            generated_at = datetime.now(timezone.utc)

        if statement_id is None:
            statement_id = (
                f"IS-{generated_at.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
            )

        timestamp_str = generated_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        # --- Pass 1: render text with placeholder for self-hash ---
        text = INTEGRITY_STATEMENT_TEXT.format(
            integrity_statement_id=statement_id,
            generated_timestamp=timestamp_str,
            app_name=app_name,
            version=version,
            git_commit=git_commit,
            scope=scope,
            scope_id=scope_id,
            manifest_filename=manifest_filename,
            manifest_sha256=manifest_sha256,
            system_component=system_component,
            pdf_sha256="[COMPUTED_AFTER_RENDER]",
        )

        # --- Pass 2: compute text hash, embed it ---
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        text = text.replace("[COMPUTED_AFTER_RENDER]", text_hash)

        text_bytes = text.encode("utf-8")
        text_sha256 = hashlib.sha256(text_bytes).hexdigest()

        # --- Optional PDF render ---
        pdf_bytes = None
        pdf_sha256 = None
        if render_pdf:
            try:
                pdf_bytes, pdf_sha256 = self._render_reportlab(text)
            except ImportError:
                pass  # reportlab not installed — skip PDF

        return IntegrityStatementResult(
            text_bytes=text_bytes,
            text_sha256=text_sha256,
            pdf_bytes=pdf_bytes,
            pdf_sha256=pdf_sha256,
            statement_id=statement_id,
        )

    # --- Legacy convenience wrappers (backward compatibility) ---

    def generate_text(self, **kwargs):
        """Return (text_string, text_sha256).  Legacy API."""
        result = self.generate(render_pdf=False, **kwargs)
        return result.text_bytes.decode("utf-8"), result.text_sha256

    def generate_pdf_bytes(self, **kwargs):
        """Return (bytes, sha256).  Legacy API — returns PDF if possible, else text."""
        result = self.generate(render_pdf=True, **kwargs)
        if result.pdf_bytes is not None:
            return result.pdf_bytes, result.pdf_sha256
        return result.text_bytes, result.text_sha256

    @staticmethod
    def _render_reportlab(text: str):
        """Render text to PDF using reportlab.  Returns (pdf_bytes, sha256)."""
        from io import BytesIO

        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        story = []
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("EVIDENT TECHNOLOGIES"):
                story.append(Paragraph(stripped, styles["Title"]))
            elif stripped and stripped[0].isdigit() and "." in stripped[:4]:
                story.append(Spacer(1, 12))
                story.append(Paragraph(stripped, styles["Heading2"]))
            elif stripped.startswith("-"):
                story.append(
                    Paragraph(f"&bull; {stripped[1:].strip()}", styles["Normal"])
                )
            elif stripped:
                story.append(Paragraph(stripped, styles["Normal"]))
            else:
                story.append(Spacer(1, 6))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
        return pdf_bytes, pdf_hash


@dataclass(frozen=True)
class IntegrityStatementResult:
    """Immutable result of integrity statement generation."""

    text_bytes: bytes
    """Deterministic UTF-8 text — the authoritative artifact."""

    text_sha256: str
    """SHA-256 hex digest of text_bytes."""

    pdf_bytes: Optional[bytes]
    """PDF render (None if reportlab unavailable or render_pdf=False)."""

    pdf_sha256: Optional[str]
    """SHA-256 hex digest of pdf_bytes (None if no PDF)."""

    statement_id: str
    """Document ID embedded in the statement text."""
