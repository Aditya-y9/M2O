"""
Semantic Search Engine for Natural Language Codebase Q&A
Uses sentence-transformers for embedding-based semantic search
"""
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticSearchEngine:
    """Natural language search over mainframe components and dependencies."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with specified embedding model."""
        self.model = SentenceTransformer(model_name)
        self.index = []
        self.metadata = []
        
    def build_index(self, report_data: Dict[str, Any]) -> None:
        """Build searchable index from portfolio and assessment data."""
        documents = []
        meta = []
        
        # Index portfolio components
        portfolio = report_data.get("portfolio", {})
        
        # Programs
        for prog in portfolio.get("programs", []):
            doc = f"Program {prog.get('name', 'Unknown')}: {prog.get('description', '')} Type: {prog.get('program_type', '')} Language: {prog.get('language', '')}"
            documents.append(doc)
            meta.append({
                "type": "program",
                "id": prog.get("id", ""),
                "name": prog.get("name", ""),
                "risk_level": self._calculate_component_risk(prog, report_data),
                "details": prog
            })
        
        # Data stores
        for ds in portfolio.get("data_stores", []):
            doc = f"Database {ds.get('name', 'Unknown')}: Type {ds.get('type', '')} Access pattern: {ds.get('access_pattern', '')}"
            documents.append(doc)
            meta.append({
                "type": "data_store",
                "id": ds.get("id", ""),
                "name": ds.get("name", ""),
                "risk_level": "medium",
                "details": ds
            })
        
        # Transactions
        for txn in portfolio.get("transactions", []):
            doc = f"Transaction {txn.get('name', 'Unknown')}: {txn.get('description', '')} Type: {txn.get('txn_type', '')}"
            documents.append(doc)
            meta.append({
                "type": "transaction",
                "id": txn.get("id", ""),
                "name": txn.get("name", ""),
                "risk_level": "high" if txn.get("txn_type") == "online" else "medium",
                "details": txn
            })
        
        # Jobs
        for job in portfolio.get("jobs", []):
            doc = f"Batch Job {job.get('name', 'Unknown')}: {job.get('description', '')} Schedule: {job.get('schedule', '')}"
            documents.append(doc)
            meta.append({
                "type": "job",
                "id": job.get("id", ""),
                "name": job.get("name", ""),
                "risk_level": "medium",
                "details": job
            })
        
        # Index risks from assessment
        assessment = report_data.get("assessment_report", {})
        for risk in assessment.get("risks", []):
            doc = f"Risk: {risk.get('title', '')} - {risk.get('description', '')} Severity: {risk.get('severity', '')} Mitigation: {risk.get('mitigation_strategy', '')}"
            documents.append(doc)
            meta.append({
                "type": "risk",
                "id": f"risk_{len(meta)}",
                "name": risk.get("title", ""),
                "risk_level": risk.get("severity", "medium"),
                "details": risk
            })
        
        # Generate embeddings
        if documents:
            self.index = self.model.encode(documents, convert_to_numpy=True)
            self.metadata = meta
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search using natural language query.
        
        Args:
            query: Natural language question (e.g., "What are the riskiest database components?")
            top_k: Number of results to return
            
        Returns:
            List of matching components with scores and metadata
        """
        if not self.index or len(self.index) == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Calculate cosine similarity
        similarities = np.dot(self.index, query_embedding) / (
            np.linalg.norm(self.index, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Similarity threshold
                result = self.metadata[idx].copy()
                result["relevance_score"] = float(similarities[idx])
                results.append(result)
        
        return results
    
    def _calculate_component_risk(self, component: Dict[str, Any], report_data: Dict[str, Any]) -> str:
        """Calculate risk level for a component based on graph data."""
        graph = report_data.get("dependency_graph", {})
        nodes = {n.get("id"): n for n in graph.get("nodes", [])}
        edges = graph.get("edges", [])
        
        comp_id = component.get("id", "")
        
        # Count dependencies
        in_degree = sum(1 for e in edges if e.get("target") == comp_id)
        out_degree = sum(1 for e in edges if e.get("source") == comp_id)
        
        # Risk calculation (same as dashboard)
        risk_score = (in_degree * 2 + out_degree)
        
        if risk_score > 15:
            return "high"
        elif risk_score > 8:
            return "medium"
        else:
            return "low"


def create_conversational_response(query: str, results: List[Dict[str, Any]]) -> str:
    """Generate natural language response from search results."""
    if not results:
        return f"I couldn't find anything matching '{query}' in the current portfolio. Try rephrasing your question."
    
    # Analyze query intent
    query_lower = query.lower()
    
    if "risk" in query_lower or "dangerous" in query_lower or "problem" in query_lower:
        high_risk = [r for r in results if r.get("risk_level") == "high"]
        if high_risk:
            components = ", ".join([r.get("name", "Unknown") for r in high_risk[:3]])
            return f"The highest-risk components are: {components}. These have the most dependencies and would cause significant blast radius if modified."
        else:
            return f"Based on your query, I found {len(results)} components. The riskiest is {results[0].get('name')} (relevance: {results[0].get('relevance_score', 0):.0%})."
    
    elif "database" in query_lower or "data" in query_lower:
        data_stores = [r for r in results if r.get("type") == "data_store"]
        if data_stores:
            names = ", ".join([r.get("name", "Unknown") for r in data_stores[:3]])
            return f"Found {len(data_stores)} database components: {names}."
        else:
            return f"Found {len(results)} components related to data. Top match: {results[0].get('name')}."
    
    elif "batch" in query_lower or "job" in query_lower:
        jobs = [r for r in results if r.get("type") == "job"]
        if jobs:
            names = ", ".join([r.get("name", "Unknown") for r in jobs[:3]])
            return f"Found {len(jobs)} batch jobs: {names}."
        else:
            return f"Top match for batch/job query: {results[0].get('name')}."
    
    elif "payment" in query_lower or "transaction" in query_lower:
        txns = [r for r in results if r.get("type") == "transaction"]
        if txns:
            names = ", ".join([r.get("name", "Unknown") for r in txns[:3]])
            return f"Found {len(txns)} transaction components: {names}."
        else:
            return f"Top match: {results[0].get('name')} (relevance: {results[0].get('relevance_score', 0):.0%})."
    
    # Default response
    top_result = results[0]
    return f"Found {len(results)} matches. Top result: {top_result.get('name')} ({top_result.get('type')}) with {top_result.get('relevance_score', 0):.0%} relevance."
