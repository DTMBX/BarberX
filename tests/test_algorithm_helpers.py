"""
Unit tests for algorithm helper functions.
============================================
Tests standalone utility functions that do not require DB access.
Targets coverage gaps in:
  - bulk_dedup.py (perceptual hashing, hamming distance, similarity)
  - redaction_verify.py (text-layer check, annotation check, byte leakage)
  - access_anomaly.py (share-link abuse, auth failures, off-hours access)
  - bates_generator.py (Bates number generation, text-marker fallback)
"""

import io
import struct
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Bulk Dedup helpers
# ---------------------------------------------------------------------------

class TestHammingDistance:
    """Tests for _hamming_distance."""

    def test_identical_hashes(self):
        from algorithms.bulk_dedup import _hamming_distance
        assert _hamming_distance("ff", "ff") == 0

    def test_one_bit_different(self):
        from algorithms.bulk_dedup import _hamming_distance
        # 0x0f = 0000_1111, 0x0e = 0000_1110 → 1 bit different
        assert _hamming_distance("0f", "0e") == 1

    def test_all_bits_different(self):
        from algorithms.bulk_dedup import _hamming_distance
        # 0x00 vs 0xff → 8 bits different
        assert _hamming_distance("00", "ff") == 8

    def test_multi_byte(self):
        from algorithms.bulk_dedup import _hamming_distance
        assert _hamming_distance("0000", "0001") == 1

    def test_unequal_length_returns_negative(self):
        from algorithms.bulk_dedup import _hamming_distance
        assert _hamming_distance("ff", "ffff") == -1


class TestSimilarityScore:
    """Tests for _similarity_score."""

    def test_identical(self):
        from algorithms.bulk_dedup import _similarity_score
        assert _similarity_score(0, 64) == 1.0

    def test_completely_different(self):
        from algorithms.bulk_dedup import _similarity_score
        assert _similarity_score(64, 64) == 0.0

    def test_half_similar(self):
        from algorithms.bulk_dedup import _similarity_score
        assert _similarity_score(32, 64) == 0.5

    def test_zero_total_bits(self):
        from algorithms.bulk_dedup import _similarity_score
        assert _similarity_score(0, 0) == 0.0


class TestComputeAverageHash:
    """Tests for _compute_average_hash."""

    def test_valid_image_returns_hex_string(self):
        from algorithms.bulk_dedup import _compute_average_hash
        # Create a minimal valid PNG-like image via PIL
        from PIL import Image

        img = Image.new("L", (16, 16), color=128)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        result = _compute_average_hash(buf.getvalue(), hash_size=8)
        assert result is not None
        assert isinstance(result, str)
        # 8x8 → 64 bits → 16 hex chars
        assert len(result) == 16

    def test_deterministic_same_image(self):
        from algorithms.bulk_dedup import _compute_average_hash
        from PIL import Image

        img = Image.new("L", (32, 32), color=200)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = buf.getvalue()
        h1 = _compute_average_hash(data)
        h2 = _compute_average_hash(data)
        assert h1 == h2

    def test_different_images_different_hashes(self):
        from algorithms.bulk_dedup import _compute_average_hash
        from PIL import Image

        # Create images with different patterns (not solid) so aHash differs.
        # Solid-color images all produce the same hash (all-zeros) because
        # every pixel equals the mean.
        img_a = Image.new("L", (16, 16), color=0)
        # Create a gradient so that some pixels are above the mean
        pixels_a = list(range(256))  # 0..255
        img_a = Image.new("L", (16, 16))
        img_a.putdata(pixels_a)
        buf_a = io.BytesIO()
        img_a.save(buf_a, format="PNG")

        # Inverted gradient
        pixels_b = list(range(255, -1, -1))
        img_b = Image.new("L", (16, 16))
        img_b.putdata(pixels_b)
        buf_b = io.BytesIO()
        img_b.save(buf_b, format="PNG")

        ha = _compute_average_hash(buf_a.getvalue())
        hb = _compute_average_hash(buf_b.getvalue())
        assert ha != hb

    def test_invalid_bytes_returns_none(self):
        from algorithms.bulk_dedup import _compute_average_hash
        result = _compute_average_hash(b"not an image at all")
        assert result is None


