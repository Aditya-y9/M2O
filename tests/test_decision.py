"""Tests for Target Platform Decision Engine (OCP vs VM)."""

import pytest
from modernizeiq.parsers.metadata_loader import MetadataLoader
from modernizeiq.analyzers.portfolio_analyzer import PortfolioAnalyzer
from modernizeiq.decision.platform_evaluator import TargetPlatformDecisionEngine
from modernizeiq.models.assessment import TargetPlatform


def test_core_banking_recommends_ocp():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/core_banking_deposit")

    analyzer = PortfolioAnalyzer()
    assessment = analyzer.run_assessment(portfolio)

    decision_engine = TargetPlatformDecisionEngine()
    decision = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment["dimension_scores"],
        risks=assessment["risks"],
        overall_score=assessment["overall_normalized_score"],
    )

    # Core banking has relational DB2, pseudo-conversational CICS, no VSAM
    # OpenShift (OCP) must be the primary recommendation
    assert decision["primary_platform"] == TargetPlatform.OPENSHIFT
    assert decision["ocp_score"] > decision["vm_score"]
    assert "adr" in decision
    assert decision["adr"]["status"] == "Accepted"


def test_policy_admin_recommends_vm():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/policy_admin_monolith")

    analyzer = PortfolioAnalyzer()
    assessment = analyzer.run_assessment(portfolio)

    decision_engine = TargetPlatformDecisionEngine()
    decision = decision_engine.evaluate(
        portfolio=portfolio,
        dimension_scores=assessment["dimension_scores"],
        risks=assessment["risks"],
        overall_score=assessment["overall_normalized_score"],
    )

    # Policy admin has conversational CICS and VSAM KSDS files
    # Should penalize OCP and recommend Linux VM
    assert decision["primary_platform"] == TargetPlatform.LINUX_VM
    assert decision["vm_score"] >= decision["ocp_score"]
