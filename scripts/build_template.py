"""Builder script to generate deslopped dashboard_template.py."""
import sys
from pathlib import Path

template_code = '''"""Self-Contained Interactive HTML5 Visual Modernization Dashboard Template.

Generates a modern, responsive, high-density dark-mode single-page visual dashboard with
interactive topology graphs, semantic cluster scatter maps, 12-factor audits,
and VM vs OCP comparison matrices following Swiss Utilitarian console design.
"""

import json
from typing import Dict, Any


def render_html_dashboard(report_data: Dict[str, Any]) -> str:
    """Renders report dictionary into a self-contained, deslopped HTML5 dashboard."""
    report_json_str = json.dumps(report_data, default=str).replace("</script>", "<\\\\/script>")

    pf = report_data.get("portfolio", {})
    decision = report_data.get("decision", {})
    assessment = report_data.get("assessment", {})
    graph_data = report_data.get("dependency_graph", {})
    clusters = report_data.get("semantic_clusters", [])
    coords = report_data.get("semantic_coords", {})

    app_name = pf.get("app_name", "Application Modernization")
    app_id = pf.get("app_id", "APP-001")
    domain = pf.get("domain", "Enterprise")
    criticality = pf.get("business_criticality", "HIGH")
    
    primary_platform = decision.get("primary_platform", "Red Hat OpenShift (OCP)")
    secondary_platform = decision.get("secondary_platform", "Linux Virtual Machine (VM)")
    recommended_disposition = decision.get("recommended_disposition", "Refactor / Containerize")
    ocp_score = decision.get("ocp_score", 0.0)
    vm_score = decision.get("vm_score", 0.0)
    decision_summary = decision.get("decision_summary", "")
    
    overall_score = assessment.get("overall_normalized_score", 0.0)
    readiness_rating = assessment.get("overall_readiness_rating", "MODERATE")
    person_days = assessment.get("total_estimated_person_days", 0.0)
    avg_factor_score = assessment.get("average_factor_score", 0.0)

    programs = pf.get("programs", [])
    total_loc = sum(p.get("lines_of_code", 0) for p in programs)
    datasets = pf.get("datasets", [])
    cics_txns = pf.get("cics_transactions", [])
    db2_tables = pf.get("db2_tables", [])
    
    nodes = graph_data.get("nodes", [])
    links = graph_data.get("links", [])
    graph_metrics = graph_data.get("metrics", {})
    circular_deps = graph_metrics.get("circular_dependencies", 0)
    graph_density = graph_metrics.get("density", 0.0)

    risks = assessment.get("risks", [])
    blockers = [r for r in risks if str(r.get("severity", "")).upper() == "CRITICAL" or "blocker" in str(r.get("title", "")).lower()]
    blocker_count = len(blockers)

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModernizeIQ // {app_name} ({app_id}) Modernization Assessment</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
                    }},
                    colors: {{
                        obsidian: '#0A0E17',
                        surface: '#111726',
                        subsurface: '#182032',
                        borderHairline: '#232D3F',
                        borderSubtle: '#1B2436',
                        textPrimary: '#F1F5F9',
                        textMuted: '#94A3B8',
                        textDim: '#64748B',
                        ocpMint: '#10B981',
                        vmAmber: '#D97706',
                        blockerRed: '#EF4444',
                        infoSky: '#38BDF8'
                    }}
                }}
            }}
        }};
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
        
        * {{
            box-sizing: border-box;
            border-color: #232D3F;
        }}
        body {{
            background-color: #0A0E17;
            color: #F1F5F9;
            font-family: 'IBM Plex Sans', -apple-system, sans-serif;
            font-feature-settings: "cv02", "cv03", "cv04", "cv11";
            -webkit-font-smoothing: antialiased;
        }}
        .font-mono {{
            font-family: 'IBM Plex Mono', monospace;
            font-variant-numeric: tabular-nums;
        }}
        .tabular-nums {{
            font-variant-numeric: tabular-nums;
        }}
        /* Clean scrollbars */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: #0A0E17;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #232D3F;
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #334155;
        }}
        .hairline-border {{
            border: 1px solid #232D3F;
        }}
        .active-tab {{
            border-bottom: 2px solid #10B981;
            color: #F1F5F9;
            background-color: #182032;
        }}
        .inactive-tab {{
            border-bottom: 2px solid transparent;
            color: #94A3B8;
        }}
        .inactive-tab:hover {{
            color: #F1F5F9;
            background-color: #111726;
        }}
    </style>
</head>
<body class="min-h-screen bg-obsidian text-textPrimary antialiased selection:bg-ocpMint/20 selection:text-white">

    <!-- TOP SYSTEM STATUS & NAVIGATION -->
    <header class="sticky top-0 z-50 bg-surface/95 backdrop-blur border-b border-borderHairline">
        <div class="max-w-[1720px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="flex items-center gap-2">
                    <span class="w-3 h-3 bg-ocpMint rounded-sm inline-block"></span>
                    <span class="font-bold text-lg tracking-wider font-mono text-white">MODERNIZE<span class="text-ocpMint">IQ</span></span>
                </div>
                <span class="text-xs text-borderHairline font-mono">|</span>
                <span class="text-xs font-mono px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline uppercase tracking-wide">Enterprise Architect Workbench</span>
                <span class="text-xs text-borderHairline font-mono hidden sm:inline">|</span>
                <div class="hidden sm:flex items-center gap-2 text-xs font-mono text-textMuted">
                    <span class="text-textPrimary font-semibold">{app_name}</span>
                    <span class="text-textDim">[{app_id}]</span>
                    <span class="px-1.5 py-0.2 text-[10px] bg-subsurface rounded border border-borderHairline text-infoSky">{domain}</span>
                    <span class="px-1.5 py-0.2 text-[10px] bg-subsurface rounded border border-borderHairline text-amber-400">CRITICALITY: {criticality}</span>
                </div>
            </div>

            <!-- Global Action Controls -->
            <div class="flex items-center gap-2 text-xs font-mono">
                <button onclick="copyAdrMarkdown()" class="px-2.5 py-1.5 rounded bg-subsurface hover:bg-slate-700/60 border border-borderHairline text-textMuted hover:text-white transition-colors flex items-center gap-1.5" title="Copy Architecture Decision Record in Markdown">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                    <span>Copy ADR.md</span>
                </button>
                <button onclick="downloadJsonDossier()" class="px-2.5 py-1.5 rounded bg-subsurface hover:bg-slate-700/60 border border-borderHairline text-textMuted hover:text-white transition-colors flex items-center gap-1.5" title="Export Full Assessment JSON">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                    <span>Export JSON</span>
                </button>
                <button onclick="window.print()" class="px-2.5 py-1.5 rounded bg-subsurface hover:bg-slate-700/60 border border-borderHairline text-textMuted hover:text-white transition-colors flex items-center gap-1.5" title="Print Executive Dossier">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4H7v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
                    <span>Print Dossier</span>
                </button>
            </div>
        </div>
    </header>

    <main class="max-w-[1720px] mx-auto px-4 sm:px-6 py-6 space-y-6">

        <!-- ZONE 1: ARCHITECTURAL DECISION COMMAND CENTER -->
        <section class="grid grid-cols-1 lg:grid-cols-12 gap-4">
            
            <!-- Platform Target Recommendation Hero Banner (8 Cols) -->
            <div class="lg:col-span-8 bg-surface rounded-md border border-borderHairline p-5 flex flex-col justify-between">
                <div class="space-y-3">
                    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-borderHairline pb-3">
                        <div class="flex items-center gap-2">
                            <span class="text-[11px] font-mono uppercase tracking-wider text-textDim">Target Architectural Recommendation</span>
                            <span class="w-1.5 h-1.5 rounded-full bg-ocpMint"></span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-mono px-2 py-0.5 rounded border {'border-emerald-500/30 bg-emerald-500/10 text-ocpMint' if 'OpenShift' in primary_platform else 'border-amber-500/30 bg-amber-500/10 text-vmAmber'} font-semibold uppercase">
                                {recommended_disposition}
                            </span>
                            <span class="text-xs font-mono px-2 py-0.5 rounded {'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' if blocker_count == 0 else 'border-rose-500/30 bg-rose-500/10 text-blockerRed'} border">
                                {blocker_count} Hard Blockers
                            </span>
                        </div>
                    </div>

                    <div class="flex flex-col md:flex-row md:items-baseline justify-between gap-2 pt-1">
                        <div>
                            <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-2">
                                {primary_platform}
                            </h1>
                            <p class="text-xs text-textMuted mt-1 max-w-2xl font-normal leading-relaxed">
                                {decision_summary}
                            </p>
                        </div>
                        <div class="text-right flex md:flex-col items-baseline md:items-end justify-between md:justify-center border-t md:border-t-0 border-borderHairline pt-2 md:pt-0">
                            <span class="text-[11px] font-mono text-textDim">Remediation Effort</span>
                            <span class="text-xl sm:text-2xl font-bold font-mono text-white tabular-nums">{person_days:.0f} <span class="text-xs font-normal text-textMuted">Person-Days</span></span>
                        </div>
                    </div>
                </div>

                <!-- Comparative Target Score Bar -->
                <div class="mt-4 pt-3 border-t border-borderHairline grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                    <div class="space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-textMuted flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-sm bg-ocpMint"></span>
                                Red Hat OpenShift (OCP) Containerization
                            </span>
                            <span class="font-bold text-white tabular-nums">{ocp_score:.1f}%</span>
                        </div>
                        <div class="w-full h-2 bg-subsurface rounded-sm overflow-hidden border border-borderHairline">
                            <div class="h-full bg-ocpMint rounded-sm transition-all duration-500" style="width: {min(100, max(0, ocp_score))}%;"></div>
                        </div>
                        <p class="text-[11px] text-textDim">Microservices, stateless horizontal autoscaling, declarative GitOps.</p>
                    </div>

                    <div class="space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-textMuted flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-sm bg-vmAmber"></span>
                                Linux Virtual Machine (VM) Rehosting
                            </span>
                            <span class="font-bold text-white tabular-nums">{vm_score:.1f}%</span>
                        </div>
                        <div class="w-full h-2 bg-subsurface rounded-sm overflow-hidden border border-borderHairline">
                            <div class="h-full bg-vmAmber rounded-sm transition-all duration-500" style="width: {min(100, max(0, vm_score))}%;"></div>
                        </div>
                        <p class="text-[11px] text-textDim">Direct lift-and-shift with emulated runtimes, preserving legacy state.</p>
                    </div>
                </div>
            </div>

            <!-- Key Architectural Telemetry KPIs (4 Cols) -->
            <div class="lg:col-span-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-2 gap-2.5">
                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">Programs / LOC</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono text-white tabular-nums">{len(programs)}</div>
                        <span class="text-[10px] font-mono text-textMuted">{total_loc:,} lines</span>
                    </div>
                </div>

                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">Data Structures</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono text-white tabular-nums">{len(datasets)}</div>
                        <span class="text-[10px] font-mono text-textMuted">{len([d for d in datasets if d.get('dataset_type')=='VSAM'])} VSAM / {len(db2_tables)} DB2</span>
                    </div>
                </div>

                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">Online Txns</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono text-white tabular-nums">{len(cics_txns)}</div>
                        <span class="text-[10px] font-mono text-textMuted">CICS Transactions</span>
                    </div>
                </div>

                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">12-Factor Score</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono text-infoSky tabular-nums">{avg_factor_score*10:.1f}%</div>
                        <span class="text-[10px] font-mono text-textMuted">Cloud Native Compliance</span>
                    </div>
                </div>

                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">Graph Density</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono text-white tabular-nums">{graph_density:.3f}</div>
                        <span class="text-[10px] font-mono text-textMuted">{len(links)} linkages / {len(nodes)} nodes</span>
                    </div>
                </div>

                <div class="bg-surface p-3 rounded-md border border-borderHairline flex flex-col justify-between">
                    <span class="text-[11px] font-mono text-textDim uppercase tracking-wider">Circular Paths</span>
                    <div class="mt-2">
                        <div class="text-xl font-bold font-mono {'text-blockerRed' if circular_deps > 0 else 'text-ocpMint'} tabular-nums">{circular_deps}</div>
                        <span class="text-[10px] font-mono text-textMuted">{'Refactoring Blockers' if circular_deps > 0 else 'Clean Directed DAG'}</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- ZONE 2: 3-MODE ARCHITECTURAL WORKBENCH -->
        <section class="space-y-4">
            
            <!-- Mode Switcher Tabs -->
            <div class="flex items-center justify-between border-b border-borderHairline bg-surface/50 rounded-t-md px-2 pt-2">
                <nav class="flex space-x-1" aria-label="Workbench Modes">
                    <button id="tab-btn-topology" onclick="switchWorkbenchMode('topology')" class="active-tab px-4 py-2.5 text-xs font-mono font-medium rounded-t transition-all flex items-center gap-2">
                        <span class="text-textDim">01 //</span>
                        <span>Dependency Topology &amp; Blast Radius</span>
                        <span class="ml-1 text-[10px] px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-textMuted tabular-nums">{len(nodes)} nodes</span>
                    </button>
                    <button id="tab-btn-domains" onclick="switchWorkbenchMode('domains')" class="inactive-tab px-4 py-2.5 text-xs font-mono font-medium rounded-t transition-all flex items-center gap-2">
                        <span class="text-textDim">02 //</span>
                        <span>Semantic Domain Decomposition</span>
                        <span class="ml-1 text-[10px] px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-textMuted tabular-nums">{len(clusters)} services</span>
                    </button>
                    <button id="tab-btn-audit" onclick="switchWorkbenchMode('audit')" class="inactive-tab px-4 py-2.5 text-xs font-mono font-medium rounded-t transition-all flex items-center gap-2">
                        <span class="text-textDim">03 //</span>
                        <span>Technical Audit &amp; Decision Record</span>
                        <span class="ml-1 text-[10px] px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-textMuted tabular-nums">8 Dimensions &bull; ADR</span>
                    </button>
                </nav>

                <div class="hidden sm:flex items-center gap-3 pr-3 text-xs font-mono text-textDim">
                    <span>Target: <span class="text-textPrimary">{primary_platform}</span></span>
                    <span>&bull;</span>
                    <span>Readiness: <span class="{'text-emerald-400' if 'HIGH' in readiness_rating else 'text-amber-400'}">{readiness_rating}</span></span>
                </div>
            </div>

            <!-- MODE 1: DEPENDENCY TOPOLOGY & BLAST RADIUS -->
            <div id="mode-topology" class="space-y-4">
                <div class="grid grid-cols-1 xl:grid-cols-12 gap-4">
                    
                    <!-- Graph Canvas Area (8 Cols) -->
                    <div class="xl:col-span-8 bg-surface rounded-md border border-borderHairline flex flex-col h-[650px] relative overflow-hidden">
                        
                        <!-- Toolbar -->
                        <div class="px-4 py-2.5 border-b border-borderHairline bg-surface flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                            <div class="flex items-center gap-2">
                                <span class="text-textDim">FILTER:</span>
                                <button onclick="filterTopology('ALL')" class="topo-filter-btn px-2 py-0.5 rounded bg-subsurface text-white border border-borderHairline hover:bg-slate-700">ALL ({len(nodes)})</button>
                                <button onclick="filterTopology('PROGRAM')" class="topo-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:bg-slate-700">PROGRAMS</button>
                                <button onclick="filterTopology('DATASET')" class="topo-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:bg-slate-700">DATASETS</button>
                                <button onclick="filterTopology('CICS_TRANSACTION')" class="topo-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:bg-slate-700">CICS TXNS</button>
                                <button onclick="filterTopology('CIRCULAR')" class="topo-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:bg-slate-700 {'text-blockerRed font-semibold' if circular_deps > 0 else ''}">CIRCULAR ONLY</button>
                            </div>

                            <div class="flex items-center gap-2">
                                <input type="text" id="topoSearch" placeholder="Search node ID..." oninput="searchTopology(this.value)" class="bg-obsidian border border-borderHairline text-white text-xs px-2 py-1 rounded w-40 focus:outline-none focus:border-infoSky font-mono" />
                                <button onclick="resetTopologyZoom()" class="p-1 rounded bg-subsurface border border-borderHairline text-textMuted hover:text-white" title="Reset Graph View">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/></svg>
                                </button>
                            </div>
                        </div>

                        <!-- Graph Canvas -->
                        <div class="relative flex-1 bg-obsidian overflow-hidden" id="graphContainer">
                            <svg id="dependencySvg" class="w-full h-full cursor-grab active:cursor-grabbing select-none"></svg>
                            
                            <!-- Graph Legend Inset -->
                            <div class="absolute bottom-3 left-3 bg-surface/90 backdrop-blur p-2.5 rounded border border-borderHairline text-[11px] font-mono space-y-1.5 shadow-lg">
                                <div class="text-textDim text-[10px] uppercase font-semibold">Legend</div>
                                <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-infoSky inline-block"></span><span class="text-textMuted">COBOL Program</span></div>
                                <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-sm bg-ocpMint inline-block"></span><span class="text-textMuted">Dataset (VSAM/SEQ)</span></div>
                                <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-sm bg-amber-400 inline-block"></span><span class="text-textMuted">CICS Transaction</span></div>
                                <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-indigo-400 inline-block"></span><span class="text-textMuted">Database (DB2/IMS)</span></div>
                                <div class="flex items-center gap-2"><span class="w-4 h-0.5 bg-blockerRed inline-block"></span><span class="text-blockerRed">Circular Dependency</span></div>
                            </div>

                            <!-- Interactive Help Tooltip Overlay -->
                            <div class="absolute top-3 right-3 bg-surface/80 p-2 rounded border border-borderHairline text-[10px] font-mono text-textDim pointer-events-none">
                                Click node to inspect blast radius &bull; Drag to pan &bull; Scroll to zoom
                            </div>
                        </div>
                    </div>

                    <!-- Instant Blast Radius Inspector Drawer (4 Cols) -->
                    <div class="xl:col-span-4 bg-surface rounded-md border border-borderHairline p-4 flex flex-col h-[650px]">
                        <div class="border-b border-borderHairline pb-3 flex items-center justify-between">
                            <div>
                                <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Architectural Blast Radius Inspector</h3>
                                <div id="inspectorNodeId" class="text-base font-bold font-mono text-white mt-0.5">SELECT A NODE</div>
                            </div>
                            <span id="inspectorNodeType" class="text-[10px] font-mono px-2 py-0.5 rounded bg-subsurface border border-borderHairline text-textMuted uppercase">NONE</span>
                        </div>

                        <!-- Inspector Details Body -->
                        <div id="inspectorDetails" class="flex-1 overflow-y-auto py-3 space-y-4 font-mono text-xs">
                            <div class="p-8 text-center text-textDim">
                                <svg class="w-10 h-10 mx-auto mb-2 text-borderHairline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"/></svg>
                                Click any node in the topology graph to calculate immediate blast radius, upstream caller programs, and downstream data mutations.
                            </div>
                        </div>

                        <!-- Platform Containerization Impact footer -->
                        <div id="inspectorFooter" class="border-t border-borderHairline pt-3 mt-auto hidden font-mono text-xs space-y-2">
                            <div class="flex justify-between items-center text-[11px]">
                                <span class="text-textDim">Container Isolation Score:</span>
                                <span id="inspectorIsolation" class="font-bold text-ocpMint">READY</span>
                            </div>
                            <div id="inspectorRecommendation" class="p-2 rounded bg-subsurface border border-borderHairline text-[11px] text-textMuted">
                                Safe for independent extraction into an OpenShift deployment container.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODE 2: SEMANTIC DOMAIN DECOMPOSITION -->
            <div id="mode-domains" class="space-y-4 hidden">
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
                    
                    <!-- 2D Embedding Scatter Map (5 Cols) -->
                    <div class="lg:col-span-5 bg-surface rounded-md border border-borderHairline p-4 flex flex-col h-[650px]">
                        <div class="border-b border-borderHairline pb-3">
                            <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Semantic Embedding Landscape (2D Projection)</h3>
                            <p class="text-xs text-textMuted mt-0.5">High-dimensional vector embeddings generated via <code class="text-infoSky font-mono">all-MiniLM-L6-v2</code> projected to 2D latent space.</p>
                        </div>
                        <div class="flex-1 relative mt-3 flex items-center justify-center bg-obsidian rounded border border-borderHairline overflow-hidden p-2">
                            <canvas id="semanticScatterChart" class="w-full h-full"></canvas>
                        </div>
                        <div class="mt-3 text-[11px] font-mono text-textDim flex items-center justify-between border-t border-borderHairline pt-2">
                            <span>Points close together share high business domain similarity.</span>
                            <span class="text-textMuted">{len(clusters)} Cluster Domains</span>
                        </div>
                    </div>

                    <!-- Target Microservice Candidates Grid (7 Cols) -->
                    <div class="lg:col-span-7 bg-surface rounded-md border border-borderHairline p-4 flex flex-col h-[650px]">
                        <div class="border-b border-borderHairline pb-3 flex items-center justify-between">
                            <div>
                                <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Target Microservice Candidates</h3>
                                <p class="text-xs text-textMuted mt-0.5">Extracted domain clusters recommended for OpenShift container shapes.</p>
                            </div>
                            <span class="text-xs font-mono px-2 py-0.5 rounded bg-subsurface text-ocpMint border border-emerald-500/30">
                                {len(clusters)} Autonomous Services
                            </span>
                        </div>

                        <!-- Candidates Scroll Area -->
                        <div class="flex-1 overflow-y-auto space-y-3 mt-3 pr-1 font-mono text-xs">
                            {"".join([f"""
                            <div class="p-3.5 rounded bg-subsurface border border-borderHairline hover:border-slate-600 transition-colors space-y-2.5">
                                <div class="flex items-start justify-between gap-2">
                                    <div>
                                        <div class="flex items-center gap-2">
                                            <span class="w-2 h-2 rounded-full bg-ocpMint"></span>
                                            <span class="font-bold text-white text-sm">{c.get('cluster_name', 'DomainService')}</span>
                                        </div>
                                        <div class="text-[11px] text-infoSky mt-0.5">Domain: {c.get('domain_tag', 'CORE')} &bull; Type: {c.get('suggested_service_type', 'Microservice')}</div>
                                    </div>
                                    <div class="text-right">
                                        <span class="px-2 py-0.5 rounded text-[10px] bg-obsidian border border-borderHairline text-textMuted">
                                            Shape: {c.get('suggested_container_shape', '500m CPU / 1Gi RAM')}
                                        </span>
                                    </div>
                                </div>

                                <div class="grid grid-cols-2 gap-2 text-[11px] bg-obsidian/60 p-2 rounded border border-borderHairline">
                                    <div>
                                        <span class="text-textDim">Cohesion Score:</span>
                                        <span class="text-emerald-400 font-semibold tabular-nums ml-1">{(c.get('cohesion_score', 0.0) or 0.0)*100:.1f}%</span>
                                    </div>
                                    <div>
                                        <span class="text-textDim">Coupling Score:</span>
                                        <span class="text-amber-400 font-semibold tabular-nums ml-1">{(c.get('coupling_score', 0.0) or 0.0)*100:.1f}%</span>
                                    </div>
                                </div>

                                <div class="space-y-1 text-[11px]">
                                    <div class="text-textDim font-medium">Bound Application Artifacts:</div>
                                    <div class="flex flex-wrap gap-1">
                                        {"".join([f'<span class="px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-textPrimary text-[10px]">{p}</span>' for p in c.get('programs', [])])}
                                        {"".join([f'<span class="px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-ocpMint text-[10px]">{d}</span>' for d in c.get('datasets', [])])}
                                        {"".join([f'<span class="px-1.5 py-0.2 rounded bg-obsidian border border-borderHairline text-amber-400 text-[10px]">{t}</span>' for t in c.get('cics_txns', [])])}
                                    </div>
                                </div>
                            </div>
                            """ for c in clusters])}
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODE 3: TECHNICAL AUDIT & DECISION RECORD -->
            <div id="mode-audit" class="space-y-4 hidden">
                
                <!-- 8-Dimension Assessment Grid & Radar Chart -->
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
                    <!-- Radar Chart (5 Cols) -->
                    <div class="lg:col-span-5 bg-surface rounded-md border border-borderHairline p-4 flex flex-col h-[480px]">
                        <div class="border-b border-borderHairline pb-2.5">
                            <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">8-Dimension Architectural Radar</h3>
                            <p class="text-xs text-textMuted mt-0.5">Comprehensive multi-dimensional evaluation of mainframe workload profile.</p>
                        </div>
                        <div class="flex-1 relative mt-2 flex items-center justify-center">
                            <canvas id="dimensionRadarChart" class="w-full h-full"></canvas>
                        </div>
                    </div>

                    <!-- Dimension Breakdown Table (7 Cols) -->
                    <div class="lg:col-span-7 bg-surface rounded-md border border-borderHairline p-4 flex flex-col h-[480px]">
                        <div class="border-b border-borderHairline pb-2.5 flex items-center justify-between">
                            <div>
                                <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Dimension Score Breakdown</h3>
                                <p class="text-xs text-textMuted mt-0.5">Normalized readiness scores across enterprise evaluation vectors.</p>
                            </div>
                            <span class="text-xs font-mono px-2 py-0.5 rounded bg-subsurface text-white border border-borderHairline">
                                Overall: <span class="text-ocpMint font-bold tabular-nums">{overall_score:.1f}%</span>
                            </span>
                        </div>

                        <div class="flex-1 overflow-y-auto mt-2 pr-1">
                            <table class="w-full text-left font-mono text-xs border-collapse">
                                <thead>
                                    <tr class="border-b border-borderHairline text-textDim text-[11px]">
                                        <th class="py-2 font-normal">DIMENSION</th>
                                        <th class="py-2 font-normal text-right">SCORE</th>
                                        <th class="py-2 font-normal text-right">WEIGHT</th>
                                        <th class="py-2 font-normal text-right">BLOCKERS</th>
                                        <th class="py-2 font-normal pl-4">STRATEGIC GUIDANCE</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-borderHairline">
                                    {"".join([f"""
                                    <tr class="hover:bg-subsurface/60 transition-colors">
                                        <td class="py-2 font-semibold text-white">{d.get('name', d.get('dimension'))}</td>
                                        <td class="py-2 text-right tabular-nums {'text-emerald-400' if (d.get('score', 0) or 0) >= 70 else 'text-amber-400' if (d.get('score', 0) or 0) >= 45 else 'text-rose-400'} font-bold">
                                            {d.get('score', 0.0):.1f}%
                                        </td>
                                        <td class="py-2 text-right text-textDim tabular-nums">{d.get('weight', 0.0):.2f}</td>
                                        <td class="py-2 text-right tabular-nums {'text-blockerRed font-bold' if len(d.get('blockers', [])) > 0 else 'text-textDim'}">
                                            {len(d.get('blockers', []))}
                                        </td>
                                        <td class="py-2 pl-4 text-textMuted text-[11px] truncate max-w-xs" title="{'; '.join(d.get('recommendations', []))}">
                                            {'; '.join(d.get('recommendations', ['No immediate remediation necessary']))}
                                        </td>
                                    </tr>
                                    """ for d in assessment.get('dimension_scores', [])])}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Twelve-Factor Cloud Native Compliance Grid -->
                <div class="bg-surface rounded-md border border-borderHairline p-4">
                    <div class="border-b border-borderHairline pb-3 flex items-center justify-between">
                        <div>
                            <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Twelve-Factor App Modernization Compliance</h3>
                            <p class="text-xs text-textMuted mt-0.5">Audit of cloud native readiness vectors for OpenShift container deployment.</p>
                        </div>
                        <span class="text-xs font-mono px-2 py-0.5 rounded bg-subsurface text-infoSky border border-borderHairline">
                            Compliance: <span class="font-bold tabular-nums">{avg_factor_score*10:.1f}%</span>
                        </span>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 mt-4 font-mono text-xs">
                        {"".join([f"""
                        <div class="p-3 rounded bg-subsurface border border-borderHairline space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-[10px] text-textDim font-bold">FACTOR {f.get('factor_number')}</span>
                                <span class="text-[10px] px-1.5 py-0.2 rounded border {'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' if f.get('score', 0) >= 8 else 'border-amber-500/30 bg-amber-500/10 text-amber-400' if f.get('score', 0) >= 5 else 'border-rose-500/30 bg-rose-500/10 text-rose-400'}">
                                    {f.get('status', 'EVALUATED')}
                                </span>
                            </div>
                            <div class="font-bold text-white text-xs truncate" title="{f.get('factor_name')}">{f.get('factor_name')}</div>
                            <div class="text-[11px] text-textMuted leading-relaxed">{f.get('notes', '')}</div>
                            <div class="text-[10px] text-textDim pt-1 border-t border-borderHairline">
                                Remediation: <span class="text-textMuted">{f.get('remediation_required', 'None')}</span>
                            </div>
                        </div>
                        """ for f in assessment.get('twelve_factor_compliance', [])])}
                    </div>
                </div>

                <!-- Prioritized Risk & Remediation Register -->
                <div class="bg-surface rounded-md border border-borderHairline p-4">
                    <div class="border-b border-borderHairline pb-3 flex flex-wrap items-center justify-between gap-3">
                        <div>
                            <h3 class="text-xs font-mono uppercase tracking-wider text-textDim">Prioritized Risk &amp; Remediation Register</h3>
                            <p class="text-xs text-textMuted mt-0.5">Critical blockers, architectural obstacles, and platform impacts.</p>
                        </div>
                        
                        <div class="flex items-center gap-2 text-xs font-mono">
                            <span class="text-textDim">SEVERITY:</span>
                            <button onclick="filterRisks('ALL')" class="risk-filter-btn px-2 py-0.5 rounded bg-subsurface text-white border border-borderHairline">ALL ({len(risks)})</button>
                            <button onclick="filterRisks('CRITICAL')" class="risk-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:text-white">CRITICAL</button>
                            <button onclick="filterRisks('HIGH')" class="risk-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:text-white">HIGH</button>
                            <button onclick="filterRisks('MEDIUM')" class="risk-filter-btn px-2 py-0.5 rounded bg-subsurface text-textMuted border border-borderHairline hover:text-white">MEDIUM</button>
                        </div>
                    </div>

                    <div class="overflow-x-auto mt-3">
                        <table class="w-full text-left font-mono text-xs border-collapse">
                            <thead>
                                <tr class="border-b border-borderHairline text-textDim text-[11px]">
                                    <th class="py-2.5 font-normal">ID</th>
                                    <th class="py-2.5 font-normal">SEVERITY</th>
                                    <th class="py-2.5 font-normal">TITLE &amp; DESCRIPTION</th>
                                    <th class="py-2.5 font-normal">PLATFORM IMPACT</th>
                                    <th class="py-2.5 font-normal">MITIGATION STRATEGY</th>
                                </tr>
                            </thead>
                            <tbody id="riskTableBody" class="divide-y divide-borderHairline">
                                {"".join([f"""
                                <tr class="risk-row hover:bg-subsurface/60 transition-colors" data-severity="{str(r.get('severity', '')).upper()}">
                                    <td class="py-2.5 text-textDim font-bold">{r.get('risk_id', 'RSK-00')}</td>
                                    <td class="py-2.5">
                                        <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase border {'border-rose-500/30 bg-rose-500/10 text-blockerRed' if str(r.get('severity', '')).upper()=='CRITICAL' else 'border-amber-500/30 bg-amber-500/10 text-amber-400' if str(r.get('severity', '')).upper()=='HIGH' else 'border-blue-500/30 bg-blue-500/10 text-sky-400'}">
                                            {r.get('severity', 'MEDIUM')}
                                        </span>
                                    </td>
                                    <td class="py-2.5 max-w-sm">
                                        <div class="font-bold text-white">{r.get('title', '')}</div>
                                        <div class="text-[11px] text-textMuted mt-0.5 leading-normal">{r.get('description', '')}</div>
                                    </td>
                                    <td class="py-2.5 text-textDim text-[11px] max-w-xs">{r.get('platform_impact', '')}</td>
                                    <td class="py-2.5 text-textMuted text-[11px] max-w-sm leading-normal">{r.get('mitigation_strategy', '')}</td>
                                </tr>
                                """ for r in risks])}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Architectural Decision Record (ADR) Container -->
                <div class="bg-surface rounded-md border border-borderHairline p-5 space-y-4">
                    <div class="border-b border-borderHairline pb-3 flex flex-wrap items-center justify-between gap-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-sm bg-ocpMint"></span>
                            <h3 class="text-sm font-mono uppercase tracking-wider text-white font-bold">Architecture Decision Record (ADR)</h3>
                            <span class="text-xs font-mono text-textDim">// Michael Nygard Standard</span>
                        </div>
                        <span class="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-ocpMint border border-emerald-500/30 font-semibold uppercase">
                            STATUS: {decision.get('adr', {}).get('status', 'ACCEPTED')}
                        </span>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 font-mono text-xs">
                        <div class="lg:col-span-8 space-y-4">
                            <div>
                                <span class="text-textDim text-[11px] uppercase block mb-1">Title &amp; Scope:</span>
                                <div class="text-base font-bold text-white">{decision.get('adr', {}).get('title', 'Target Architecture Decision')}</div>
                            </div>

                            <div>
                                <span class="text-textDim text-[11px] uppercase block mb-1">Context &amp; Architectural Drivers:</span>
                                <p class="text-textMuted text-xs leading-relaxed bg-subsurface p-3 rounded border border-borderHairline">
                                    {decision.get('adr', {}).get('context', '')}
                                </p>
                            </div>

                            <div>
                                <span class="text-textDim text-[11px] uppercase block mb-1">Decision:</span>
                                <div class="text-xs text-white leading-relaxed bg-subsurface p-3 rounded border border-borderHairline border-l-2 border-l-ocpMint">
                                    {decision.get('adr', {}).get('decision', '')}
                                </div>
                            </div>

                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                                <div class="p-3 rounded bg-subsurface border border-borderHairline space-y-1.5">
                                    <span class="text-emerald-400 font-bold flex items-center gap-1.5">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                        Positive Consequences
                                    </span>
                                    <ul class="text-[11px] text-textMuted space-y-1 list-disc list-inside">
                                        {"".join([f'<li>{c}</li>' for c in decision.get('adr', {}).get('consequences', {}).get('positive', [])])}
                                    </ul>
                                </div>

                                <div class="p-3 rounded bg-subsurface border border-borderHairline space-y-1.5">
                                    <span class="text-amber-400 font-bold flex items-center gap-1.5">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                                        Negative &amp; Managed Trade-offs
                                    </span>
                                    <ul class="text-[11px] text-textMuted space-y-1 list-disc list-inside">
                                        {"".join([f'<li>{c}</li>' for c in decision.get('adr', {}).get('consequences', {}).get('negative', [])])}
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <!-- Trade-off Matrix Side-by-Side (4 Cols) -->
                        <div class="lg:col-span-4 bg-subsurface p-3.5 rounded border border-borderHairline flex flex-col justify-between">
                            <div>
                                <span class="text-textDim text-[11px] uppercase block mb-2 font-bold">Target Trade-off Evaluation</span>
                                <div class="space-y-3">
                                    {"".join([f"""
                                    <div class="border-b border-borderHairline pb-2 space-y-1">
                                        <div class="flex justify-between text-[11px]">
                                            <span class="text-textMuted">{k.replace('_', ' ').title()}</span>
                                            <span class="text-textDim font-mono">OCP vs VM</span>
                                        </div>
                                        <div class="flex justify-between text-[11px] font-bold">
                                            <span class="text-ocpMint">{v.get('ocp', 'N/A')}</span>
                                            <span class="text-vmAmber">{v.get('vm', 'N/A')}</span>
                                        </div>
                                    </div>
                                    """ for k, v in decision.get('trade_off_matrix', {}).items() if isinstance(v, dict)])}
                                </div>
                            </div>

                            <div class="pt-3 border-t border-borderHairline text-[10px] text-textDim leading-normal">
                                Decision validated through ModernizeIQ Multi-Dimensional Metamodel Analysis.
                            </div>
                        </div>
                    </div>
                </div>

            </div>

        </section>

    </main>

    <!-- Raw Data Payload for Client-Side Scripting -->
    <script id="modernizeiq-payload" type="application/json">
        {report_json_str}
    </script>

    <!-- CLIENT INTERACTIVITY LOGIC -->
    <script>
        const reportData = JSON.parse(document.getElementById('modernizeiq-payload').textContent);
        const graphData = reportData.dependency_graph || {{ nodes: [], links: [] }};
        const nodes = graphData.nodes || [];
        const links = graphData.links || [];

        // Workbench Mode Switcher
        function switchWorkbenchMode(mode) {{
            const modes = ['topology', 'domains', 'audit'];
            modes.forEach(m => {{
                const el = document.getElementById(`mode-${{m}}`);
                const btn = document.getElementById(`tab-btn-${{m}}`);
                if (m === mode) {{
                    el.classList.remove('hidden');
                    btn.classList.add('active-tab');
                    btn.classList.remove('inactive-tab');
                }} else {{
                    el.classList.add('hidden');
                    btn.classList.remove('active-tab');
                    btn.classList.add('inactive-tab');
                }}
            }});
            if (mode === 'domains' && window.scatterChart) {{
                window.scatterChart.resize();
            }}
            if (mode === 'audit' && window.radarChart) {{
                window.radarChart.resize();
            }}
        }}

        // ==========================================
        // TOPOLOGY GRAPH (D3-LIKE INTERACTIVE SVG)
        // ==========================================
        let currentFilter = 'ALL';
        let currentSearch = '';
        let svgTransform = {{ x: 0, y: 0, scale: 1 }};
        let isDragging = false;
        let startPos = {{ x: 0, y: 0 }};

        function initTopologyGraph() {{
            const svg = document.getElementById('dependencySvg');
            const width = svg.clientWidth || 900;
            const height = svg.clientHeight || 600;

            // Generate deterministic layout coordinates if none present
            const nodeCount = nodes.length;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) * 0.38;

            nodes.forEach((n, idx) => {{
                if (n.x === undefined || n.y === undefined) {{
                    const angle = (idx / nodeCount) * 2 * Math.PI;
                    n.x = centerX + radius * Math.cos(angle);
                    n.y = centerY + radius * Math.sin(angle);
                }}
            }});

            renderTopologySvg();

            // Pan and Zoom listeners
            svg.addEventListener('mousedown', (e) => {{
                if (e.target.tagName === 'circle' || e.target.tagName === 'rect' || e.target.tagName === 'text') return;
                isDragging = true;
                startPos = {{ x: e.clientX - svgTransform.x, y: e.clientY - svgTransform.y }};
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;
                svgTransform.x = e.clientX - startPos.x;
                svgTransform.y = e.clientY - startPos.y;
                updateSvgTransform();
            }});

            window.addEventListener('mouseup', () => {{
                isDragging = false;
            }});

            svg.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                svgTransform.scale = Math.max(0.2, Math.min(3.5, svgTransform.scale * delta));
                updateSvgTransform();
            }});
        }}

        function updateSvgTransform() {{
            const g = document.getElementById('topologyViewport');
            if (g) {{
                g.setAttribute('transform', `translate(${{svgTransform.x}}, ${{svgTransform.y}}) scale(${{svgTransform.scale}})`);
            }}
        }}

        function resetTopologyZoom() {{
            svgTransform = {{ x: 0, y: 0, scale: 1 }};
            updateSvgTransform();
        }}

        function getNodeColor(type) {{
            switch(type) {{
                case 'PROGRAM': return '#38BDF8';
                case 'DATASET': return '#10B981';
                case 'CICS_TRANSACTION': return '#F59E0B';
                case 'DATABASE': return '#818CF8';
                default: return '#94A3B8';
            }}
        }}

        function renderTopologySvg() {{
            const svg = document.getElementById('dependencySvg');
            const width = svg.clientWidth || 900;
            const height = svg.clientHeight || 600;

            const visibleNodes = nodes.filter(n => {{
                if (currentFilter === 'ALL') return true;
                if (currentFilter === 'CIRCULAR') {{
                    return links.some(l => l.is_circular && (l.source === n.id || l.target === n.id));
                }}
                return n.type === currentFilter;
            }});

            const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
            const visibleLinks = links.filter(l => visibleNodeIds.has(l.source) && visibleNodeIds.has(l.target));

            let html = `
                <defs>
                    <marker id="arrow" viewBox="0 -5 10 10" refX="22" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#334155"></path>
                    </marker>
                    <marker id="arrow-circular" viewBox="0 -5 10 10" refX="22" refY="0" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M0,-5L10,0L0,5" fill="#EF4444"></path>
                    </marker>
                </defs>
                <g id="topologyViewport" transform="translate(${{svgTransform.x}}, ${{svgTransform.y}}) scale(${{svgTransform.scale}})">
            `;

            // Draw links
            visibleLinks.forEach(l => {{
                const s = nodes.find(n => n.id === l.source);
                const t = nodes.find(n => n.id === l.target);
                if (s && t) {{
                    const strokeColor = l.is_circular ? '#EF4444' : '#232D3F';
                    const strokeWidth = l.is_circular ? 2 : 1;
                    const dashArray = l.is_circular ? 'stroke-dasharray="4,4"' : '';
                    const marker = l.is_circular ? 'marker-end="url(#arrow-circular)"' : 'marker-end="url(#arrow)"';
                    html += `<line x1="${{s.x}}" y1="${{s.y}}" x2="${{t.x}}" y2="${{t.y}}" stroke="${{strokeColor}}" stroke-width="${{strokeWidth}}" ${{dashArray}} ${{marker}} />`;
                }}
            }});

            // Draw nodes
            visibleNodes.forEach(n => {{
                const color = getNodeColor(n.type);
                const matchesSearch = currentSearch && n.id.toLowerCase().includes(currentSearch.toLowerCase());
                const strokeColor = matchesSearch ? '#F1F5F9' : '#0A0E17';
                const strokeWidth = matchesSearch ? 3 : 1.5;
                const r = matchesSearch ? 14 : 10;

                html += `
                    <g class="cursor-pointer" onclick="inspectNode('${{n.id}}')">
                        <circle cx="${{n.x}}" cy="${{n.y}}" r="${{r}}" fill="${{color}}" stroke="${{strokeColor}}" stroke-width="${{strokeWidth}}"></circle>
                        <text x="${{n.x}}" y="${{n.y + 18}}" text-anchor="middle" fill="#94A3B8" font-size="10" font-family="'IBM Plex Mono', monospace">${{n.id}}</text>
                    </g>
                `;
            }});

            html += `</g>`;
            svg.innerHTML = html;
        }}

        function filterTopology(filterType) {{
            currentFilter = filterType;
            document.querySelectorAll('.topo-filter-btn').forEach(btn => {{
                if (btn.textContent.includes(filterType)) {{
                    btn.classList.add('text-white');
                    btn.classList.remove('text-textMuted');
                }} else {{
                    btn.classList.remove('text-white');
                    btn.classList.add('text-textMuted');
                }}
            }});
            renderTopologySvg();
        }}

        function searchTopology(query) {{
            currentSearch = query;
            renderTopologySvg();
        }}

        // ==========================================
        // INSTANT BLAST RADIUS INSPECTOR
        // ==========================================
        function inspectNode(nodeId) {{
            const node = nodes.find(n => n.id === nodeId);
            if (!node) return;

            document.getElementById('inspectorNodeId').textContent = node.id;
            const typeBadge = document.getElementById('inspectorNodeType');
            typeBadge.textContent = node.type;
            typeBadge.style.color = getNodeColor(node.type);

            // Compute blast radius
            const inbound = links.filter(l => l.target === nodeId);
            const outbound = links.filter(l => l.source === nodeId);
            const circular = links.filter(l => l.is_circular && (l.source === nodeId || l.target === nodeId));

            // Downstream blast radius (breadth-first traversal)
            const visited = new Set();
            const queue = [nodeId];
            while (queue.length > 0) {{
                const curr = queue.shift();
                links.filter(l => l.source === curr).forEach(l => {{
                    if (!visited.has(l.target) && l.target !== nodeId) {{
                        visited.add(l.target);
                        queue.push(l.target);
                    }}
                }});
            }}

            const details = document.getElementById('inspectorDetails');
            details.innerHTML = `
                <div class="bg-subsurface p-3 rounded border border-borderHairline space-y-2">
                    <div class="flex justify-between items-center text-[11px]">
                        <span class="text-textDim">Blast Radius Impact:</span>
                        <span class="font-bold text-white tabular-nums">${{visited.size}} Downstream Artifacts</span>
                    </div>
                    <div class="w-full h-1.5 bg-obsidian rounded overflow-hidden border border-borderHairline">
                        <div class="h-full bg-blockerRed" style="width: ${{Math.min(100, visited.size * 20)}}%;"></div>
                    </div>
                </div>

                <div class="space-y-1.5">
                    <span class="text-textDim text-[11px] uppercase block font-semibold">Immediate Callers / Upstream (${{inbound.length}}):</span>
                    <div class="flex flex-wrap gap-1">
                        ${{inbound.length > 0 ? inbound.map(l => `<span class="px-2 py-0.5 rounded bg-obsidian border border-borderHairline text-textPrimary text-[11px]">${{l.source}} <span class="text-textDim">(${l.relationship || 'CALLS'})</span></span>`).join('') : '<span class="text-textDim text-[11px]">No inbound dependencies (Root Entrypoint)</span>'}}
                    </div>
                </div>

                <div class="space-y-1.5">
                    <span class="text-textDim text-[11px] uppercase block font-semibold">Outbound Dependencies (${{outbound.length}}):</span>
                    <div class="flex flex-wrap gap-1">
                        ${{outbound.length > 0 ? outbound.map(l => `<span class="px-2 py-0.5 rounded bg-obsidian border border-borderHairline text-textPrimary text-[11px]">${{l.target}} <span class="text-textDim">(${l.relationship || 'USES'})</span></span>`).join('') : '<span class="text-textDim text-[11px]">No outbound calls (Leaf Node)</span>'}}
                    </div>
                </div>

                ${{circular.length > 0 ? `
                <div class="p-2.5 rounded bg-rose-500/10 border border-rose-500/30 text-blockerRed space-y-1">
                    <div class="font-bold text-[11px] flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                        Circular Coupling Detected
                    </div>
                    <div class="text-[10px] text-textMuted leading-relaxed">
                        Tightly bound in circular loop with: ${{circular.map(c => c.source === nodeId ? c.target : c.source).join(', ')}}. Decouple before containerization.
                    </div>
                </div>
                ` : ''}}
            `;

            // Update footer recommendation
            const footer = document.getElementById('inspectorFooter');
            footer.classList.remove('hidden');
            const isolation = document.getElementById('inspectorIsolation');
            const rec = document.getElementById('inspectorRecommendation');

            if (circular.length > 0) {{
                isolation.textContent = 'HIGH REFACTORING RISK';
                isolation.className = 'font-bold text-blockerRed';
                rec.textContent = 'Must refactor circular dependency before containerizing. Candidate for monolithic VM rehost first.';
            }} else if (visited.size > 5) {{
                isolation.textContent = 'MODERATE BLAST RADIUS';
                isolation.className = 'font-bold text-amber-400';
                rec.textContent = 'Changes to this component impact over 5 downstream systems. Maintain contract tests.';
            }} else {{
                isolation.textContent = 'READY FOR OPENSHIFT';
                isolation.className = 'font-bold text-ocpMint';
                rec.textContent = 'Clean decoupling profile. Safe for autonomous microservice container packaging.';
            }}
        }}

        // ==========================================
        // CHART.JS: RADAR & SEMANTIC SCATTER CHARTS
        // ==========================================
        function initCharts() {{
            // 8-Dimension Radar Chart
            const dimScores = reportData.assessment?.dimension_scores || [];
            const radarLabels = dimScores.map(d => d.name || d.dimension);
            const radarValues = dimScores.map(d => d.score || 0);

            const ctxRadar = document.getElementById('dimensionRadarChart');
            if (ctxRadar) {{
                window.radarChart = new Chart(ctxRadar, {{
                    type: 'radar',
                    data: {{
                        labels: radarLabels,
                        datasets: [{{
                            label: 'Workload Dimension Score',
                            data: radarValues,
                            backgroundColor: 'rgba(16, 185, 129, 0.15)',
                            borderColor: '#10B981',
                            borderWidth: 2,
                            pointBackgroundColor: '#10B981',
                            pointBorderColor: '#0A0E17',
                            pointHoverBackgroundColor: '#FFFFFF',
                            pointRadius: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            r: {{
                                angleLines: {{ color: '#232D3F' }},
                                grid: {{ color: '#232D3F' }},
                                pointLabels: {{
                                    color: '#94A3B8',
                                    font: {{ family: "'IBM Plex Mono', monospace", size: 10 }}
                                }},
                                ticks: {{
                                    display: false,
                                    min: 0,
                                    max: 100,
                                    stepSize: 20
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                backgroundColor: '#111726',
                                borderColor: '#232D3F',
                                borderWidth: 1,
                                titleFont: {{ family: "'IBM Plex Sans', sans-serif" }},
                                bodyFont: {{ family: "'IBM Plex Mono', monospace" }}
                            }}
                        }}
                    }}
                }});
            }}

            // Semantic Embedding Scatter Plot
            const clusters = reportData.semantic_clusters || [];
            const coords = reportData.semantic_coords || {{}};
            const progCoords = coords.programs || {{}};

            const clusterColors = ['#10B981', '#38BDF8', '#F59E0B', '#A78BFA', '#F472B6', '#34D399'];
            const scatterDatasets = clusters.map((c, idx) => {{
                const color = clusterColors[idx % clusterColors.length];
                const clusterProgs = c.programs || [];
                const points = clusterProgs.map(p => {{
                    const pt = progCoords[p] || [Math.random() * 2 - 1, Math.random() * 2 - 1];
                    return {{ x: pt[0], y: pt[1], label: p }};
                }});

                return {{
                    label: c.cluster_name || `Cluster ${{idx + 1}}`,
                    data: points,
                    backgroundColor: color,
                    borderColor: '#0A0E17',
                    borderWidth: 1,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }};
            }});

            const ctxScatter = document.getElementById('semanticScatterChart');
            if (ctxScatter) {{
                window.scatterChart = new Chart(ctxScatter, {{
                    type: 'scatter',
                    data: {{ datasets: scatterDatasets }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            x: {{
                                grid: {{ color: '#1B2436' }},
                                ticks: {{ color: '#64748B', font: {{ family: "'IBM Plex Mono', monospace", size: 9 }} }}
                            }},
                            y: {{
                                grid: {{ color: '#1B2436' }},
                                ticks: {{ color: '#64748B', font: {{ family: "'IBM Plex Mono', monospace", size: 9 }} }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    color: '#94A3B8',
                                    boxWidth: 8,
                                    font: {{ family: "'IBM Plex Mono', monospace", size: 10 }}
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: '#111726',
                                borderColor: '#232D3F',
                                borderWidth: 1,
                                callbacks: {{
                                    label: function(context) {{
                                        return `${{context.raw.label || 'Artifact'}} (${{context.dataset.label}})`;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        // ==========================================
        // RISK REGISTER FILTERING
        // ==========================================
        function filterRisks(severity) {{
            document.querySelectorAll('.risk-filter-btn').forEach(btn => {{
                if (btn.textContent.includes(severity)) {{
                    btn.classList.add('text-white');
                    btn.classList.remove('text-textMuted');
                }} else {{
                    btn.classList.remove('text-white');
                    btn.classList.add('text-textMuted');
                }}
            }});

            document.querySelectorAll('.risk-row').forEach(row => {{
                const rowSev = row.getAttribute('data-severity');
                if (severity === 'ALL' || rowSev === severity) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}

        // ==========================================
        // EXPORT HELPERS
        // ==========================================
        function copyAdrMarkdown() {{
            const adr = reportData.decision?.adr || {{}};
            const md = `# ADR: ${{adr.title || 'Architecture Decision Record'}}
Status: ${{adr.status || 'Accepted'}}

## Context
${{adr.context || ''}}

## Decision
${{adr.decision || ''}}

## Consequences
### Positive
${{(adr.consequences?.positive || []).map(p => `- ${{p}}`).join('\\n')}}

### Negative & Managed Trade-offs
${{(adr.consequences?.negative || []).map(n => `- ${{n}}`).join('\\n')}}

---
*Generated by ModernizeIQ Architectural Assessment Engine*
`;
            navigator.clipboard.writeText(md).then(() => {{
                alert('ADR copied to clipboard in Markdown format.');
            }}).catch(() => {{
                alert('Failed to copy to clipboard.');
            }});
        }}

        function downloadJsonDossier() {{
            const str = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
            const dl = document.createElement('a');
            dl.setAttribute("href", str);
            dl.setAttribute("download", `ModernizeIQ_${{reportData.portfolio?.app_id || 'Assessment'}}.json`);
            dl.click();
        }}

        // Initialization on Load
        window.addEventListener('DOMContentLoaded', () => {{
            initTopologyGraph();
            initCharts();
        }});
    </script>
</body>
</html>
"""
'''

with open("src/modernizeiq/ui/dashboard_template.py", "w", encoding="utf-8") as f:
    f.write(template_code)

print("Successfully wrote src/modernizeiq/ui/dashboard_template.py")