# ---------------------------------------------------------------------------
# Redaction Verify helpers
# ---------------------------------------------------------------------------

class TestCheckPdfTextLayer:
    """Tests for _check_pdf_text_layer."""

    def test_non_pdf_bytes_returns_error_or_none(self):
        from algorithms.redaction_verify import _check_pdf_text_layer
        result = _check_pdf_text_layer(b"this is not a pdf")
        # Should return a dict with has_text_layer=None and an error
        assert result["has_text_layer"] is None
        assert "error" in result or "note" in result

    def test_valid_pdf_returns_dict(self):
        """If PyPDF2 is available, exercise the reader path with a minimal PDF."""
        from algorithms.redaction_verify import _check_pdf_text_layer
        # Create minimal valid PDF
        pdf = _make_minimal_pdf()
        result = _check_pdf_text_layer(pdf)
        assert isinstance(result, dict)
        assert "has_text_layer" in result
        assert "extracted_length" in result


class TestCheckAnnotationRedactions:
    """Tests for _check_annotation_redactions."""

    def test_non_pdf_bytes(self):
        from algorithms.redaction_verify import _check_annotation_redactions
        result = _check_annotation_redactions(b"not-a-pdf")
        assert isinstance(result, dict)
        assert result["total_annotations"] == 0

    def test_valid_pdf_no_annotations(self):
        from algorithms.redaction_verify import _check_annotation_redactions
        pdf = _make_minimal_pdf()
        result = _check_annotation_redactions(pdf)
        assert isinstance(result, dict)
        assert result["redaction_annotations"] == 0
        assert result["has_unapplied_redactions"] is False or result["has_unapplied_redactions"] is None


class TestCheckByteLeakage:
    """Tests for _check_byte_leakage."""

    def test_no_leakage(self):
        from algorithms.redaction_verify import _check_byte_leakage
        original = b"A" * 100 + b"SENSITIVE CONTENT HERE GOES ON AND ON FOR MANY CHARS" + b"A" * 100
        redacted = b"B" * 200 + b"REDACTED" * 20
        result = _check_byte_leakage(original, redacted, sample_size=50)
        assert isinstance(result, dict)
        assert result["potential_leakage"] is False

    def test_leakage_detected(self):
        from algorithms.redaction_verify import _check_byte_leakage
        # Use non-printable byte (\x00) to separate segments so the extractor
        # finds 'shared_segment' as its own run rather than merging it with
        # surrounding text.
        shared_segment = b"ThisIsALongSegmentThatShouldBeDetectedAsLeakageInTheRedactedVersion!!"
        original = b"START" + b"\x00" + shared_segment + b"\x00" + b"END"
        redacted = b"REDACTED" + b"\x00" + shared_segment + b"\x00" + b"DONE"
        result = _check_byte_leakage(original, redacted, sample_size=10)
        assert result["potential_leakage"] is True
        assert result["segments_found_in_redacted"] > 0

    def test_empty_original(self):
        from algorithms.redaction_verify import _check_byte_leakage
        result = _check_byte_leakage(b"", b"anything", sample_size=10)
        assert result["segments_checked"] == 0
        assert result["potential_leakage"] is False

    def test_sample_size_larger_than_content(self):
        from algorithms.redaction_verify import _check_byte_leakage
        result = _check_byte_leakage(b"short", b"short", sample_size=50)
        assert result["segments_checked"] == 0


# ---------------------------------------------------------------------------
# Access Anomaly helpers
# ---------------------------------------------------------------------------

class TestDetectShareLinkAbuse:
    """Tests for _detect_share_link_abuse."""

    def test_no_share_events_returns_empty(self):
        from algorithms.access_anomaly import _detect_share_link_abuse
        entries = [
            {"action": "download", "ip_address": "1.2.3.4",
             "timestamp": datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)},
        ]
        result = _detect_share_link_abuse(entries, window_minutes=60, threshold=3)
        assert result == []

    def test_abuse_detected(self):
        from algorithms.access_anomaly import _detect_share_link_abuse
        base = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        entries = [
            {"action": "share_link_accessed", "ip_address": "10.0.0.1",
             "timestamp": base + timedelta(minutes=i)}
            for i in range(10)
        ]
        result = _detect_share_link_abuse(entries, window_minutes=60, threshold=5)
        assert len(result) == 1
        assert result[0]["type"] == "share_link_abuse"
        assert result[0]["ip_address"] == "10.0.0.1"

    def test_below_threshold_no_anomaly(self):
        from algorithms.access_anomaly import _detect_share_link_abuse
        base = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        entries = [
            {"action": "share_link_accessed", "ip_address": "10.0.0.1",
             "timestamp": base + timedelta(minutes=i)}
            for i in range(3)
        ]
        result = _detect_share_link_abuse(entries, window_minutes=60, threshold=5)
        assert result == []


