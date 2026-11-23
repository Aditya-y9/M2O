"""ModernizeIQ Domain Metamodel (OMG KDM/ASTM aligned)."""

from .artifacts import (
    CobolProgram,
    Copybook,
    JclJob,
    JclStep,
    CicsTransaction,
    BmsMapset,
    DatabaseTable,
    VsamDataset,
    SecurityProfile,
    NonFunctionalRequirements,
    ApplicationPortfolio,
)
from .assessment import (
    DimensionScore,
    AssessmentReport,
    PlatformCandidate,
    RDisposition,
    TargetPlatform,
    RiskFactor,
    RemediationAction,
    FactorCompliance,
)
from .graph import (
    GraphNode,
    GraphEdge,
    DependencyGraphData,
    DomainCluster,
)

__all__ = [
    "CobolProgram",
    "Copybook",
    "JclJob",
    "JclStep",
    "CicsTransaction",
    "BmsMapset",
    "DatabaseTable",
    "VsamDataset",
    "SecurityProfile",
    "NonFunctionalRequirements",
    "ApplicationPortfolio",
    "DimensionScore",
    "AssessmentReport",
    "PlatformCandidate",
    "RDisposition",
    "TargetPlatform",
    "RiskFactor",
    "RemediationAction",
    "FactorCompliance",
    "GraphNode",
    "GraphEdge",
    "DependencyGraphData",
    "DomainCluster",
]
