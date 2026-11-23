"""Dimension 2: Coupling & Shared Components Analyzer."""

from __future__ import annotations
from typing import List, Tuple, Dict, Set
from collections import defaultdict
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class CouplingAnalyzer(BaseDimensionAnalyzer):
    """Analyzes program-to-program coupling, copybook explosion, fan-in/fan-out, and circular references."""

    @property
    def dimension_name(self) -> str:
        return "Coupling & Shared Components"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        programs = portfolio.programs
        copybooks = portfolio.copybooks
        risks: List[RiskFactor] = []

        if not programs:
            return DimensionScore(
                dimension_name=self.dimension_name,
                raw_score=1.5,
                normalized_score=87.5,
                readiness_rating="High",
                key_findings=["No programs to analyze for coupling."],
                strengths=["Zero coupling overhead."],
                blockers=[],
            ), risks

        # Calculate Fan-Out (calls made) and Fan-In (calls received)
        fan_out: Dict[str, int] = {}
        fan_in: Dict[str, int] = defaultdict(int)
        call_graph: Dict[str, Set[str]] = defaultdict(set)

        for p_id, p in programs.items():
            targets = set(p.static_calls) | set(p.cics_links) | set(p.cics_xctls)
            call_graph[p_id] = targets
            fan_out[p_id] = len(targets)
            for tgt in targets:
                fan_in[tgt] += 1

        # Calculate Copybook Sharing
        shared_copybooks: Dict[str, List[str]] = defaultdict(list)
        for cb_name, cb in copybooks.items():
            shared_copybooks[cb_name] = cb.referenced_by_programs

        max_shared_cb = max(shared_copybooks.items(), key=lambda x: len(x[1])) if shared_copybooks else ("None", [])
        avg_fan_out = sum(fan_out.values()) / max(1, len(programs))
        max_fan_in = max(fan_in.items(), key=lambda x: x[1]) if fan_in else ("None", 0)

        # Detect Circular Dependencies in call_graph
        cycles = self._detect_cycles(call_graph)

        score = 1.2
        findings: List[str] = [
            f"Analyzed {len(programs)} program(s) across {len(copybooks)} copybook(s).",
            f"Average Fan-Out: {avg_fan_out:.1f}. Highest Fan-In program: '{max_fan_in[0]}' (referenced by {max_fan_in[1]} programs).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # Evaluate Shared Copybooks (Tight data structure coupling)
        if len(max_shared_cb[1]) > 5:
            score += 1.0
            risks.append(RiskFactor(
                risk_id="RISK-CP-01",
                title="Widespread Data Structure Coupling (Copybook Explosion)",
                description=f"Copybook '{max_shared_cb[0]}' is shared across {len(max_shared_cb[1])} programs. Any data layout modification forces mass recompilation.",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=[max_shared_cb[0]] + max_shared_cb[1][:5],
                migration_impact="Prevents independent microservice deployment on OpenShift; tight shared data model.",
                remediation_strategy="Decouple into explicit JSON/Protobuf domain DTOs with independent versioning schemas.",
                effort_person_days=len(max_shared_cb[1]) * 1.5,
            ))
            findings.append(f"Highly coupled copybook '{max_shared_cb[0]}' used by {len(max_shared_cb[1])} modules.")
        elif len(max_shared_cb[1]) <= 2:
            strengths.append("Low copybook cross-program coupling; data structures are localized.")

        # Evaluate High Fan-Out (God Objects / Monolithic orchestrators)
        high_fan_out = [p_id for p_id, count in fan_out.items() if count > 8]
        if high_fan_out:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-CP-02",
                title="High Fan-Out Orchestrator Monolith",
                description=f"Programs {high_fan_out} invoke more than 8 external programs, exhibiting high procedural fan-out.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=high_fan_out,
                migration_impact="Complex integration boundaries when splitting into containers.",
                remediation_strategy="Introduce an API Gateway, event bus (Kafka), or workflow orchestrator (Temporal/Camel-K).",
                effort_person_days=len(high_fan_out) * 3,
            ))

        # Evaluate Circular Dependencies
        if cycles:
            score += 1.5
            cycle_desc = " -> ".join(cycles[0])
            risks.append(RiskFactor(
                risk_id="RISK-CP-03",
                title="Circular Call Graph Dependency",
                description=f"Detected cyclic invocation path: {cycle_desc}.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=cycles[0],
                migration_impact="Circular runtime calls cause stack overflows and dependency lockouts in microservices.",
                remediation_strategy="Break cycle via asynchronous messaging or Inversion of Control (dependency inversion).",
                effort_person_days=6,
            ))
            blockers.append(f"Circular dependency cycle: {cycle_desc}")
        else:
            strengths.append("Acyclic program call graph (no circular recursion detected).")

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

    def _detect_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        visited = set()
        stack = []
        cycles = []

        def dfs(node: str):
            if node in stack:
                cycle_start = stack.index(node)
                cycles.append(stack[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            stack.append(node)
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            stack.pop()

        for n in list(graph.keys()):
            if n not in visited:
                dfs(n)

        return cycles
