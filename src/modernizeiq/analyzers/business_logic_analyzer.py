"""Dimension 1: Business Logic & Code Complexity Analyzer."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class BusinessLogicAnalyzer(BaseDimensionAnalyzer):
    """Analyzes business logic modularity, McCabe cyclomatic complexity, and legacy anti-patterns."""

    @property
    def dimension_name(self) -> str:
        return "Business Logic & Code Complexity"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        programs = list(portfolio.programs.values())
        risks: List[RiskFactor] = []

        if not programs:
            return DimensionScore(
                dimension_name=self.dimension_name,
                raw_score=2.0,
                normalized_score=40.0,
                readiness_rating="Medium",
                key_findings=["No COBOL programs detected in the portfolio."],
                strengths=["Minimal application code footprint."],
                blockers=[],
            ), risks

        total_cc = sum(p.cyclomatic_complexity for p in programs)
        avg_cc = total_cc / len(programs)
        max_cc_prog = max(programs, key=lambda p: p.cyclomatic_complexity)
        total_loc = sum(p.lines_of_code for p in programs)

        # Anti-pattern counts
        alter_progs = [p for p in programs if p.alter_statements_count > 0]
        unref_paragraphs = sum(len(p.unreferenced_paragraphs) for p in programs)
        dynamic_calls = sum(len(p.dynamic_calls) for p in programs)

        # Base scoring: 1.0 (best/lowest complexity) to 5.0 (worst/highest complexity)
        # 1.0 - 2.0: Clean, structured modular COBOL (High Readiness)
        # 2.0 - 3.5: Moderate complexity, some legacy branching
        # 3.5 - 5.0: Spaghetti code, ALTER verbs, monolithic procedures (Blocker)
        score = 1.5

        findings: List[str] = [
            f"Analyzed {len(programs)} COBOL program(s) totaling {total_loc:,} lines of code.",
            f"Average Cyclomatic Complexity: {avg_cc:.1f} (Peak: {max_cc_prog.cyclomatic_complexity} in {max_cc_prog.program_id}).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # Evaluate Cyclomatic Complexity
        if avg_cc > 50:
            score += 1.5
            risks.append(RiskFactor(
                risk_id="RISK-BL-01",
                title="Extreme Cyclomatic Complexity Monolith",
                description=f"Average Cyclomatic Complexity ({avg_cc:.1f}) exceeds enterprise threshold (50). Program {max_cc_prog.program_id} has {max_cc_prog.cyclomatic_complexity} branching paths.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=[max_cc_prog.program_id],
                migration_impact="High risk of logic regression during automated microservice extraction or Java/Go refactoring.",
                remediation_strategy="Execute paragraph isolation and extract business rule logic into pure deterministic domains before containerizing.",
                effort_person_days=len(programs) * 5,
            ))
            blockers.append(f"Monolithic program {max_cc_prog.program_id} with McCabe Complexity {max_cc_prog.cyclomatic_complexity}")
        elif avg_cc > 25:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-BL-02",
                title="High Branching Complexity",
                description=f"Average Cyclomatic Complexity ({avg_cc:.1f}) indicates dense procedural logic.",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=[p.program_id for p in programs if p.cyclomatic_complexity > 30],
                migration_impact="Increases test generation burden and regression surface during containerization.",
                remediation_strategy="Refactor nested IF/EVALUATE into modular dispatch tables or micro-components.",
                effort_person_days=len(programs) * 2,
            ))
        else:
            strengths.append(f"Well-structured procedural branching (Avg Cyclomatic Complexity: {avg_cc:.1f}).")

        # Evaluate ALTER statements (Dynamic self-modifying code)
        if alter_progs:
            score += 1.0
            risks.append(RiskFactor(
                risk_id="RISK-BL-03",
                title="Self-Modifying Code (ALTER Statement)",
                description=f"Detected {sum(p.alter_statements_count for p in alter_progs)} ALTER statements across {len(alter_progs)} program(s). ALTER dynamically mutates GO TO targets at runtime.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=[p.program_id for p in alter_progs],
                migration_impact="Cannot run reliably in stateless container runtimes or modern multi-threaded architectures.",
                remediation_strategy="Mandatory elimination: replace ALTER with standard PERFORM or EVALUATE state machines.",
                effort_person_days=len(alter_progs) * 4,
            ))
            blockers.append(f"Self-modifying ALTER statements found in {', '.join(p.program_id for p in alter_progs)}")
        else:
            strengths.append("Zero self-modifying code (no ALTER statements detected).")

        # Evaluate Unreferenced Paragraphs (Dead Code)
        if unref_paragraphs > 0:
            findings.append(f"Detected {unref_paragraphs} unreferenced paragraphs (dead code candidates).")

        # Evaluate Dynamic Calls
        if dynamic_calls > 0:
            score += 0.4
            findings.append(f"Found {dynamic_calls} dynamic CALL statements using identifier variables.")
            risks.append(RiskFactor(
                risk_id="RISK-BL-04",
                title="Dynamic Identifier CALLs",
                description=f"Portfolio utilizes {dynamic_calls} dynamic CALL statements, obscuring compile-time dependency graphs.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[p.program_id for p in programs if p.dynamic_calls],
                migration_impact="Dynamic module resolution requires runtime classpath/library configuration in containers.",
                remediation_strategy="Map dynamic call targets via static registry or Dependency Injection configuration.",
                effort_person_days=max(2, dynamic_calls * 1),
            ))

        clamped_score = min(5.0, max(1.0, score))
        # Normalized score: 100 is best (score 1.0), 0 is worst (score 5.0)
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
