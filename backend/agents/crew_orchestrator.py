import asyncio
import time
from typing import List, Callable, Optional
from models.schemas import (
    AnalysisResult, AgentResult, AgentStatus,
    RiskFinding, FutureScenario, NegotiationAlternative,
    ContractType, RiskScore
)
from agents.legal_agents import LegalAgents
from services.rag_engine import RAGEngine
from services.risk_engine import RiskEngine
from datetime import datetime, timezone


class CrewOrchestrator:
    """
    Orchestrates the 8 LexGuard AI agents in sequence.
    Broadcasts progress via WebSocket callback.
    """

    def __init__(self):
        self.agents = LegalAgents()
        self.rag = RAGEngine()
        self.risk_engine = RiskEngine()
        self.agent_results: List[AgentResult] = []

    def run(
        self,
        analysis_id: str,
        full_text: str,
        filename: str,
        progress_cb: Optional[Callable] = None
    ) -> AnalysisResult:
        """
        Main orchestration pipeline. Runs all 8 agents sequentially
        with progress callbacks for live WebSocket updates.
        """
        all_findings: List[RiskFinding] = []
        start_time = time.time()

        def agent_cb(agent_name: str, status: AgentStatus, message: str, progress: int):
            """Internal callback that tracks agent results and broadcasts progress."""
            if progress_cb:
                progress_cb(agent_name, status, message, progress,
                            len(all_findings))
            print(f"[{agent_name}] [{status.value}] {message} ({progress}%)")

        # ── PHASE 1: RAG Setup ─────────────────────────────────────────
        agent_cb("RAG Engine", AgentStatus.RUNNING, "Chunking and embedding contract...", 2)
        chunks = self.rag.chunk_text(full_text)
        self.rag.store_chunks(analysis_id, chunks)
        agent_cb("RAG Engine", AgentStatus.DONE, f"Stored {len(chunks)} semantic chunks", 8)

        # ── AGENT 1: Contract Classifier ───────────────────────────────
        t0 = time.time()
        contract_type = self.agents.classify_contract(full_text, agent_cb)
        self.agent_results.append(AgentResult(
            agent_name="Contract Classifier",
            status=AgentStatus.DONE,
            summary=f"Contract identified as: {contract_type.value}",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 2: Legal Risk Analyst ────────────────────────────────
        t0 = time.time()
        # Retrieve most relevant chunks for legal risk queries
        legal_chunks = self.rag.retrieve(analysis_id, "harmful clauses risks obligations penalties", 8)
        legal_findings = self.agents.analyze_legal_risks(legal_chunks, contract_type, agent_cb)
        all_findings.extend(legal_findings)
        self.agent_results.append(AgentResult(
            agent_name="Legal Risk Agent",
            status=AgentStatus.DONE,
            findings=legal_findings,
            summary=f"Found {len(legal_findings)} legal risks",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 3: Privacy & Data Agent ─────────────────────────────
        t0 = time.time()
        privacy_findings = self.agents.analyze_privacy_risks(full_text, contract_type, agent_cb)
        all_findings.extend(privacy_findings)
        self.agent_results.append(AgentResult(
            agent_name="Privacy Agent",
            status=AgentStatus.DONE,
            findings=privacy_findings,
            summary=f"Found {len(privacy_findings)} privacy risks",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 4: Financial Liability Agent ────────────────────────
        t0 = time.time()
        financial_findings = self.agents.analyze_financial_risks(full_text, contract_type, agent_cb)
        all_findings.extend(financial_findings)
        self.agent_results.append(AgentResult(
            agent_name="Financial Agent",
            status=AgentStatus.DONE,
            findings=financial_findings,
            summary=f"Found {len(financial_findings)} financial risks",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 5: Ambiguity Detector ───────────────────────────────
        t0 = time.time()
        ambiguity_findings = self.agents.detect_ambiguity(full_text, contract_type, agent_cb)
        all_findings.extend(ambiguity_findings)
        self.agent_results.append(AgentResult(
            agent_name="Ambiguity Detector",
            status=AgentStatus.DONE,
            findings=ambiguity_findings,
            summary=f"Found {len(ambiguity_findings)} ambiguous clauses",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── Calculate Risk Score (before future/negotiation agents) ───
        prioritized_findings = self.risk_engine.prioritize_findings(all_findings)
        risk_score = self.risk_engine.calculate(prioritized_findings)

        # ── AGENT 6: Future Consequence Simulator ─────────────────────
        t0 = time.time()
        future_scenarios = self.agents.simulate_future_consequences(
            prioritized_findings, contract_type, agent_cb
        )
        self.agent_results.append(AgentResult(
            agent_name="Future Simulator",
            status=AgentStatus.DONE,
            summary=f"Simulated {len(future_scenarios)} future scenarios",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 7: Negotiation Advisor ──────────────────────────────
        t0 = time.time()
        negotiation_recs = self.agents.generate_negotiation_advice(
            prioritized_findings, contract_type, agent_cb
        )
        self.agent_results.append(AgentResult(
            agent_name="Negotiation Advisor",
            status=AgentStatus.DONE,
            summary=f"Generated {len(negotiation_recs)} negotiation strategies",
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        # ── AGENT 8: Judge / Synthesizer ──────────────────────────────
        t0 = time.time()
        verdict = self.agents.synthesize_verdict(
            prioritized_findings, contract_type, risk_score.overall_score, agent_cb
        )
        self.agent_results.append(AgentResult(
            agent_name="Judge Agent",
            status=AgentStatus.DONE,
            summary=verdict.get("recommendation", "REVIEW WITH LAWYER"),
            processing_time_seconds=round(time.time() - t0, 2)
        ))

        total_time = round(time.time() - start_time, 1)
        print(f"\n[Orchestrator] Analysis complete in {total_time}s. "
              f"{len(all_findings)} total findings. "
              f"Risk: {risk_score.overall_score}/100 [{risk_score.level.value}]")

        return AnalysisResult(
            analysis_id=analysis_id,
            contract_type=contract_type,
            file_name=filename,
            total_clauses_found=len(chunks),
            risk_score=risk_score,
            findings=prioritized_findings,
            agent_results=self.agent_results,
            future_scenarios=future_scenarios,
            negotiation_recommendations=negotiation_recs,
            executive_summary=verdict.get("executive_summary", ""),
            one_liner_verdict=verdict.get("one_liner_verdict", ""),
            created_at=datetime.now(timezone.utc).isoformat()
        )
