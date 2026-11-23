"""ModernizeIQ Command Line Interface."""

from __future__ import annotations
import argparse
import sys
import webbrowser
from pathlib import Path

from .parsers.metadata_loader import MetadataLoader
from .analyzers.portfolio_analyzer import PortfolioAnalyzer
from .semantic.clusterer import SemanticClusterer
from .decision.platform_evaluator import TargetPlatformDecisionEngine
from .graph.graph_engine import DependencyGraphEngine
from .reporting.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        prog="modernizeiq",
        description="ModernizeIQ: Mainframe-to-Distributed Architectural Intelligence & Assessment Ecosystem",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze mainframe application artifacts")
    analyze_parser.add_argument("path", help="Path to portfolio directory or metadata JSON file")
    analyze_parser.add_argument("--out-dir", "--output-dir", "-o", default="./reports", help="Output directory for reports")
    analyze_parser.add_argument("--visual", "-v", action="store_true", help="Automatically launch visual dashboard in browser")
    analyze_parser.add_argument("--json", action="store_true", help="Generate machine-readable JSON report")
    analyze_parser.add_argument("--md", action="store_true", help="Generate Markdown dossier")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start REST API & Web Dashboard Server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind")

    args = parser.parse_args()

    if args.command == "analyze":
        run_analysis(args)
    elif args.command == "serve":
        run_server(args)
    else:
        parser.print_help()


