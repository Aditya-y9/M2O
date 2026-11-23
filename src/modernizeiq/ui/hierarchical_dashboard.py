"""
Hierarchical Zoomable Dashboard with Multi-Level Drill-Down
App Level → Component Level → Class Level → Function Level
"""
import json
from typing import Dict, List, Any

def generate_hierarchical_graph_data(report_data: Dict) -> Dict:
    """Generate hierarchical graph data with app→component→class→function levels."""
    
    portfolio = report_data.get("portfolio", {})
    programs = portfolio.get("programs", [])
    
    # Build hierarchical structure
    app_node = {
        "id": "app_root",
        "name": portfolio.get("app_name", "Application"),
        "type": "application",
        "level": 0,
        "children": []
    }
    
    # Group programs into components (subsystems)
    component_groups = {}
    for prog in programs:
        component = prog.get("subsystem", "CORE")
        if component not in component_groups:
            component_groups[component] = []
        component_groups[component].append(prog)
    
    # Build component nodes
    for component_name, progs in component_groups.items():
        component_node = {
            "id": f"comp_{component_name}",
            "name": component_name,
            "type": "component",
            "level": 1,
            "program_count": len(progs),
            "children": []
        }
        
        # Add programs as "classes" (3rd level)
        for prog in progs:
            prog_node = {
                "id": prog.get("name", "UNKNOWN"),
                "name": prog.get("name", "UNKNOWN"),
                "type": "program",
                "level": 2,
                "language": prog.get("language", "COBOL"),
                "lines": prog.get("lines_of_code", 0),
                "risk_score": prog.get("complexity_score", 50),
                "children": []
            }
            
            # Add mock functions (4th level) - in real system would parse COBOL
            function_count = max(3, prog.get("lines_of_code", 100) // 100)
            for i in range(min(function_count, 10)):  # Cap at 10 functions
                func_node = {
                    "id": f"{prog.get('name', 'UNKNOWN')}_func_{i}",
                    "name": f"PARAGRAPH-{i+1:02d}",
                    "type": "function",
                    "level": 3,
                    "lines": prog.get("lines_of_code", 100) // function_count
                }
                prog_node["children"].append(func_node)
            
            component_node["children"].append(prog_node)
        
        app_node["children"].append(component_node)
    
    return app_node


def render_hierarchical_dashboard(report_data: Dict) -> str:
    """Render hierarchical zoomable dashboard."""
    
    # Generate hierarchical data
    hierarchy_data = generate_hierarchical_graph_data(report_data)
    hierarchy_json = json.dumps(hierarchy_data).replace("</", "<\\/")
    
    portfolio = report_data.get("portfolio", {})
    app_name = portfolio.get("app_name", "Application")
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModernizeIQ - Hierarchical Explorer - {app_name}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e17;
            color: #e4e8f0;
            overflow: hidden;
        }}
        
        #controls {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(17, 23, 38, 0.95);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #232d3f;
            z-index: 1000;
            min-width: 280px;
        }}
        
        #controls h2 {{
            font-size: 18px;
            margin-bottom: 12px;
            color: #58D3A5;
        }}
        
        #current-level {{
            font-size: 14px;
            margin-bottom: 16px;
            padding: 12px;
            background: #0e1320;
            border-radius: 4px;
            border-left: 3px solid #58D3A5;
        }}
        
        .level-indicator {{
            font-size: 12px;
            opacity: 0.7;
            margin-bottom: 4px;
        }}
        
        .level-name {{
            font-size: 16px;
            font-weight: 600;
        }}
        
        .breadcrumb {{
            font-size: 11px;
            opacity: 0.5;
            margin-top: 4px;
        }}
        
        button {{
            width: 100%;
            padding: 10px;
            margin: 6px 0;
            background: #182033;
            border: 1px solid #232d3f;
            color: #e4e8f0;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}
        
        button:hover {{
            background: #232d3f;
            border-color: #58D3A5;
        }}
        
        button:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        
        #legend {{
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid #232d3f;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 12px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            margin-right: 10px;
        }}
        
        #viz {{
            width: 100vw;
            height: 100vh;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .node:hover {{
            filter: brightness(1.2);
        }}
        
        .node-label {{
            font-size: 11px;
            fill: #e4e8f0;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
        }}
        
        .node-count {{
            font-size: 9px;
            fill: #a0a8b8;
            text-anchor: middle;
            pointer-events: none;
        }}
        
        .link {{
            fill: none;
            stroke: #232d3f;
            stroke-width: 1.5px;
            opacity: 0.6;
        }}
        
        .instructions {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(17, 23, 38, 0.95);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #232d3f;
            font-size: 12px;
            max-width: 300px;
        }}
        
        .instructions strong {{
            color: #58D3A5;
            display: block;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div id="controls">
        <h2>🔍 Hierarchy Explorer</h2>
        <div id="current-level">
            <div class="level-indicator">Current Level:</div>
            <div class="level-name" id="level-name">Application Level</div>
            <div class="breadcrumb" id="breadcrumb">Root</div>
        </div>
        <button id="zoom-in" disabled>🔎 Zoom Into Selected</button>
        <button id="zoom-out" disabled>⬆️ Zoom Out</button>
        <button id="reset-view">🏠 Reset to App Level</button>
        
        <div id="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #58D3A5;"></div>
                <span>Application (Level 0)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4A9EE0;"></div>
                <span>Component (Level 1)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #E3B65D;"></div>
                <span>Program/Class (Level 2)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #E07856;"></div>
                <span>Function (Level 3)</span>
            </div>
        </div>
    </div>
    
    <div class="instructions">
        <strong>How to Navigate:</strong>
        • Click any node to select it<br>
        • Click "Zoom Into Selected" to drill down<br>
        • Click "Zoom Out" to go back up<br>
        • Scroll to zoom, drag to pan
    </div>
    
    <svg id="viz"></svg>
    
    <script>
        // Data
        const hierarchyData = {hierarchy_json};
        
        // State
        let currentRoot = hierarchyData;
        let selectedNode = null;
        let breadcrumb = [hierarchyData];
        
        // Colors by level
        const levelColors = {{
            0: '#58D3A5',  // Application - Green
            1: '#4A9EE0',  // Component - Blue
            2: '#E3B65D',  // Program - Amber
            3: '#E07856'   // Function - Orange
        }};
        
        const levelNames = {{
            0: 'Application Level',
            1: 'Component Level',
            2: 'Program Level',
            3: 'Function Level'
        }};
        
        // Setup
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select('#viz')
            .attr('width', width)
            .attr('height', height);
        
        const g = svg.append('g');
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        // Tree layout
        const tree = d3.tree()
            .size([height - 100, width - 400]);
        
        function update(source) {{
            const root = d3.hierarchy(source);
            const treeData = tree(root);
            
            // Links
            const links = g.selectAll('.link')
                .data(treeData.links(), d => d.target.data.id);
            
            links.exit().remove();
            
            const linkEnter = links.enter()
                .append('path')
                .attr('class', 'link')
                .attr('d', d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));
            
            links.merge(linkEnter)
                .transition()
                .duration(500)
                .attr('d', d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));
            
            // Nodes
            const nodes = g.selectAll('.node')
                .data(treeData.descendants(), d => d.data.id);
            
            nodes.exit().remove();
            
            const nodeEnter = nodes.enter()
                .append('g')
                .attr('class', 'node')
                .attr('transform', d => `translate(${{d.y}},${{d.x}})`)
                .on('click', (event, d) => {{
                    event.stopPropagation();
                    selectNode(d);
                }});
            
            nodeEnter.append('circle')
                .attr('r', d => {{
                    if (d.data.level === 0) return 20;
                    if (d.data.level === 1) return 16;
                    if (d.data.level === 2) return 12;
                    return 8;
                }})
                .attr('fill', d => levelColors[d.data.level] || '#888')
                .attr('stroke', '#0a0e17')
                .attr('stroke-width', 2);
            
            nodeEnter.append('text')
                .attr('class', 'node-label')
                .attr('dy', d => d.data.level === 0 ? -28 : -18)
                .text(d => d.data.name.length > 20 ? d.data.name.substring(0, 17) + '...' : d.data.name);
            
            nodeEnter.append('text')
                .attr('class', 'node-count')
                .attr('dy', d => d.data.level === 0 ? 32 : 24)
                .text(d => {{
                    if (d.data.children && d.data.children.length > 0) {{
                        return `(${{d.data.children.length}} children)`;
                    }}
                    if (d.data.lines) {{
                        return `${{d.data.lines}} lines`;
                    }}
                    return '';
                }});
            
            nodes.merge(nodeEnter)
                .transition()
                .duration(500)
                .attr('transform', d => `translate(${{d.y}},${{d.x}})`);
            
            // Update UI
            updateLevelIndicator();
        }}
        
        function selectNode(node) {{
            selectedNode = node;
            
            // Visual feedback
            g.selectAll('circle')
                .attr('stroke', d => d === node ? '#58D3A5' : '#0a0e17')
                .attr('stroke-width', d => d === node ? 4 : 2);
            
            // Enable/disable zoom in
            const hasChildren = node.data.children && node.data.children.length > 0;
            document.getElementById('zoom-in').disabled = !hasChildren;
        }}
        
        function zoomIn() {{
            if (!selectedNode || !selectedNode.data.children || selectedNode.data.children.length === 0) return;
            
            breadcrumb.push(currentRoot);
            currentRoot = selectedNode.data;
            selectedNode = null;
            
            update(currentRoot);
            document.getElementById('zoom-out').disabled = false;
            document.getElementById('zoom-in').disabled = true;
        }}
        
        function zoomOut() {{
            if (breadcrumb.length === 0) return;
            
            currentRoot = breadcrumb.pop();
            selectedNode = null;
            
            update(currentRoot);
            document.getElementById('zoom-out').disabled = breadcrumb.length === 0;
            document.getElementById('zoom-in').disabled = true;
        }}
        
        function resetView() {{
            currentRoot = hierarchyData;
            breadcrumb = [hierarchyData];
            selectedNode = null;
            
            update(currentRoot);
            document.getElementById('zoom-out').disabled = true;
            document.getElementById('zoom-in').disabled = true;
            
            // Reset zoom
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        function updateLevelIndicator() {{
            const levelName = levelNames[currentRoot.level] || 'Unknown Level';
            document.getElementById('level-name').textContent = levelName;
            
            const path = breadcrumb.map(n => n.name).join(' → ');
            document.getElementById('breadcrumb').textContent = path + (breadcrumb.length > 0 ? ' → ' + currentRoot.name : '');
        }}
        
        // Event listeners
        document.getElementById('zoom-in').addEventListener('click', zoomIn);
        document.getElementById('zoom-out').addEventListener('click', zoomOut);
        document.getElementById('reset-view').addEventListener('click', resetView);
        
        // Initial render
        update(hierarchyData);
        
        // Center initial view
        svg.call(zoom.transform, d3.zoomIdentity.translate(50, height / 2).scale(0.8));
    </script>
</body>
</html>
"""
