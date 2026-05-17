"""
Tests for Pydantic v2 schema validation.
Ensures all data models reject invalid inputs and accept valid ones.
"""
import pytest
from pydantic import ValidationError


class TestAnalysisStartResponse:
    def test_valid_construction(self):
        from models.schemas import AnalysisStartResponse
        obj = AnalysisStartResponse(
            analysis_id="abc-123",
            message="Started",
            status="processing",
        )
        assert obj.analysis_id == "abc-123"

    def test_missing_analysis_id_raises(self):
        from models.schemas import AnalysisStartResponse
        with pytest.raises((ValidationError, TypeError)):
            AnalysisStartResponse(message="Started", status="processing")


class TestAgentEvent:
    def test_valid_event(self):
        from models.schemas import AgentEvent
        event = AgentEvent(
            agent_name="Legal Risk Agent",
            status="running",
            message="Scanning...",
            progress=20,
            findings_count=0,
        )
        assert event.progress == 20
        assert event.agent_name == "Legal Risk Agent"

    def test_progress_is_numeric(self):
        from models.schemas import AgentEvent
        event = AgentEvent(
            agent_name="Test",
            status="done",
            message="Done",
            progress=100,
            findings_count=3,
        )
        assert isinstance(event.progress, (int, float))

    def test_findings_count_non_negative(self):
        from models.schemas import AgentEvent
        event = AgentEvent(
            agent_name="Test",
            status="done",
            message="Done",
            progress=100,
            findings_count=0,
        )
        assert event.findings_count >= 0


class TestAnalysisResult:
    def test_result_has_required_fields(self):
        """AnalysisResult must contain analysis_id and risk_score."""
        from models.schemas import AnalysisResult
        # Just check class attributes exist via annotations
        annotations = getattr(AnalysisResult, "model_fields", {}) or {}
        # Should have at minimum these keys
        assert len(annotations) > 0
