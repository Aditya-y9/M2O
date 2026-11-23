"""ModernizeIQ FastAPI REST API Service."""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..parsers.metadata_loader import MetadataLoader
from ..analyzers.portfolio_analyzer import PortfolioAnalyzer
from ..semantic.clusterer import SemanticClusterer
from ..decision.platform_evaluator import TargetPlatformDecisionEngine
from ..graph.graph_engine import DependencyGraphEngine
from ..reporting.report_generator import ReportGenerator
from ..ui.dashboard_template import generate_dashboard_html
from ..ai.semantic_search import SemanticSearchEngine, generate_conversational_answer


app = FastAPI(
    title="ModernizeIQ API",
    description="Mainframe-to-Distributed Architectural Intelligence & Assessment Ecosystem",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metadata_loader = MetadataLoader()
portfolio_analyzer = PortfolioAnalyzer()
semantic_clusterer = SemanticClusterer()
decision_engine = TargetPlatformDecisionEngine()
graph_engine = DependencyGraphEngine()
report_generator = ReportGenerator()
semantic_search = SemanticSearchEngine()

# In-memory cache of latest assessment
_LATEST_REPORT: Dict[str, Any] = {}
_SEARCH_INDEX_BUILT: bool = False


@app.get("/", response_class=HTMLResponse)
def root():
    if _LATEST_REPORT:
        return generate_dashboard_html(_LATEST_REPORT)
    return """
    <html>
        <head><title>ModernizeIQ API</title><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="bg-slate-950 text-slate-100 flex items-center justify-center min-h-screen">
            <div class="max-w-md p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
                <div class="h-12 w-12 rounded-xl bg-cyan-500 mx-auto flex items-center justify-center font-bold text-xl">M</div>
                <h1 class="text-2xl font-bold">ModernizeIQ Ecosystem</h1>
                <p class="text-sm text-slate-400">Mainframe-to-Distributed Modernization Assessment Engine.</p>
                <div class="pt-2">
                    <a href="/docs" class="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs inline-block">Explore OpenAPI Docs</a>
                </div>
            </div>
        </body>
    </html>
    """


@app.post("/api/analyze/directory")
def analyze_directory(dir_path: str = Query(..., description="Absolute path to application folder")):
    global _LATEST_REPORT
    try:
        portfolio = metadata_loader.load_from_directory(dir_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load directory: {str(e)}")

    assessment_results = portfolio_analyzer.run_assessment(portfolio)
    clusters, coords = semantic_clusterer.cluster_portfolio(portfolio)
    decision_results = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment_results["dimension_scores"],
        risks=assessment_results["risks"],
        overall_score=assessment_results["overall_normalized_score"],
    )
    graph_data = graph_engine.build_graph(portfolio)

    report_dict = {
        "portfolio": portfolio.dict(),
        "assessment": {
            "dimension_scores": [d.dict() for d in assessment_results["dimension_scores"]],
            "overall_normalized_score": assessment_results["overall_normalized_score"],
            "overall_raw_score": assessment_results["overall_raw_score"],
            "overall_readiness_rating": assessment_results["overall_readiness_rating"],
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
            "ocp_score": decision_results["ocp_score"],
            "vm_score": decision_results["vm_score"],
            "decision_summary": decision_results["decision_summary"],
            "logical_justification": decision_results["logical_justification"],
            "trade_off_matrix": decision_results["trade_off_matrix"],
            "platform_candidates": [c.dict() for c in decision_results["platform_candidates"]],
            "adr": decision_results["adr"],
        },
        "dependency_graph": graph_data.dict(),
    }

    _LATEST_REPORT = report_dict
    
    # Build semantic search index
    global _SEARCH_INDEX_BUILT
    semantic_search.build_index(report_dict)
    _SEARCH_INDEX_BUILT = True
    
    return report_dict


@app.get("/api/dashboard", response_class=HTMLResponse)
def get_dashboard():
    if not _LATEST_REPORT:
        raise HTTPException(status_code=404, detail="No assessment report available yet. Run /api/analyze/directory first.")
    return generate_dashboard_html(_LATEST_REPORT)


@app.get("/api/blast-radius")
def get_blast_radius(artifact_id: str = Query(..., description="Target node ID")):
    if not _LATEST_REPORT:
        raise HTTPException(status_code=404, detail="No application portfolio loaded.")
    portfolio = metadata_loader.load_from_json(json.dumps(_LATEST_REPORT["portfolio"]))
    radius = graph_engine.calculate_blast_radius(portfolio, artifact_id)
    return radius


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/api/semantic-search")
def semantic_search_endpoint(request: SemanticSearchRequest):
    """Natural language Q&A over mainframe components."""
    if not _LATEST_REPORT:
        raise HTTPException(status_code=404, detail="No assessment report available. Run /api/analyze/directory first.")
    
    if not _SEARCH_INDEX_BUILT:
        # Build index on-demand if not already built
        semantic_search.build_index(_LATEST_REPORT)
    
    # Perform semantic search
    results = semantic_search.search(_LATEST_REPORT, request.query, top_k=request.top_k)
    
    # Generate conversational answer
    answer = generate_conversational_answer(request.query, results, _LATEST_REPORT)
    
    return {
        "query": request.query,
        "answer": answer,
        "results": results,
        "result_count": len(results)
    }
