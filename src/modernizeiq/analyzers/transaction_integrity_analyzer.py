"""Dimension 6: Transaction Integrity & State Analyzer (2PC, SYNCPOINT, Rollback)."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class TransactionIntegrityAnalyzer(BaseDimensionAnalyzer):
    """Analyzes CICS SYNCPOINT, Two-Phase Commit (2PC), distributed locks, and state boundaries."""

    @property
    def dimension_name(self) -> str:
        return "Transaction Integrity & State"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        programs = list(portfolio.programs.values())
        risks: List[RiskFactor] = []

        total_syncpoints = sum(p.cics_syncpoints_count for p in programs)
        syncpoint_progs = [p for p in programs if p.cics_syncpoints_count > 0]

        # Check for heterogeneous resource updates (DB2 + VSAM + MQ)
        heterogeneous_progs = [
            p for p in programs
            if (len(p.sql_tables_accessed) > 0 and len(p.vsam_files_accessed) > 0)
        ]

        score = 1.0
        findings: List[str] = [
            f"Detected {total_syncpoints} explicit CICS SYNCPOINT statement(s) across {len(syncpoint_progs)} program(s).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Evaluate Heterogeneous Resource Coordination (Two-Phase Commit / 2PC)
        if heterogeneous_progs:
            score += 2.0
            risks.append(RiskFactor(
                risk_id="RISK-TX-01",
                title="Heterogeneous Multi-Resource Two-Phase Commit (2PC)",
                description=f"Programs {[p.program_id for p in heterogeneous_progs]} execute atomic coordinated writes across both DB2 relational tables and VSAM files under mainframe syncpoint.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=[p.program_id for p in heterogeneous_progs],
                migration_impact="Fatal blocker for native microservices. Distributed ACID 2PC across independent container microservices introduces latency, deadlocks, and CAP theorem partition failures.",
                remediation_strategy="Refactor into an eventual consistency Saga pattern (Orchestrated Saga with Kafka/Temporal) or consolidate storage into a single ACID database before migration.",
                effort_person_days=len(heterogeneous_progs) * 6,
            ))
            blockers.append(f"Atomic 2PC across DB2 and VSAM in {', '.join(p.program_id for p in heterogeneous_progs)}")
        elif syncpoint_progs:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-TX-02",
                title="Explicit CICS SYNCPOINT Demarcation",
                description=f"{len(syncpoint_progs)} program(s) manage transaction boundaries explicitly via EXEC CICS SYNCPOINT.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[p.program_id for p in syncpoint_progs],
                migration_impact="Transaction boundaries must be mapped to Spring @Transactional or database transaction contexts.",
                remediation_strategy="Wrap business logic in declarative transaction boundaries or outbox pattern.",
                effort_person_days=len(syncpoint_progs) * 2,
            ))
            findings.append(f"{len(syncpoint_progs)} programs have explicit manual syncpoint commits.")
        else:
            strengths.append("Standard single-resource unit-of-work (implicit commit on program termination).")

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
