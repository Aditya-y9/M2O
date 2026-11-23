"""Twelve-Factor App Cloud-Native Readiness Evaluator.

Assesses how well legacy mainframe applications align with the 12-Factor principles
required for resilient, horizontally scalable containerization on Red Hat OpenShift (OCP).
"""

from __future__ import annotations
from typing import List, Dict
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import FactorCompliance


class TwelveFactorAnalyzer:
    """Evaluates the 12 Factors for container readiness."""

    def analyze(self, portfolio: ApplicationPortfolio) -> List[FactorCompliance]:
        results: List[FactorCompliance] = []
        programs = list(portfolio.programs.values())
        cics_progs = [p for p in programs if p.is_cics_program]
        conversational_count = sum(1 for p in cics_progs if p.is_conversational)
        shared_vsam_count = len(portfolio.vsam_files)
        total_syncpoints = sum(p.cics_syncpoints_count for p in programs)

        # Factor 1: Codebase (One codebase tracked in revision control, many deploys)
        results.append(FactorCompliance(
            factor_id="I",
            name="Codebase",
            status="Compliant",
            score=85.0,
            gap_analysis="Mainframe PDS/Panvalet libraries can be migrated into Git repositories with branching.",
            remediation="Establish unified Git repository with trunk-based development.",
        ))

        # Factor 2: Dependencies (Explicitly declare and isolate dependencies)
        dyn_calls = sum(len(p.dynamic_calls) for p in programs)
        f2_score = 45.0 if dyn_calls > 0 else 75.0
        results.append(FactorCompliance(
            factor_id="II",
            name="Dependencies",
            status="Partial" if dyn_calls > 0 else "Compliant",
            score=f2_score,
            gap_analysis=f"Dynamic CALL statements ({dyn_calls} found) and STEPLIB/JOBLIB concatenate implicit search orders.",
            remediation="Declare external libraries in Maven/Gradle/Go modules or container image manifest.",
        ))

        # Factor 3: Config (Store config in the environment)
        results.append(FactorCompliance(
            factor_id="III",
            name="Config",
            status="Non-Compliant",
            score=30.0,
            gap_analysis="Environment parameters, dataset names, and CICS region IDs are hardcoded in JCL cards and COBOL WORKING-STORAGE.",
            remediation="Externalize parameters to Kubernetes ConfigMaps and Secrets injected as environment variables.",
        ))

        # Factor 4: Backing Services (Treat backing services as attached resources)
        f4_score = 40.0 if shared_vsam_count > 0 else 80.0
        results.append(FactorCompliance(
            factor_id="IV",
            name="Backing Services",
            status="Partial" if shared_vsam_count > 0 else "Compliant",
            score=f4_score,
            gap_analysis=f"Tightly bound to local mainframe subsystems (VSAM RLS, DB2 Subsystem ID). {shared_vsam_count} VSAM datasets bound to physical DASD volumes.",
            remediation="Abstract databases, message queues, and object storage behind standard URIs and connection pools.",
        ))

        # Factor 5: Build, Release, Run (Strictly separate build and run stages)
        results.append(FactorCompliance(
            factor_id="V",
            name="Build, Release, Run",
            status="Compliant",
            score=80.0,
            gap_analysis="Mainframe compile/link-edit separates binaries from execution, easily adaptable to container multi-stage builds.",
            remediation="Containerize build step using Red Hat Universal Base Image (UBI) and Tekton / OpenShift Pipelines.",
        ))

        # Factor 6: Processes (Execute the app as one or more stateless processes)
        if conversational_count > 0:
            f6_status = "Non-Compliant"
            f6_score = 20.0
            f6_gap = f"{conversational_count} conversational CICS programs hold task and terminal memory across user interactions."
            f6_rem = "Refactor to pseudo-conversational with external Redis/Memcached session stores, or adopt stateless REST."
        else:
            f6_status = "Compliant"
            f6_score = 90.0
            f6_gap = "Pseudo-conversational CICS or headless batch allows stateless pod scaling."
            f6_rem = "Ensure all in-memory variables are localized to single request scopes."

        results.append(FactorCompliance(
            factor_id="VI",
            name="Processes",
            status=f6_status,
            score=f6_score,
            gap_analysis=f6_gap,
            remediation=f6_rem,
        ))

        # Factor 7: Port Binding (Export services via port binding)
        has_bms = len(portfolio.mapsets) > 0
        results.append(FactorCompliance(
            factor_id="VII",
            name="Port Binding",
            status="Non-Compliant" if has_bms else "Compliant",
            score=35.0 if has_bms else 90.0,
            gap_analysis="BMS 3270 maps communicate through SNA terminal LU pools rather than self-contained HTTP/gRPC port binding.",
            remediation="Expose HTTP/REST or gRPC endpoints bound to container ports 8080/8443, fronted by OpenShift Routes.",
        ))

        # Factor 8: Concurrency (Scale out via the process model)
        f8_score = 35.0 if total_syncpoints > 5 or shared_vsam_count > 3 else 80.0
        results.append(FactorCompliance(
            factor_id="VIII",
            name="Concurrency",
            status="Partial" if f8_score < 70 else "Compliant",
            score=f8_score,
            gap_analysis="Mainframe relies on scale-up vertical MIPS and CICS multi-region operation (MRO). Concurrent pod scaling blocked by file locks.",
            remediation="Enable OpenShift Horizontal Pod Autoscaler (HPA) using CPU/memory and custom Prometheus metrics.",
        ))

        # Factor 9: Disposability (Maximize robustness with fast startup and graceful shutdown)
        results.append(FactorCompliance(
            factor_id="IX",
            name="Disposability",
            status="Partial",
            score=60.0,
            gap_analysis="Mainframe programs expect warm region memory pools; cold startup overhead requires optimization.",
            remediation="Implement Kubernetes liveness and readiness probes with graceful SIGTERM termination hooks.",
        ))

        # Factor 10: Dev/Prod Parity (Keep development, staging, and production as similar as possible)
        results.append(FactorCompliance(
            factor_id="X",
            name="Dev/Prod Parity",
            status="Non-Compliant",
            score=25.0,
            gap_analysis="Massive disparity between developer workstations (Windows/macOS x86) and production IBM z/OS mainframes.",
            remediation="Standardize on containerized local dev environment (Minikube / OpenShift Local / Podman Desktop).",
        ))

        # Factor 11: Logs (Treat logs as event streams)
        results.append(FactorCompliance(
            factor_id="XI",
            name="Logs",
            status="Partial",
            score=50.0,
            gap_analysis="Logs directed to spool datasets (SYSOUT, CESE, JESMSGLG) with rigid 132-character record layouts.",
            remediation="Direct structured JSON logs to stdout/stderr; collect via OpenShift Logging (Fluentd / Vector / OpenSearch).",
        ))

        # Factor 12: Admin Processes (Run admin/management tasks as one-off processes)
        has_jcl = len(portfolio.jobs) > 0
        results.append(FactorCompliance(
            factor_id="XII",
            name="Admin Processes",
            status="Compliant",
            score=85.0 if has_jcl else 70.0,
            gap_analysis="JCL batch jobs naturally map to Kubernetes one-off Jobs and CronJobs.",
            remediation="Convert administrative JCL scripts to containerized Kubernetes Jobs executed via oc create job.",
        ))

        return results
