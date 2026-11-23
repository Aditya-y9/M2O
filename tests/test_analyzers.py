"""Tests for 8-Dimensional Modernization Analyzers & Twelve-Factor Evaluator."""

import pytest
from modernizeiq.parsers.metadata_loader import MetadataLoader
from modernizeiq.analyzers.portfolio_analyzer import PortfolioAnalyzer


def test_core_banking_assessment():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/core_banking_deposit")

    analyzer = PortfolioAnalyzer()
    results = analyzer.run_assessment(portfolio)

    assert "dimension_scores" in results
    assert len(results["dimension_scores"]) == 8
    assert results["overall_normalized_score"] > 60
    assert len(results["twelve_factor_compliance"]) == 12


def test_policy_admin_monolith_assessment():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/policy_admin_monolith")

    analyzer = PortfolioAnalyzer()
    results = analyzer.run_assessment(portfolio)

    assert len(results["dimension_scores"]) == 8
    # Policy admin has conversational CICS and VSAM files, should flag risks
    risk_titles = [r.title for r in results["risks"]]
    assert any("VSAM" in t or "Conversational" in t or "ALTER" in t for t in risk_titles)
