"""Semantic Domain Clustering and Microservice Boundary Decomposition."""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from ..models.artifacts import ApplicationPortfolio, CobolProgram
from ..models.graph import DomainCluster
from .embedder import SemanticEmbedder


class SemanticClusterer:
    """Groups mainframe programs into bounded-context microservice candidates."""

    def __init__(self, embedder: SemanticEmbedder = None):
        self.embedder = embedder or SemanticEmbedder()

    def cluster_portfolio(
        self, portfolio: ApplicationPortfolio, n_clusters: int = None
    ) -> Tuple[List[DomainCluster], Dict[str, Tuple[float, float]]]:
        """
        Decomposes portfolio programs into semantic microservice clusters.
        Returns:
            Tuple of (List[DomainCluster], Dict[program_id, (x, y) 2D projection coords])
        """
        programs = list(portfolio.programs.values())
        if not programs:
            return [], {}

        # 1. Build rich semantic text representations
        corpus: List[str] = []
        prog_ids: List[str] = []
        for p in programs:
            prog_ids.append(p.program_id)
            corpus.append(self._create_program_text(p))

        # 2. Compute 384-dim embeddings
        embeddings = self.embedder.embed_texts(corpus)

        # 3. Determine optimal number of clusters
        k = n_clusters
        if not k:
            if len(programs) <= 3:
                k = 1
            elif len(programs) <= 6:
                k = 2
            elif len(programs) <= 12:
                k = 3
            else:
                k = min(6, max(3, len(programs) // 4))

        k = min(k, len(programs))

        # 4. Perform Agglomerative Hierarchical Clustering with cosine distance
        if k > 1:
            clustering = AgglomerativeClustering(
                n_clusters=k,
                metric="cosine",
                linkage="average",
            )
            labels = clustering.fit_predict(embeddings)
        else:
            labels = np.zeros(len(programs), dtype=int)

        # 5. Compute 2D PCA projection for visual mapping
        coords_2d = self._compute_2d_coordinates(embeddings, prog_ids)

        # 6. Build Domain Clusters with semantic cohesion
        clusters: List[DomainCluster] = []
        for cluster_idx in range(k):
            member_indices = [i for i, lbl in enumerate(labels) if lbl == cluster_idx]
            member_progs = [programs[i] for i in member_indices]
            member_ids = [p.program_id for p in member_progs]

            if not member_ids:
                continue

            cluster_embeddings = embeddings[member_indices]
            if len(member_indices) > 1:
                sim_matrix = cosine_similarity(cluster_embeddings)
                # Average off-diagonal similarity
                mask = ~np.eye(len(member_indices), dtype=bool)
                cohesion = float(sim_matrix[mask].mean()) if mask.any() else 1.0
            else:
                cohesion = 1.0

            # Derive cluster name and description based on dominant vocabulary
            cluster_name, domain_desc = self._derive_cluster_identity(member_progs, cluster_idx + 1)

            # Check if this cluster is a good candidate for containerization
            all_cics_conv = any(p.is_conversational for p in member_progs)
            all_2pc = any(p.cics_syncpoints_count > 0 and p.vsam_files_accessed and p.sql_tables_accessed for p in member_progs)
            readiness = "Low (Stateful / 2PC Blocker)" if (all_cics_conv or all_2pc) else "High (Stateless Microservice)"

            clusters.append(DomainCluster(
                cluster_id=f"CLUSTER-{cluster_idx + 1}",
                cluster_name=cluster_name,
                business_domain=domain_desc,
                programs=member_ids,
                cohesion_score=round(max(0.0, min(1.0, cohesion)), 2),
                suggested_target=readiness,
            ))

        coords_list: List[Dict[str, Any]] = []
        for i, pid in enumerate(prog_ids):
            pt = coords_2d.get(pid, (0.0, 0.0))
            cluster_label = f"CLUSTER-{labels[i] + 1}"
            coords_list.append({
                "program_id": pid,
                "x": pt[0],
                "y": pt[1],
                "cluster": cluster_label,
            })

        return clusters, coords_list

    def _create_program_text(self, p: CobolProgram) -> str:
        tokens = [p.program_id]
        if p.description:
            tokens.append(p.description)
        tokens.extend(p.copybooks_used)
        tokens.extend(p.sql_tables_accessed)
        tokens.extend(p.vsam_files_accessed)
        tokens.extend(p.cics_links)
        tokens.extend(p.cics_xctls)
        if p.is_cics_program:
            tokens.append("cics online transaction bms screen")
        if p.is_batch_program:
            tokens.append("jcl batch processing dataset")
        if p.sql_queries_count > 0:
            tokens.append("relational database db2 sql")
        if p.cics_syncpoints_count > 0:
            tokens.append("transaction syncpoint commit rollback")
        return " ".join(tokens)

    def _compute_2d_coordinates(
        self, embeddings: np.ndarray, prog_ids: List[str]
    ) -> Dict[str, Tuple[float, float]]:
        """Projects high-dim embeddings into 2D space scaled to [-100, 100] for visual charting."""
        n_samples = len(prog_ids)
        if n_samples == 0:
            return {}
        if n_samples == 1:
            return {prog_ids[0]: (0.0, 0.0)}

        if n_samples == 2:
            pca = PCA(n_components=1)
            p1d = pca.fit_transform(embeddings).flatten()
            scale = 80.0 / (np.max(np.abs(p1d)) + 1e-6)
            return {
                prog_ids[0]: (-float(p1d[0] * scale), 0.0),
                prog_ids[1]: (float(p1d[1] * scale), 0.0),
            }

        pca = PCA(n_components=2)
        proj_2d = pca.fit_transform(embeddings)

        # Scale to [-90, 90] for dashboard canvas display
        max_abs = np.max(np.abs(proj_2d)) + 1e-6
        scaled = (proj_2d / max_abs) * 85.0

        coords: Dict[str, Tuple[float, float]] = {}
        for i, pid in enumerate(prog_ids):
            coords[pid] = (round(float(scaled[i, 0]), 1), round(float(scaled[i, 1]), 1))
        return coords

    def _derive_cluster_identity(self, progs: List[CobolProgram], cluster_num: int) -> Tuple[str, str]:
        all_text = " ".join(self._create_program_text(p) for p in progs).upper()

        if any(w in all_text for w in ["ACCOUNT", "BALANCE", "DEPOSIT", "WITHDRAW", "SAVINGS", "CHECKING"]):
            return f"Account Services ({cluster_num})", "Core Account Management & Balance Ledger"
        elif any(w in all_text for w in ["PAYMENT", "TRANSFER", "CLEARING", "SETTLE", "WIRE", "CARD"]):
            return f"Payment Services ({cluster_num})", "Transaction Routing, Payments & Settlement"
        elif any(w in all_text for w in ["CUSTOMER", "CLIENT", "PARTY", "PROFILE", "ADDRESS", "KYC"]):
            return f"Customer Domain ({cluster_num})", "Customer Identity, Profiles & Preferences"
        elif any(w in all_text for w in ["LOAN", "MORTGAGE", "CREDIT", "COLLATERAL", "DEBT"]):
            return f"Lending Domain ({cluster_num})", "Loan Servicing, Credit Scoring & Amortization"
        elif any(w in all_text for w in ["REWARD", "LOYALTY", "POINT", "TIER", "DISCOUNT"]):
            return f"Loyalty Domain ({cluster_num})", "Customer Loyalty, Points Ledger & Promotions"
        elif any(w in all_text for w in ["AUDIT", "SECURITY", "AUTH", "LOG", "RACF"]):
            return f"Security & Audit ({cluster_num})", "Identity, Access Control & Compliance Logging"
        elif any(w in all_text for w in ["REPORT", "BATCH", "EXTRACT", "STATEMENT", "MONTH"]):
            return f"Reporting Services ({cluster_num})", "Financial Statements & Analytical Reporting"
        else:
            return f"Business Subsystem {cluster_num}", "Modular Business Logic Component"
