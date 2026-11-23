"""Security profile parser for RACF, ACF2, and Top Secret definitions."""

from __future__ import annotations
import re
from typing import List, Dict, Optional, Set

from ..models.artifacts import SecurityProfile


class SecurityParser:
    """Parses RACF / ESM commands or security profiles."""

    RE_RDEFINE = re.compile(r"RDEFINE\s+([A-Za-z0-9_-]+)\s+([A-Za-z0-9_.*-]+)", re.IGNORECASE)
    RE_PERMIT = re.compile(r"PERMIT\s+.*?\bACCESS\((.*?)\)", re.IGNORECASE)

    def parse_racf(self, text: str) -> SecurityProfile:
        classes: Set[str] = set()
        has_saf_exits = "ICH" in text.upper() or "RACROUTE" in text.upper() or "EXIT" in text.upper()
        has_surrogate = "SURROGAT" in text.upper()

        for m in self.RE_RDEFINE.finditer(text):
            classes.add(m.group(1).upper())

        compliance = []
        if "PCI" in text.upper():
            compliance.append("PCI-DSS")
        if "SOX" in text.upper():
            compliance.append("SOX")
        if "HIPAA" in text.upper():
            compliance.append("HIPAA")

        return SecurityProfile(
            esm_type="RACF",
            resource_classes_used=sorted(list(classes)),
            has_saf_exits=has_saf_exits,
            has_surrogate_security=has_surrogate,
            compliance_frameworks=compliance,
        )
