"""Parsers for CICS CSD definitions and 3270 BMS (Basic Mapping Support) screens."""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from ..models.artifacts import CicsTransaction, BmsMapset, BmsMap


class CicsCsdParser:
    """Parses CICS CSD (CICS System Definition) / RDO statements."""

    RE_DEFINE_TRANS = re.compile(
        r"DEFINE\s+TRANSACTION\s*\(\s*([A-Za-z0-9]+)\s*\).*?PROGRAM\s*\(\s*([A-Za-z0-9_-]+)\s*\)",
        re.IGNORECASE | re.DOTALL,
    )
    RE_DESCRIPTION = re.compile(r"DESCRIPTION\s*\(\s*['\"](.*?)['\"]\s*\)", re.IGNORECASE)

    def parse_csd(self, text: str) -> Dict[str, CicsTransaction]:
        transactions: Dict[str, CicsTransaction] = {}
        for m in self.RE_DEFINE_TRANS.finditer(text):
            trans_id = m.group(1).upper()
            program = m.group(2).upper()
            block = m.group(0)

            desc_m = self.RE_DESCRIPTION.search(block)
            desc = desc_m.group(1) if desc_m else f"Transaction {trans_id}"

            transactions[trans_id] = CicsTransaction(
                trans_id=trans_id,
                initial_program=program,
                description=desc,
                is_restartable=True,
            )
        return transactions


class BmsParser:
    """Parses 3270 BMS (Basic Mapping Support) macro definitions."""

    RE_MAPSET = re.compile(r"^([A-Za-z0-9_-]+)\s+DFHMSD\s+TYPE=([A-Za-z0-9&]+)", re.IGNORECASE | re.MULTILINE)
    RE_MAP = re.compile(r"^([A-Za-z0-9_-]+)\s+DFHMDI\s+", re.IGNORECASE | re.MULTILINE)
    RE_FIELD = re.compile(r"^\s*(?:[A-Za-z0-9_-]+)?\s+DFHMDF\s+(.*)$", re.IGNORECASE | re.MULTILINE)

    def parse_code(self, bms_text: str, file_path: Optional[str] = None) -> BmsMapset:
        mapset_match = self.RE_MAPSET.search(bms_text)
        mapset_name = mapset_match.group(1).upper() if mapset_match else "UNKNOWN_MAPSET"
        if file_path and mapset_name == "UNKNOWN_MAPSET":
            mapset_name = Path(file_path).stem.upper()

        map_names = self.RE_MAP.findall(bms_text)
        fields = self.RE_FIELD.findall(bms_text)

        has_cursor = "ATTRB=(...IC" in bms_text.upper() or "CURSOR" in bms_text.upper() or ",IC," in bms_text.upper() or ",IC)" in bms_text.upper() or "(IC)" in bms_text.upper() or "IC" in bms_text.upper()
        has_mdt = "ATTRB=(...MDT" in bms_text.upper() or "MDT" in bms_text.upper() or "FSET" in bms_text.upper()

        # Detect PF Key bindings mentioned in comments or macros
        pf_keys = set(re.findall(r"\bPF([0-9]{1,2})\b", bms_text, re.IGNORECASE))
        pf_keys_sorted = sorted([f"PF{k}" for k in pf_keys], key=lambda x: int(x[2:]))

        bms_maps: List[BmsMap] = []
        if map_names:
            for m_name in map_names:
                bms_maps.append(
                    BmsMap(
                        map_name=m_name.upper(),
                        has_cursor_positioning=has_cursor,
                        modified_data_tags=has_mdt,
                        fields_count=len(fields),
                    )
                )
        else:
            bms_maps.append(
                BmsMap(
                    map_name=mapset_name,
                    has_cursor_positioning=has_cursor,
                    modified_data_tags=has_mdt,
                    fields_count=len(fields),
                )
            )

        return BmsMapset(
            mapset_name=mapset_name,
            file_path=file_path,
            maps_count=max(1, len(bms_maps)),
            maps=bms_maps,
            total_fields=len(fields),
            has_cursor_logic=has_cursor,
            has_mdt_logic=has_mdt,
            pf_keys_used=pf_keys_sorted,
        )

    def parse_text(self, bms_text: str, file_path: Optional[str] = None) -> BmsMapset:
        return self.parse_code(bms_text, file_path=file_path)

    def parse_file(self, file_path: str) -> BmsMapset:
        content = Path(file_path).read_text(encoding="latin-1", errors="replace")
        return self.parse_code(content, file_path=file_path)
