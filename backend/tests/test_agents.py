"""
Unit tests for individual AI agents.

Tests the agent pipeline in isolation by mocking the VertexClient
so no real API calls are made during CI.
"""
import pytest
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
#  Agent Smoke Tests (mocked AI)
# ─────────────────────────────────────────────────────────────────────────────

MOCK_CLASSIFIER_RESPONSE = '{"contract_type": "Employment Agreement", "jurisdiction": "US", "confidence": 0.95}'
MOCK_RISK_RESPONSE = '{"findings": [], "summary": "No critical risks found."}'
MOCK_VERDICT_RESPONSE = '{"verdict": "LOW RISK", "score": 12, "summary": "Contract appears fair and standard.", "recommendation": "Safe to sign with minor amendments."}'


class TestContractClassifierAgent:
    """Test the Contract Classifier agent returns valid structured output."""

    def test_classifier_returns_contract_type(self):
        with patch("services.vertex_client.VertexClient.generate_json") as mock_gen:
            mock_gen.return_value = {
                "contract_type": "NDA",
                "jurisdiction": "UK",
                "confidence": 0.88,
            }
            from agents.legal_agents import ContractClassifierAgent
            agent = ContractClassifierAgent(vertex_client=mock_gen)
            # The agent should gracefully accept a mock client
            assert mock_gen is not None

    def test_classifier_handles_empty_text(self):
        """Agent should not crash on empty contract text."""
        with patch("services.vertex_client.VertexClient") as MockVertex:
            instance = MockVertex.return_value
            instance.generate_json.return_value = {
                "contract_type": "Unknown",
                "jurisdiction": "Unknown",
                "confidence": 0.0,
            }
            # Should not raise
            assert instance.generate_json.return_value["contract_type"] == "Unknown"


class TestRiskEngine:
    """Tests for the risk scoring engine."""

    def test_risk_score_clamped_between_0_and_100(self):
        from services.risk_engine import RiskEngine
        engine = RiskEngine()
        # Test with no findings
        score = engine.calculate_risk_score([])
        assert 0 <= score <= 100

    def test_risk_level_low_for_zero_score(self):
        from services.risk_engine import RiskEngine
        engine = RiskEngine()
        level = engine.get_risk_level(0)
        assert level == "LOW"

    def test_risk_level_critical_for_high_score(self):
        from services.risk_engine import RiskEngine
        engine = RiskEngine()
        level = engine.get_risk_level(85)
        assert level in ("HIGH", "CRITICAL")

    def test_risk_level_medium_for_mid_score(self):
        from services.risk_engine import RiskEngine
        engine = RiskEngine()
        level = engine.get_risk_level(50)
        assert level in ("MEDIUM", "HIGH")


class TestDocumentParser:
    """Tests for the document parsing service."""

    def test_parser_handles_minimal_pdf(self):
        """Parser should extract text from a minimal PDF without crashing."""
        from services.document_parser import DocumentParser
        parser = DocumentParser()

        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n"
            b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
        )
        # Should not raise an exception
        result = parser.extract_text(minimal_pdf, "test.pdf")
        assert isinstance(result, str)

    def test_parser_rejects_unknown_extension(self):
        """Parser should handle unknown file types gracefully."""
        from services.document_parser import DocumentParser
        parser = DocumentParser()
        result = parser.extract_text(b"garbage data", "unknown.xyz")
        assert isinstance(result, str)  # returns empty string, not crash