class TestDetectAuthFailures:
    """Tests for _detect_auth_failures."""

    def test_no_failures_returns_empty(self):
        from algorithms.access_anomaly import _detect_auth_failures
        entries = [
            {"action": "download", "ip_address": "1.2.3.4",
             "timestamp": datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)},
        ]
        result = _detect_auth_failures(entries, window_minutes=15, threshold=3)
        assert result == []

    def test_auth_burst_detected(self):
        from algorithms.access_anomaly import _detect_auth_failures
        base = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        entries = [
            {"action": "auth_fail_login", "ip_address": "192.168.1.1",
             "timestamp": base + timedelta(seconds=i * 10)}
            for i in range(15)
        ]
        result = _detect_auth_failures(entries, window_minutes=15, threshold=10)
        assert len(result) == 1
        assert result[0]["type"] == "auth_failure_burst"
        assert result[0]["severity"] == "alert"

    def test_below_threshold_no_anomaly(self):
        from algorithms.access_anomaly import _detect_auth_failures
        base = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        entries = [
            {"action": "auth_fail_login", "ip_address": "192.168.1.1",
             "timestamp": base + timedelta(seconds=i * 10)}
            for i in range(5)
        ]
        result = _detect_auth_failures(entries, window_minutes=15, threshold=10)
        assert result == []


class TestDetectOffHoursAccess:
    """Tests for _detect_off_hours_access."""

    def test_off_hours_detected(self):
        from algorithms.access_anomaly import _detect_off_hours_access
        # Create 10 entries at 2 AM UTC (well within off-hours 22:00-06:00)
        entries = [
            {"action": "view", "actor": "night-owl",
             "timestamp": datetime(2024, 1, i + 1, 2, 0, tzinfo=timezone.utc)}
            for i in range(10)
        ]
        result = _detect_off_hours_access(entries, off_hours_start=22, off_hours_end=6)
        assert len(result) == 1
        assert result[0]["type"] == "off_hours_access"
        assert result[0]["actor"] == "night-owl"

    def test_business_hours_no_anomaly(self):
        from algorithms.access_anomaly import _detect_off_hours_access
        # All during business hours (noon)
        entries = [
            {"action": "view", "actor": "normal-user",
             "timestamp": datetime(2024, 1, i + 1, 12, 0, tzinfo=timezone.utc)}
            for i in range(10)
        ]
        result = _detect_off_hours_access(entries)
        assert result == []

    def test_no_entries_returns_empty(self):
        from algorithms.access_anomaly import _detect_off_hours_access
        result = _detect_off_hours_access([])
        assert result == []

    def test_less_than_threshold_no_anomaly(self):
        from algorithms.access_anomaly import _detect_off_hours_access
        # Only 3 events at off-hours (threshold is 5)
        entries = [
            {"action": "view", "actor": "rare-user",
             "timestamp": datetime(2024, 1, i + 1, 3, 0, tzinfo=timezone.utc)}
            for i in range(3)
        ]
        result = _detect_off_hours_access(entries, off_hours_start=22, off_hours_end=6)
        assert result == []


# ---------------------------------------------------------------------------
# Bates Generator helpers
# ---------------------------------------------------------------------------

