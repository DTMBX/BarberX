import zipfile

from backend.tools.cli.exporter import export_case


def test_export_embeds_exact_canonical_manifest_bytes(tmp_path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()

    canonical = case_dir / "manifests" / "manifest.canonical.json"
    canonical.parent.mkdir(parents=True)
    canonical_bytes = b'{ "schema_version": "1.1.0", "originals": [] }'
    canonical.write_bytes(canonical_bytes)

    zip_path = tmp_path / "export.zip"
    export_case(case_dir, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        embedded = zf.read("manifests/manifest.canonical.json")

    assert embedded == canonical_bytes
