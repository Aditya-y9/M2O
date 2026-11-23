"""Base analyzer interface for ModernizeIQ dimensions."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple
from ..models.artifacts import ApplicationPortfolio
from ..models.assessment import DimensionScore, RiskFactor


class BaseDimensionAnalyzer(ABC):
    """Abstract base class for all 8 dimension analyzers."""

    @property
    @abstractmethod
    def dimension_name(self) -> str:
        """Name of the dimension."""
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight of the dimension in the overall composite score (0.0 to 1.0)."""
        pass

    @abstractmethod
    def analyze(self, portfolio: ApplicationPortfolio) -> Tuple[DimensionScore, List[RiskFactor]]:
        """
        Analyze the application portfolio across this dimension.
        Returns:
            Tuple of (DimensionScore, List[RiskFactor])
        """
        pass
