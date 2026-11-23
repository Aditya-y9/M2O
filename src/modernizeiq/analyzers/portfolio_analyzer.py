"""Master Portfolio Modernization Assessment Orchestrator."""

from __future__ import annotations
from typing import List, Dict
import statistics

from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import (
    DimensionScore,
    RiskFactor,
    RemediationAction,
    FactorCompliance,
    RDisposition,
    TargetPlatform,
)
from .business_logic_analyzer import BusinessLogicAnalyzer
from .coupling_analyzer import CouplingAnalyzer
from .data_architecture_analyzer import DataArchitectureAnalyzer
from .online_ui_analyzer import OnlineUiAnalyzer
from .batch_orchestration_analyzer import BatchOrchestrationAnalyzer
from .transaction_integrity_analyzer import TransactionIntegrityAnalyzer
from .security_analyzer import SecurityArchitectureAnalyzer
from .nfr_analyzer import NfrAnalyzer
from .twelve_factor_analyzer import TwelveFactorAnalyzer


class PortfolioAnalyzer:
    """Runs all 8 dimension analyzers, evaluates 12-factor compliance, and aggregates scores."""

    def __init__(self):
        self.analyzers = [
            BusinessLogicAnalyzer(),
            CouplingAnalyzer(),
            DataArchitectureAnalyzer(),
            OnlineUiAnalyzer(),
            BatchOrchestrationAnalyzer(),
            TransactionIntegrityAnalyzer(),
            SecurityArchitectureAnalyzer(),
            NfrAnalyzer(),
        ]
        self.twelve_factor_analyzer = TwelveFactorAnalyzer()

    def run_assessment(self, portfolio: ApplicationPortfolio) -> Dict[str, any]:
        dimension_scores: List[DimensionScore] = []
        all_risks: List[RiskFactor] = []

        total_weight = sum(a.weight for a in self.analyzers)
        weighted_normalized_sum = 0.0
        weighted_raw_sum = 0.0

        for analyzer in self.analyzers:
            score, risks = analyzer.analyze(portfolio)
            dimension_scores.append(score)
            all_risks.extend(risks)
            weighted_normalized_sum += score.normalized_score * analyzer.weight
            weighted_raw_sum += score.raw_score * analyzer.weight

        overall_normalized = round(weighted_normalized_sum / total_weight, 1)
        overall_raw = round(weighted_raw_sum / total_weight, 2)

        # 12-Factor Compliance
        factor_compliance = self.twelve_factor_analyzer.analyze(portfolio)
        avg_factor_score = round(statistics.mean(f.score for f in factor_compliance), 1)

        # Sort risks by severity: Critical -> High -> Medium -> Low
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        all_risks.sort(key=lambda r: (severity_order.get(r.severity, 4), -r.effort_person_days))

        # Overall Containerization Readiness
        # Score >= 75: High
        # Score 50 - 74: Medium
        # Score < 50: Low / Blocker
        if overall_normalized >= 75.0:
            readiness_rating = "High Readiness (Container-Ready for OpenShift)"
            initial_disposition = RDisposition.REFACTOR
            target_platform = TargetPlatform.OPENSHIFT
        elif overall_normalized >= 50.0:
            readiness_rating = "Medium Readiness (Conditional / Replatform to VM or OpenShift after refactoring)"
            initial_disposition = RDisposition.REPLATFORM
            target_platform = TargetPlatform.VIRTUAL_MACHINE
        else:
            readiness_rating = "Low Readiness (Heavy Blocker / Retain Core with API Gateway or Lift-to-VM)"
            initial_disposition = RDisposition.REHOST
            target_platform = TargetPlatform.VIRTUAL_MACHINE

        # Generate Actionable Remediation Roadmap
        remediations: List[RemediationAction] = []
        for i, risk in enumerate(all_risks[:8], 1):
            phase = 1 if risk.severity == "Critical" else (2 if risk.severity == "High" else 3)
            remediations.append(RemediationAction(
                action_id=f"REM-{i:02d}",
                title=f"Resolve {risk.title}",
                description=risk.remediation_strategy,
                priority=risk.severity,
                phase=phase,
                estimated_days=risk.effort_person_days,
                target_platform=TargetPlatform.OPENSHIFT if phase > 1 else TargetPlatform.VIRTUAL_MACHINE,
            ))

        total_person_days = sum(r.effort_person_days for r in all_risks)

        return {
            "dimension_scores": dimension_scores,
            "overall_normalized_score": overall_normalized,
            "overall_raw_score": overall_raw,
            "overall_readiness_rating": readiness_rating,
            "twelve_factor_compliance": factor_compliance,
            "average_factor_score": avg_factor_score,
            "risks": all_risks,
            "remediations": remediations,
            "total_estimated_person_days": total_person_days,
            "initial_disposition": initial_disposition,
            "target_platform": target_platform,
        }
