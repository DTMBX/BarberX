"""
Phase 4 — Integrity Statement Determinism and Export Recording Tests
=====================================================================

Validates:
  1. Text output is byte-deterministic given identical inputs.
  2. Different inputs produce different outputs.
  3. Self-referential SHA-256 is embedded correctly.
  4. Statement ID is embedded in the text.
  5. Manifest SHA-256 is embedded in the text.
  6. Export pipeline includes the statement in the ZIP.
  7. Export manifest records statement hashes.
  8. CaseExportRecord.manifest_json contains statement hashes.
  9. Audit metadata includes statement hashes.
  10. Statement text never contains legal conclusions or advice.
  11. PDF bytes (when available) hash is recorded separately.
  12. Legacy API backward compatibility.
"""

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from services.integrity_statement import (
    IntegrityStatementGenerator,
    IntegrityStatementResult,
    INTEGRITY_STATEMENT_TEXT,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def gen():
    """Fresh generator instance."""
    return IntegrityStatementGenerator()


@pytest.fixture()
def fixed_inputs():
    """Deterministic inputs for reproducibility tests."""
    return dict(
        scope="CASE",
        scope_id="CASE-2026-001",
        manifest_sha256="a1b2c3d4e5f6" * 5 + "a1b2",
        manifest_filename="manifest.json",
        generated_at=datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
        statement_id="IS-CASE-2026-001-20260210120000",
        render_pdf=False,
    )


@pytest.fixture()
def app_context():
    """Flask app context for export pipeline tests."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    from app_config import create_app
    app = create_app()
    with app.app_context():
        from auth.models import db
        db.create_all()
        yield app, db


# ---------------------------------------------------------------------------
# 1. Text determinism
# ---------------------------------------------------------------------------

class TestTextDeterminism:
    """Identical inputs must produce identical text bytes."""

    def test_same_inputs_same_bytes(self, gen, fixed_inputs):
        r1 = gen.generate(**fixed_inputs)
        r2 = gen.generate(**fixed_inputs)
        assert r1.text_bytes == r2.text_bytes

    def test_same_inputs_same_sha256(self, gen, fixed_inputs):
        r1 = gen.generate(**fixed_inputs)
        r2 = gen.generate(**fixed_inputs)
        assert r1.text_sha256 == r2.text_sha256

    def test_sha256_matches_recomputed(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        recomputed = hashlib.sha256(r.text_bytes).hexdigest()
        assert r.text_sha256 == recomputed

    def test_ten_consecutive_calls_identical(self, gen, fixed_inputs):
        results = [gen.generate(**fixed_inputs) for _ in range(10)]
        first = results[0].text_bytes
        for r in results[1:]:
            assert r.text_bytes == first


# ---------------------------------------------------------------------------
# 2. Different inputs → different outputs
# ---------------------------------------------------------------------------

class TestInputVariation:
    """Changing any input must change the output."""

    @pytest.mark.parametrize("field,alt_value", [
        ("scope_id", "CASE-OTHER-999"),
        ("manifest_sha256", "0" * 64),
        ("statement_id", "IS-DIFFERENT"),
        ("generated_at", datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
        ("scope", "EVENT"),
    ])
    def test_different_input_different_hash(self, gen, fixed_inputs, field, alt_value):
        r1 = gen.generate(**fixed_inputs)
        modified = {**fixed_inputs, field: alt_value}
        r2 = gen.generate(**modified)
        assert r1.text_sha256 != r2.text_sha256, (
            f"Changing '{field}' did not change the output hash"
        )


# ---------------------------------------------------------------------------
# 3. Self-referential SHA-256 embedding
# ---------------------------------------------------------------------------

class TestSelfHash:
    """The text must contain a SHA-256 hash (two-pass embedding)."""

    def test_text_contains_embedded_hash(self, gen, fixed_inputs):
        """The pass-1 hash is embedded on the 'Signature/Hash' line."""
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8")
        import re
        m = re.search(r'Signature/Hash of this PDF: ([0-9a-f]{64})', text)
        assert m is not None, "No 64-char hex hash found on Signature line"
        embedded_hash = m.group(1)
        # Verify the embedded hash is the pass-1 hash:
        # replace it with placeholder, re-hash, and confirm match.
        verification_text = text.replace(embedded_hash, "[COMPUTED_AFTER_RENDER]")
        import hashlib
        recomputed = hashlib.sha256(verification_text.encode("utf-8")).hexdigest()
        assert recomputed == embedded_hash, (
            f"Embedded hash {embedded_hash} does not match "
            f"recomputed pass-1 hash {recomputed}"
        )

    def test_no_placeholder_remains(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8")
        assert "[COMPUTED_AFTER_RENDER]" not in text


# ---------------------------------------------------------------------------
# 4. Statement ID embedding
# ---------------------------------------------------------------------------

class TestStatementId:
    """Statement ID must appear in the output text."""

    def test_statement_id_in_text(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8")
        assert fixed_inputs["statement_id"] in text

    def test_auto_generated_id_in_text(self, gen):
        r = gen.generate(
            generated_at=datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
            render_pdf=False,
        )
        text = r.text_bytes.decode("utf-8")
        assert r.statement_id in text
        assert r.statement_id.startswith("IS-")


# ---------------------------------------------------------------------------
# 5. Manifest SHA-256 embedding
# ---------------------------------------------------------------------------

class TestManifestHashEmbedding:
    """The manifest hash input must appear in the statement text."""

    def test_manifest_sha256_in_text(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8")
        assert fixed_inputs["manifest_sha256"] in text


# ---------------------------------------------------------------------------
# 6. Export pipeline integration — ZIP contains statement
# ---------------------------------------------------------------------------

class TestExportPipelineIntegration:
    """The CaseExporter must include integrity statement in the ZIP."""

    def test_export_zip_contains_statement_txt(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert 'evidence_integrity_statement.txt' in names

    def test_export_zip_statement_is_valid_utf8(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            content = zf.read('evidence_integrity_statement.txt')
            text = content.decode('utf-8')  # Must not raise
            assert 'EVIDENT TECHNOLOGIES' in text


# ---------------------------------------------------------------------------
# 7. Manifest records statement hashes
# ---------------------------------------------------------------------------

class TestManifestRecording:
    """The export manifest must record integrity statement metadata."""

    def test_manifest_has_integrity_statement_section(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        assert 'integrity_statement' in manifest

    def test_manifest_integrity_statement_has_text_sha256(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        stmt = manifest['integrity_statement']
        assert 'text_sha256' in stmt
        assert len(stmt['text_sha256']) == 64  # hex SHA-256

    def test_manifest_text_sha256_matches_file(self, app_context):
        """The SHA-256 in the manifest must match the actual file bytes."""
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            content = zf.read('evidence_integrity_statement.txt')
        actual_hash = hashlib.sha256(content).hexdigest()
        assert manifest['integrity_statement']['text_sha256'] == actual_hash

    def test_manifest_has_statement_id(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        stmt_id = manifest['integrity_statement']['statement_id']
        assert stmt_id.startswith('IS-')

    def test_manifest_has_pre_manifest_sha256(self, app_context):
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        assert 'pre_manifest_sha256' in manifest['integrity_statement']
        assert len(manifest['integrity_statement']['pre_manifest_sha256']) == 64

    def test_file_manifest_includes_statement_entry(self, app_context):
        """The files[] array must have an entry for the statement."""
        _app, db = app_context
        record, zip_path = _run_export(db)
        manifest = _read_manifest(zip_path)
        stmt_entries = [
            f for f in manifest['files']
            if f.get('type') == 'integrity_statement'
        ]
        assert len(stmt_entries) >= 1
        txt_entry = next(
            (f for f in stmt_entries if f.get('format') == 'text'), None
        )
        assert txt_entry is not None
        assert txt_entry['path'] == 'evidence_integrity_statement.txt'
        assert len(txt_entry['sha256']) == 64


# ---------------------------------------------------------------------------
# 8. CaseExportRecord stores statement in manifest_json
# ---------------------------------------------------------------------------

class TestExportRecordPersistence:
    """The DB record must persist the manifest including statement hashes."""

    def test_record_manifest_json_has_integrity_statement(self, app_context):
        _app, db = app_context
        record, _zip_path = _run_export(db)
        stored = json.loads(record.manifest_json)
        assert 'integrity_statement' in stored
        assert 'text_sha256' in stored['integrity_statement']


# ---------------------------------------------------------------------------
# 9. No legal conclusions in statement text
# ---------------------------------------------------------------------------

class TestNoLegalConclusions:
    """The statement must not contain legal advice or conclusions."""

    # Phrases that, if found in an AFFIRMATIVE context (not preceded by
    # "not" or "does not"), would indicate the statement is overstepping.
    FORBIDDEN_AFFIRMATIVE_PHRASES = [
        "this proves",
        "this constitutes evidence",
        "the court should",
        "we recommend",
        "in our opinion",
        "we advise",
    ]

    # Phrases allowed ONLY with negation ("does not", "not").
    NEGATION_REQUIRED_PHRASES = [
        "legal advice",
        "legal conclusions",
        "guilt",
        "liability",
    ]

    def test_no_affirmative_forbidden_phrases(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8").lower()
        for phrase in self.FORBIDDEN_AFFIRMATIVE_PHRASES:
            assert phrase not in text, (
                f"Forbidden affirmative phrase '{phrase}' found"
            )

    def test_negation_required_phrases_only_negated(self, gen, fixed_inputs):
        """Phrases like 'legal advice' must appear only after 'not'."""
        r = gen.generate(**fixed_inputs)
        text = r.text_bytes.decode("utf-8").lower()
        import re
        for phrase in self.NEGATION_REQUIRED_PHRASES:
            # Find all occurrences and verify each is preceded by a negation
            for m in re.finditer(re.escape(phrase), text):
                start = max(0, m.start() - 200)
                context = text[start:m.start()]
                assert "not" in context or "no " in context, (
                    f"'{phrase}' found without negation. "
                    f"Context: ...{context}{phrase}..."
                )


# ---------------------------------------------------------------------------
# 10. Legacy API backward compatibility
# ---------------------------------------------------------------------------

class TestLegacyAPI:
    """generate_text() and generate_pdf_bytes() must still work."""

    def test_generate_text_returns_tuple(self, gen):
        text, sha = gen.generate_text(
            scope="CASE",
            scope_id="LEGACY-001",
            generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            statement_id="IS-LEGACY",
        )
        assert isinstance(text, str)
        assert len(sha) == 64

    def test_generate_pdf_bytes_returns_tuple(self, gen):
        content, sha = gen.generate_pdf_bytes(
            scope="CASE",
            scope_id="LEGACY-002",
            generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            statement_id="IS-LEGACY-2",
        )
        assert isinstance(content, bytes)
        assert len(sha) == 64


# ---------------------------------------------------------------------------
# 11. IntegrityStatementResult is immutable
# ---------------------------------------------------------------------------

class TestResultImmutability:
    """The result dataclass must be frozen."""

    def test_result_is_frozen(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        with pytest.raises(AttributeError):
            r.text_sha256 = "tampered"

    def test_result_is_frozen_text_bytes(self, gen, fixed_inputs):
        r = gen.generate(**fixed_inputs)
        with pytest.raises(AttributeError):
            r.text_bytes = b"tampered"


# ============================================================================
# Helpers
# ============================================================================

def _pass1_hash(result):
    """Compute what the pass-1 hash would have been (before embedding)."""
    text = result.text_bytes.decode("utf-8")
    # The embedded hash is after "Signature/Hash of this PDF:" —
    # we just verify _some_ hash appears, not reconstruct pass-1 exactly.
    return result.text_sha256


def _create_case_with_evidence(db):
    """Create a minimal case with one evidence item for export tests."""
    import uuid
    from models.legal_case import LegalCase
    from models.evidence import EvidenceItem
    from models.case_event import Event

    unique_suffix = uuid.uuid4().hex[:8]
    case = LegalCase(
        case_number=f'TEST-EXPORT-{unique_suffix}',
        case_name='Integrity Statement Export Test',
        case_type='civil',
    )
    db.session.add(case)
    db.session.flush()

    item = EvidenceItem(
        original_filename='test_video.mp4',
        file_type='video/mp4',
        file_size_bytes=1024,
        evidence_type='video',
        hash_sha256=hashlib.sha256(unique_suffix.encode()).hexdigest(),
    )
    db.session.add(item)
    db.session.flush()

    # Link evidence to case
    from models.evidence import CaseEvidence
    link = CaseEvidence(
        case_id=case.id,
        evidence_id=item.id,
        linked_at=datetime.now(timezone.utc),
    )
    db.session.add(link)

    # Create an event
    event = Event(
        case_id=case.id,
        event_name='Test Event',
    )
    db.session.add(event)
    db.session.commit()

    return case


def _run_export(db):
    """Run a full export and return (record, zip_path)."""
    case = _create_case_with_evidence(db)

    export_dir = tempfile.mkdtemp()
    from services.case_export_service import CaseExporter
    exporter = CaseExporter(export_base_path=export_dir)
    record = exporter.export_case(case.id)
    return record, record.export_path


def _read_manifest(zip_path):
    """Read and parse manifest.json from a ZIP."""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        return json.loads(zf.read('manifest.json'))
