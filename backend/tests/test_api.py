"""
Integration tests for FastAPI endpoints.
Uses httpx TestClient — no real AI calls (mocked).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Patch heavy services before importing app
with patch("services.firestore_client.FirestoreClient.__init__", return_value=None), \
     patch("services.logging_client.CloudLogger.__init__", return_value=None), \
     patch("services.tts_client.TTSClient.__init__", return_value=None), \
     patch("services.nlp_client.NLPClient.__init__", return_value=None), \
     patch("services.storage_client.StorageClient.__init__", return_value=None):
    from main import app, analysis_store

client = TestClient(app)


class TestHealthEndpoint:

    def test_health_returns_200(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_has_status_field(self):
        resp = client.get("/api/health")
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_has_version(self):
        resp = client.get("/api/health")
        assert resp.json()["version"] == "1.0.0"

    def test_health_has_google_services_field(self):
        resp = client.get("/api/health")
        assert "google_services" in resp.json()

    def test_health_has_timestamp(self):
        resp = client.get("/api/health")
        assert "timestamp" in resp.json()


class TestAnalyzeEndpoint:

    def test_no_file_returns_422(self):
        resp = client.post("/api/analyze")
        assert resp.status_code == 422

    def test_unsupported_extension_returns_400(self):
        resp = client.post(
            "/api/analyze",
            files={"file": ("contract.xlsx", b"data", "application/octet-stream")},
        )
        assert resp.status_code == 400

    def test_empty_file_returns_400(self):
        resp = client.post(
            "/api/analyze",
            files={"file": ("contract.pdf", b"", "application/pdf")},
        )
        assert resp.status_code == 400

    def test_valid_pdf_upload_returns_analysis_id(self):
        with patch("main.threading.Thread") as mock_thread, \
             patch("main._firestore") as mock_fs, \
             patch("main._storage") as mock_st:
            mock_thread.return_value = MagicMock()
            mock_fs.create_analysis_record = MagicMock()
            mock_st.enabled = False

            resp = client.post(
                "/api/analyze",
                files={"file": ("test.pdf", b"fake pdf content", "application/pdf")},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "analysis_id" in body
        assert body["status"] == "processing"

    def test_valid_docx_upload_returns_analysis_id(self):
        with patch("main.threading.Thread") as mock_thread, \
             patch("main._firestore") as mock_fs, \
             patch("main._storage") as mock_st:
            mock_thread.return_value = MagicMock()
            mock_fs.create_analysis_record = MagicMock()
            mock_st.enabled = False

            resp = client.post(
                "/api/analyze",
                files={"file": ("contract.docx", b"fake docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            )
        assert resp.status_code == 200
        assert "analysis_id" in resp.json()

    def test_oversized_file_returns_413(self):
        big_data = b"x" * (21 * 1024 * 1024)  # 21 MB
        resp = client.post(
            "/api/analyze",
            files={"file": ("large.pdf", big_data, "application/pdf")},
        )
        assert resp.status_code == 413


class TestAnalysisResultEndpoint:

    def test_unknown_id_returns_404(self):
        resp = client.get("/api/analysis/nonexistent-id-12345")
        assert resp.status_code == 404

    def test_processing_status_returns_200_with_processing(self):
        analysis_store["test-proc-id"] = {"status": "processing", "filename": "a.pdf"}
        resp = client.get("/api/analysis/test-proc-id")
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"

    def test_error_status_returns_500(self):
        analysis_store["test-err-id"] = {"status": "error", "error": "Something went wrong"}
        resp = client.get("/api/analysis/test-err-id")
        assert resp.status_code == 500

    def test_complete_status_returns_result(self):
        analysis_store["test-done-id"] = {
            "status": "complete",
            "result": {"analysis_id": "test-done-id", "contract_type": "NDA"},
        }
        resp = client.get("/api/analysis/test-done-id")
        assert resp.status_code == 200
        assert resp.json()["contract_type"] == "NDA"

    def test_invalid_short_id_returns_400(self):
        resp = client.get("/api/analysis/ab")
        assert resp.status_code == 400


class TestStatusEndpoint:

    def test_known_id_returns_status(self):
        analysis_store["test-status-id"] = {"status": "processing", "filename": "b.pdf"}
        resp = client.get("/api/analysis/test-status-id/status")
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"

    def test_unknown_id_returns_404(self):
        resp = client.get("/api/analysis/not-here-xyz/status")
        assert resp.status_code == 404


class TestHistoryEndpoint:

    def test_history_returns_200(self):
        with patch("main._firestore") as mock_fs:
            mock_fs.is_available.return_value = False
            resp = client.get("/api/history")
        assert resp.status_code == 200
        assert "analyses" in resp.json()

    def test_history_limit_too_large_returns_400(self):
        resp = client.get("/api/history?limit=200")
        assert resp.status_code == 400

    def test_history_limit_zero_returns_400(self):
        resp = client.get("/api/history?limit=0")
        assert resp.status_code == 400


class TestTTSEndpoints:

    def test_tts_verdict_not_complete_returns_404(self):
        analysis_store["tts-proc-id"] = {"status": "processing"}
        resp = client.get("/api/tts/tts-proc-id/verdict")
        assert resp.status_code == 404

    def test_tts_finding_unknown_analysis_returns_404(self):
        resp = client.get("/api/tts/no-such-id/finding/abc123")
        assert resp.status_code == 404

    def test_tts_verdict_no_service_returns_503(self):
        analysis_store["tts-done-id"] = {
            "status": "complete",
            "result": {"one_liner_verdict": "Do not sign.", "executive_summary": "Risky."},
        }
        with patch("main._tts") as mock_tts:
            mock_tts.is_available.return_value = False
            resp = client.get("/api/tts/tts-done-id/verdict")
        assert resp.status_code == 503
