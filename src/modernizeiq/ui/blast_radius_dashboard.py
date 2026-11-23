"""
Blast Radius Dashboard - Single-page interactive dependency visualization
Industry-proven patterns: Thoughtworks knowledge graphs + D3.js force layout + ROI focus
"""
import json
from typing import Any, Dict, List
from pathlib import Path
from modernizeiq.ui.evidence_exporter import (
    generate_evidence_package,
    export_to_json,
    generate_executive_summary_html
)


def _safe_get(obj: Any, *keys, default=""):
    """Safely navigate nested dict/object with fallback."""
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            return default
        if current is None:
            return default
    return current


def _escape_html(text: str) -> str:
    """HTML-escape user-controlled strings."""
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def _calculate_roi_metrics(report_data: Dict) -> Dict[str, Any]:
    """Calculate ROI metrics from assessment data."""
    assessment = report_data.get("assessment_report", {})
    portfolio = report_data.get("portfolio", {})
    graph = report_data.get("dependency_graph", {})
    
    # Extract key metrics
    risk_score = _safe_get(assessment, "overall_score", default=0)
    node_count = len(_safe_get(graph, "nodes", default=[]))
    edge_count = len(_safe_get(graph, "edges", default=[]))
    
    # Calculate complexity factor (edges per node)
    complexity = round(edge_count / node_count, 1) if node_count > 0 else 0
    
    # Estimate effort (person-days) based on complexity and risk
    # Industry baseline: 1-2 days per program for low coupling, 3-5 for high
    base_effort_per_node = 2.0
    complexity_multiplier = 1.0 + (complexity * 0.2)  # +20% per dependency
    risk_multiplier = 1.0 + ((100 - risk_score) / 100)  # Higher risk = more effort
    
    effort_days = int(node_count * base_effort_per_node * complexity_multiplier * risk_multiplier)
    
    # Estimate annual savings (mainframe MIPS cost)
    # Industry avg: $3,000-$5,000 per MIPS/year, typical app = 50-200 MIPS
    mips_estimate = node_count * 5  # Conservative: 5 MIPS per program
    cost_per_mips = 4000  # Mid-range
    mainframe_annual_cost = mips_estimate * cost_per_mips
    
    # Cloud cost = ~30-40% of mainframe (industry benchmark)
    cloud_annual_cost = int(mainframe_annual_cost * 0.35)
    annual_savings = mainframe_annual_cost - cloud_annual_cost
    
    # Payback period (months)
    # Assume $800/day blended rate for modernization team
    modernization_cost = effort_days * 800
    payback_months = int((modernization_cost / annual_savings) * 12) if annual_savings > 0 else 999
    
    return {
        "risk_score": int(risk_score),
        "effort_days": effort_days,
        "annual_savings": annual_savings,
        "mainframe_annual_cost": mainframe_annual_cost,
        "cloud_annual_cost": cloud_annual_cost,
        "modernization_cost": modernization_cost,
        "payback_months": payback_months,
        "complexity_factor": complexity,
        "node_count": node_count,
        "edge_count": edge_count
    }


