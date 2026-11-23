"""Target Platform Decision Engine: OpenShift (OCP) vs Linux Virtual Machine (VM).

Evaluates application characteristics against container-native and virtual-machine
hosting models, generating multi-dimensional suitability scores, trade-off matrices,
and detailed Architecture Decision Records (ADR).
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple

from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import (
    PlatformCandidate,
    TargetPlatform,
    RDisposition,
    DimensionScore,
    RiskFactor,
)


class TargetPlatformDecisionEngine:
    """Computes comparative suitability between Red Hat OpenShift (OCP) and Linux VMs."""

    def evaluate(
        self,
        portfolio: ApplicationPortfolio,
        dimension_scores: List[DimensionScore],
        risks: List[RiskFactor],
        overall_score: float,
    ) -> Dict[str, Any]:
        """
        Calculates platform fit, detailed logical justification, trade-off matrix, and ADR.
        """
        programs = list(portfolio.programs.values())
        cics_progs = [p for p in programs if p.is_cics_program]
        conversational_count = sum(1 for p in cics_progs if p.is_conversational)
        vsam_count = len(portfolio.vsam_files)
        table_count = len(portfolio.tables)
        jcl_count = len(portfolio.jobs)
        total_syncpoints = sum(p.cics_syncpoints_count for p in programs)
        alter_count = sum(p.alter_statements_count for p in programs)
        custom_exits = len(portfolio.security.custom_exits)
        latency_sla = portfolio.nfrs.target_response_time_ms
        availability = portfolio.nfrs.availability_percentage

        # -------------------------------------------------------------
        # 1. Calculate OpenShift (OCP) Suitability Score (0 - 100)
        # -------------------------------------------------------------
        ocp_score = 90.0
        ocp_pros: List[str] = [
            "Horizontal Pod Autoscaling (HPA) enables dynamic resource elasticity during transaction surges.",
            "Declarative GitOps deployments via ArgoCD with automated rollback and zero-downtime rolling updates.",
            "Complete elimination of recurring IBM mainframe MIPS licensing costs.",
            "Rich cloud-native observability ecosystem (OpenTelemetry, Prometheus, Grafana, Jaeger).",
            "Universal Linux base image (UBI) standardizes runtime across dev, staging, and production.",
        ]
        ocp_cons: List[str] = []
        ocp_blockers: List[str] = []

        # Deductions for OCP based on container anti-patterns:
        if conversational_count > 0:
            deduction = min(35.0, conversational_count * 10.0)
            ocp_score -= deduction
            msg = f"{conversational_count} conversational CICS program(s) bind terminal state to memory, violating pod statelessness."
            ocp_cons.append(msg)
            ocp_blockers.append(msg)

        if vsam_count > 0:
            deduction = min(25.0, vsam_count * 4.0)
            ocp_score -= deduction
            msg = f"{vsam_count} shared VSAM dataset(s) lack POSIX distributed record-level lock semantics across container replicas."
            ocp_cons.append(msg)
            if vsam_count > 3:
                ocp_blockers.append(msg)

        if total_syncpoints > 0 and vsam_count > 0 and table_count > 0:
            ocp_score -= 20.0
            msg = "Heterogeneous Two-Phase Commit (2PC) across DB2 and VSAM cannot be natively coordinated across container pods without Saga redesign."
            ocp_cons.append(msg)
            ocp_blockers.append(msg)

        if alter_count > 0:
            ocp_score -= 15.0
            ocp_cons.append(f"{alter_count} self-modifying ALTER statement(s) prevent thread-safe container execution.")

        if custom_exits > 0:
            ocp_score -= 20.0
            msg = f"{custom_exits} custom Assembler SAF security exit(s) cannot run in Linux container runtimes."
            ocp_cons.append(msg)
            ocp_blockers.append(msg)

        if latency_sla <= 10:
            ocp_score -= 15.0
            ocp_cons.append(f"Sub-10ms response time ({latency_sla}ms) is vulnerable to container overlay networking (SDN/OVN) packet jitter.")

        ocp_score = max(10.0, min(100.0, ocp_score))

        # -------------------------------------------------------------
        # 2. Calculate Linux Virtual Machine (VM) Suitability Score (0 - 100)
        # -------------------------------------------------------------
        # VMs (e.g. Micro Focus Enterprise Server, AWS Blu Age / Raincode, vSphere) excel at
        # preserving monolithic state, shared memory, and z/OS utilities with minimal code change.
        vm_score = 65.0
        vm_pros: List[str] = [
            "Full compatibility with stateful CICS conversational programs and shared memory (CWA/TWA).",
            "Mainframe emulation runtimes (e.g., Micro Focus Enterprise Server) support native VSAM KSDS/ESDS files.",
            "Lowest code modification risk: allows verbatim compilation of existing COBOL business logic.",
            "Fastest time-to-market: eliminates the multi-year redesign required for microservices.",
            "Retains existing JCL execution sequences and step COND return codes.",
        ]
        vm_cons: List[str] = [
            "Retains monolithic architectural debt without microservice modularity or independent deployment cycles.",
            "Requires ongoing commercial mainframe emulation runtime licenses (e.g. Micro Focus/Raincode).",
            "Scaling requires coarse-grained vertical VM resizing or active-passive clustering rather than sub-second pod autoscaling.",
            "Heavier resource footprint and longer boot times compared to lightweight container pods.",
        ]

        if conversational_count > 0 or vsam_count > 0:
            vm_score += 15.0  # VM is much better suited if application has heavy legacy state
        if custom_exits > 0:
            vm_score += 10.0  # Emulators often have pluggable C/C++ SAF modules
        if overall_score < 50.0:
            vm_score += 10.0  # Low overall readiness pushes strongly toward VM rehosting

        vm_score = max(20.0, min(95.0, vm_score))

        # -------------------------------------------------------------
        # 3. Decision Determination: OCP vs VM vs Retain
        # -------------------------------------------------------------
        if ocp_score >= 70.0 and len(ocp_blockers) == 0:
            primary_platform = TargetPlatform.OPENSHIFT
            secondary_platform = TargetPlatform.VIRTUAL_MACHINE
            recommended_disposition = RDisposition.REFACTOR
            decision_summary = (
                f"RECOMMENDATION: RED HAT OPENSHIFT (OCP) CONTAINER PLATFORM (Score: {ocp_score:.1f}/100). "
                f"The application exhibits clean modular boundaries, stateless transactions, and relational persistence, "
                f"making it an ideal candidate for cloud-native containerization and microservice refactoring."
            )
        elif ocp_score >= 45.0 or (vm_score > ocp_score and len(ocp_blockers) <= 2):
            primary_platform = TargetPlatform.VIRTUAL_MACHINE
            secondary_platform = TargetPlatform.OPENSHIFT
            recommended_disposition = RDisposition.REPLATFORM
            decision_summary = (
                f"RECOMMENDATION: LINUX VIRTUAL MACHINE (VM) REHOST / REPLATFORM (Score: {vm_score:.1f}/100 vs OCP: {ocp_score:.1f}/100). "
                f"The application has {len(ocp_blockers)} container blocker(s) (e.g. {'; '.join(ocp_blockers[:2])}). "
                f"Hosting on Linux VMs via an enterprise mainframe emulation runtime achieves fastest time-to-value "
                f"while eliminating mainframe MIPS, serving as Phase 1 before gradual container refactoring."
            )
        else:
            primary_platform = TargetPlatform.HYBRID_MAINFRAME
            secondary_platform = TargetPlatform.VIRTUAL_MACHINE
            recommended_disposition = RDisposition.RETAIN
            decision_summary = (
                f"RECOMMENDATION: HYBRID MAINFRAME COEXISTENCE (Retain Core on z/OS, Modernize Edges). "
                f"Extreme low-latency SLA ({latency_sla}ms), custom Assembler exits, or deep multi-resource 2PC "
                f"make immediate distributed hosting high-risk. Expose APIs via z/OS Connect EE while isolating microservices."
            )

        # -------------------------------------------------------------
        # 4. Detailed Logical Explanation
        # -------------------------------------------------------------
        logical_justification = self._generate_logical_justification(
            portfolio, primary_platform, ocp_score, vm_score, ocp_blockers, ocp_pros, ocp_cons
        )

        # -------------------------------------------------------------
        # 5. Comparative Trade-off Matrix (0-100 scores across 8 vectors)
        # -------------------------------------------------------------
        trade_off_matrix = [
            {
                "vector": "Elasticity & Horizontal Scaling",
                "ocp_rating": 95,
                "vm_rating": 45,
                "analysis": "OCP scales pods in seconds via HPA; VMs require minutes to spin up and load images.",
            },
            {
                "vector": "Migration Speed & Time-to-Market",
                "ocp_rating": 40 if ocp_blockers else 75,
                "vm_rating": 90,
                "analysis": "VM rehosting requires minimal code modification; OCP requires refactoring state and batch orchestration.",
            },
            {
                "vector": "Operational Independence & Licensing",
                "ocp_rating": 90,
                "vm_rating": 50,
                "analysis": "OCP runs open-source runtimes with standard subscriptions; VMs often require specialized legacy emulation licenses.",
            },
            {
                "vector": "Stateful Transaction & Session Tolerance",
                "ocp_rating": 30 if conversational_count > 0 else 85,
                "vm_rating": 95,
                "analysis": "VMs support long-lived conversational memory and TWA/CWA; OCP strictly mandates stateless processes.",
            },
            {
                "vector": "Data Consistency & File Locking",
                "ocp_rating": 45 if vsam_count > 0 else 90,
                "vm_rating": 85,
                "analysis": "VMs emulate OS-level shared file systems and record locking; OCP containers require externalized distributed data grids.",
            },
            {
                "vector": "DevOps & Modern Talent Availability",
                "ocp_rating": 95,
                "vm_rating": 60,
                "analysis": "Kubernetes/OpenShift attracts modern cloud engineers; legacy VM emulation maintains specialized skills barrier.",
            },
            {
                "vector": "Low Latency & Network Overhead",
                "ocp_rating": 75,
                "vm_rating": 88,
                "analysis": "VMs bypass container overlay networks (SDN/OVN) and service mesh proxies, saving 2-5ms per hop.",
            },
            {
                "vector": "Long-Term Strategic Agility",
                "ocp_rating": 98,
                "vm_rating": 55,
                "analysis": "OCP aligns with enterprise cloud-native roadmap; VM rehost is often viewed as technical debt deferral.",
            },
        ]

        # -------------------------------------------------------------
        # 6. Architecture Decision Record (ADR)
        # -------------------------------------------------------------
        adr = {
            "adr_id": f"ADR-{portfolio.app_id}-001",
            "title": f"Target Hosting Platform Selection for {portfolio.app_name}",
            "status": "Accepted",
            "context": (
                f"Evaluation of {portfolio.app_name} ({len(portfolio.programs)} programs, {len(portfolio.jobs)} jobs, "
                f"{len(portfolio.tables)} tables, {len(portfolio.vsam_files)} VSAM files) transitioning from IBM z/OS."
            ),
            "decision": f"Adopt {primary_platform.value} as the primary target platform ({recommended_disposition.value}).",
            "justification": logical_justification["summary"],
            "consequences_positive": ocp_pros if primary_platform == TargetPlatform.OPENSHIFT else vm_pros,
            "consequences_negative": ocp_cons if primary_platform == TargetPlatform.OPENSHIFT else vm_cons,
            "roadmap_phases": [
                {
                    "phase": 1,
                    "name": "Phase 1: Remediation & Decoupling",
                    "focus": "Resolve critical blockers (eliminate ALTER verbs, decouple VSAM, extract session state).",
                    "duration_months": 3,
                },
                {
                    "phase": 2,
                    "name": f"Phase 2: Deployment to {primary_platform.value}",
                    "focus": f"Build automated CI/CD pipelines, configure {primary_platform.value} resources, and execute migration.",
                    "duration_months": 6,
                },
                {
                    "phase": 3,
                    "name": "Phase 3: Validation, Cutover & Mainframe Decommission",
                    "focus": "Parallel run testing, dark launch verification, zero-downtime cutover, and MIPS de-allocation.",
                    "duration_months": 3,
                },
            ],
        }

        candidates = [
            PlatformCandidate(
                platform=TargetPlatform.OPENSHIFT,
                suitability_score=round(ocp_score, 1),
                is_recommended=(primary_platform == TargetPlatform.OPENSHIFT),
                pros=ocp_pros,
                cons=ocp_cons,
                blockers=ocp_blockers,
                migration_path=f"{RDisposition.REFACTOR.value} to Cloud-Native Microservices",
                estimated_cost_index="Medium Capital / Very Low Operational (Zero MIPS)",
            ),
            PlatformCandidate(
                platform=TargetPlatform.VIRTUAL_MACHINE,
                suitability_score=round(vm_score, 1),
                is_recommended=(primary_platform == TargetPlatform.VIRTUAL_MACHINE),
                pros=vm_pros,
                cons=vm_cons,
                blockers=[],
                migration_path=f"{RDisposition.REPLATFORM.value} / Lift-and-Shift to Linux VMs",
                estimated_cost_index="Low Capital / Medium Operational (Emulation Software Subscriptions)",
            ),
            PlatformCandidate(
                platform=TargetPlatform.HYBRID_MAINFRAME,
                suitability_score=60.0 if primary_platform == TargetPlatform.HYBRID_MAINFRAME else 35.0,
                is_recommended=(primary_platform == TargetPlatform.HYBRID_MAINFRAME),
                pros=["Guarantees 100% logic and data integrity with zero migration risk."],
                cons=["Continues incurring heavy mainframe MIPS software licensing fees."],
                blockers=[],
                migration_path=f"{RDisposition.RETAIN.value} with API Gateway Abstraction",
                estimated_cost_index="Zero Capital / Very High Operational (Ongoing MIPS)",
            ),
        ]

        return {
            "primary_platform": primary_platform,
            "secondary_platform": secondary_platform,
            "recommended_disposition": recommended_disposition,
            "ocp_score": round(ocp_score, 1),
            "vm_score": round(vm_score, 1),
            "decision_summary": decision_summary,
            "logical_justification": logical_justification,
            "trade_off_matrix": trade_off_matrix,
            "platform_candidates": candidates,
            "adr": adr,
        }

    def _generate_logical_justification(
        self,
        portfolio: ApplicationPortfolio,
        target: TargetPlatform,
        ocp_score: float,
        vm_score: float,
        ocp_blockers: List[str],
        ocp_pros: List[str],
        ocp_cons: List[str],
    ) -> Dict[str, Any]:
        """Creates detailed architectural rationale tailored to the application's characteristics."""
        reasons: List[str] = []

        if target == TargetPlatform.OPENSHIFT:
            reasons.append(
                f"1. STATELESS READINESS: The application operates with pseudo-conversational CICS transactions or stateless services. "
                f"There are no active terminal memory locks, enabling horizontal pod scaling across Red Hat OpenShift nodes without session stickiness issues."
            )
            reasons.append(
                f"2. PERSISTENCE MODULARITY: The data layer is decoupled from mainframe-specific VSAM record locks and runs primarily on relational DB2 schemas, "
                f"which translate seamlessly to distributed databases like PostgreSQL, Amazon Aurora, or Crunchy Data on OpenShift."
            )
            reasons.append(
                f"3. BUSINESS VALUE & AGILITY: Containerization unlocks automated GitOps deployment pipelines, canary deployments, "
                f"and integration with event-driven services (Kafka) with zero ongoing mainframe MIPS cost."
            )
        elif target == TargetPlatform.VIRTUAL_MACHINE:
            reasons.append(
                f"1. ARCHITECTURAL IMPEDANCE MISMATCH: Direct containerization on OpenShift is constrained by {len(ocp_blockers)} critical blocker(s): "
                f"{'; '.join(ocp_blockers[:2])}."
            )
            reasons.append(
                f"2. PRESERVATION OF STATE & CONCURRENCY: Hosting on Linux Virtual Machines running an enterprise mainframe emulator (such as Micro Focus Enterprise Server "
                f"or AWS Blu Age) provides native support for conversational CICS regions, shared CWA/TWA memory pools, and POSIX record-level VSAM file emulation."
            )
            reasons.append(
                f"3. RISK MITIGATION & VELOCITY: Rehosting to VMs allows the organization to cut z/OS hardware and MIPS software fees immediately (often saving 60-70% TCO) "
                f"without incurring the regression risks of a multi-year complete application rewrite. Once stabilized on Linux VMs, modular services can be incrementally extracted into OpenShift containers."
            )
        else:
            reasons.append(
                f"1. MISSION-CRITICAL COEXISTENCE: The application's non-functional requirements (response time: {portfolio.nfrs.target_response_time_ms}ms, "
                f"availability: {portfolio.nfrs.availability_percentage}%) demand the sub-millisecond coupling and hardware fault tolerance of z/OS Parallel Sysplex."
            )
            reasons.append(
                f"2. HYBRID INTEGRATION: The recommended strategy is to encapsulate the mainframe core behind z/OS Connect EE REST APIs or an event mesh, "
                f"modernizing front-end channels and reporting on OpenShift while preserving core transactional integrity on the mainframe."
            )

        return {
            "summary": " ".join(reasons),
            "key_drivers": reasons,
            "ocp_suitability": ocp_score,
            "vm_suitability": vm_score,
        }
