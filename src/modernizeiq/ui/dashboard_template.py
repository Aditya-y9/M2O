"""
Dashboard HTML template generation for ModernizeIQ reports.
Routes to enhanced AI-powered dashboard with breakthrough features.
"""
try:
    from modernizeiq.ui.enhanced_dashboard import render_enhanced_dashboard
    USE_ENHANCED = True
except ImportError:
    from modernizeiq.ui.blast_radius_dashboard import render_blast_radius_dashboard
    USE_ENHANCED = False


def generate_dashboard_html(report_data: dict) -> str:
    """
    Generate interactive HTML dashboard from assessment report data.
    
    Uses enhanced AI-powered dashboard if available, falls back to basic blast radius.
    
    Args:
        report_data: Dictionary containing:
            - portfolio: ApplicationPortfolio data
            - dependency_graph: DependencyGraphData with nodes/edges
            - assessment_report: Risk and readiness analysis
            - platform_decision: Modernization recommendations
    
    Returns:
        Complete HTML string for the dashboard with AI features:
        - Natural Language Q&A with semantic search
        - What-If Scenario Simulator with drag-and-drop
        - Real-time risk/ROI recalculation
        - Automated migration plan generation
    """
    if USE_ENHANCED:
        return render_enhanced_dashboard(report_data)
    else:
        return render_blast_radius_dashboard(report_data)
