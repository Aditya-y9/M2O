"""Generate HTML dashboards for sample portfolios."""
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modernizeiq.parsers.metadata_loader import MetadataLoader
from modernizeiq.analyzers.portfolio_analyzer import PortfolioAnalyzer
from modernizeiq.semantic.clusterer import SemanticClusterer
from modernizeiq.decision.platform_evaluator import TargetPlatformDecisionEngine
from modernizeiq.graph.graph_engine import DependencyGraphEngine
from modernizeiq.reporting.report_generator import ReportGenerator


def generate_report_for_portfolio(portfolio_name: str):
    """Generate full report for a given portfolio."""
    print(f"\n{'='*60}")
    print(f"Generating report for: {portfolio_name}")
    print(f"{'='*60}")
    
    # Load portfolio
    loader = MetadataLoader()
    portfolio_path = f"data/sample_portfolios/{portfolio_name}"
    portfolio = loader.load_from_directory(portfolio_path)
    print(f"[OK] Loaded portfolio from {portfolio_path}")
    
    # Run assessment
    analyzer = PortfolioAnalyzer()
    assessment = analyzer.run_assessment(portfolio)
    print(f"[OK] Completed assessment - Score: {assessment['overall_normalized_score']:.2f}")
    
    # Semantic clustering
    clusterer = SemanticClusterer()
    clusters, coords = clusterer.cluster_portfolio(portfolio)
    print(f"[OK] Identified {len(clusters)} semantic clusters")
    
    # Platform decision
    decision_engine = TargetPlatformDecisionEngine()
    decision = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment["dimension_scores"],
        risks=assessment["risks"],
        overall_score=assessment["overall_normalized_score"],
    )
    print(f"[OK] Platform decision: {decision['primary_platform'].value}")
    
    # Dependency graph
    graph_engine = DependencyGraphEngine()
    graph_data = graph_engine.build_graph(portfolio)
    print(f"[OK] Built dependency graph - {len(graph_data.nodes)} nodes, {len(graph_data.edges)} edges")
    
    # Build report dictionary
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
    
    # Generate outputs
    report_gen = ReportGenerator()
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    html_path = output_dir / f"{portfolio_name}_dashboard.html"
    report_gen.generate_html_dashboard(report_dict, str(html_path))
    print(f"[OK] Generated HTML dashboard: {html_path}")
    
    md_path = output_dir / f"{portfolio_name}_dossier.md"
    report_gen.generate_markdown_dossier(report_dict, str(md_path))
    print(f"[OK] Generated Markdown dossier: {md_path}")
    
    json_path = output_dir / f"{portfolio_name}_data.json"
    report_gen.generate_json_report(report_dict, str(json_path))
    print(f"[OK] Generated JSON data: {json_path}")
    
    return html_path


if __name__ == "__main__":
    portfolios = [
        "core_banking_deposit",
        "policy_admin_monolith",
        "payment_clearing_hub",
    ]
    
    html_files = []
    for portfolio_name in portfolios:
        try:
            html_path = generate_report_for_portfolio(portfolio_name)
            html_files.append(html_path)
        except Exception as e:
            print(f"[ERROR] Error generating report for {portfolio_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("REPORT GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Generated {len(html_files)} HTML dashboards:")
    for html_file in html_files:
        print(f"  - {html_file}")
    print("\nOpen any dashboard in your browser to view the interactive UI.")
