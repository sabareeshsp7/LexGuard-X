// ─── Shared TypeScript types ─────────────────────────────────────────────────
// Kept in a separate file so components can import types without triggering
// Vite/esbuild module-value resolution errors.

export interface AgentEvent {
  agent_name: string;
  status: 'pending' | 'running' | 'done' | 'error';
  message: string;
  progress: number;
  findings_count: number;
}

export interface RiskScore {
  overall_score: number;
  level: string;
  privacy_score: number;
  financial_score: number;
  legal_score: number;
  ip_score: number;
  ambiguity_score: number;
  employment_score: number;
}

export interface RiskFinding {
  clause_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  category: string;
  clause_text: string;
  plain_explanation: string;
  problematic_language: string;
  industry_standard: string;
  user_rights_impacted: string[];
  user_impact_score: number;
}

export interface FutureScenario {
  scenario_type: string;
  trigger: string;
  user_loss: string;
  financial_impact: string;
  probability: string;
  timeline: string;
}

export interface NegotiationAlternative {
  revised_text: string;
  why_better: string;
  likelihood_accepted: string;
  fallback: string;
}

export interface AgentResult {
  agent_name: string;
  summary: string;
  processing_time_seconds: number;
  findings: RiskFinding[];
}

export interface AnalysisResult {
  analysis_id: string;
  contract_type: string;
  file_name: string;
  total_clauses_found: number;
  risk_score: RiskScore;
  findings: RiskFinding[];
  future_scenarios: FutureScenario[];
  negotiation_recommendations: NegotiationAlternative[];
  executive_summary: string;
  one_liner_verdict: string;
  agent_results: AgentResult[];
  created_at: string;
  status?: string;
}
