"""End-to-End Analysis & Visual Report Generation Tests."""

from pathlib import Path
import pytest
from modernizeiq.parsers.metadata_loader import MetadataLoader
from modernizeiq.analyzers.portfolio_analyzer import PortfolioAnalyzer
from modernizeiq.semantic.clusterer import SemanticClusterer
from modernizeiq.decision.platform_evaluator import TargetPlatformDecisionEngine
from modernizeiq.graph.graph_engine import DependencyGraphEngine
from modernizeiq.reporting.report_generator import ReportGenerator
from modernizeiq.ui.dashboard_template import generate_dashboard_html


def test_full_pipeline_core_banking(tmp_path):
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/core_banking_deposit")

    analyzer = PortfolioAnalyzer()
    assessment = analyzer.run_assessment(portfolio)

    clusterer = SemanticClusterer()
    clusters, coords = clusterer.cluster_portfolio(portfolio)

    decision_engine = TargetPlatformDecisionEngine()
    decision = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment["dimension_scores"],
        risks=assessment["risks"],
        overall_score=assessment["overall_normalized_score"],
    )

    graph_engine = DependencyGraphEngine()
    graph_data = graph_engine.build_graph(portfolio)

    report_dict = {
        "portfolio": portfolio.dict(),
        "assessment": {
            "dimension_scores": [d.dict() for d in assessment["dimension_scores"]],
            "overall_normalized_score": assessment["overall_normalized_score"],
            "overall_raw_score": assessment["overall_raw_score"],
            "overall_readiness_rating": assessment["overall_readiness_rating"],
            "twelve_factor_compliance": [f.dict() for f in assessment["twelve_factor_compliance"]],
            "average_factor_score": assessment["average_factor_score"],
            "risks": [r.dict() for r in assessment["risks"]],
            "remediations": [rem.dict() for rem in assessment["remediations"]],
            "total_estimated_person_days": assessment["total_estimated_person_days"],
            "initial_disposition": assessment["initial_disposition"].value,
            "target_platform": assessment["target_platform"].value,
        },
        "semantic_clusters": [c.dict() for c in clusters],
        "semantic_coords": coords,
        "decision": {
            "primary_platform": decision["primary_platform"].value,
            "secondary_platform": decision["secondary_platform"].value,
            "recommended_disposition": decision["recommended_disposition"].value,
            "ocp_score": decision["ocp_score"],
            "vm_score": decision["vm_score"],
            "decision_summary": decision["decision_summary"],
            "logical_justification": decision["logical_justification"],
            "trade_off_matrix": decision["trade_off_matrix"],
            "platform_candidates": [c.dict() for c in decision["platform_candidates"]],
            "adr": decision["adr"],
        },
        "dependency_graph": graph_data.dict(),
    }

    report_gen = ReportGenerator()
    html_out = tmp_path / "dashboard.html"
    md_out = tmp_path / "dossier.md"
    json_out = tmp_path / "data.json"

    report_gen.generate_html_dashboard(report_dict, str(html_out))
    report_gen.generate_markdown_dossier(report_dict, str(md_out))
    report_gen.generate_json_report(report_dict, str(json_out))

    assert html_out.exists()
    assert md_out.exists()
    assert json_out.exists()

    html_text = html_out.read_text(encoding="utf-8")
    assert "ModernizeIQ" in html_text
    assert "Blast Radius Engine" in html_text
    assert "Core Banking Deposit Subsystem" in html_text
    # New dashboard shows ROI metrics
    assert "Risk Score" in html_text or "RISK SCORE" in html_text
    assert "Effort" in html_text or "EFFORT" in html_text
    assert "Savings" in html_text or "SAVINGS" in html_text
    # Graph elements
    assert "graph" in html_text or "Graph" in html_text
    # No external dependencies
    assert "https://cdn.tailwindcss.com" not in html_text
    assert "chart.umd.min.js" not in html_text
    assert "fonts.googleapis.com" not in html_text
    # No template placeholders
    assert "__APP_NAME__" not in html_text
    assert "<!--__WORKBENCH_CONTENT__-->" not in html_text


def test_dashboard_escapes_portfolio_and_risk_text():
    report = {
        "portfolio": {
            "app_name": "Cash <Ledger>",
            "app_id": "APP-001",
            "business_domain": "Retail & Payments",
            "programs": {}, "copybooks": {}, "jobs": {}, "transactions": {},
            "mapsets": {}, "tables": {}, "vsam_files": {},
        },
        "assessment_report": {
            "overall_score": 62,
            "readiness_rating": "Conditional",
            "dimension_scores": [],
            "twelve_factor_compliance": [],
            "risks": [{
                "id": "R-1", "severity": "high", "category": "security",
                "description": "Do not render <script>alert(1)</script>",
                "mitigation_strategy": "Verify & isolate shared credentials.",
            }],
        },
        "platform_decision": {
            "primary_recommendation": {
                "platform": "Linux VM",
                "rationale": "Use a staged move"
            }
        },
        "semantic_clusters": [],
        "dependency_graph": {"nodes": [], "edges": []},
    }

    html_text = generate_dashboard_html(report)

    assert "Cash &lt;Ledger&gt;" in html_text
    assert "Do not render &lt;script&gt;alert(1)&lt;/script&gt;" in html_text
    assert "<script>alert(1)</script>" not in html_text
