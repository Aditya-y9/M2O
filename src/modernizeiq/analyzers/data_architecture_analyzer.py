"""Dimension 3: Data Architecture & Persistence Analyzer."""

from __future__ import annotations
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor
from .base_analyzer import BaseDimensionAnalyzer


class DataArchitectureAnalyzer(BaseDimensionAnalyzer):
    """Analyzes DB2 relational schemas, VSAM dataset coupling, and EBCDIC-ASCII conversion risk."""

    @property
    def dimension_name(self) -> str:
        return "Data Architecture & Persistence"

    @property
    def weight(self) -> float:
        return 0.15

    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        tables = portfolio.tables
        vsam_files = portfolio.vsam_files
        programs = list(portfolio.programs.values())
        risks: List[RiskFactor] = []

        total_tables = len(tables)
        total_vsam = len(vsam_files)

        score = 1.0
        findings: List[str] = [
            f"Detected {total_tables} DB2 Table(s) and {total_vsam} VSAM Dataset(s).",
        ]
        strengths: List[str] = []
        blockers: List[str] = []

        # 1. Evaluate VSAM file dependencies (High impedance match with cloud-native containers)
        if total_vsam > 0:
            vsam_sharing = {v_name: len(v.accessed_by_programs) for v_name, v in vsam_files.items()}
            max_vsam = max(vsam_sharing.items(), key=lambda x: x[1]) if vsam_sharing else ("None", 0)

            # VSAM files require either mainframe record-level sharing (RLS), mainframe emulation, or database refactoring
            if total_vsam > 5 or max_vsam[1] > 2:
                score += 1.8
                risks.append(RiskFactor(
                    risk_id="RISK-DATA-01",
                    title="Shared VSAM Flat File Persistence",
                    description=f"Portfolio depends on {total_vsam} VSAM files. Dataset '{max_vsam[0]}' is accessed concurrently by {max_vsam[1]} programs. File locking in distributed containers lacks POSIX record-level lock semantics.",
                    dimension=self.dimension_name,
                    severity="Critical",
                    affected_artifacts=list(vsam_files.keys()),
                    migration_impact="Direct containerization blocked without data migration or emulation driver; risk of data corruption.",
                    remediation_strategy="Migrate VSAM files to PostgreSQL or MongoDB with document/key-value indexing, or deploy an in-memory data grid (Redis/Hazelcast).",
                    effort_person_days=total_vsam * 4,
                ))
                blockers.append(f"{total_vsam} VSAM files accessed concurrently without distributed record-level locks")
            else:
                score += 0.9
                risks.append(RiskFactor(
                    risk_id="RISK-DATA-02",
                    title="VSAM Dataset Dependencies",
                    description=f"Found {total_vsam} VSAM dataset(s). Requires data conversion to relational or document storage.",
                    dimension=self.dimension_name,
                    severity="High",
                    affected_artifacts=list(vsam_files.keys()),
                    migration_impact="Containers cannot mount native VSAM datasets directly.",
                    remediation_strategy="Convert VSAM clusters to relational tables using AWS DMS, Qlik, or custom ETL.",
                    effort_person_days=total_vsam * 2,
                ))
        else:
            strengths.append("Zero VSAM flat files detected; modern relational DB2 persistence utilized.")

        # 2. Evaluate DB2 Relational Tables
        if total_tables > 0:
            findings.append(f"DB2 relational database utilized across {total_tables} tables.")
            # Check for programs with embedded SQL
            sql_progs = [p for p in programs if p.sql_queries_count > 0]
            if sql_progs:
                findings.append(f"{len(sql_progs)} program(s) execute embedded EXEC SQL commands.")
                strengths.append("Relational SQL schema readily maps to distributed databases (PostgreSQL/Cloud SQL).")

        # 3. Packed Decimal & EBCDIC-ASCII conversion risk
        # Scan programs for COMP-3 (packed decimal) in copybooks or variables
        packed_count = sum(1 for p in programs if any("COMP-3" in cb.upper() for cb in p.copybooks_used))
        if packed_count > 0 or any("COMP-3" in str(cb).upper() for cb in portfolio.copybooks.values()):
            score += 0.5
            risks.append(RiskFactor(
                risk_id="RISK-DATA-03",
                title="EBCDIC & Packed Decimal (COMP-3) Collation Risk",
                description="High prevalence of COMP-3 binary packed decimals and EBCDIC alphanumeric encoding.",
                dimension=self.dimension_name,
                severity="Medium",
                affected_artifacts=[p.program_id for p in programs if any("COMP-3" in cb.upper() for cb in p.copybooks_used)],
                migration_impact="Sorting, string comparison, and decimal rounding differ between EBCDIC and ASCII on Linux x86.",
                remediation_strategy="Apply strict byte-array mapping or transition to IEEE 754 floating point / BigDecimal types.",
                effort_person_days=len(programs) * 1.0,
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