def _build_graph_data(report_data: Dict) -> Dict:
    """Build D3.js-compatible graph data with risk scoring per node."""
    graph = report_data.get("dependency_graph", {})
    nodes = _safe_get(graph, "nodes", default=[])
    edges = _safe_get(graph, "edges", default=[])
    
    # Calculate risk per node based on in-degree + out-degree
    node_risk = {}
    in_degree = {}
    out_degree = {}
    
    for edge in edges:
        source = _safe_get(edge, "source", default="")
        target = _safe_get(edge, "target", default="")
        if source:
            out_degree[source] = out_degree.get(source, 0) + 1
        if target:
            in_degree[target] = in_degree.get(target, 0) + 1
    
    # Risk = high coupling (many deps) + being depended on (blast radius)
    for node in nodes:
        node_id = _safe_get(node, "id", default="")
        in_deg = in_degree.get(node_id, 0)
        out_deg = out_degree.get(node_id, 0)
        
        # Risk score: in-degree weighted 2x (breaking this breaks others)
        risk = (in_deg * 2) + out_deg
        node_risk[node_id] = risk
    
    # Normalize risk to 0-100 scale
    max_risk = max(node_risk.values()) if node_risk else 1
    for node_id in node_risk:
        node_risk[node_id] = int((node_risk[node_id] / max_risk) * 100)
    
    # Build D3 nodes with risk metadata
    d3_nodes = []
    for node in nodes:
        node_id = _safe_get(node, "id", default="")
        node_type = _safe_get(node, "type", default="program")
        node_name = _safe_get(node, "name", default=node_id)
        
        risk = node_risk.get(node_id, 0)
        
        # Determine color based on risk
        if risk < 30:
            color = "#58D3A5"  # Green (low risk)
        elif risk < 70:
            color = "#E3B65D"  # Amber (medium risk)
        else:
            color = "#EF4444"  # Red (high risk)
        
        d3_nodes.append({
            "id": node_id,
            "name": node_name,
            "type": node_type,
            "risk": risk,
            "color": color,
            "in_degree": in_degree.get(node_id, 0),
            "out_degree": out_degree.get(node_id, 0)
        })
    
    # Build D3 edges
    d3_edges = []
    for edge in edges:
        source = _safe_get(edge, "source", default="")
        target = _safe_get(edge, "target", default="")
        edge_type = _safe_get(edge, "type", default="calls")
        
        if source and target:
            d3_edges.append({
                "source": source,
                "target": target,
                "type": edge_type
            })
    
    return {
        "nodes": d3_nodes,
        "links": d3_edges
    }


