"""Dimension 4: Online Transactions & UI Analyzer (CICS & BMS 3270)."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class OnlineUiAnalyzer(BaseDimensionAnalyzer):
    """Analyzes CICS transaction processing, stateful conversational transactions, and BMS 3270 UI coupling."""

    @property
    def dimension_name(self) -> str:
        return "Online Transactions & UI"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        programs = list(portfolio.programs.values())
        transactions = portfolio.transactions
        mapsets = portfolio.mapsets
        risks: List[RiskFactor] = []

        total_tx = len(transactions)
        total_maps = len(mapsets)
        cics_progs = [p for p in programs if p.is_cics_program]

        if not cics_progs and not total_tx and not total_maps:
            return DimensionScore(
                dimension_name=self.dimension_name,
                raw_score=1.0,
                normalized_score=100.0,
                readiness_rating="High",
                key_findings=["Batch-only or headless portfolio; no online CICS/BMS artifacts detected."],
                strengths=["Zero 3270 UI legacy debt or CICS terminal session binding."],
                blockers=[],
            ), risks

        score = 1.2
        findings: List[str] = [
            f"Detected {len(cics_progs)} CICS program(s), {total_tx} transaction(s), and {total_maps} BMS 3270 mapset(s).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Evaluate Conversational vs Pseudo-conversational state
        # A conversational program holds the CICS task open during user think time.
        conversational_progs = [p for p in cics_progs if p.is_conversational]
        if conversational_progs:
            score += 2.0
            risks.append(RiskFactor(
                risk_id="RISK-CICS-01",
                title="Stateful Conversational CICS Transactions",
                description=f"Programs {[p.program_id for p in conversational_progs]} hold internal state and active task locks across terminal interactions.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=[p.program_id for p in conversational_progs],
                migration_impact="Fatal blocker for stateless horizontal pod autoscaling on OpenShift (Factor VI: Processes). Session memory is tied to single runtime instances.",
                remediation_strategy="Refactor into pseudo-conversational architecture using external session stores (Redis) or expose RESTful stateless APIs with JWT tokens.",
                effort_person_days=len(conversational_progs) * 5,
            ))
            blockers.append(f"Conversational CICS programs holding state: {', '.join(p.program_id for p in conversational_progs)}")
        else:
            strengths.append("Zero conversational CICS transactions detected; pseudo-conversational pattern utilized.")

        # 2. Evaluate BMS 3270 Green-Screen Dependency
        if total_maps > 0:
            score += 1.0
            risks.append(RiskFactor(
                risk_id="RISK-CICS-02",
                title="BMS 3270 Green-Screen User Interface Coupling",
                description=f"Portfolio includes {total_maps} BMS mapsets containing 3270 datastreams, cursor positions, and Modified Data Tags (MDT).",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=list(mapsets.keys()),
                migration_impact="Requires terminal emulation middleware or complete front-end UI re-architecture (React/Angular/Vue).",
                remediation_strategy="Generate OpenAPI REST specifications from BMS field layouts and build modern responsive web components.",
                effort_person_days=total_maps * 3,
            ))
            findings.append(f"{total_maps} BMS 3270 screen mapset(s) require UI modernization.")
        else:
            strengths.append("No BMS 3270 terminal screens; portfolio operates as service/API layer.")

        # 3. Evaluate COMMAREA constraints (Legacy 32KB limit vs modern payloads)
        commarea_progs = [p for p in cics_progs if p.commarea_size_bytes > 0]
        large_commarea = [p for p in commarea_progs if p.commarea_size_bytes > 30000]
        if large_commarea:
            score += 0.5
            risks.append(RiskFactor(
                risk_id="RISK-CICS-03",
                title="Legacy 32KB COMMAREA Saturation",
                description=f"Programs {[p.program_id for p in large_commarea]} approach the 32,767-byte CICS COMMAREA boundary.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[p.program_id for p in large_commarea],
                migration_impact="Fragile memory buffers; prone to truncation or buffer overrun during marshaling.",
                remediation_strategy="Migrate to CICS Channels and Containers or modern structured JSON payloads.",
                effort_person_days=len(large_commarea) * 2,
            ))

        clamped_score = min(5.0, max(1.0, score))
        norm_score = max(0.0, min(100.0, (5.0 - clamped_score) / 4.0 * 100.0))
        rating = "High" if norm_score >= 70 else ("Medium" if norm_score >= 40 else "Low")

        return DimensionScore(
            dimension_name=self.dimension_name,
            raw_score=round(clamped_score, 2),
            normalized_score=round(norm_score, 1),
            readiness_rating=rating,
            key_findings=findings,
            strengths=strengths,
            blockers=blockers,
        ), risks
