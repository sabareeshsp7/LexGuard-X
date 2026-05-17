"""
Tests for Pydantic data schemas — validation and constraint enforcement.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pydantic import ValidationError
from models.schemas import (
    RiskFinding, RiskScore, FutureScenario, NegotiationAlternative,
    AnalysisResult, AnalysisStartResponse, AgentResult, AgentEvent,
    SeverityLevel, RiskCategory, ContractType, AgentStatus,
)


class TestSeverityLevel:
    def test_all_values_valid(self):
        for v in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            assert SeverityLevel(v).value == v

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            SeverityLevel("EXTREME")


class TestRiskCategory:
    def test_all_categories_valid(self):
        cats = [
            "NON_COMPETE", "IP_TRANSFER", "TERMINATION", "ARBITRATION",
            "PRIVACY", "FINANCIAL", "LIABILITY", "DATA_COLLECTION",
            "AMBIGUITY", "OTHER",
        ]
        for c in cats:
            assert RiskCategory(c).value == c


class TestContractType:
    def test_employment_value(self):
        assert ContractType.EMPLOYMENT.value == "Employment Agreement"

    def test_nda_value(self):
        assert ContractType.NDA.value == "Non-Disclosure Agreement"

    def test_unknown_value(self):
        assert ContractType.UNKNOWN.value == "Unknown"


class TestRiskFinding:
    def _valid_payload(self, **overrides):
        base = {
            "clause_id": "abc12345",
            "severity": SeverityLevel.HIGH,
            "category": RiskCategory.PRIVACY,
            "clause_text": "We may share your data with third parties.",
            "plain_explanation": "Your data can be sold.",
            "problematic_language": "share your data with third parties",
            "industry_standard": "Sharing should require explicit consent.",
            "user_rights_impacted": ["Privacy", "Data minimization"],
            "user_impact_score": 7.5,
        }
        base.update(overrides)
        return base

    def test_valid_finding_creates_successfully(self):
        finding = RiskFinding(**self._valid_payload())
        assert finding.severity == SeverityLevel.HIGH
        assert finding.user_impact_score == 7.5

    def test_impact_score_below_zero_raises(self):
        with pytest.raises(ValidationError):
            RiskFinding(**self._valid_payload(user_impact_score=-1.0))

    def test_impact_score_above_10_raises(self):
        with pytest.raises(ValidationError):
            RiskFinding(**self._valid_payload(user_impact_score=10.1))

    def test_impact_score_boundary_0_is_valid(self):
        f = RiskFinding(**self._valid_payload(user_impact_score=0.0))
        assert f.user_impact_score == 0.0

    def test_impact_score_boundary_10_is_valid(self):
        f = RiskFinding(**self._valid_payload(user_impact_score=10.0))
        assert f.user_impact_score == 10.0

    def test_empty_user_rights_allowed(self):
        f = RiskFinding(**self._valid_payload(user_rights_impacted=[]))
        assert f.user_rights_impacted == []

    def test_missing_required_field_raises(self):
        payload = self._valid_payload()
        del payload["clause_text"]
        with pytest.raises(ValidationError):
            RiskFinding(**payload)

    def test_invalid_severity_raises(self):
        with pytest.raises(ValidationError):
            RiskFinding(**self._valid_payload(severity="EXTREME"))


class TestRiskScore:
    def test_valid_score_creates(self):
        score = RiskScore(
            overall_score=55.0,
            level=SeverityLevel.HIGH,
        )
        assert score.overall_score == 55.0

    def test_overall_score_below_zero_raises(self):
        with pytest.raises(ValidationError):
            RiskScore(overall_score=-1.0, level=SeverityLevel.LOW)

    def test_overall_score_above_100_raises(self):
        with pytest.raises(ValidationError):
            RiskScore(overall_score=100.1, level=SeverityLevel.CRITICAL)

    def test_dimension_scores_default_to_zero(self):
        score = RiskScore(overall_score=0.0, level=SeverityLevel.LOW)
        assert score.privacy_score == 0.0
        assert score.financial_score == 0.0
        assert score.legal_score == 0.0
        assert score.ip_score == 0.0
        assert score.ambiguity_score == 0.0
        assert score.employment_score == 0.0

    def test_dimension_score_above_100_raises(self):
        with pytest.raises(ValidationError):
            RiskScore(
                overall_score=50.0,
                level=SeverityLevel.HIGH,
                privacy_score=101.0,
            )


class TestFutureScenario:
    def test_valid_scenario(self):
        s = FutureScenario(
            scenario_type="worst_case",
            trigger="You change jobs within 12 months",
            user_loss="Forfeit $15,000 in unvested equity",
            financial_impact="$10,000-$20,000",
            probability="Medium",
            timeline="Within 1 year of signing",
        )
        assert s.scenario_type == "worst_case"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            FutureScenario(
                scenario_type="worst_case",
                trigger="...",
                # missing required fields
            )


class TestNegotiationAlternative:
    def test_valid_alternative(self):
        alt = NegotiationAlternative(
            revised_text="The non-compete shall be limited to 6 months.",
            why_better="Shorter duration is fair and enforceable.",
            likelihood_accepted="Medium",
            fallback="Request 12 months instead of 24.",
        )
        assert alt.likelihood_accepted == "Medium"


class TestAnalysisStartResponse:
    def test_valid_response(self):
        r = AnalysisStartResponse(
            analysis_id="abc-123",
            message="Started",
            status="processing",
        )
        assert r.status == "processing"

    def test_missing_analysis_id_raises(self):
        with pytest.raises(ValidationError):
            AnalysisStartResponse(message="Started", status="processing")


class TestAgentStatus:
    def test_all_statuses_valid(self):
        for v in ["pending", "running", "done", "error"]:
            assert AgentStatus(v).value == v
