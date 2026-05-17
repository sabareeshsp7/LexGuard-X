"""
Pytest configuration and shared fixtures for LexGuard X test suite.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Point to a test-specific env before importing the app
os.environ.setdefault("GCP_PROJECT_ID", "test-project")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("UPLOAD_DIR", "/tmp/test_uploads")
os.environ.setdefault("CHROMA_PERSIST_DIR", "/tmp/test_chroma")


@pytest.fixture(scope="module")
def client():
    """Return a FastAPI test client with the full app mounted."""
    from main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid 1-page PDF for upload tests."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f\n"
        b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )
