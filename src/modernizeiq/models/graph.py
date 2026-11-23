"""Dependency graph, blast radius, and domain clustering metamodels."""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """A node in the application architecture knowledge graph."""
    id: str
    label: str
    type: str  # "Program", "Copybook", "Job", "Table", "Vsam", "Transaction", "Mapset"
    complexity_score: float = 1.0
    lines_of_code: int = 0
    color: str = "#3B82F6"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    complexity: float = 1.0
    loc: int = 0
    subsystem: str = "MAINFRAME"
    cluster_id: Optional[Any] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True, "extra": "allow"}


class GraphEdge(BaseModel):
    """A typed relationship in the knowledge graph."""
    source: str
    target: str
    type: str  # "CALLS", "CICS_LINK", "CICS_XCTL", "USES_COPYBOOK", "QUERIES_TABLE", "ACCESSES_VSAM", "EXECUTES", "TRANS_INVOKES"
    label: str = ""
    weight: float = 1.0
    is_dynamic: bool = False
    properties: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True, "extra": "allow"}


class DependencyGraphData(BaseModel):
    """Complete graph payload for visualization and analysis."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    total_nodes: int = 0
    total_edges: int = 0
    god_objects: List[str] = Field(default_factory=list)
    cycles_detected: Any = 0
    metrics: Dict[str, Any] = Field(default_factory=dict)
    blast_radius_summary: Dict[str, int] = Field(default_factory=dict)

    model_config = {"populate_by_name": True, "extra": "allow"}


class DomainCluster(BaseModel):
    """A bounded context / candidate microservice discovered through semantic & graph clustering."""
    cluster_id: Any = "CLUSTER-1"
    cluster_name: str
    business_domain: str = ""
    programs: List[str] = Field(default_factory=list)
    copybooks: List[str] = Field(default_factory=list)
    tables: List[str] = Field(default_factory=list)
    cohesion_score: float = 1.0
    coupling_score: float = 0.0
    recommended_service_name: str = ""
    description: str = ""
    suggested_target: str = ""
