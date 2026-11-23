"""Enterprise Dependency Graph and Blast Radius Engine using NetworkX."""

from __future__ import annotations
from typing import List, Dict, Set, Any, Optional
import networkx as nx

from ..models.artifacts import ApplicationPortfolio
from ..models.graph import GraphNode, GraphEdge, DependencyGraphData


class DependencyGraphEngine:
    """Builds and analyzes multi-artifact dependency networks with blast-radius computation."""

    def build_graph(self, portfolio: ApplicationPortfolio) -> DependencyGraphData:
        G = nx.DiGraph()

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        # Color palette for visual rendering
        type_colors = {
            "Program": "#3B82F6",       # Blue
            "Copybook": "#8B5CF6",      # Purple
            "Table": "#10B981",         # Green
            "Vsam": "#F59E0B",          # Amber
            "Job": "#EC4899",           # Pink
            "Transaction": "#06B6D4",   # Cyan
            "Mapset": "#F97316",        # Orange
        }

        # 1. Add COBOL Programs
        for p_id, p in portfolio.programs.items():
            # Node color readiness: Green (clean), Yellow (moderate), Red (ALTER or Conversational)
            status_color = "#EF4444" if (p.alter_statements_count > 0 or p.is_conversational) else (
                "#F59E0B" if (p.cyclomatic_complexity > 30 or len(p.vsam_files_accessed) > 0) else "#10B981"
            )
            node = GraphNode(
                id=p_id,
                label=p_id,
                type="Program",
                complexity_score=float(p.cyclomatic_complexity),
                lines_of_code=p.lines_of_code,
                color=status_color,
                metadata={
                    "is_cics": p.is_cics_program,
                    "is_batch": p.is_batch_program,
                    "is_conversational": p.is_conversational,
                    "cyclomatic_complexity": p.cyclomatic_complexity,
                    "maintainability_index": round(p.maintainability_index, 1),
                },
            )
            nodes.append(node)
            G.add_node(p_id, **node.dict())

        # 2. Add Copybooks
        for cb_name, cb in portfolio.copybooks.items():
            node = GraphNode(
                id=f"CPY_{cb_name}",
                label=cb_name,
                type="Copybook",
                complexity_score=float(cb.field_count),
                lines_of_code=cb.field_count * 2,
                color=type_colors["Copybook"],
                metadata={
                    "field_count": cb.field_count,
                    "has_redefines": cb.has_redefines,
                    "referenced_by_count": len(cb.referenced_by_programs),
                },
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # 3. Add DB2 Tables
        for t_name, tbl in portfolio.tables.items():
            node = GraphNode(
                id=f"TBL_{t_name}",
                label=t_name,
                type="Table",
                complexity_score=float(tbl.column_count),
                lines_of_code=tbl.column_count,
                color=type_colors["Table"],
                metadata={
                    "column_count": tbl.column_count,
                    "primary_key": tbl.primary_key,
                },
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # 4. Add VSAM Files
        for v_name, vsam in portfolio.vsam_files.items():
            node = GraphNode(
                id=f"VSAM_{v_name}",
                label=v_name,
                type="Vsam",
                complexity_score=10.0,
                lines_of_code=0,
                color=type_colors["Vsam"],
                metadata={
                    "organization": vsam.organization.value,
                    "record_length": vsam.record_length,
                },
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # 5. Add JCL Jobs
        for j_name, job in portfolio.jobs.items():
            node = GraphNode(
                id=f"JOB_{j_name}",
                label=j_name,
                type="Job",
                complexity_score=float(len(job.steps)),
                lines_of_code=len(job.steps) * 15,
                color=type_colors["Job"],
                metadata={"steps_count": len(job.steps)},
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # 6. Add CICS Transactions
        for tx_id, tx in portfolio.transactions.items():
            node = GraphNode(
                id=f"TX_{tx_id}",
                label=tx_id,
                type="Transaction",
                complexity_score=5.0,
                lines_of_code=0,
                color=type_colors["Transaction"],
                metadata={"program_name": tx.program_name},
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # 7. Add BMS Mapsets
        for m_name, mapset in portfolio.mapsets.items():
            node = GraphNode(
                id=f"BMS_{m_name}",
                label=m_name,
                type="Mapset",
                complexity_score=float(mapset.total_fields_count),
                lines_of_code=mapset.total_fields_count * 3,
                color=type_colors["Mapset"],
                metadata={"maps_count": len(mapset.maps), "fields_count": mapset.total_fields_count},
            )
            nodes.append(node)
            G.add_node(node.id, **node.dict())

        # -------------------------------------------------------------
        # Connect Edges
        # -------------------------------------------------------------
        # Program -> Program (Static & Dynamic Calls, CICS LINK/XCTL)
        for p_id, p in portfolio.programs.items():
            for called in p.static_calls:
                if called in portfolio.programs:
                    edge = GraphEdge(source=p_id, target=called, type="CALLS", label="CALL")
                    edges.append(edge)
                    G.add_edge(p_id, called, type="CALLS")

            for linked in p.cics_links:
                if linked in portfolio.programs:
                    edge = GraphEdge(source=p_id, target=linked, type="CICS_LINK", label="EXEC CICS LINK")
                    edges.append(edge)
                    G.add_edge(p_id, linked, type="CICS_LINK")

            for xctl in p.cics_xctls:
                if xctl in portfolio.programs:
                    edge = GraphEdge(source=p_id, target=xctl, type="CICS_XCTL", label="EXEC CICS XCTL")
                    edges.append(edge)
                    G.add_edge(p_id, xctl, type="CICS_XCTL")

            # Program -> Copybook
            for cb in p.copybooks_used:
                cb_id = f"CPY_{cb}"
                if G.has_node(cb_id):
                    edge = GraphEdge(source=p_id, target=cb_id, type="USES_COPYBOOK", label="COPY")
                    edges.append(edge)
                    G.add_edge(p_id, cb_id, type="USES_COPYBOOK")

            # Program -> Table
            for tbl in p.sql_tables_accessed:
                tbl_id = f"TBL_{tbl}"
                if G.has_node(tbl_id):
                    edge = GraphEdge(source=p_id, target=tbl_id, type="QUERIES_TABLE", label="EXEC SQL")
                    edges.append(edge)
                    G.add_edge(p_id, tbl_id, type="QUERIES_TABLE")

            # Program -> VSAM
            for vf in p.vsam_files_accessed:
                vsam_id = f"VSAM_{vf}"
                if G.has_node(vsam_id):
                    edge = GraphEdge(source=p_id, target=vsam_id, type="ACCESSES_VSAM", label="READ/WRITE")
                    edges.append(edge)
                    G.add_edge(p_id, vsam_id, type="ACCESSES_VSAM")

        # JCL Job -> Program
        for j_name, job in portfolio.jobs.items():
            job_id = f"JOB_{j_name}"
            for step in job.steps:
                if step.program_name in portfolio.programs:
                    edge = GraphEdge(source=job_id, target=step.program_name, type="EXECUTES", label=f"STEP: {step.step_name}")
                    edges.append(edge)
                    G.add_edge(job_id, step.program_name, type="EXECUTES")

        # CICS Transaction -> Program
        for tx_id, tx in portfolio.transactions.items():
            t_id = f"TX_{tx_id}"
            if tx.program_name in portfolio.programs:
                edge = GraphEdge(source=t_id, target=tx.program_name, type="TRANS_INVOKES", label="TRANSID")
                edges.append(edge)
                G.add_edge(t_id, tx.program_name, type="TRANS_INVOKES")

        # -------------------------------------------------------------
        # Graph Analytics: Centrality & God Objects
        # -------------------------------------------------------------
        god_objects: List[str] = []
        if len(G) > 0:
            deg_centrality = nx.degree_centrality(G)
            sorted_nodes = sorted(deg_centrality.items(), key=lambda x: x[1], reverse=True)
            for nid, cent in sorted_nodes[:5]:
                if cent > 0.2:
                    god_objects.append(nid)

        # Detect Cycles
        cycles_count = len(list(nx.simple_cycles(G))) if len(G) > 0 else 0

        return DependencyGraphData(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
            god_objects=god_objects,
            cycles_detected=cycles_count,
        )

    def calculate_blast_radius(self, portfolio: ApplicationPortfolio, target_node_id: str) -> Dict[str, Any]:
        """
        Calculates the transitive blast radius if target_node_id is modified or fails.
        Traces downstream dependencies across the entire enterprise graph.
        """
        graph_data = self.build_graph(portfolio)
        G = nx.DiGraph()
        for e in graph_data.edges:
            G.add_edge(e.source, e.target, type=e.type)

        # Normalized ID search (handling prefix or bare program name)
        matched_id = None
        for n in graph_data.nodes:
            if n.id.upper() == target_node_id.upper() or n.label.upper() == target_node_id.upper():
                matched_id = n.id
                break

        if not matched_id or not G.has_node(matched_id):
            return {
                "target_node": target_node_id,
                "found": False,
                "impact_level": "None",
                "total_impacted_artifacts": 0,
                "impacted_nodes": [],
            }

        # Transitive dependents (nodes that depend on matched_id) -> Reverse graph traversal
        G_rev = G.reverse()
        descendants = nx.descendants(G_rev, matched_id)

        # Categorize by depth
        impacted: List[Dict[str, Any]] = []
        for d in descendants:
            length = nx.shortest_path_length(G_rev, source=matched_id, target=d)
            node_info = next((n for n in graph_data.nodes if n.id == d), None)
            impacted.append({
                "id": d,
                "label": node_info.label if node_info else d,
                "type": node_info.type if node_info else "Unknown",
                "dependency_depth": length,
            })

        impacted.sort(key=lambda x: (x["dependency_depth"], x["label"]))

        count = len(impacted)
        level = "Critical" if count > 8 else ("High" if count > 4 else ("Medium" if count > 1 else "Low"))

        return {
            "target_node": matched_id,
            "found": True,
            "impact_level": level,
            "total_impacted_artifacts": count,
            "impacted_nodes": impacted,
        }
