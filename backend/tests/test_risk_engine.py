"""
Tests for RiskEngine — deterministic risk scoring logic.
No AI calls involved; fully unit-testable.
"""

import pytest
import sys
import os

# Allow imports from backend root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.risk_engine import RiskEngine
from models.schemas import (
    RiskFinding, RiskScore, SeverityLevel, RiskCategory
)


def _make_finding(
    severity: SeverityLevel,
    category: RiskCategory,
    impact: float = 5.0,
) -> RiskFinding:
    """Helper: create a minimal RiskFinding."""
    return RiskFinding(
        clause_id="test01",
        severity=severity,
        category=category,
        clause_text="Sample clause text for testing purposes.",
        plain_explanation="This clause may harm the user.",
        problematic_language="at our sole discretion",
        industry_standard="Should be mutually agreed upon.",
        user_rights_impacted=["Right to notice"],
        user_impact_score=impact,
    )


class TestRiskEngine:
    """Unit tests for RiskEngine scoring and prioritization."""

    def setup_method(self):
        self.engine = RiskEngine()

    # ── Score calculation ──────────────────────────────────────────

    def test_empty_findings_returns_zero_score(self):
        score = self.engine.calculate([])
        assert score.overall_score == 0
        assert score.level == SeverityLevel.LOW

    def test_single_critical_finding_scores_above_25(self):
        findings = [_make_finding(SeverityLevel.CRITICAL, RiskCategory.IP_TRANSFER)]
        score = self.engine.calculate(findings)
        # CRITICAL base=25 + IP_TRANSFER bonus=10 → 35
        assert score.overall_score >= 35

    def test_single_low_finding_stays_low_level(self):
        findings = [_make_finding(SeverityLevel.LOW, RiskCategory.OTHER)]
        score = self.engine.calculate(findings)
        assert score.level == SeverityLevel.LOW

    def test_score_never_exceeds_100(self):
        # 20 CRITICAL IP_TRANSFER findings — should clamp at 100
        findings = [
            _make_finding(SeverityLevel.CRITICAL, RiskCategory.IP_TRANSFER)
            for _ in range(20)
        ]
        score = self.engine.calculate(findings)
        assert score.overall_score <= 100.0

    def test_score_is_non_negative(self):
        findings = [_make_finding(SeverityLevel.LOW, RiskCategory.AMBIGUITY)]
        score = self.engine.calculate(findings)
        assert score.overall_score >= 0.0

    # ── Severity thresholds ────────────────────────────────────────

    def test_critical_level_at_75_plus(self):
        # Force score over 75 with multiple critical IP findings
        findings = [
            _make_finding(SeverityLevel.CRITICAL, RiskCategory.IP_TRANSFER)
            for _ in range(4)
        ]
        score = self.engine.calculate(findings)
        if score.overall_score >= 75:
            assert score.level == SeverityLevel.CRITICAL

    def test_high_level_between_50_and_74(self):
        findings = [
            _make_finding(SeverityLevel.HIGH, RiskCategory.NON_COMPETE),
            _make_finding(SeverityLevel.HIGH, RiskCategory.ARBITRATION),
        ]
        score = self.engine.calculate(findings)
        # 2×(15+8) + 2×(7) = 46+14 = 60 → HIGH
        if 50 <= score.overall_score < 75:
            assert score.level == SeverityLevel.HIGH

    # ── Dimension scores ───────────────────────────────────────────

    def test_privacy_finding_increments_privacy_score(self):
        findings = [_make_finding(SeverityLevel.HIGH, RiskCategory.PRIVACY)]
        score = self.engine.calculate(findings)
        assert score.privacy_score > 0

    def test_financial_finding_increments_financial_score(self):
        findings = [_make_finding(SeverityLevel.MEDIUM, RiskCategory.FINANCIAL)]
        score = self.engine.calculate(findings)
        assert score.financial_score > 0

    def test_ip_finding_increments_ip_score(self):
        findings = [_make_finding(SeverityLevel.CRITICAL, RiskCategory.IP_TRANSFER)]
        score = self.engine.calculate(findings)
        assert score.ip_score > 0

    def test_non_compete_increments_employment_score(self):
        findings = [_make_finding(SeverityLevel.HIGH, RiskCategory.NON_COMPETE)]
        score = self.engine.calculate(findings)
        assert score.employment_score > 0

    def test_dimension_scores_never_exceed_100(self):
        findings = [
            _make_finding(SeverityLevel.CRITICAL, RiskCategory.PRIVACY)
            for _ in range(10)
        ]
        score = self.engine.calculate(findings)
        assert score.privacy_score <= 100.0

    # ── Risk labels ────────────────────────────────────────────────

    def test_get_risk_label_critical(self):
        label = self.engine.get_risk_label(80.0)
        assert "CRITICAL" in label

    def test_get_risk_label_high(self):
        label = self.engine.get_risk_label(60.0)
        assert "HIGH" in label

    def test_get_risk_label_medium(self):
        label = self.engine.get_risk_label(30.0)
        assert "MEDIUM" in label

    def test_get_risk_label_low(self):
        label = self.engine.get_risk_label(10.0)
        assert "LOW" in label

    # ── Prioritization ─────────────────────────────────────────────

    def test_prioritize_returns_critical_first(self):
        findings = [
            _make_finding(SeverityLevel.LOW, RiskCategory.AMBIGUITY, 1.0),
            _make_finding(SeverityLevel.CRITICAL, RiskCategory.IP_TRANSFER, 9.0),
            _make_finding(SeverityLevel.MEDIUM, RiskCategory.PRIVACY, 5.0),
        ]
        prioritized = self.engine.prioritize_findings(findings)
        assert prioritized[0].severity == SeverityLevel.CRITICAL

    def test_prioritize_sorts_by_impact_within_same_severity(self):
        findings = [
            _make_finding(SeverityLevel.HIGH, RiskCategory.FINANCIAL, 3.0),
            _make_finding(SeverityLevel.HIGH, RiskCategory.ARBITRATION, 8.0),
        ]
        prioritized = self.engine.prioritize_findings(findings)
        assert prioritized[0].user_impact_score == 8.0

    def test_prioritize_empty_list_returns_empty(self):
        result = self.engine.prioritize_findings([])
        assert result == []

    def test_prioritize_preserves_all_findings(self):
        findings = [
            _make_finding(SeverityLevel.LOW, RiskCategory.OTHER),
            _make_finding(SeverityLevel.HIGH, RiskCategory.PRIVACY),
        ]
        result = self.engine.prioritize_findings(findings)
        assert len(result) == 2

    # ── RiskScore model validation ─────────────────────────────────

    def test_risk_score_model_fields_present(self):
        findings = [_make_finding(SeverityLevel.MEDIUM, RiskCategory.LIABILITY)]
        score = self.engine.calculate(findings)
        assert hasattr(score, "overall_score")
        assert hasattr(score, "level")
        assert hasattr(score, "privacy_score")
        assert hasattr(score, "financial_score")
        assert hasattr(score, "legal_score")
        assert hasattr(score, "ip_score")
        assert hasattr(score, "ambiguity_score")
        assert hasattr(score, "employment_score")
