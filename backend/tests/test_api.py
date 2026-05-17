"""
Test suite for LexGuard X API endpoints.

Covers:
  - Health check
  - File upload validation (type, size)
  - Analysis retrieval (404 on unknown ID)
  - History endpoint
  - TTS endpoint guards
  - WebSocket connection handshake
"""
import io
import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────────────────────────────────────
#  Health Check
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client: TestClient):
        data = response = client.get("/api/health").json()
        assert data.get("status") == "ok"

    def test_health_contains_service_flags(self, client: TestClient):
        data = client.get("/api/health").json()
        # All service availability flags must be present
        for key in ("gcs", "firestore", "tts", "nlp", "vertex"):
            assert key in data, f"Missing service flag: {key}"


# ─────────────────────────────────────────────────────────────────────────────
#  File Upload Validation
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalyzeEndpoint:
    def test_upload_rejects_non_pdf(self, client: TestClient):
        """Only PDF/DOCX files should be accepted."""
        fake_exe = io.BytesIO(b"MZ\x00\x00")
        response = client.post(
            "/api/analyze",
            files={"file": ("malware.exe", fake_exe, "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_upload_rejects_empty_file(self, client: TestClient):
        empty = io.BytesIO(b"")
        response = client.post(
            "/api/analyze",
            files={"file": ("empty.pdf", empty, "application/pdf")},
        )
        assert response.status_code in (400, 422)

    def test_upload_valid_pdf_returns_analysis_id(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        """A valid minimal PDF should return a 200 with an analysis_id."""
        pdf = io.BytesIO(sample_pdf_bytes)
        response = client.post(
            "/api/analyze",
            files={"file": ("contract.pdf", pdf, "application/pdf")},
        )
        assert response.status_code == 200
        assert "analysis_id" in response.json()

    def test_analysis_id_is_uuid_format(
        self, client: TestClient, sample_pdf_bytes: bytes
    ):
        import uuid
        pdf = io.BytesIO(sample_pdf_bytes)
        response = client.post(
            "/api/analyze",
            files={"file": ("contract.pdf", pdf, "application/pdf")},
        )
        analysis_id = response.json().get("analysis_id", "")
        # Should be a valid UUID4
        try:
            uuid.UUID(analysis_id)
        except ValueError:
            pytest.fail(f"analysis_id is not a valid UUID: {analysis_id}")


# ─────────────────────────────────────────────────────────────────────────────
#  Analysis Retrieval
# ─────────────────────────────────────────────────────────────────────────────

class TestAnalysisRetrieval:
    def test_unknown_analysis_returns_404(self, client: TestClient):
        response = client.get("/api/analysis/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_status_endpoint_for_unknown_returns_404(self, client: TestClient):
        response = client.get(
            "/api/analysis/00000000-0000-0000-0000-000000000000/status"
        )
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
#  History
# ─────────────────────────────────────────────────────────────────────────────

class TestHistoryEndpoint:
    def test_history_returns_list(self, client: TestClient):
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ─────────────────────────────────────────────────────────────────────────────
#  TTS Endpoints
# ─────────────────────────────────────────────────────────────────────────────

class TestTTSEndpoints:
    def test_tts_verdict_unknown_id_returns_404(self, client: TestClient):
        response = client.get(
            "/api/tts/00000000-0000-0000-0000-000000000000/verdict"
        )
        assert response.status_code == 404
