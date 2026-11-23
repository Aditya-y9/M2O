"""Evidence Package Exporter - Generate comprehensive evidence for stakeholders."""

import json
from datetime import datetime
from typing import Dict, Any


def generate_evidence_package(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive evidence package for export.
    
    Returns a structured evidence document with:
    - Executive summary
    - Risk analysis with source metadata
    - ROI calculations with assumptions
    - Dependency graph evidence
    - Actionable recommendations
    """
    portfolio = report_data.get("portfolio", {})
    assessment = report_data.get("assessment_report", {})
    decision = report_data.get("platform_decision", {})
    graph = report_data.get("dependency_graph", {})
    
    app_name = portfolio.get("app_name", "Unknown Application")
    
    # Calculate key metrics
    total_artifacts = (
        len(portfolio.get("programs", {})) +
        len(portfolio.get("copybooks", {})) +
        len(portfolio.get("tables", {})) +
        len(portfolio.get("jobs", {}))
    )
    
    risk_count = len([r for r in assessment.get("risks", []) if r.get("severity") == "high"])
    
    # Build evidence package
    evidence = {
        "generated_at": datetime.now().isoformat(),
        "application": {
            "name": app_name,
            "id": portfolio.get("app_id", "N/A"),
            "domain": portfolio.get("business_domain", "N/A"),
            "total_artifacts": total_artifacts
        },
        "executive_summary": {
            "readiness_score": assessment.get("overall_score", 0),
            "readiness_rating": assessment.get("readiness_rating", "Unknown"),
            "primary_recommendation": decision.get("primary_recommendation", {}).get("platform", "N/A"),
            "high_severity_risks": risk_count,
            "total_dependencies": len(graph.get("edges", [])),
            "key_finding": _generate_key_finding(assessment, decision)
        },
        "risk_analysis": {
            "risks": _format_risks_with_evidence(assessment.get("risks", [])),
            "mitigation_strategies": _extract_mitigations(assessment.get("risks", []))
        },
        "roi_calculation": _calculate_detailed_roi(portfolio, graph),
        "dependency_evidence": {
            "total_nodes": len(graph.get("nodes", [])),
            "total_edges": len(graph.get("edges", [])),
            "critical_dependencies": _identify_critical_dependencies(graph),
            "blast_radius_analysis": _analyze_blast_radius(graph)
        },
        "recommendations": {
            "immediate_actions": _generate_immediate_actions(assessment, decision),
            "migration_sequence": _generate_migration_sequence(graph),
            "success_criteria": _define_success_criteria(assessment)
        },
        "methodology": {
            "analysis_approach": "Static dependency analysis with AI-enhanced semantic clustering",
            "risk_scoring": "Weighted graph centrality (in-degree × 2 + out-degree)",
            "roi_assumptions": [
                "Mainframe MIPS cost: $3,000-5,000/year",
                "Cloud cost: 30-40% of mainframe",
                "Blended modernization rate: $800/day",
                "Annual savings: (MIPS × $4K) × 0.65"
            ]
        }
    }
    
    return evidence


def _generate_key_finding(assessment: Dict, decision: Dict) -> str:
    """Generate the single most important finding."""
    score = assessment.get("overall_score", 0)
    platform = decision.get("primary_recommendation", {}).get("platform", "cloud platform")
    
    if score >= 80:
        return f"Application is highly suitable for {platform} with minimal refactoring required."
    elif score >= 60:
        return f"Application can migrate to {platform} with moderate refactoring of identified components."
    else:
        return f"Application requires significant refactoring before {platform} migration is viable."


def _format_risks_with_evidence(risks: list) -> list:
    """Format risks with source evidence."""
    formatted = []
    for risk in risks:
        formatted.append({
            "id": risk.get("id", "N/A"),
            "severity": risk.get("severity", "unknown"),
            "category": risk.get("category", "general"),
            "description": risk.get("description", ""),
            "evidence": {
                "affected_components": risk.get("affected_components", []),
                "source_analysis": "Detected via dependency graph analysis and pattern matching"
            },
            "business_impact": _assess_business_impact(risk),
            "mitigation": risk.get("mitigation_strategy", "No mitigation defined")
        })
    return formatted


def _extract_mitigations(risks: list) -> list:
    """Extract unique mitigation strategies."""
    mitigations = set()
    for risk in risks:
        if "mitigation_strategy" in risk:
            mitigations.add(risk["mitigation_strategy"])
    return list(mitigations)


def _assess_business_impact(risk: Dict) -> str:
    """Assess business impact of a risk."""
    severity = risk.get("severity", "low")
    if severity == "high":
        return "Critical - may block migration or cause production incidents"
    elif severity == "medium":
        return "Significant - will increase migration effort and timeline"
    else:
        return "Minor - can be addressed during normal migration activities"


def _calculate_detailed_roi(portfolio: Dict, graph: Dict) -> Dict:
    """Calculate detailed ROI with breakdown."""
    # Estimate MIPS based on artifact count (rough heuristic)
    artifact_count = (
        len(portfolio.get("programs", {})) +
        len(portfolio.get("copybooks", {})) +
        len(portfolio.get("jobs", {}))
    )
    estimated_mips = max(100, artifact_count * 10)
    
    # Costs
    mainframe_annual = estimated_mips * 4000  # $4K per MIPS
    cloud_annual = int(mainframe_annual * 0.35)  # 35% of mainframe
    annual_savings = mainframe_annual - cloud_annual
    
    # Effort
    node_count = len(graph.get("nodes", []))
    effort_days = max(90, node_count * 5)  # 5 days per component minimum
    effort_cost = effort_days * 800  # $800/day blended rate
    
    payback_months = round((effort_cost / annual_savings) * 12) if annual_savings > 0 else 999
    
    return {
        "current_state": {
            "estimated_mips": estimated_mips,
            "annual_mainframe_cost": mainframe_annual,
            "cost_per_artifact": round(mainframe_annual / max(1, artifact_count))
        },
        "target_state": {
            "annual_cloud_cost": cloud_annual,
            "cost_reduction_percent": 65
        },
        "migration_investment": {
            "effort_days": effort_days,
            "estimated_cost": effort_cost,
            "blended_rate": 800
        },
        "financial_outcome": {
            "annual_savings": annual_savings,
            "payback_period_months": payback_months,
            "three_year_net_benefit": (annual_savings * 3) - effort_cost,
            "roi_percentage": round(((annual_savings * 3) - effort_cost) / effort_cost * 100)
        }
    }


def _identify_critical_dependencies(graph: Dict) -> list:
    """Identify components with highest dependency impact."""
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    
    # Count in-degree and out-degree for each node
    in_degree = {}
    out_degree = {}
    
    for edge in edges:
        source = edge.get("source", "")
        target = edge.get("target", "")
        out_degree[source] = out_degree.get(source, 0) + 1
        in_degree[target] = in_degree.get(target, 0) + 1
    
    # Find top 5 critical nodes
    critical = []
    for node in nodes:
        node_id = node.get("id", "")
        in_deg = in_degree.get(node_id, 0)
        out_deg = out_degree.get(node_id, 0)
        impact_score = (in_deg * 2) + out_deg
        
        if impact_score > 0:
            critical.append({
                "id": node_id,
                "type": node.get("type", "unknown"),
                "impact_score": impact_score,
                "dependents": in_deg,
                "dependencies": out_deg,
                "reason": f"Affects {in_deg} components, depends on {out_deg} components"
            })
    
    # Sort by impact score descending, return top 5
    critical.sort(key=lambda x: x["impact_score"], reverse=True)
    return critical[:5]


def _analyze_blast_radius(graph: Dict) -> Dict:
    """Analyze overall blast radius characteristics."""
    edges = graph.get("edges", [])
    nodes = graph.get("nodes", [])
    
    if not nodes:
        return {"analysis": "No components to analyze"}
    
    avg_connections = len(edges) / len(nodes) if nodes else 0
    
    return {
        "total_components": len(nodes),
        "total_dependencies": len(edges),
        "average_connections_per_component": round(avg_connections, 2),
        "coupling_assessment": _assess_coupling(avg_connections),
        "recommendation": _recommend_decoupling_strategy(avg_connections)
    }


def _assess_coupling(avg_connections: float) -> str:
    """Assess coupling level."""
    if avg_connections < 2:
        return "Low coupling - components are relatively independent"
    elif avg_connections < 4:
        return "Moderate coupling - typical enterprise application"
    else:
        return "High coupling - significant refactoring recommended before migration"


def _recommend_decoupling_strategy(avg_connections: float) -> str:
    """Recommend decoupling strategy."""
    if avg_connections < 2:
        return "Current architecture supports microservices approach"
    elif avg_connections < 4:
        return "Consider domain-driven design to identify bounded contexts"
    else:
        return "Recommend strangler fig pattern with careful dependency management"


def _generate_immediate_actions(assessment: Dict, decision: Dict) -> list:
    """Generate immediate action items."""
    actions = []
    
    high_risks = [r for r in assessment.get("risks", []) if r.get("severity") == "high"]
    if high_risks:
        actions.append({
            "priority": 1,
            "action": "Address high-severity risks",
            "description": f"Resolve {len(high_risks)} high-severity risks before proceeding",
            "timeline": "1-2 weeks"
        })
    
    actions.append({
        "priority": 2,
        "action": "Validate dependency analysis",
        "description": "Review identified dependencies with application SMEs",
        "timeline": "1 week"
    })
    
    actions.append({
        "priority": 3,
        "action": "Prepare target environment",
        "description": f"Set up {decision.get('primary_recommendation', {}).get('platform', 'target platform')} infrastructure",
        "timeline": "2-3 weeks"
    })
    
    return actions


def _generate_migration_sequence(graph: Dict) -> list:
    """Generate recommended migration sequence."""
    return [
        {
            "phase": 1,
            "name": "Foundation Components",
            "description": "Migrate leaf nodes with no dependencies first",
            "risk": "Low",
            "duration": "4-6 weeks"
        },
        {
            "phase": 2,
            "name": "Core Business Logic",
            "description": "Migrate central components with validated dependencies",
            "risk": "Medium",
            "duration": "8-12 weeks"
        },
        {
            "phase": 3,
            "name": "Integration Layer",
            "description": "Complete integration and end-to-end testing",
            "risk": "Medium-High",
            "duration": "4-6 weeks"
        }
    ]


def _define_success_criteria(assessment: Dict) -> list:
    """Define success criteria for migration."""
    return [
        "All high-severity risks resolved or mitigated",
        "95%+ functional parity with mainframe system",
        "Response time within 20% of mainframe baseline",
        "Zero data loss during migration",
        "Successful completion of parallel run for 2 weeks",
        f"Achievement of {assessment.get('readiness_rating', 'target')} readiness level"
    ]


def export_to_json(evidence: Dict) -> str:
    """Export evidence package as formatted JSON."""
    return json.dumps(evidence, indent=2)


def generate_executive_summary_html(evidence: Dict) -> str:
    """Generate a concise HTML executive summary."""
    summary = evidence.get("executive_summary", {})
    app = evidence.get("application", {})
    
    html = f"""
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; background: #0A0E17; color: #E5E7EB;">
        <h1 style="color: #58D3A5; margin-bottom: 1rem;">Modernization Assessment: {app.get('name', 'N/A')}</h1>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0;">
            <div style="background: #111827; padding: 1.5rem; border-radius: 0.5rem; border-left: 3px solid #58D3A5;">
                <div style="font-size: 2rem; font-weight: 700; color: #58D3A5;">{summary.get('readiness_score', 0)}/100</div>
                <div style="font-size: 0.875rem; color: #9CA3AF; margin-top: 0.5rem;">Readiness Score</div>
            </div>
            <div style="background: #111827; padding: 1.5rem; border-radius: 0.5rem; border-left: 3px solid #E3B65D;">
                <div style="font-size: 2rem; font-weight: 700; color: #E3B65D;">{summary.get('high_severity_risks', 0)}</div>
                <div style="font-size: 0.875rem; color: #9CA3AF; margin-top: 0.5rem;">Critical Risks</div>
            </div>
            <div style="background: #111827; padding: 1.5rem; border-radius: 0.5rem; border-left: 3px solid #7C3AED;">
                <div style="font-size: 2rem; font-weight: 700; color: #7C3AED;">{summary.get('total_dependencies', 0)}</div>
                <div style="font-size: 0.875rem; color: #9CA3AF; margin-top: 0.5rem;">Dependencies</div>
            </div>
        </div>
        
        <div style="background: #111827; padding: 1.5rem; border-radius: 0.5rem; margin: 2rem 0;">
            <h2 style="color: #E5E7EB; font-size: 1.125rem; margin-bottom: 1rem;">Key Finding</h2>
            <p style="color: #9CA3AF; line-height: 1.6;">{summary.get('key_finding', 'No key finding available')}</p>
        </div>
        
        <div style="background: #111827; padding: 1.5rem; border-radius: 0.5rem;">
            <h2 style="color: #E5E7EB; font-size: 1.125rem; margin-bottom: 1rem;">Recommendation</h2>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: #58D3A5; width: 4px; height: 40px; border-radius: 2px;"></div>
                <div>
                    <div style="font-weight: 600; color: #E5E7EB; margin-bottom: 0.25rem;">{summary.get('primary_recommendation', 'N/A')}</div>
                    <div style="font-size: 0.875rem; color: #9CA3AF;">Target Platform</div>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #374151; font-size: 0.75rem; color: #6B7280; text-align: center;">
            Generated by ModernizeIQ Blast Radius Engine | {evidence.get('generated_at', 'N/A')}
        </div>
    </div>
    """
    
    return html
