"""
Tests for Court Package Export Mode
====================================
Verifies:
  - Exhibit directories are correctly numbered.
  - INDEX.csv and INDEX.json are present and well-formed.
  - SHA-256 hashes in INDEX.json match actual file contents.
  - Deterministic output given identical inputs.
  - Derivative viewer materials are clearly labeled.
  - PACKAGE_HASH.txt records INDEX.json hash.
"""

import csv
import hashlib
import io
import json
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

from services.court_package import CourtPackageExporter, CourtPackageResult


# ---------------------------------------------------------------------------
# Mock objects (no database required)
# ---------------------------------------------------------------------------


@dataclass
class MockCase:
    case_number: str = "TEST-COURT-001"
    case_name: str = "Court Package Test"


@dataclass
class MockEvidence:
    id: int = 1
    evidence_id: str = "ev-uuid-001"
    original_filename: str = "body_cam_001.mp4"
    file_type: str = "video/mp4"
    hash_sha256: str = ""
    stored_path: str = ""


@pytest.fixture
def tmp_export(tmp_path):
    return CourtPackageExporter(export_base_path=str(tmp_path / "court"))


@pytest.fixture
def evidence_files(tmp_path):
    """Create mock evidence files on disk and return MockEvidence objects."""
    items = []
    for i in range(3):
        content = f"evidence content {i}".encode()
        fpath = tmp_path / f"evidence_{i}.bin"
        fpath.write_bytes(content)
        item = MockEvidence(
            id=i + 1,
            evidence_id=f"ev-uuid-{i:03d}",
            original_filename=f"evidence_{i}.bin",
            file_type="application/octet-stream",
            hash_sha256=hashlib.sha256(content).hexdigest(),
            stored_path=str(fpath),
        )
        items.append(item)
    return items


@pytest.fixture
def fixed_time():
    return datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc)


# ===========================================================================
# 1. Basic package structure
# ===========================================================================


class TestPackageStructure:

    def test_package_creates_zip(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, f"Exhibit {i}") for i, e in enumerate(evidence_files)],
            generated_at=fixed_time,
        )
        assert result.success
        assert Path(result.package_path).exists()
        assert result.package_path.endswith(".zip")

    def test_exhibit_directories_numbered(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, f"Desc {i}") for i, e in enumerate(evidence_files)],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            names = zf.namelist()
            assert any(n.startswith("Exhibit_001/") for n in names)
            assert any(n.startswith("Exhibit_002/") for n in names)
            assert any(n.startswith("Exhibit_003/") for n in names)

    def test_exhibit_count_matches(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        assert result.exhibit_count == 3


# ===========================================================================
# 2. INDEX.csv
# ===========================================================================


class TestIndexCSV:

    def test_csv_present_in_zip(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "INDEX.csv" in zf.namelist()

    def test_csv_has_correct_rows(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, f"desc_{i}") for i, e in enumerate(evidence_files)],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            csv_text = zf.read("INDEX.csv").decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 3
        assert rows[0]["Exhibit"] == "Exhibit_001"
        assert rows[0]["SHA256"] != ""

    def test_csv_sha256_matches_file(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            csv_text = zf.read("INDEX.csv").decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                exhibit = row["Exhibit"]
                filename = row["Filename"]
                expected_sha = row["SHA256"]
                actual_data = zf.read(f"{exhibit}/{filename}")
                actual_sha = hashlib.sha256(actual_data).hexdigest()
                assert actual_sha == expected_sha


# ===========================================================================
# 3. INDEX.json
# ===========================================================================


class TestIndexJSON:

    def test_json_present_in_zip(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "INDEX.json" in zf.namelist()

    def test_json_has_case_metadata(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            index = json.loads(zf.read("INDEX.json"))

        assert index["court_package"]["case_number"] == "TEST-COURT-001"
        assert index["court_package"]["exhibit_count"] == 3

    def test_json_hashes_match_files(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            index = json.loads(zf.read("INDEX.json"))
            for path, expected_sha in index["file_manifest"].items():
                if path in zf.namelist():
                    actual = hashlib.sha256(zf.read(path)).hexdigest()
                    assert actual == expected_sha, f"Hash mismatch for {path}"


# ===========================================================================
# 4. Determinism
# ===========================================================================


class TestDeterminism:

    def test_identical_inputs_produce_identical_index(
        self, tmp_export, evidence_files, fixed_time
    ):
        """INDEX.json should be byte-identical for same inputs."""
        def build():
            result = tmp_export.build_package(
                case=MockCase(),
                exhibits=[(e, f"d{i}") for i, e in enumerate(evidence_files)],
                generated_at=fixed_time,
            )
            with zipfile.ZipFile(result.package_path, "r") as zf:
                return zf.read("INDEX.json")

        first = build()
        second = build()
        assert first == second

    def test_index_sha256_on_result(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            actual = hashlib.sha256(zf.read("INDEX.json")).hexdigest()
        assert result.index_sha256 == actual


# ===========================================================================
# 5. PACKAGE_HASH.txt
# ===========================================================================


class TestPackageHash:

    def test_package_hash_file_present(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "PACKAGE_HASH.txt" in zf.namelist()

    def test_package_hash_records_index_sha(self, tmp_export, evidence_files, fixed_time):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            text = zf.read("PACKAGE_HASH.txt").decode("utf-8")
        assert result.index_sha256 in text


# ===========================================================================
# 6. Offline viewer labeling
# ===========================================================================


class TestOfflineViewer:

    def test_viewer_notice_present_when_enabled(
        self, tmp_export, evidence_files, fixed_time
    ):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
            include_offline_viewer=True,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "_viewer/NOTICE.txt" in zf.namelist()
            notice = zf.read("_viewer/NOTICE.txt").decode("utf-8")
            assert "DERIVATIVE" in notice
            assert "NOT original evidence" in notice

    def test_viewer_absent_when_disabled(
        self, tmp_export, evidence_files, fixed_time
    ):
        result = tmp_export.build_package(
            case=MockCase(),
            exhibits=[(e, "") for e in evidence_files],
            generated_at=fixed_time,
            include_offline_viewer=False,
        )
        with zipfile.ZipFile(result.package_path, "r") as zf:
            assert "_viewer/NOTICE.txt" not in zf.namelist()