class TestGenerateBatesNumber:
    """Tests for _generate_bates_number."""

    def test_default_width(self):
        from algorithms.bates_generator import _generate_bates_number
        assert _generate_bates_number("EVD", 1) == "EVD-000001"

    def test_custom_width(self):
        from algorithms.bates_generator import _generate_bates_number
        assert _generate_bates_number("EX", 42, width=4) == "EX-0042"

    def test_large_number(self):
        from algorithms.bates_generator import _generate_bates_number
        assert _generate_bates_number("DOC", 999999) == "DOC-999999"

    def test_overflow_width(self):
        from algorithms.bates_generator import _generate_bates_number
        # Number wider than width still works (no truncation)
        result = _generate_bates_number("A", 1234567, width=4)
        assert result == "A-1234567"


class TestStampTextOnPdfBytes:
    """Tests for _stamp_text_on_pdf_bytes."""

    def test_fallback_for_non_pdf_bytes(self):
        from algorithms.bates_generator import _stamp_text_on_pdf_bytes
        content = b"This is plain text, not a PDF"
        result = _stamp_text_on_pdf_bytes(content, "EVD-000001")
        # Should fall back to text marker
        assert result.startswith(b"[BATES: EVD-000001]\n")
        assert content in result

    def test_fallback_preserves_original(self):
        from algorithms.bates_generator import _stamp_text_on_pdf_bytes
        original = b"original content bytes"
        result = _stamp_text_on_pdf_bytes(original, "DOC-000042")
        assert original in result

    def test_fallback_includes_bates_number(self):
        from algorithms.bates_generator import _stamp_text_on_pdf_bytes
        result = _stamp_text_on_pdf_bytes(b"data", "PREFIX-099999")
        assert b"PREFIX-099999" in result

    def test_valid_pdf_produces_output(self):
        """If reportlab and PyPDF2 are available, test with a real minimal PDF."""
        from algorithms.bates_generator import _stamp_text_on_pdf_bytes
        pdf = _make_minimal_pdf()
        result = _stamp_text_on_pdf_bytes(pdf, "EVD-000001")
        assert len(result) > 0
        # The result should either be a valid stamped PDF or a text-marker fallback
        assert b"EVD-000001" in result or result.startswith(b"%PDF")

    def test_position_parameter(self):
        from algorithms.bates_generator import _stamp_text_on_pdf_bytes
        result = _stamp_text_on_pdf_bytes(b"data", "X-001", position="bottom_left")
        assert b"X-001" in result


# ---------------------------------------------------------------------------
# Timeline Alignment helpers
# ---------------------------------------------------------------------------

