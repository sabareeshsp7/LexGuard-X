from typing import List, Dict
from models.schemas import RiskFinding, RiskScore, SeverityLevel, RiskCategory


class RiskEngine:
    """
    Calculates weighted risk scores from agent findings.
    Produces an overall score (0-100) and per-category breakdown.
    """

    # Base weights by severity
    SEVERITY_WEIGHTS = {
        SeverityLevel.CRITICAL: 25,
        SeverityLevel.HIGH: 15,
        SeverityLevel.MEDIUM: 8,
        SeverityLevel.LOW: 3,
    }

    # Category danger bonuses (added on top of severity)
    CATEGORY_BONUSES = {
        RiskCategory.IP_TRANSFER: 10,
        RiskCategory.NON_COMPETE: 8,
        RiskCategory.ARBITRATION: 7,
        RiskCategory.PRIVACY: 6,
        RiskCategory.DATA_COLLECTION: 6,
        RiskCategory.FINANCIAL: 5,
        RiskCategory.TERMINATION: 5,
        RiskCategory.LIABILITY: 4,
        RiskCategory.AMBIGUITY: 2,
        RiskCategory.OTHER: 0,
    }

    # Category → score dimension mapping
    CATEGORY_DIMENSION = {
        RiskCategory.NON_COMPETE: "employment_score",
        RiskCategory.TERMINATION: "employment_score",
        RiskCategory.IP_TRANSFER: "ip_score",
        RiskCategory.PRIVACY: "privacy_score",
        RiskCategory.DATA_COLLECTION: "privacy_score",
        RiskCategory.FINANCIAL: "financial_score",
        RiskCategory.ARBITRATION: "legal_score",
        RiskCategory.LIABILITY: "legal_score",
        RiskCategory.AMBIGUITY: "ambiguity_score",
        RiskCategory.OTHER: "legal_score",
    }

    def calculate(self, findings: List[RiskFinding]) -> RiskScore:
        """Calculate full risk score from list of findings."""

        if not findings:
            return RiskScore(
                overall_score=0,
                level=SeverityLevel.LOW,
            )

        # Calculate overall score
        base_score = sum(
            self.SEVERITY_WEIGHTS.get(f.severity, 3)
            for f in findings
        )
        bonus = sum(
            self.CATEGORY_BONUSES.get(f.category, 0)
            for f in findings
        )
        overall = min(100.0, base_score + bonus)

        # Determine level
        if overall >= 75:
            level = SeverityLevel.CRITICAL
        elif overall >= 50:
            level = SeverityLevel.HIGH
        elif overall >= 25:
            level = SeverityLevel.MEDIUM
        else:
            level = SeverityLevel.LOW

        # Calculate per-category dimension scores
        dimension_scores: Dict[str, float] = {
            "privacy_score": 0.0,
            "financial_score": 0.0,
            "legal_score": 0.0,
            "ip_score": 0.0,
            "ambiguity_score": 0.0,
            "employment_score": 0.0,
        }

        for finding in findings:
            dim = self.CATEGORY_DIMENSION.get(finding.category, "legal_score")
            dimension_scores[dim] += self.SEVERITY_WEIGHTS.get(finding.severity, 3)

        # Normalize each dimension to 0-100
        for key in dimension_scores:
            dimension_scores[key] = min(100.0, dimension_scores[key])

        return RiskScore(
            overall_score=round(overall, 1),
            level=level,
            **{k: round(v, 1) for k, v in dimension_scores.items()}
        )

    def get_risk_label(self, score: float) -> str:
        """Human-readable label for a score."""
        if score >= 75:
            return "CRITICAL — Do not sign without legal review"
        elif score >= 50:
            return "HIGH RISK — Significant concerns found"
        elif score >= 25:
            return "MEDIUM RISK — Review highlighted clauses"
        else:
            return "LOW RISK — Minor issues found"

    def prioritize_findings(self, findings: List[RiskFinding]) -> List[RiskFinding]:
        """Sort findings by severity and impact score."""
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3,
        }
        return sorted(
            findings,
            key=lambda f: (severity_order[f.severity], -f.user_impact_score)
        )
