"""Tests for health check and basic API functionality."""

from __future__ import annotations

from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Health check should report service status."""

    def test_health_returns_200(self, client):
        """Health endpoint should always return 200."""
        with (
            patch("app.main.Redis") as mock_redis_cls,
            patch("app.main.engine") as mock_engine,
        ):
            # Mock Redis ping
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            mock_redis_cls.from_url.return_value = mock_redis

            # Mock DB connection
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            resp = client.get("/health")
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] in ("healthy", "degraded")
            assert "version" in body


class TestCasesEndpoint:
    """CRUD for cases."""

    def test_create_case(self, client):
        resp = client.post(
            "/api/v1/cases",
            json={"title": "Test Case", "created_by": "pytest"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Test Case"
        assert body["status"] == "open"
        assert "id" in body

    def test_list_cases_empty(self, client):
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_cases_after_create(self, client):
        client.post("/api/v1/cases", json={"title": "C1", "created_by": "pytest"})
        client.post("/api/v1/cases", json={"title": "C2", "created_by": "pytest"})
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_case(self, client, sample_case_id):
        resp = client.get(f"/api/v1/cases/{sample_case_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sample_case_id

    def test_get_case_404(self, client):
        import uuid
        resp = client.get(f"/api/v1/cases/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestEvidenceInit:
    """Evidence upload init flow."""

    def test_init_upload_creates_row(self, client, sample_case_id):
        resp = client.post(
            "/api/v1/evidence/init",
            json={
                "case_id": sample_case_id,
                "filename": "body-cam-1.mp4",
                "content_type": "video/mp4",
                "size_bytes": 5000,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "evidence_id" in body
        assert body["upload_url"] == "https://minio.test/presigned"

    def test_init_upload_bad_case(self, client):
        import uuid
        resp = client.post(
            "/api/v1/evidence/init",
            json={
                "case_id": str(uuid.uuid4()),
                "filename": "file.mp4",
                "content_type": "video/mp4",
                "size_bytes": 100,
            },
        )
        assert resp.status_code == 404

    def test_init_upload_bad_mime(self, client, sample_case_id):
        resp = client.post(
            "/api/v1/evidence/init",
            json={
                "case_id": sample_case_id,
                "filename": "script.sh",
                "content_type": "text/x-shellscript",
                "size_bytes": 100,
            },
        )
        assert resp.status_code == 422


class TestEvidenceComplete:
    """Evidence complete / duplicate detection."""

    def test_complete_already_finalized_returns_409(self, client, sample_evidence):
        """If evidence already has sha256, complete should 409."""
        resp = client.post(
            "/api/v1/evidence/complete",
            json={"evidence_id": str(sample_evidence.id)},
        )
        assert resp.status_code == 409
        assert "already finalized" in resp.json()["detail"]


class TestIssuesCRUD:
    """Issues endpoint tests."""

    def test_create_issue(self, client, sample_case_id):
        resp = client.post(
            "/api/v1/issues",
            json={
                "case_id": sample_case_id,
                "title": "Excessive force allegation",
                "narrative": "Officer used unnecessary force during arrest.",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Excessive force allegation"
        assert body["status"] == "open"

    def test_list_issues_by_case(self, client, sample_case_id):
        # Create 2 issues
        for i in range(2):
            client.post(
                "/api/v1/issues",
                json={
                    "case_id": sample_case_id,
                    "title": f"Issue {i}",
                    "narrative": "Details...",
                },
            )
        resp = client.get(f"/api/v1/issues?case_id={sample_case_id}")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_update_issue(self, client, sample_case_id):
        create_resp = client.post(
            "/api/v1/issues",
            json={
                "case_id": sample_case_id,
                "title": "Test issue",
                "narrative": "Original narrative",
            },
        )
        issue_id = create_resp.json()["id"]

        patch_resp = client.patch(
            f"/api/v1/issues/{issue_id}",
            json={"status": "confirmed"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "confirmed"


class TestArtifactsList:
    """Artifacts list endpoint."""

    def test_list_artifacts_empty(self, client, sample_case_id):
        resp = client.get(f"/api/v1/artifacts?case_id={sample_case_id}")
        assert resp.status_code == 200
        assert resp.json() == []


class TestTimeline:
    """Timeline endpoint."""

    def test_timeline_empty(self, client, sample_case_id):
        resp = client.get(f"/api/v1/timeline/{sample_case_id}")
        assert resp.status_code == 200
        # May have events from case creation
        assert isinstance(resp.json(), list)


class TestManifest:
    """Manifest export/verify."""

    def test_export_manifest(self, client, sample_case_id, sample_evidence):
        resp = client.get(f"/api/v1/manifest/{sample_case_id}/export")
        assert resp.status_code == 200
        body = resp.json()
        assert "case_id" in body
        assert "hmac_signature" in body
        assert "evidence_hashes" in body
        assert len(body["evidence_hashes"]) >= 1

    def test_verify_manifest_roundtrip(self, client, sample_case_id, sample_evidence):
        """Export then verify should pass."""
        export_resp = client.get(f"/api/v1/manifest/{sample_case_id}/export")
        manifest = export_resp.json()

        verify_resp = client.post("/api/v1/manifest/verify", json=manifest)
        assert verify_resp.status_code == 200
        body = verify_resp.json()
        assert body["sha256_valid"] is True
        assert body["hmac_valid"] is True
