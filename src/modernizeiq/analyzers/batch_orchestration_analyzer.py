"""Dimension 5: Batch Processing & JCL Orchestration Analyzer."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class BatchOrchestrationAnalyzer(BaseDimensionAnalyzer):
    """Analyzes JCL jobs, COND code branching, Generation Data Groups (GDG), and batch window elasticity."""

    @property
    def dimension_name(self) -> str:
        return "Batch Processing & Orchestration"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        jobs = list(portfolio.jobs.values())
        risks: List[RiskFactor] = []

        total_jobs = len(jobs)
        total_steps = sum(len(j.steps) for j in jobs)

        if not jobs:
            return DimensionScore(
                dimension_name=self.dimension_name,
                raw_score=1.0,
                normalized_score=100.0,
                readiness_rating="High",
                key_findings=["No JCL batch jobs detected; pure online/service architecture."],
                strengths=["Zero legacy batch orchestration coupling."],
                blockers=[],
            ), risks

        score = 1.2
        findings: List[str] = [
            f"Detected {total_jobs} JCL Job(s) containing {total_steps} execution step(s).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Evaluate Generation Data Groups (GDG)
        gdg_jobs = [j for j in jobs if j.gdg_datasets_count > 0]
        total_gdgs = sum(j.gdg_datasets_count for j in jobs)
        if total_gdgs > 0:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-BATCH-01",
                title="Generation Data Group (GDG) Versioning Dependencies",
                description=f"Detected {total_gdgs} GDG dataset references across {len(gdg_jobs)} jobs. GDG relative generation references (e.g. (+1), (0)) are specific to z/OS catalog management.",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=[j.job_name for j in gdg_jobs],
                migration_impact="Cloud storage (S3/Ceph) lacks native automated generational rolling rollbacks.",
                remediation_strategy="Replace GDG rolling with timestamped object prefixes or MinIO/S3 versioned bucket policies.",
                effort_person_days=total_gdgs * 1.5,
            ))
            findings.append(f"{total_gdgs} Generation Data Group (GDG) relative references in use.")
        else:
            strengths.append("No Generation Data Groups (GDGs); datasets follow deterministic naming.")

        # 2. Evaluate Complex COND Code Branching
        complex_cond_jobs = [j for j in jobs if any(s.has_cond_logic for s in j.steps)]
        if complex_cond_jobs:
            score += 0.9
            risks.append(RiskFactor(
                risk_id="RISK-BATCH-02",
                title="Complex JCL COND Step Branching",
                description=f"{len(complex_cond_jobs)} job(s) utilize conditional return-code branching (e.g., COND=(4,LT)).",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[j.job_name for j in complex_cond_jobs],
                migration_impact="Requires translation into Directed Acyclic Graphs (DAGs) in Kubernetes/Argo/Airflow.",
                remediation_strategy="Refactor step conditionals into Airflow BranchPythonOperator or Argo Workflows 'when' expressions.",
                effort_person_days=len(complex_cond_jobs) * 2,
            ))
            findings.append(f"{len(complex_cond_jobs)} jobs contain conditional step execution logic.")
        else:
            strengths.append("Linear step execution in JCL jobs; simple DAG translation.")

        # 3. Check for z/OS native utilities (DFSORT, ICETOOL)
        sort_steps = sum(1 for j in jobs for s in j.steps if s.program_name in ("SORT", "DFSORT", "ICETOOL"))
        if sort_steps > 0:
            score += 0.6
            risks.append(RiskFactor(
                risk_id="RISK-BATCH-03",
                title="Mainframe Sort Utility Lock-in (DFSORT/ICETOOL)",
                description=f"Identified {sort_steps} step(s) executing DFSORT/ICETOOL control cards.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[j.job_name for j in jobs if any(s.program_name in ("SORT", "DFSORT", "ICETOOL") for s in j.steps)],
                migration_impact="Custom sort card syntax (INCLUDE, OMIT, INREC, OUTREC) requires modern SQL or Spark/Python data pipeline equivalent.",
                remediation_strategy="Translate sort control cards into PySpark / DuckDB SQL data transformations.",
                effort_person_days=sort_steps * 1.0,
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
