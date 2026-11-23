"""Dimension 8: Operational NFRs & Blast Radius Analyzer."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class NfrAnalyzer(BaseDimensionAnalyzer):
    """Analyzes Non-Functional Requirements: Latency SLAs, peak TPS, 99.999% availability, and blast radius."""

    @property
    def dimension_name(self) -> str:
        return "Operational NFRs & Blast Radius"

    @property
    def weight(self) -> float:
        return 0.10

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        nfr = portfolio.nfrs
        risks: List[RiskFactor] = []

        score = 1.0
        findings: List[str] = [
            f"Latency SLA: {nfr.target_response_time_ms} ms. Availability: {nfr.availability_percentage}%. Peak TPS: {nfr.peak_transactions_per_sec:,}.",
            f"Business Criticality: {nfr.business_criticality} (RTO: {nfr.rto_minutes} min, RPO: {nfr.rpo_minutes} min).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Extreme Latency SLA (< 10ms - Mainframe memory-to-memory vs network hop in containers)
        if nfr.target_response_time_ms <= 15:
            score += 1.8
            risks.append(RiskFactor(
                risk_id="RISK-NFR-01",
                title="Ultra-Low Sub-Millisecond Latency Requirement",
                description=f"Target response time of {nfr.target_response_time_ms} ms relies on z/OS channel-to-channel and HIPERSPACE in-memory bus.",
                dimension=self.dimension_name,
                severity="Critical",
                affected_artifacts=["NFR-Latency"],
                migration_impact="In Kubernetes/OpenShift, container overlay networking (SDN/OVN), ingress proxies, and sidecar meshes typically introduce 3-10ms of latency per hop.",
                remediation_strategy="Evaluate eBPF (Cilium) kernel-bypass networking, high-performance host-networking VMs, or co-locate microservices in the same pod/node.",
                effort_person_days=8,
            ))
            blockers.append(f"Sub-15ms latency SLA ({nfr.target_response_time_ms}ms) challenging for container network overlay")
        elif nfr.target_response_time_ms <= 100:
            strengths.append(f"Standard enterprise response time SLA ({nfr.target_response_time_ms} ms) achievable on OpenShift.")
        else:
            strengths.append(f"Relaxed latency SLA ({nfr.target_response_time_ms} ms). Highly cloud-friendly.")

        # 2. Availability (Five Nines: 99.999% - Mainframe Parallel Sysplex)
        if nfr.availability_percentage >= 99.999:
            score += 1.2
            risks.append(RiskFactor(
                risk_id="RISK-NFR-02",
                title="Extreme Five-Nines (99.999%) High-Availability SLA",
                description="Five-Nines allows only 5.26 minutes of downtime per YEAR. Mainframe achieves this via Parallel Sysplex and GDPS multi-site coupling facility.",
                dimension=self.dimension_name,
                severity="High",
                affected_artifacts=["NFR-Availability"],
                migration_impact="Single-cluster Kubernetes cannot guarantee 99.999%. Requires multi-region active-active OpenShift deployments with global server load balancing (GSLB).",
                remediation_strategy="Architect active-active multi-cluster OpenShift topology with automated BGP failover and distributed multi-master DB.",
                effort_person_days=12,
            ))
            findings.append("99.999% availability requires multi-cluster active-active deployment.")
        else:
            strengths.append(f"Standard high availability target ({nfr.availability_percentage}%) natively supported by OpenShift pod replicas.")

        # 3. Peak TPS & Batch Elasticity
        if nfr.peak_transactions_per_sec > 10000:
            score += 0.8
            risks.append(RiskFactor(
                risk_id="RISK-NFR-03",
                title="Extreme High-Volume Throughput (>10,000 TPS)",
                description=f"Peak load of {nfr.peak_transactions_per_sec:,} TPS demands aggressive horizontal pod autoscaling and connection pooling.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=["NFR-Throughput"],
                migration_impact="Database connection saturation and CPU throttling under sudden spikes.",
                remediation_strategy="Implement KEDA event-driven autoscaling, read-replicas, and distributed caching (Redis cluster).",
                effort_person_days=6,
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
