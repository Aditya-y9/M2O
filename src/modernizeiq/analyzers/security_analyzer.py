"""Dimension 7: Security & Identity Architecture Analyzer."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class SecurityArchitectureAnalyzer(BaseDimensionAnalyzer):
    """Analyzes RACF/ACF2 resource classes, SAF user exits, and IAM federation readiness."""

    @property
    def dimension_name(self) -> str:
        return "Security & Identity"

    @property
    def weight(self) -> float:
        return 0.10

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        sec = portfolio.security
        risks: List[RiskFactor] = []

        score = 1.0
        findings: List[str] = [
            f"Security Manager: {sec.security_manager.value}. Resource Classes: {len(sec.resource_classes)}. User Exits: {len(sec.custom_exits)}.",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Evaluate Custom Assembler SAF Exits
        if sec.custom_exits:
            score += 1.8
            risks.append(RiskFactor(
                risk_id="RISK-SEC-01",
                title="Custom Mainframe Assembler SAF Security Exits",
                description=f"Detected {len(sec.custom_exits)} custom security exits ({', '.join(sec.custom_exits)}). These execute in supervisor state / authorized library (APF) to enforce non-standard entitlement logic.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=sec.custom_exits,
                migration_impact="Cannot run in Linux containers. Custom assembler routines must be reverse engineered into modern Policy-as-Code (Open Policy Agent / OPA) or Spring Security.",
                remediation_strategy="Decompile assembler exit rules and translate into OPA Rego policies or Keycloak custom authenticator SPIs.",
                effort_person_days=len(sec.custom_exits) * 8,
            ))
            blockers.append(f"Custom Assembler SAF security exits: {', '.join(sec.custom_exits)}")
        else:
            strengths.append("Standard security profiles without custom low-level assembler exits.")

        # 2. Evaluate Surrogate User ID Switching
        if sec.uses_surrogate:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-SEC-02",
                title="RACF SURROGAT Identity Impersonation",
                description="Application relies on RACF SURROGAT class to switch identity contexts without password re-verification.",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=["SURROGAT"],
                migration_impact="Must be replaced with OAuth2 Token Exchange (RFC 8693) or mTLS SPIFFE/SPIRE identity attestation on OpenShift.",
                remediation_strategy="Implement OAuth 2.0 Token Exchange or Kubernetes ServiceAccount impersonation.",
                effort_person_days=4,
            ))
            findings.append("Uses RACF SURROGAT user impersonation.")
        else:
            strengths.append("Direct user credential or service identity model.")

        # 3. Evaluate Resource Classes (FACILITY, TCICSTRN)
        if len(sec.resource_classes) > 4:
            score += 0.4
            findings.append(f"Complex entitlement model with {len(sec.resource_classes)} active RACF classes.")
            risks.append(RiskFactor(
                risk_id="RISK-SEC-03",
                title="Complex RACF Class Entitlements",
                description=f"Application enforces granular rules across {len(sec.resource_classes)} resource classes ({', '.join(sec.resource_classes)}).",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=sec.resource_classes,
                migration_impact="Requires RBAC/ABAC role mapping in target IAM system.",
                remediation_strategy="Map RACF profiles to OpenShift RBAC and OAuth2 scopes.",
                effort_person_days=3,
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
