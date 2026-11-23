"""Modernization assessment scoring models, 7R disposition, and platform recommendations."""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class TargetPlatform(str, Enum):
    OPENSHIFT = "Red Hat OpenShift Container Platform (OCP)"
    VIRTUAL_MACHINE = "Enterprise Linux Virtual Machine (VM)"
    LINUX_VM = "Enterprise Linux Virtual Machine (VM)"
    MAINFRAME_RETAIN = "Retain on Mainframe (z/OS)"
    HYBRID_COEXIST = "Hybrid Coexistence (Distributed API + Mainframe Core)"
    HYBRID_MAINFRAME = "Hybrid Coexistence (Distributed API + Mainframe Core)"


class RDisposition(str, Enum):
    REFACTOR = "Refactor (Cloud-Native Containerization on OCP)"
    REPLATFORM = "Replatform (Containerized COBOL / Lift & Reshape on OCP)"
    REHOST = "Rehost (Lift & Shift to Linux VM via Micro Focus / CloudFrame)"
    RETAIN = "Retain (Keep on Mainframe - Low ROI / High Blast Radius)"
    RETIRE = "Retire (Decommission - Zero Activity / Redundant)"
    REPURCHASE = "Repurchase (Replace with SaaS/COTS)"


class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class DimensionScore(BaseModel):
    """Evaluation of one of the 8 core modernization dimensions."""
    dimension_key: str = ""
    dimension_name: str
    score: float = 1.0
    raw_score: float = 1.0
    weight: float = 0.125
    readiness_percentage: float = 100.0
    normalized_score: float = 100.0
    readiness_rating: str = "High"
    findings: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    boosters: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)


class FactorCompliance(BaseModel):
    """Compliance with 12-Factor cloud-native application principles."""
    factor_number: int = 1
    factor_id: str = "I"
    factor_name: str = ""
    name: str = ""
    compliance_score: float = 1.0
    score: float = 85.0
    status: str = "Compliant"  # "Compliant", "Partially Compliant", "Non-Compliant"
    legacy_gap: str = ""
    gap_analysis: str = ""
    remediation: str = ""


class RiskFactor(BaseModel):
    """Specific technical or operational risk identified during assessment."""
    risk_id: str
    category: str = ""
    dimension: str = ""
    severity: Any = RiskLevel.MODERATE
    title: str
    description: str
    impact: str = ""
    migration_impact: str = ""
    mitigation_strategy: str = ""
    remediation_strategy: str = ""
    affected_artifacts: List[str] = Field(default_factory=list)
    effort_person_days: int = 1


class RemediationAction(BaseModel):
    """Concrete remediation playbook action."""
    action_id: str
    title: str = ""
    target_component: str = ""
    effort_story_points: int = 1
    effort_person_days: int = 1
    estimated_days: int = 1
    priority: Any = "P1 - High"
    phase: int = 1
    description: str = ""
    target_pattern: str = ""
    target_platform: Any = TargetPlatform.OPENSHIFT
    recommended_tools: List[str] = Field(default_factory=list)


class PlatformCandidate(BaseModel):
    """Fit and score for a specific deployment platform."""
    platform: TargetPlatform
    suitability_score: float = Field(..., ge=0.0, le=100.0)
    is_recommended: bool = False
    fit_summary: str = ""
    migration_path: str = ""
    estimated_cost_index: str = ""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    key_requirements: List[str] = Field(default_factory=list)


class ModernizationWave(BaseModel):
    """Wave migration plan component."""
    wave_number: int
    wave_name: str
    programs_included: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    estimated_duration_weeks: int = 4
    prerequisites: List[str] = Field(default_factory=list)
    rationale: str


class AssessmentReport(BaseModel):
    """Complete comprehensive modernization assessment report for an application."""
    app_id: str
    app_name: str
    assessment_timestamp: str
    overall_readiness_score: float = Field(..., ge=0.0, le=100.0)
    containerizability_index: float = Field(..., ge=0.0, le=100.0)
    overall_complexity_score: float = Field(..., ge=1.0, le=5.0)

    # Primary Recommendations
    recommended_disposition: RDisposition
    recommended_platform: TargetPlatform
    executive_summary: str
    architectural_rationale: str

    # Platform Evaluation
    platform_evaluations: Dict[str, PlatformCandidate] = Field(default_factory=dict)

    # 8 Dimensional Scores
    dimension_scores: Dict[str, DimensionScore] = Field(default_factory=dict)

    # 12-Factor App Analysis
    twelve_factor_scores: List[FactorCompliance] = Field(default_factory=list)

    # Risks & Remediation
    top_risks: List[RiskFactor] = Field(default_factory=list)
    remediation_roadmap: List[RemediationAction] = Field(default_factory=list)
    migration_waves: List[ModernizationWave] = Field(default_factory=list)

    # Statistics & Inventory Summary
    inventory_summary: Dict[str, Any] = Field(default_factory=dict)