class TestParseTimestamp:
    """Tests for _parse_timestamp covering all format branches."""

    def test_none_returns_none(self):
        from algorithms.timeline_alignment import _parse_timestamp
        assert _parse_timestamp(None) is None

    def test_datetime_with_tz(self):
        from algorithms.timeline_alignment import _parse_timestamp
        dt = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
        result = _parse_timestamp(dt)
        assert result == dt

    def test_datetime_without_tz_gets_utc(self):
        from algorithms.timeline_alignment import _parse_timestamp
        dt = datetime(2024, 1, 15, 12, 0)
        result = _parse_timestamp(dt)
        assert result.tzinfo == timezone.utc

    def test_iso_string_with_tz(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15T12:00:00+00:00")
        assert result is not None
        assert result.year == 2024

    def test_iso_string_with_fractional_tz(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15T12:00:00.123456+00:00")
        assert result is not None

    def test_iso_string_no_tz(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15T12:00:00")
        assert result is not None
        assert result.tzinfo == timezone.utc

    def test_iso_string_fractional_no_tz(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15T12:00:00.500000")
        assert result is not None
        assert result.tzinfo == timezone.utc

    def test_space_separated(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15 12:00:00")
        assert result is not None

    def test_space_separated_fractional(self):
        from algorithms.timeline_alignment import _parse_timestamp
        result = _parse_timestamp("2024-01-15 12:00:00.500000")
        assert result is not None

    def test_unparseable_returns_none(self):
        from algorithms.timeline_alignment import _parse_timestamp
        assert _parse_timestamp("not a date") is None

    def test_integer_returns_none(self):
        from algorithms.timeline_alignment import _parse_timestamp
        # Integers are not handled (not str or datetime)
        assert _parse_timestamp(12345) is None


class TestDetectClockDrift:
    """Tests for _detect_clock_drift."""

    def test_empty_groups_returns_empty(self):
        from algorithms.timeline_alignment import _detect_clock_drift
        result = _detect_clock_drift({})
        assert result == []

    def test_single_device_no_drift(self):
        from algorithms.timeline_alignment import _detect_clock_drift
        groups = {
            "phone-A": [{"normalized_ts": datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)}],
        }
        result = _detect_clock_drift(groups)
        assert result == []


# ---------------------------------------------------------------------------
# Redaction Verify _execute with mocked DB
# ---------------------------------------------------------------------------

class TestRedactionVerifyExecute:
    """Tests for RedactionVerifyAlgorithm._execute with mocked DB/FS."""

    def _make_mock_item(self, item_id, filename, file_type, sha256, is_redacted=False, store_id=None):
        item = MagicMock()
        item.id = item_id
        item.original_filename = filename
        item.file_type = file_type
        item.hash_sha256 = sha256
        item.is_redacted = is_redacted
        item.evidence_store_id = store_id
        return item

    def _make_params(self, case_id="case-1", tenant_id="org-1"):
        from algorithms.base import AlgorithmParams
        return AlgorithmParams(
            case_id=case_id,
            tenant_id=tenant_id,
            actor_id="test-actor",
            actor_name="Test Actor",
            extra={},
        )

    def _make_mock_context(self, case_exists=True, items=None, links=None):
        db_session = MagicMock()
        evidence_store = MagicMock()

        # Build query chain mocks
        case_query = MagicMock()
        link_query = MagicMock()
        item_query = MagicMock()

        def query_side_effect(model):
            model_name = model.__name__ if hasattr(model, '__name__') else str(model)
            if "LegalCase" in model_name:
                return case_query
            elif "CaseEvidence" in model_name:
                return link_query
            elif "EvidenceItem" in model_name:
                return item_query
            return MagicMock()

        db_session.query.side_effect = query_side_effect

        # Case exists?
        mock_case = MagicMock() if case_exists else None
        case_query.filter_by.return_value.first.return_value = mock_case

        # Links
        mock_links = links or []
        link_filter = MagicMock()
        link_filter.filter.return_value.all.return_value = mock_links
        link_query.filter_by.return_value = link_filter

        # Items
        mock_items = items or []
        item_filter = MagicMock()
        item_filter.order_by.return_value.all.return_value = mock_items
        item_query.filter.return_value = item_filter

        return {"db_session": db_session, "evidence_store": evidence_store}

    def test_case_not_found_raises(self):
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        ctx = self._make_mock_context(case_exists=False)
        with pytest.raises(ValueError, match="not found"):
            algo._execute(self._make_params(), ctx)

    def test_no_items_returns_empty_report(self):
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        ctx = self._make_mock_context(case_exists=True, items=[], links=[])
        result = algo._execute(self._make_params(), ctx)
        assert result["total_checked"] == 0
        assert result["items"] == []

    def test_non_redacted_items_skipped(self):
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        item = self._make_mock_item(1, "doc.pdf", "pdf", "abc123", is_redacted=False)
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        result = algo._execute(self._make_params(), ctx)
        assert result["total_checked"] == 0

    def test_redacted_item_no_hash_skipped(self):
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        item = self._make_mock_item(1, "doc.pdf", "pdf", None, is_redacted=True)
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        result = algo._execute(self._make_params(), ctx)
        assert result["total_checked"] == 0

    def test_redacted_item_original_not_found(self):
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        item = self._make_mock_item(1, "doc.pdf", "pdf", "abc123", is_redacted=True, store_id=None)
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        ctx["evidence_store"].get_original_path.return_value = None
        result = algo._execute(self._make_params(), ctx)
        assert result["total_checked"] == 1
        assert result["items"][0]["status"] == "skipped"

    def test_redacted_item_no_manifest_derivative(self):
        """Redacted item with store_id but no derivative in manifest → skipped."""
        from algorithms.redaction_verify import RedactionVerifyAlgorithm
        algo = RedactionVerifyAlgorithm()
        item = self._make_mock_item(1, "doc.pdf", "pdf", "abc123", is_redacted=True, store_id="store-1")
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        ctx["evidence_store"].get_original_path.return_value = "/fake/path.pdf"
        # Manifest with no derivatives
        mock_manifest = MagicMock()
        mock_manifest.derivatives = []
        ctx["evidence_store"].load_manifest.return_value = mock_manifest
        result = algo._execute(self._make_params(), ctx)
        assert result["total_checked"] == 1
        assert result["items"][0]["status"] == "skipped"
        assert "No redacted derivative" in result["items"][0]["reason"]

    def test_redacted_item_full_check_path(self):
        """Full check path: redacted item with both files present (non-PDF)."""
        import hashlib
        import tempfile
        import os
        from pathlib import Path
        from algorithms.redaction_verify import RedactionVerifyAlgorithm

        algo = RedactionVerifyAlgorithm()

        original_content = b"Original sensitive document content here with lots of text"
        redacted_content = b"REDACTED document XXXX XXXXX XXXXX XXXXX XXXXX"
        original_hash = hashlib.sha256(original_content).hexdigest()

        item = self._make_mock_item(1, "doc.txt", "txt", original_hash, is_redacted=True, store_id="store-1")
        link = MagicMock()
        link.evidence_id = 1

        # Write temp files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(original_content)
            original_path = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(redacted_content)
            redacted_path = f.name

        try:
            ctx = self._make_mock_context(items=[item], links=[link])
            ctx["evidence_store"].get_original_path.return_value = original_path

            # Mock manifest with a redacted derivative
            mock_deriv = MagicMock()
            mock_deriv.derivative_type = "redacted"
            mock_deriv.filename = "redacted.txt"
            mock_deriv.sha256 = hashlib.sha256(redacted_content).hexdigest()
            mock_manifest = MagicMock()
            mock_manifest.derivatives = [mock_deriv]
            ctx["evidence_store"].load_manifest.return_value = mock_manifest

            # Mock derivative dir to point to our temp file
            mock_deriv_dir = MagicMock()
            candidate_path = MagicMock()
            candidate_path.exists.return_value = True
            candidate_path.__str__ = lambda self: redacted_path
            mock_deriv_dir.__truediv__ = lambda self, other: candidate_path
            ctx["evidence_store"]._derivative_dir.return_value = mock_deriv_dir

            # Patch open to handle the candidate_path mock
            import builtins
            real_open = builtins.open

            def patched_open(path, *args, **kwargs):
                path_str = str(path)
                if path_str == str(candidate_path):
                    return real_open(redacted_path, *args, **kwargs)
                return real_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=patched_open):
                result = algo._execute(self._make_params(), ctx)

            assert result["total_checked"] == 1
            item_result = result["items"][0]
            assert item_result["status"] in ("pass", "warning", "fail")
            assert "checks" in item_result
            assert "hash_comparison" in item_result["checks"]
            # Hashes should differ
            assert item_result["checks"]["hash_comparison"]["differs"] is True
        finally:
            os.unlink(original_path)
            os.unlink(redacted_path)

    def test_redacted_pdf_with_text_layer_check(self):
        """Full path for a PDF item exercises text-layer and annotation checks."""
        import hashlib
        import tempfile
        import os
        from algorithms.redaction_verify import RedactionVerifyAlgorithm

        algo = RedactionVerifyAlgorithm()

        # Create a minimal PDF with some text
        original_pdf = _make_minimal_pdf()
        # Slightly different PDF for the "redacted" version
        redacted_pdf = _make_minimal_pdf()  # Same content = warning-level since hash may match
        original_hash = hashlib.sha256(original_pdf).hexdigest()

        item = MagicMock()
        item.id = 1
        item.original_filename = "contract.pdf"
        item.file_type = "pdf"
        item.hash_sha256 = original_hash
        item.is_redacted = True
        item.evidence_store_id = "store-1"

        link = MagicMock()
        link.evidence_id = 1

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(original_pdf)
            original_path = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(redacted_pdf)
            redacted_path = f.name

        try:
            ctx = self._make_mock_context(items=[item], links=[link])
            ctx["evidence_store"].get_original_path.return_value = original_path

            mock_deriv = MagicMock()
            mock_deriv.derivative_type = "redacted"
            mock_deriv.filename = "redacted.pdf"
            mock_deriv.sha256 = hashlib.sha256(redacted_pdf).hexdigest()
            mock_manifest = MagicMock()
            mock_manifest.derivatives = [mock_deriv]
            ctx["evidence_store"].load_manifest.return_value = mock_manifest

            mock_deriv_dir = MagicMock()
            candidate_path = MagicMock()
            candidate_path.exists.return_value = True
            candidate_path.__str__ = lambda self: redacted_path
            mock_deriv_dir.__truediv__ = lambda self, other: candidate_path
            ctx["evidence_store"]._derivative_dir.return_value = mock_deriv_dir

            import builtins
            real_open = builtins.open

            def patched_open(path, *args, **kwargs):
                path_str = str(path)
                if path_str == str(candidate_path):
                    return real_open(redacted_path, *args, **kwargs)
                return real_open(path, *args, **kwargs)

            with patch("builtins.open", side_effect=patched_open):
                result = algo._execute(self._make_params(), ctx)

            assert result["total_checked"] == 1
            item_result = result["items"][0]
            assert "checks" in item_result
            # PDF should trigger text_layer check
            assert "text_layer" in item_result["checks"]
            assert "annotations" in item_result["checks"]
            assert "byte_leakage" in item_result["checks"]
            assert "hash_comparison" in item_result["checks"]
        finally:
            os.unlink(original_path)
            os.unlink(redacted_path)


# ---------------------------------------------------------------------------
# Integrity Sweep _execute with mocked DB
# ---------------------------------------------------------------------------

class TestIntegritySweepExecute:
    """Tests for IntegritySweepAlgorithm._execute with mocked DB/FS."""

    def _make_params(self, case_id="case-1", tenant_id="org-1"):
        from algorithms.base import AlgorithmParams
        return AlgorithmParams(
            case_id=case_id,
            tenant_id=tenant_id,
            actor_id="test-actor",
            actor_name="Test Actor",
            extra={},
        )

    def _make_mock_context(self, case_exists=True, items=None, links=None):
        db_session = MagicMock()
        evidence_store = MagicMock()

        def query_side_effect(model):
            model_name = model.__name__ if hasattr(model, '__name__') else str(model)
            if "LegalCase" in model_name:
                q = MagicMock()
                mock_case = MagicMock() if case_exists else None
                q.filter_by.return_value.first.return_value = mock_case
                return q
            elif "CaseEvidence" in model_name:
                q = MagicMock()
                mock_links = links or []
                q.filter_by.return_value.filter.return_value.all.return_value = mock_links
                return q
            elif "EvidenceItem" in model_name:
                q = MagicMock()
                mock_items = items or []
                q.filter.return_value.order_by.return_value.all.return_value = mock_items
                return q
            return MagicMock()

        db_session.query.side_effect = query_side_effect
        return {"db_session": db_session, "evidence_store": evidence_store}

    def test_case_not_found_raises(self):
        from algorithms.integrity_sweep import IntegritySweepAlgorithm
        algo = IntegritySweepAlgorithm()
        ctx = self._make_mock_context(case_exists=False)
        with pytest.raises(ValueError, match="not found"):
            algo._execute(self._make_params(), ctx)

    def test_empty_case_returns_report(self):
        from algorithms.integrity_sweep import IntegritySweepAlgorithm
        algo = IntegritySweepAlgorithm()
        ctx = self._make_mock_context(items=[], links=[])
        result = algo._execute(self._make_params(), ctx)
        assert result["total_items"] == 0
        assert result["all_passed"] is True

    def test_item_without_hash_is_error(self):
        from algorithms.integrity_sweep import IntegritySweepAlgorithm
        algo = IntegritySweepAlgorithm()
        item = MagicMock()
        item.id = 1
        item.original_filename = "doc.pdf"
        item.hash_sha256 = None
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        result = algo._execute(self._make_params(), ctx)
        assert result["summary"]["error"] == 1

    def test_item_file_missing_is_missing(self):
        from algorithms.integrity_sweep import IntegritySweepAlgorithm
        algo = IntegritySweepAlgorithm()
        item = MagicMock()
        item.id = 1
        item.original_filename = "doc.pdf"
        item.hash_sha256 = "abc123"
        item.evidence_store_id = "store-1"
        link = MagicMock()
        link.evidence_id = 1
        ctx = self._make_mock_context(items=[item], links=[link])
        ctx["evidence_store"].get_original_path.return_value = None
        result = algo._execute(self._make_params(), ctx)
        assert result["summary"]["missing"] == 1

    def test_item_hash_matches_is_pass(self):
        import hashlib
        import tempfile
        import os
        from algorithms.integrity_sweep import IntegritySweepAlgorithm

        content = b"evidence file content for integrity test"
        expected_hash = hashlib.sha256(content).hexdigest()

        algo = IntegritySweepAlgorithm()
        item = MagicMock()
        item.id = 1
        item.original_filename = "doc.pdf"
        item.hash_sha256 = expected_hash
        item.evidence_store_id = "store-1"
        link = MagicMock()
        link.evidence_id = 1

        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            ctx = self._make_mock_context(items=[item], links=[link])
            ctx["evidence_store"].get_original_path.return_value = tmp_path
            result = algo._execute(self._make_params(), ctx)
            assert result["summary"]["pass"] == 1
            assert result["all_passed"] is True
        finally:
            os.unlink(tmp_path)

    def test_item_hash_mismatch_is_fail(self):
        import tempfile
        import os
        from algorithms.integrity_sweep import IntegritySweepAlgorithm

        algo = IntegritySweepAlgorithm()
        item = MagicMock()
        item.id = 1
        item.original_filename = "doc.pdf"
        item.hash_sha256 = "wrong_hash_value"
        item.evidence_store_id = "store-1"
        link = MagicMock()
        link.evidence_id = 1

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"actual content")
            tmp_path = tmp.name

        try:
            ctx = self._make_mock_context(items=[item], links=[link])
            ctx["evidence_store"].get_original_path.return_value = tmp_path
            result = algo._execute(self._make_params(), ctx)
            assert result["summary"]["fail"] == 1
            assert result["all_passed"] is False
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Bulk Dedup _execute with mocked DB
# ---------------------------------------------------------------------------

class TestBulkDedupExecute:
    """Tests for BulkDedupAlgorithm._execute with mocked DB/FS."""

    def _make_params(self, case_id="case-1", tenant_id="org-1"):
        from algorithms.base import AlgorithmParams
        return AlgorithmParams(
            case_id=case_id,
            tenant_id=tenant_id,
            actor_id="test-actor",
            actor_name="Test Actor",
            extra={"near_dedup": False},
        )

    def test_case_not_found_raises(self):
        from algorithms.bulk_dedup import BulkDedupAlgorithm
        algo = BulkDedupAlgorithm()
        db_session = MagicMock()
        q = MagicMock()
        db_session.query.return_value = q
        q.filter_by.return_value.first.return_value = None

        ctx = {"db_session": db_session, "evidence_store": MagicMock()}
        with pytest.raises(ValueError, match="not found"):
            algo._execute(self._make_params(), ctx)


# ---------------------------------------------------------------------------
# Provenance Graph _execute with mocked DB
# ---------------------------------------------------------------------------

class TestProvenanceGraphExecute:
    """Tests for ProvenanceGraphAlgorithm._execute with mocked DB/FS."""

    def _make_params(self, case_id="case-1", tenant_id="org-1"):
        from algorithms.base import AlgorithmParams
        return AlgorithmParams(
            case_id=case_id,
            tenant_id=tenant_id,
            actor_id="test-actor",
            actor_name="Test Actor",
            extra={},
        )

    def test_case_not_found_raises(self):
        from algorithms.provenance_graph import ProvenanceGraphAlgorithm
        algo = ProvenanceGraphAlgorithm()
        db_session = MagicMock()
        q = MagicMock()
        db_session.query.return_value = q
        q.filter_by.return_value.first.return_value = None

        ctx = {"db_session": db_session, "evidence_store": MagicMock()}
        with pytest.raises(ValueError, match="not found"):
            algo._execute(self._make_params(), ctx)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_minimal_pdf() -> bytes:
    """Create a minimal valid PDF for testing."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(100, 700, "Test document for Evident algorithm tests.")
        c.showPage()
        c.save()
        return buf.getvalue()
    except ImportError:
        # Fallback: hand-craft a minimal PDF
        return (
            b"%PDF-1.0\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\n"
            b"startxref\n183\n%%EOF"
        )
