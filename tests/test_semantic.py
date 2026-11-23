"""Tests for all-MiniLM-L6-v2 Semantic Clustering & 2D Projection."""

import pytest
from modernizeiq.parsers.metadata_loader import MetadataLoader
from modernizeiq.semantic.embedder import SemanticEmbedder
from modernizeiq.semantic.clusterer import SemanticClusterer


def test_semantic_embedding():
    embedder = SemanticEmbedder()
    vec = embedder.embed_text("COBOL banking ledger balance inquiry CICS DB2 SQL")

    assert len(vec) == 384
    # Check L2 normalization
    norm = sum(x**2 for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-4


def test_semantic_clustering_and_2d_projection():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/core_banking_deposit")

    clusterer = SemanticClusterer()
    clusters, coords = clusterer.cluster_portfolio(portfolio)

    assert len(clusters) > 0
    assert len(coords) == len(portfolio.cobol_programs)
    for c in coords:
        assert "x" in c and "y" in c
        assert "program_id" in c
        assert "cluster" in c
