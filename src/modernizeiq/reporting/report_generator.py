"""Multi-Format Enterprise Modernization Report Generator."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import AssessmentReport
from ..ui.dashboard_template import generate_dashboard_html


class ReportGenerator:
    """Generates visual HTML dashboards, executive Markdown dossiers, and machine-readable JSON."""

    def generate_html_dashboard(self, report_dict: Dict[str, Any], output_path: str) -> str:
        """Renders and saves self-contained interactive HTML5 dashboard."""
        html_content = generate_dashboard_html(report_dict)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html_content, encoding="utf-8")
        return str(out.resolve())

    def generate_json_report(self, report_dict: Dict[str, Any], output_path: str) -> str:
        """Saves machine-readable JSON representation."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report_dict, indent=2, default=str), encoding="utf-8")
        return str(out.resolve())

    def generate_markdown_dossier(self, report_dict: Dict[str, Any], output_path: str) -> str:
        """Generates comprehensive executive Markdown assessment document."""
        pf = report_dict.get("portfolio", {})
        decision = report_dict.get("decision", {})
        assessment = report_dict.get("assessment", {})
        dims = assessment.get("dimension_scores", [])
        risks = assessment.get("risks", [])
        adr = decision.get("adr", {})
        clusters = report_dict.get("semantic_clusters", [])

        md: list[str] = [
            f"# ModernizeIQ: Enterprise Modernization Assessment Dossier",
            f"**Application:** {pf.get('app_name')} (`{pf.get('app_id')}`)",
            f"**Target Architecture Recommendation:** **{decision.get('primary_platform')}** ({decision.get('recommended_disposition')})",
            f"**Overall Readiness Score:** `{assessment.get('overall_normalized_score')}/100` ({assessment.get('overall_readiness_rating')})",
            f"**Total Remediation Effort:** `{assessment.get('total_estimated_person_days')} Person-Days`",
            "",
            "---",
            "",
            "## 1. Executive Summary & Architectural Verdict",
            decision.get("decision_summary", "Evaluation complete."),
            "",
            "### Architectural Rationale",
            decision.get("logical_justification", {}).get("summary", ""),
            "",
            "---",
            "",
            "## 2. Target Platform Evaluation: OpenShift (OCP) vs Linux VM",
            f"- **Red Hat OpenShift (OCP) Fit Index:** `{decision.get('ocp_score')}%`",
            f"- **Linux Virtual Machine (VM) Fit Index:** `{decision.get('vm_score')}%`",
            "",
            "| Evaluation Vector | OpenShift (OCP) | Virtual Machine (VM) | Analysis |",
            "| :--- | :---: | :---: | :--- |",
        ]

        for tm in decision.get("trade_off_matrix", []):
            md.append(f"| {tm['vector']} | **{tm['ocp_rating']}%** | **{tm['vm_rating']}%** | {tm['analysis']} |")

        md.extend([
            "",
            "---",
            "",
            "## 3. 8-Dimensional Modernization Assessment Breakdown",
            "",
            "| Dimension | Score | Rating | Key Finding | Blocker Summary |",
            "| :--- | :---: | :---: | :--- | :--- |",
        ])

        for d in dims:
            blocker_txt = "; ".join(d.get("blockers", [])) if d.get("blockers") else "None"
            finding_txt = d.get("key_findings", [""])[0] if d.get("key_findings") else ""
            md.append(f"| {d['dimension_name']} | **{d['normalized_score']}%** | `{d['readiness_rating']}` | {finding_txt} | {blocker_txt} |")

        md.extend([
            "",
            "---",
            "",
            "## 4. all-MiniLM-L6-v2 Semantic Microservice Bounded Contexts",
            "Natural language and structural embedding clustering decomposed the portfolio into the following candidate services:",
            "",
        ])

        for c in clusters:
            md.append(f"### {c['cluster_name']} (Cohesion Score: `{c['cohesion_score']}`)")
            md.append(f"- **Domain Context:** {c['business_domain']}")
            md.append(f"- **Candidate Target:** `{c['suggested_target']}`")
            md.append(f"- **Member Programs:** `{', '.join(c['programs'])}`")
            md.append("")

        md.extend([
            "---",
            "",
            "## 5. Critical Risk & Anti-Pattern Catalog",
            "",
            "| Risk ID | Severity | Title | Impact | Remediation Strategy | Effort (Days) |",
            "| :--- | :---: | :--- | :--- | :--- | :---: |",
        ])

        for r in risks:
            md.append(f"| `{r['risk_id']}` | **{r['severity']}** | {r['title']} | {r['migration_impact']} | {r['remediation_strategy']} | `{r['effort_person_days']}` |")

        md.extend([
            "",
            "---",
            "",
            "## 6. Architecture Decision Record (ADR)",
            f"**Identifier:** `{adr.get('adr_id')}`",
            f"**Title:** {adr.get('title')}",
            f"**Status:** `{adr.get('status')}`",
            "",
            "### Context",
            adr.get("context", ""),
            "",
            "### Decision",
            f"**{adr.get('decision')}**",
            "",
            "### Consequences",
            "**Positive:**",
        ])

        for pos in adr.get("consequences_positive", []):
            md.append(f"- {pos}")

        md.append("\n**Negative / Retained:**")
        for neg in adr.get("consequences_negative", []):
            md.append(f"- {neg}")

        md.extend([
            "",
            "### Phased Roadmap",
        ])

        for phase in adr.get("roadmap_phases", []):
            md.append(f"- **Phase {phase['phase']}: {phase['name']}** ({phase['duration_months']} months): {phase['focus']}")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(md), encoding="utf-8")
        return str(out.resolve())