def run_analysis(args):
    input_path = Path(args.path)
    if not input_path.exists():
        print(f"Error: Path '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("  MODERNIZEIQ: MAINFRAME MODERNIZATION ASSESSMENT ECOSYSTEM")
    print("=" * 70)

    loader = MetadataLoader()
    if input_path.is_file() and input_path.suffix.lower() == ".json":
        print(f"[*] Ingesting structured metadata JSON: {input_path.name}")
        portfolio = loader.load_from_json(input_path.read_text(encoding="utf-8"))
    else:
        print(f"[*] Scanning & parsing multi-artifact directory: {input_path}")
        portfolio = loader.load_from_directory(str(input_path))

    print(f"    - COBOL Programs : {len(portfolio.cobol_programs)}")
    print(f"    - Copybooks      : {len(portfolio.copybooks)}")
    print(f"    - JCL Jobs       : {len(portfolio.jcl_jobs)}")
    print(f"    - BMS Mapsets    : {len(portfolio.bms_mapsets)}")
    print(f"    - DB2 Tables     : {len(portfolio.db2_tables)}")
    print(f"    - VSAM Files     : {len(portfolio.vsam_files)}")
    print(f"    - RACF Profiles  : {len(portfolio.racf_profiles)}")
    print("")

    # 1. 8-Dimensional Assessment & 12-Factor Compliance
    print("[1/4] Running 8-Dimensional Assessment & Twelve-Factor Compliance Engine...")
    analyzer = PortfolioAnalyzer()
    assessment_results = analyzer.run_assessment(portfolio)
    overall_score = assessment_results["overall_normalized_score"]
    overall_rating = assessment_results["overall_readiness_rating"]
    print(f"    -> Overall Cloud-Readiness Index: {overall_score}/100 ({overall_rating})")

    # 2. Semantic Domain Decomposition
    print("[2/4] Executing all-MiniLM-L6-v2 Semantic Domain Clustering & 2D Projection...")
    clusterer = SemanticClusterer()
    clusters, coords = clusterer.cluster_portfolio(portfolio)
    print(f"    -> Decomposed into {len(clusters)} candidate microservice bounded contexts.")

    # 3. Target Platform Decision Matrix (OCP vs VM)
    print("[3/4] Evaluating Target Platform Decision (OpenShift vs Linux VM)...")
    decision_engine = TargetPlatformDecisionEngine()
    decision_results = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment_results["dimension_scores"],
        risks=assessment_results["risks"],
        overall_score=overall_score,
    )
    primary = decision_results["primary_platform"].value
    ocp_s = decision_results["ocp_score"]
    vm_s = decision_results["vm_score"]
    print(f"    -> Recommended Target Platform: {primary}")
    print(f"    -> OCP Fit Index: {ocp_s}% | VM Fit Index: {vm_s}%")

    # 4. Dependency Graph & Blast Radius
    print("[4/4] Building Multi-Artifact Dependency Topology & Centrality Graph...")
    graph_engine = DependencyGraphEngine()
    graph_data = graph_engine.build_graph(portfolio)
    print(f"    -> Topology Nodes: {len(graph_data.nodes)} | Edges: {len(graph_data.edges)}")
    print("")

    # Build report dict
    report_dict = {
        "portfolio": portfolio.dict(),
        "assessment": {
            "dimension_scores": [d.dict() for d in assessment_results["dimension_scores"]],
            "overall_normalized_score": overall_score,
            "overall_raw_score": assessment_results["overall_raw_score"],
            "overall_readiness_rating": overall_rating,
            "twelve_factor_compliance": [f.dict() for f in assessment_results["twelve_factor_compliance"]],
            "average_factor_score": assessment_results["average_factor_score"],
            "risks": [r.dict() for r in assessment_results["risks"]],
            "remediations": [rem.dict() for rem in assessment_results["remediations"]],
            "total_estimated_person_days": assessment_results["total_estimated_person_days"],
            "initial_disposition": assessment_results["initial_disposition"].value,
            "target_platform": assessment_results["target_platform"].value,
        },
        "semantic_clusters": [c.dict() for c in clusters],
        "semantic_coords": coords,
        "decision": {
            "primary_platform": decision_results["primary_platform"].value,
            "secondary_platform": decision_results["secondary_platform"].value,
            "recommended_disposition": decision_results["recommended_disposition"].value,
            "ocp_score": ocp_s,
            "vm_score": vm_s,
            "decision_summary": decision_results["decision_summary"],
            "logical_justification": decision_results["logical_justification"],
            "trade_off_matrix": decision_results["trade_off_matrix"],
            "platform_candidates": [c.dict() for c in decision_results["platform_candidates"]],
            "adr": decision_results["adr"],
        },
        "dependency_graph": graph_data.dict(),
    }

    # Generate Reports
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_gen = ReportGenerator()

    html_file = out_dir / f"{portfolio.app_id}_modernization_dashboard.html"
    report_gen.generate_html_dashboard(report_dict, str(html_file))
    print(f"[+] Visual Dashboard generated at: {html_file.resolve()}")

    if args.md or True:  # Default to generate Markdown
        md_file = out_dir / f"{portfolio.app_id}_assessment_dossier.md"
        report_gen.generate_markdown_dossier(report_dict, str(md_file))
        print(f"[+] Executive Markdown dossier generated at: {md_file.resolve()}")

    if args.json:
        json_file = out_dir / f"{portfolio.app_id}_assessment_data.json"
        report_gen.generate_json_report(report_dict, str(json_file))
        print(f"[+] JSON schema data saved at: {json_file.resolve()}")

    print("\n" + "=" * 70)
    print("  ARCHITECTURAL SUMMARY VERDICT")
    print("=" * 70)
    print(f"Application: {portfolio.app_name}")
    print(f"Target Platform: {primary.upper()} ({decision_results['recommended_disposition'].value})")
    print(f"Fit Comparison: OCP {ocp_s}% vs Linux VM {vm_s}%")
    print(f"Total Remediation Workload: {assessment_results['total_estimated_person_days']} person-days")
    print(f"Key Rationale: {decision_results['logical_justification']['summary']}")
    print("=" * 70)

    if args.visual:
        print("[*] Launching Visual Dashboard in browser...")
        webbrowser.open(str(html_file.resolve()))


def run_server(args):
    import uvicorn
    print(f"[*] Starting ModernizeIQ API & Web Dashboard at http://{args.host}:{args.port}")
    uvicorn.run("modernizeiq.api.app:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