def render_blast_radius_dashboard(report_data: Dict) -> str:
    """Render single-page interactive blast radius dashboard."""
    
    # Extract core data
    portfolio = report_data.get("portfolio", {})
    app_name = _safe_get(portfolio, "app_name", default="Application Modernization")
    app_id = _safe_get(portfolio, "app_id", default="APP-001")
    
    # Calculate ROI metrics
    roi = _calculate_roi_metrics(report_data)
    
    # Build graph data
    graph_data = _build_graph_data(report_data)
    
    # Extract top risks
    assessment = report_data.get("assessment_report", {})
    risks = _safe_get(assessment, "risks", default=[])
    top_risks = sorted(risks, key=lambda r: r.get("severity", "low") == "high", reverse=True)[:3]
    
    # Decision context
    decision = report_data.get("platform_decision", {})
    recommendation = _safe_get(decision, "primary_recommendation", default={})
    platform = _safe_get(recommendation, "platform", default="To Be Determined")
    rationale = _safe_get(recommendation, "rationale", default="")
    
    # Escape all user-controlled strings
    app_name_safe = _escape_html(app_name)
    app_id_safe = _escape_html(app_id)
    platform_safe = _escape_html(platform)
    rationale_safe = _escape_html(rationale)
    
    # Build risk cards HTML
    risk_cards_html = ""
    for i, risk in enumerate(top_risks):
        severity = _safe_get(risk, "severity", default="medium")
        title = _escape_html(_safe_get(risk, "title", default="Risk Item"))
        description = _escape_html(_safe_get(risk, "description", default=""))
        mitigation = _escape_html(_safe_get(risk, "mitigation_strategy", default=""))
        
        severity_color = {
            "high": "#EF4444",
            "medium": "#E3B65D",
            "low": "#58D3A5"
        }.get(severity, "#6B7280")
        
        risk_cards_html += f"""
        <div class="risk-card" style="border-left: 4px solid {severity_color};">
            <div class="risk-header">
                <span class="risk-number">{i+1}</span>
                <span class="risk-title">{title}</span>
                <span class="risk-severity" style="color: {severity_color};">{severity.upper()}</span>
            </div>
            <div class="risk-description">{description}</div>
            <div class="risk-mitigation"><strong>Mitigation:</strong> {mitigation}</div>
        </div>
        """
    
    # Serialize graph data for JavaScript
    graph_json = json.dumps(graph_data).replace("</", "<\\/")  # Escape closing tags
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModernizeIQ: Blast Radius Engine - {app_name_safe}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0A0E17;
            color: #E5E7EB;
            overflow: hidden;
        }}
        
        .header {{
            background: #111827;
            border-bottom: 1px solid #1F2937;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 1.25rem;
            font-weight: 600;
            color: #58D3A5;
        }}
        
        .header-meta {{
            display: flex;
            gap: 2rem;
            font-size: 0.875rem;
            color: #9CA3AF;
        }}
        
        .container {{
            display: grid;
            grid-template-columns: 1fr 400px;
            height: calc(100vh - 60px);
        }}
        
        .graph-panel {{
            background: #0F1419;
            border-right: 1px solid #1F2937;
            position: relative;
        }}
        
        .graph-controls {{
            position: absolute;
            top: 1rem;
            left: 1rem;
            z-index: 10;
            display: flex;
            gap: 0.5rem;
        }}
        
        .search-box {{
            background: #111827;
            border: 1px solid #374151;
            border-radius: 0.375rem;
            padding: 0.5rem 1rem;
            color: #E5E7EB;
            font-size: 0.875rem;
            width: 300px;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #58D3A5;
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
        }}
        
        .inspector-panel {{
            background: #111827;
            overflow-y: auto;
            padding: 1.5rem;
        }}
        
        .roi-metrics {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        
        .metric-card {{
            background: #1F2937;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.875rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        
        .metric-label {{
            font-size: 0.75rem;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-risk {{ color: #E3B65D; }}
        .metric-effort {{ color: #58D3A5; }}
        .metric-savings {{ color: #60A5FA; }}
        
        .section {{
            margin-bottom: 1.5rem;
        }}
        
        .section-title {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #9CA3AF;
            margin-bottom: 0.75rem;
        }}
        
        .node-info {{
            background: #1F2937;
            border-radius: 0.5rem;
            padding: 1rem;
        }}
        
        .node-name {{
            font-size: 1.125rem;
            font-weight: 600;
            color: #58D3A5;
            margin-bottom: 0.5rem;
        }}
        
        .node-meta {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            margin-top: 0.75rem;
            font-size: 0.875rem;
        }}
        
        .node-stat {{
            color: #9CA3AF;
        }}
        
        .node-stat strong {{
            color: #E5E7EB;
        }}
        
        .risk-card {{
            background: #1F2937;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .risk-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .risk-number {{
            background: #374151;
            color: #E5E7EB;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .risk-title {{
            flex: 1;
            font-weight: 600;
            font-size: 0.875rem;
        }}
        
        .risk-severity {{
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .risk-description {{
            font-size: 0.875rem;
            color: #9CA3AF;
            margin-bottom: 0.5rem;
        }}
        
        .risk-mitigation {{
            font-size: 0.8125rem;
            color: #D1D5DB;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 0.75rem;
            margin-top: 1.5rem;
        }}
        
        .btn {{
            flex: 1;
            padding: 0.75rem 1rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: #58D3A5;
            color: #0A0E17;
        }}
        
        .btn-primary:hover {{
            background: #4BC090;
        }}
        
        .btn-secondary {{
            background: #374151;
            color: #E5E7EB;
        }}
        
        .btn-secondary:hover {{
            background: #4B5563;
        }}
        
        .legend {{
            position: absolute;
            bottom: 1rem;
            left: 1rem;
            background: #111827;
            border: 1px solid #374151;
            border-radius: 0.5rem;
            padding: 0.75rem;
            font-size: 0.8125rem;
        }}
        
        .legend-title {{
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #9CA3AF;
        }}
        
        .legend-items {{
            display: flex;
            gap: 1rem;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }}
        
        .legend-color {{
            width: 0.75rem;
            height: 0.75rem;
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 ModernizeIQ: Blast Radius Engine</h1>
        <div class="header-meta">
            <span><strong>{app_name_safe}</strong></span>
            <span>ID: {app_id_safe}</span>
        </div>
    </div>
    
    <div class="container">
        <div class="graph-panel">
            <div class="graph-controls">
                <input type="text" id="search" class="search-box" placeholder="Search programs, copybooks, tables...">
            </div>
            <svg id="graph"></svg>
            <div class="legend">
                <div class="legend-title">RISK LEVEL</div>
                <div class="legend-items">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #58D3A5;"></div>
                        <span>Low (&lt;30)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #E3B65D;"></div>
                        <span>Medium (30-70)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #EF4444;"></div>
                        <span>High (&gt;70)</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="inspector-panel">
            <div class="roi-metrics">
                <div class="metric-card">
                    <div class="metric-value metric-risk">{roi['risk_score']}/100</div>
                    <div class="metric-label">Risk Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value metric-effort">{roi['effort_days']}d</div>
                    <div class="metric-label">Effort Est.</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value metric-savings">${roi['annual_savings']//1000}K</div>
                    <div class="metric-label">Annual Savings</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Selected Node</div>
                <div id="node-inspector" class="node-info">
                    <div style="color: #9CA3AF; text-align: center; padding: 2rem;">
                        Click any node to inspect its blast radius
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Top Blocking Risks</div>
                {risk_cards_html if risk_cards_html else '<div style="color: #9CA3AF; font-size: 0.875rem;">No high-severity risks identified</div>'}
            </div>
            
            <div class="section">
                <div class="section-title">Recommendation</div>
                <div class="node-info">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">{platform_safe}</div>
                    <div style="font-size: 0.875rem; color: #9CA3AF;">{rationale_safe}</div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="exportEvidence()">📊 Export Evidence</button>
                <button class="btn btn-secondary" onclick="generatePlan()">🚀 Migration Plan</button>
            </div>
        </div>
    </div>
    
    <script>
        // Graph data from Python
        const graphData = {graph_json};
        
        // D3.js force-directed graph (minimal inline implementation)
        const svg = document.getElementById('graph');
        const width = svg.clientWidth || 800;
        const height = svg.clientHeight || 600;
        
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        
        // Simple force simulation
        let nodes = graphData.nodes.map(n => ({{
            ...n,
            x: Math.random() * width,
            y: Math.random() * height,
            vx: 0,
            vy: 0
        }}));
        
        const links = graphData.links.map(l => ({{
            source: nodes.find(n => n.id === l.source),
            target: nodes.find(n => n.id === l.target),
            type: l.type
        }})).filter(l => l.source && l.target);
        
        // Draw links
        const linkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        svg.appendChild(linkGroup);
        
        links.forEach(link => {{
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('stroke', '#374151');
            line.setAttribute('stroke-width', '1');
            line.setAttribute('stroke-opacity', '0.6');
            link.element = line;
            linkGroup.appendChild(line);
        }});
        
        // Draw nodes
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        svg.appendChild(nodeGroup);
        
        nodes.forEach(node => {{
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', '8');
            circle.setAttribute('fill', node.color);
            circle.setAttribute('stroke', '#1F2937');
            circle.setAttribute('stroke-width', '2');
            circle.setAttribute('cursor', 'pointer');
            circle.style.transition = 'all 0.2s';
            
            circle.addEventListener('click', () => selectNode(node));
            circle.addEventListener('mouseenter', () => {{
                circle.setAttribute('r', '12');
                circle.setAttribute('stroke', '#58D3A5');
            }});
            circle.addEventListener('mouseleave', () => {{
                circle.setAttribute('r', '8');
                circle.setAttribute('stroke', '#1F2937');
            }});
            
            node.element = circle;
            nodeGroup.appendChild(circle);
            
            // Label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('fill', '#9CA3AF');
            text.setAttribute('font-size', '10');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('pointer-events', 'none');
            text.textContent = node.name.length > 12 ? node.name.substring(0, 12) + '...' : node.name;
            node.label = text;
            nodeGroup.appendChild(text);
        }});
        
        // Simple force simulation (60 iterations)
        function simulate() {{
            const iterations = 60;
            const linkDistance = 100;
            const repulsion = 2000;
            const damping = 0.5;
            
            for (let i = 0; i < iterations; i++) {{
                // Link forces
                links.forEach(link => {{
                    const dx = link.target.x - link.source.x;
                    const dy = link.target.y - link.source.y;
                    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    const force = (dist - linkDistance) * 0.1;
                    
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    
                    link.source.vx += fx;
                    link.source.vy += fy;
                    link.target.vx -= fx;
                    link.target.vy -= fy;
                }});
                
                // Repulsion forces
                for (let j = 0; j < nodes.length; j++) {{
                    for (let k = j + 1; k < nodes.length; k++) {{
                        const dx = nodes[k].x - nodes[j].x;
                        const dy = nodes[k].y - nodes[j].y;
                        const distSq = dx * dx + dy * dy || 1;
                        const force = repulsion / distSq;
                        
                        const fx = (dx / Math.sqrt(distSq)) * force;
                        const fy = (dy / Math.sqrt(distSq)) * force;
                        
                        nodes[j].vx -= fx;
                        nodes[j].vy -= fy;
                        nodes[k].vx += fx;
                        nodes[k].vy += fy;
                    }}
                }}
                
                // Update positions
                nodes.forEach(node => {{
                    node.vx *= damping;
                    node.vy *= damping;
                    node.x += node.vx;
                    node.y += node.vy;
                    
                    // Bounds
                    const margin = 50;
                    node.x = Math.max(margin, Math.min(width - margin, node.x));
                    node.y = Math.max(margin, Math.min(height - margin, node.y));
                }});
            }}
            
            updatePositions();
        }}
        
        function updatePositions() {{
            links.forEach(link => {{
                link.element.setAttribute('x1', link.source.x);
                link.element.setAttribute('y1', link.source.y);
                link.element.setAttribute('x2', link.target.x);
                link.element.setAttribute('y2', link.target.y);
            }});
            
            nodes.forEach(node => {{
                node.element.setAttribute('cx', node.x);
                node.element.setAttribute('cy', node.y);
                node.label.setAttribute('x', node.x);
                node.label.setAttribute('y', node.y + 20);
            }});
        }}
        
        // Node selection
        let selectedNode = null;
        
        function selectNode(node) {{
            selectedNode = node;
            
            // Reset all nodes
            nodes.forEach(n => {{
                n.element.setAttribute('opacity', '0.3');
            }});
            links.forEach(l => {{
                l.element.setAttribute('opacity', '0.1');
            }});
            
            // Highlight selected and connected
            node.element.setAttribute('opacity', '1');
            
            const connectedIds = new Set([node.id]);
            links.forEach(link => {{
                if (link.source.id === node.id || link.target.id === node.id) {{
                    link.element.setAttribute('opacity', '0.8');
                    link.element.setAttribute('stroke-width', '2');
                    connectedIds.add(link.source.id);
                    connectedIds.add(link.target.id);
                }}
            }});
            
            nodes.forEach(n => {{
                if (connectedIds.has(n.id)) {{
                    n.element.setAttribute('opacity', '1');
                }}
            }});
            
            // Update inspector
            updateInspector(node, connectedIds.size - 1);
        }}
        
        function updateInspector(node, blastRadius) {{
            const inspector = document.getElementById('node-inspector');
            inspector.innerHTML = `
                <div class="node-name">${{escapeHtml(node.name)}}</div>
                <div style="font-size: 0.875rem; color: #9CA3AF; margin-bottom: 0.75rem;">
                    ${{node.type.toUpperCase()}}
                </div>
                <div class="node-meta">
                    <div class="node-stat"><strong>${{node.risk}}</strong> Risk Score</div>
                    <div class="node-stat"><strong>${{blastRadius}}</strong> Blast Radius</div>
                    <div class="node-stat"><strong>${{node.in_degree}}</strong> Dependents</div>
                    <div class="node-stat"><strong>${{node.out_degree}}</strong> Dependencies</div>
                </div>
            `;
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Search
        document.getElementById('search').addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            
            nodes.forEach(node => {{
                const match = node.name.toLowerCase().includes(query) || node.id.toLowerCase().includes(query);
                node.element.setAttribute('opacity', match || !query ? '1' : '0.2');
            }});
        }});
        
        // Actions
        function exportEvidence() {{
            alert('Evidence export functionality - generates PDF with risk analysis, dependencies, and ROI metrics for executive review and audit compliance.');
        }}
        
        function generatePlan() {{
            alert('Migration plan generator - creates phased implementation roadmap with team assignments, risk mitigation steps, and rollback procedures.');
        }}
        
        // Initialize
        simulate();
    </script>
</body>
</html>
"""
    
    return html
