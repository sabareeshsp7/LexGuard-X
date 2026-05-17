import json
import time
import uuid
from typing import List, Callable, Optional
from services.vertex_client import VertexClient
from models.schemas import (
    RiskFinding, FutureScenario, NegotiationAlternative,
    SeverityLevel, RiskCategory, ContractType, AgentStatus
)


class LegalAgents:
    """
    The 8 specialized AI legal agents powered by Vertex AI Gemini 3.1 Flash Lite.
    Each agent is an expert persona with a targeted prompt engineering strategy.
    """

    def __init__(self):
        self.vertex = VertexClient()

    # ─────────────────────────────────────────
    # AGENT 1: Contract Classifier
    # ─────────────────────────────────────────
    def classify_contract(self, text: str, progress_cb: Optional[Callable] = None) -> ContractType:
        """Identifies the type of contract."""
        if progress_cb:
            progress_cb("Contract Classifier", AgentStatus.RUNNING, "Identifying contract type...", 5)

        prompt = f"""You are a legal document classification expert with 20+ years of experience.
Analyze this contract text and identify its type.

Contract Text (first 3000 characters):
{text[:3000]}

Choose the SINGLE best matching category:
- Employment Agreement
- Freelance Contract
- Rental Agreement
- Privacy Policy
- SaaS Terms of Service
- Insurance Policy
- Vendor Agreement
- Non-Disclosure Agreement
- Unknown

Return ONLY valid JSON:
{{"contract_type": "Employment Agreement", "confidence": "high", "reasoning": "Contains employment terms, salary, and non-compete..."}}
"""
        try:
            result = self.vertex.generate_json(prompt)
            contract_type_str = result.get("contract_type", "Unknown")
            for ct in ContractType:
                if ct.value == contract_type_str:
                    if progress_cb:
                        progress_cb("Contract Classifier", AgentStatus.DONE, f"Detected: {ct.value}", 10)
                    return ct
        except Exception as e:
            print(f"[Classifier] Error: {e}")

        if progress_cb:
            progress_cb("Contract Classifier", AgentStatus.DONE, "Type: Unknown", 10)
        return ContractType.UNKNOWN

    # ─────────────────────────────────────────
    # AGENT 2: Legal Risk Analyst
    # ─────────────────────────────────────────
    def analyze_legal_risks(
        self,
        chunks: List[str],
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[RiskFinding]:
        """Finds harmful, exploitative, and one-sided clauses."""
        if progress_cb:
            progress_cb("Legal Risk Agent", AgentStatus.RUNNING, "Scanning for harmful clauses...", 20)

        findings = []
        # Analyze up to 8 most relevant chunks
        for i, chunk in enumerate(chunks[:8]):
            if len(chunk.strip()) < 50:
                continue
            try:
                result = self._run_legal_risk_on_chunk(chunk, contract_type.value)
                if result:
                    findings.append(result)
            except Exception as e:
                print(f"[Legal Agent] Chunk {i} error: {e}")

        if progress_cb:
            progress_cb("Legal Risk Agent", AgentStatus.DONE,
                        f"Found {len(findings)} legal risks", 35)
        return findings

    def _run_legal_risk_on_chunk(self, chunk: str, contract_type: str) -> Optional[RiskFinding]:
        prompt = f"""You are a senior contract attorney with 20+ years of litigation experience.
You EXCLUSIVELY represent the USER/EMPLOYEE/TENANT (NOT the company or employer).

Analyze this contract clause and determine if it poses risk to the user.

Contract Type: {contract_type}
Clause:
{chunk}

If this clause IS risky or harmful, return JSON. If it is standard/benign, return {{"risk": false}}.

For risky clauses:
{{
  "risk": true,
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "category": "NON_COMPETE|IP_TRANSFER|TERMINATION|ARBITRATION|PRIVACY|FINANCIAL|LIABILITY|DATA_COLLECTION|AMBIGUITY|OTHER",
  "plain_explanation": "In plain English: what this means for the user (max 3 sentences)",
  "problematic_language": "exact quote from clause that is problematic",
  "industry_standard": "What is typically standard/fair in this type of contract",
  "user_rights_impacted": ["right1", "right2"],
  "user_impact_score": 7.5
}}

IMPORTANT: Be specific. Only flag genuine risks. Rate severity honestly.
CRITICAL = could significantly harm user financially/legally/personally
HIGH = unfair or one-sided
MEDIUM = concerning but not severe
LOW = minor issue
"""
        result = self.vertex.generate_json(prompt)
        if not result.get("risk", False):
            return None

        return RiskFinding(
            clause_id=str(uuid.uuid4())[:8],
            severity=SeverityLevel(result.get("severity", "LOW")),
            category=RiskCategory(result.get("category", "OTHER")),
            clause_text=chunk[:500],
            plain_explanation=result.get("plain_explanation", ""),
            problematic_language=result.get("problematic_language", ""),
            industry_standard=result.get("industry_standard", ""),
            user_rights_impacted=result.get("user_rights_impacted", []),
            user_impact_score=float(result.get("user_impact_score", 5.0))
        )

    # ─────────────────────────────────────────
    # AGENT 3: Privacy & Data Agent
    # ─────────────────────────────────────────
    def analyze_privacy_risks(
        self,
        full_text: str,
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[RiskFinding]:
        """Detects data collection, GDPR risks, and privacy violations."""
        if progress_cb:
            progress_cb("Privacy Agent", AgentStatus.RUNNING, "Analyzing data & privacy clauses...", 38)

        prompt = f"""You are a data privacy expert and GDPR/CCPA compliance specialist.
Analyze this {contract_type.value} for privacy and data collection risks.

Contract Text:
{full_text[:4000]}

Identify ALL privacy risks. Return JSON:
{{
  "findings": [
    {{
      "severity": "HIGH",
      "category": "DATA_COLLECTION",
      "plain_explanation": "...",
      "problematic_language": "exact quote",
      "industry_standard": "...",
      "user_rights_impacted": ["Data minimization right", "Right to erasure"],
      "user_impact_score": 8.0
    }}
  ]
}}

Look for:
- Excessive personal data collection
- Sharing data with third parties without consent
- No right to deletion/erasure
- Tracking and profiling without notice
- Indefinite data retention
- Broad data use permissions

If NO privacy risks found, return {{"findings": []}}
"""
        findings = []
        try:
            result = self.vertex.generate_json(prompt)
            for item in result.get("findings", []):
                findings.append(RiskFinding(
                    clause_id=str(uuid.uuid4())[:8],
                    severity=SeverityLevel(item.get("severity", "MEDIUM")),
                    category=RiskCategory(item.get("category", "PRIVACY")),
                    clause_text=item.get("problematic_language", ""),
                    plain_explanation=item.get("plain_explanation", ""),
                    problematic_language=item.get("problematic_language", ""),
                    industry_standard=item.get("industry_standard", ""),
                    user_rights_impacted=item.get("user_rights_impacted", []),
                    user_impact_score=float(item.get("user_impact_score", 5.0))
                ))
        except Exception as e:
            print(f"[Privacy Agent] Error: {e}")

        if progress_cb:
            progress_cb("Privacy Agent", AgentStatus.DONE,
                        f"Found {len(findings)} privacy risks", 48)
        return findings

    # ─────────────────────────────────────────
    # AGENT 4: Financial Liability Agent
    # ─────────────────────────────────────────
    def analyze_financial_risks(
        self,
        full_text: str,
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[RiskFinding]:
        """Detects hidden fees, auto-renewals, and financial penalties."""
        if progress_cb:
            progress_cb("Financial Agent", AgentStatus.RUNNING, "Scanning financial clauses...", 50)

        prompt = f"""You are a financial risk analyst specializing in contract law.
Analyze this {contract_type.value} for financial risks and hidden liabilities.

Contract Text:
{full_text[:4000]}

Find ALL financial risks. Return JSON:
{{
  "findings": [
    {{
      "severity": "HIGH",
      "category": "FINANCIAL",
      "plain_explanation": "...",
      "problematic_language": "exact quote",
      "industry_standard": "...",
      "user_rights_impacted": ["Financial protection"],
      "user_impact_score": 7.0
    }}
  ]
}}

Look for:
- Hidden fees and charges
- Auto-renewal without notice
- Difficult cancellation terms
- Non-refundable deposits or fees
- Penalty clauses that favor the company
- Vague pricing that allows increases
- Liability caps that favor the company
- Indemnification clauses requiring user to pay company's legal costs

Return {{"findings": []}} if none found.
"""
        findings = []
        try:
            result = self.vertex.generate_json(prompt)
            for item in result.get("findings", []):
                findings.append(RiskFinding(
                    clause_id=str(uuid.uuid4())[:8],
                    severity=SeverityLevel(item.get("severity", "MEDIUM")),
                    category=RiskCategory(item.get("category", "FINANCIAL")),
                    clause_text=item.get("problematic_language", ""),
                    plain_explanation=item.get("plain_explanation", ""),
                    problematic_language=item.get("problematic_language", ""),
                    industry_standard=item.get("industry_standard", ""),
                    user_rights_impacted=item.get("user_rights_impacted", []),
                    user_impact_score=float(item.get("user_impact_score", 5.0))
                ))
        except Exception as e:
            print(f"[Financial Agent] Error: {e}")

        if progress_cb:
            progress_cb("Financial Agent", AgentStatus.DONE,
                        f"Found {len(findings)} financial risks", 60)
        return findings

    # ─────────────────────────────────────────
    # AGENT 5: Ambiguity Detector
    # ─────────────────────────────────────────
    def detect_ambiguity(
        self,
        full_text: str,
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[RiskFinding]:
        """Identifies vague, contradictory, and undefined language."""
        if progress_cb:
            progress_cb("Ambiguity Detector", AgentStatus.RUNNING, "Detecting vague language...", 62)

        prompt = f"""You are a linguistic and legal clarity expert.
Analyze this {contract_type.value} for ambiguous, vague, or contradictory language.

Contract Text:
{full_text[:4000]}

Return JSON:
{{
  "findings": [
    {{
      "severity": "MEDIUM",
      "category": "AMBIGUITY",
      "plain_explanation": "This phrase is undefined and could be interpreted broadly against you",
      "problematic_language": "exact vague quote",
      "industry_standard": "Should clearly define scope and duration",
      "user_rights_impacted": ["Legal clarity", "Informed consent"],
      "user_impact_score": 6.0
    }}
  ]
}}

Look for:
- Undefined terms like "reasonable", "at our discretion", "as deemed appropriate"
- Contradictions between sections
- Clauses that give one party unlimited interpretation power
- Missing definitions for key obligations
- Vague timelines ("soon", "promptly", "within a reasonable time")

Return {{"findings": []}} if none found.
"""
        findings = []
        try:
            result = self.vertex.generate_json(prompt)
            for item in result.get("findings", []):
                findings.append(RiskFinding(
                    clause_id=str(uuid.uuid4())[:8],
                    severity=SeverityLevel(item.get("severity", "MEDIUM")),
                    category=RiskCategory.AMBIGUITY,
                    clause_text=item.get("problematic_language", ""),
                    plain_explanation=item.get("plain_explanation", ""),
                    problematic_language=item.get("problematic_language", ""),
                    industry_standard=item.get("industry_standard", ""),
                    user_rights_impacted=item.get("user_rights_impacted", []),
                    user_impact_score=float(item.get("user_impact_score", 4.0))
                ))
        except Exception as e:
            print(f"[Ambiguity Agent] Error: {e}")

        if progress_cb:
            progress_cb("Ambiguity Detector", AgentStatus.DONE,
                        f"Found {len(findings)} ambiguous clauses", 70)
        return findings

    # ─────────────────────────────────────────
    # AGENT 6: Future Consequence Simulator
    # ─────────────────────────────────────────
    def simulate_future_consequences(
        self,
        findings: List[RiskFinding],
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[FutureScenario]:
        """Simulates 3 real-world scenarios after signing."""
        if progress_cb:
            progress_cb("Future Simulator", AgentStatus.RUNNING, "Simulating future scenarios...", 72)

        if not findings:
            if progress_cb:
                progress_cb("Future Simulator", AgentStatus.DONE, "No risks to simulate", 80)
            return []

        # Use top 3 most critical findings for simulation
        top_findings = sorted(findings, key=lambda f: f.user_impact_score, reverse=True)[:3]
        findings_summary = "\n".join([
            f"- [{f.severity.value}] {f.category.value}: {f.plain_explanation}"
            for f in top_findings
        ])

        prompt = f"""You are a legal risk scenario analyst. 
Simulate 3 realistic future scenarios for someone who signs this {contract_type.value}.

Key risks identified:
{findings_summary}

Return JSON:
{{
  "scenarios": [
    {{
      "scenario_type": "best_case",
      "trigger": "What would have to happen for this to be enforced",
      "user_loss": "What the user loses (be specific)",
      "financial_impact": "Estimated financial impact e.g. $2,000-$10,000",
      "probability": "Low|Medium|High",
      "timeline": "When this typically occurs e.g. within 6 months of signing"
    }},
    {{
      "scenario_type": "realistic",
      ...
    }},
    {{
      "scenario_type": "worst_case",
      ...
    }}
  ]
}}

Make scenarios concrete, specific, and realistic. Not hypothetical horror stories.
"""
        try:
            result = self.vertex.generate_json(prompt)
            scenarios = []
            for s in result.get("scenarios", []):
                scenarios.append(FutureScenario(
                    scenario_type=s.get("scenario_type", "unknown"),
                    trigger=s.get("trigger", ""),
                    user_loss=s.get("user_loss", ""),
                    financial_impact=s.get("financial_impact", "Unknown"),
                    probability=s.get("probability", "Medium"),
                    timeline=s.get("timeline", "Unknown")
                ))

            if progress_cb:
                progress_cb("Future Simulator", AgentStatus.DONE, "3 scenarios simulated", 80)
            return scenarios
        except Exception as e:
            print(f"[Future Agent] Error: {e}")
            if progress_cb:
                progress_cb("Future Simulator", AgentStatus.ERROR, f"Simulation error: {e}", 80)
            return []

    # ─────────────────────────────────────────
    # AGENT 7: Negotiation Advisor
    # ─────────────────────────────────────────
    def generate_negotiation_advice(
        self,
        findings: List[RiskFinding],
        contract_type: ContractType,
        progress_cb: Optional[Callable] = None
    ) -> List[NegotiationAlternative]:
        """Suggests counter-clauses and negotiation strategies."""
        if progress_cb:
            progress_cb("Negotiation Advisor", AgentStatus.RUNNING, "Drafting negotiation strategy...", 82)

        if not findings:
            if progress_cb:
                progress_cb("Negotiation Advisor", AgentStatus.DONE, "No negotiations needed", 90)
            return []

        critical_findings = [f for f in findings if f.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
        if not critical_findings:
            critical_findings = findings[:2]

        alternatives = []
        for finding in critical_findings[:3]:
            prompt = f"""You are an expert contract negotiation specialist representing the USER.
Provide 1 negotiation alternative for this risky clause.

Contract Type: {contract_type.value}
Problematic Clause: {finding.clause_text[:400]}
Issue: {finding.plain_explanation}
Category: {finding.category.value}

Return JSON:
{{
  "revised_text": "Here is the revised clause text that protects the user better...",
  "why_better": "This version is better because...",
  "likelihood_accepted": "Low|Medium|High",
  "fallback": "If they won't accept this, the minimum acceptable compromise is..."
}}
"""
            try:
                result = self.vertex.generate_json(prompt)
                alternatives.append(NegotiationAlternative(
                    revised_text=result.get("revised_text", ""),
                    why_better=result.get("why_better", ""),
                    likelihood_accepted=result.get("likelihood_accepted", "Medium"),
                    fallback=result.get("fallback", "")
                ))
            except Exception as e:
                print(f"[Negotiation Agent] Error: {e}")

        if progress_cb:
            progress_cb("Negotiation Advisor", AgentStatus.DONE,
                        f"{len(alternatives)} negotiation strategies ready", 90)
        return alternatives

    # ─────────────────────────────────────────
    # AGENT 8: Judge / Synthesizer
    # ─────────────────────────────────────────
    def synthesize_verdict(
        self,
        findings: List[RiskFinding],
        contract_type: ContractType,
        risk_score: float,
        progress_cb: Optional[Callable] = None
    ) -> dict:
        """Combines all findings into a final executive summary and one-liner verdict."""
        if progress_cb:
            progress_cb("Judge Agent", AgentStatus.RUNNING, "Synthesizing final verdict...", 92)

        severity_counts = {}
        for f in findings:
            severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1

        findings_summary = "\n".join([
            f"- [{f.severity.value}] {f.category.value}: {f.plain_explanation[:100]}"
            for f in findings[:10]
        ])

        prompt = f"""You are the Chief Legal Judge synthesizing findings from multiple AI legal agents.

Contract Type: {contract_type.value}
Overall Risk Score: {risk_score}/100
Finding Summary:
{findings_summary}
Severity Counts: {json.dumps(severity_counts)}

Provide:
1. executive_summary: 3-4 sentence plain English summary for someone with no legal background
2. one_liner_verdict: ONE sentence verdict (like a judge's ruling) — direct, clear, actionable
3. recommendation: "SIGN", "NEGOTIATE", "DO NOT SIGN", or "REVIEW WITH LAWYER"

Return JSON:
{{
  "executive_summary": "...",
  "one_liner_verdict": "...",
  "recommendation": "NEGOTIATE"
}}
"""
        try:
            result = self.vertex.generate_json(prompt)
            if progress_cb:
                progress_cb("Judge Agent", AgentStatus.DONE, "Verdict ready", 100)
            return result
        except Exception as e:
            print(f"[Judge Agent] Error: {e}")
            if progress_cb:
                progress_cb("Judge Agent", AgentStatus.ERROR, f"Error: {e}", 100)
            return {
                "executive_summary": "Analysis complete. Review the findings carefully.",
                "one_liner_verdict": "Multiple risks detected — consult a lawyer before signing.",
                "recommendation": "REVIEW WITH LAWYER"
            }
