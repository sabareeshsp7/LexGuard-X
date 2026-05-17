from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ─────────────────────────────────────────
#  Enums
# ─────────────────────────────────────────

class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskCategory(str, Enum):
    NON_COMPETE = "NON_COMPETE"
    IP_TRANSFER = "IP_TRANSFER"
    TERMINATION = "TERMINATION"
    ARBITRATION = "ARBITRATION"
    PRIVACY = "PRIVACY"
    FINANCIAL = "FINANCIAL"
    LIABILITY = "LIABILITY"
    DATA_COLLECTION = "DATA_COLLECTION"
    AMBIGUITY = "AMBIGUITY"
    OTHER = "OTHER"

class ContractType(str, Enum):
    EMPLOYMENT = "Employment Agreement"
    FREELANCE = "Freelance Contract"
    RENTAL = "Rental Agreement"
    PRIVACY_POLICY = "Privacy Policy"
    SAAS_TERMS = "SaaS Terms of Service"
    INSURANCE = "Insurance Policy"
    VENDOR = "Vendor Agreement"
    NDA = "Non-Disclosure Agreement"
    UNKNOWN = "Unknown"

class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


# ─────────────────────────────────────────
#  Risk Finding
# ─────────────────────────────────────────

class RiskFinding(BaseModel):
    clause_id: str
    severity: SeverityLevel
    category: RiskCategory
    clause_text: str = Field(..., description="The original clause text")
    plain_explanation: str = Field(..., description="Plain English explanation")
    problematic_language: str = Field(..., description="Exact quote of problematic part")
    industry_standard: str = Field(..., description="What is normal in this contract type")
    user_rights_impacted: List[str] = Field(default_factory=list)
    user_impact_score: float = Field(ge=0, le=10)


# ─────────────────────────────────────────
#  Future Scenario
# ─────────────────────────────────────────

class FutureScenario(BaseModel):
    scenario_type: str  # best_case, realistic, worst_case
    trigger: str
    user_loss: str
    financial_impact: str
    probability: str  # Low, Medium, High
    timeline: str


# ─────────────────────────────────────────
#  Negotiation Alternative
# ─────────────────────────────────────────

class NegotiationAlternative(BaseModel):
    revised_text: str
    why_better: str
    likelihood_accepted: str  # Low, Medium, High
    fallback: str


# ─────────────────────────────────────────
#  Agent Result
# ─────────────────────────────────────────

class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus
    findings: List[RiskFinding] = Field(default_factory=list)
    summary: str = ""
    processing_time_seconds: float = 0.0


# ─────────────────────────────────────────
#  Risk Score
# ─────────────────────────────────────────

class RiskScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    level: SeverityLevel
    privacy_score: float = Field(ge=0, le=100, default=0)
    financial_score: float = Field(ge=0, le=100, default=0)
    legal_score: float = Field(ge=0, le=100, default=0)
    ip_score: float = Field(ge=0, le=100, default=0)
    ambiguity_score: float = Field(ge=0, le=100, default=0)
    employment_score: float = Field(ge=0, le=100, default=0)


# ─────────────────────────────────────────
#  Full Analysis Result
# ─────────────────────────────────────────

class AnalysisResult(BaseModel):
    analysis_id: str
    contract_type: ContractType
    file_name: str
    total_clauses_found: int
    risk_score: RiskScore
    findings: List[RiskFinding]
    agent_results: List[AgentResult]
    future_scenarios: List[FutureScenario]
    negotiation_recommendations: List[NegotiationAlternative]
    executive_summary: str
    one_liner_verdict: str
    created_at: str


# ─────────────────────────────────────────
#  WebSocket Agent Event
# ─────────────────────────────────────────

class AgentEvent(BaseModel):
    analysis_id: str
    agent_name: str
    status: AgentStatus
    message: str
    progress: int = Field(ge=0, le=100)
    findings_count: int = 0


# ─────────────────────────────────────────
#  API Response Models
# ─────────────────────────────────────────

class AnalysisStartResponse(BaseModel):
    analysis_id: str
    message: str
    status: str

class ErrorResponse(BaseModel):
    error: str
    detail: str
