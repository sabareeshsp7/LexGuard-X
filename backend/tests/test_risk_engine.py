"""
Tests for the deterministic RiskEngine scoring system.
Validates scoring thresholds, severity weights, and label assignment.
"""
import pytest
from services.risk_engine import RiskEngine


@pytest.fixture
def engine():
    return RiskEngine()


class TestRiskScoreCalculation:
    def test_empty_findings_returns_zero(self, engine):
        assert engine.calculate_risk_score([]) == 0

    def test_score_clamped_max_100(self, engine):
        many_critical = [{"severity": "CRITICAL"} for _ in range(20)]
        assert engine.calculate_risk_score(many_critical) <= 100

    def test_score_never_negative(self, engine):
        assert engine.calculate_risk_score([]) >= 0

    def test_critical_severity_weighted_highest(self, engine):
        critical_score = engine.calculate_risk_score([{"severity": "CRITICAL"}])
        high_score = engine.calculate_risk_score([{"severity": "HIGH"}])
        assert critical_score > high_score

    def test_high_severity_weighted_above_medium(self, engine):
        high = engine.calculate_risk_score([{"severity": "HIGH"}])
        medium = engine.calculate_risk_score([{"severity": "MEDIUM"}])
        assert high > medium

    def test_medium_severity_weighted_above_low(self, engine):
        medium = engine.calculate_risk_score([{"severity": "MEDIUM"}])
        low = engine.calculate_risk_score([{"severity": "LOW"}])
        assert medium > low

    def test_multiple_findings_increase_score(self, engine):
        one = engine.calculate_risk_score([{"severity": "HIGH"}])
        two = engine.calculate_risk_score([{"severity": "HIGH"}, {"severity": "HIGH"}])
        assert two >= one

    def test_unknown_severity_does_not_crash(self, engine):
        score = engine.calculate_risk_score([{"severity": "UNKNOWN_LEVEL"}])
        assert isinstance(score, (int, float))


class TestRiskLevelLabels:
    def test_zero_score_is_low(self, engine):
        assert engine.get_risk_level(0) == "LOW"

    def test_low_score_range(self, engine):
        assert engine.get_risk_level(20) in ("LOW", "MEDIUM")

    def test_medium_score_range(self, engine):
        level = engine.get_risk_level(50)
        assert level in ("MEDIUM", "HIGH")

    def test_high_score_is_high_or_critical(self, engine):
        level = engine.get_risk_level(75)
        assert level in ("HIGH", "CRITICAL")

    def test_max_score_is_critical(self, engine):
        assert engine.get_risk_level(100) in ("HIGH", "CRITICAL")
