"""Parsers for DB2 DDL schemas and VSAM IDCAMS DEFINE CLUSTER statements."""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from ..models.artifacts import DatabaseTable, VsamDataset, VsamType


class DataParser:
    """Parses database and storage definitions (DB2 DDL and VSAM clusters)."""

    RE_CREATE_TABLE = re.compile(
        r"CREATE\s+TABLE\s+([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)\s*\((.*?)\)(?:;|\s+IN\s+)",
        re.IGNORECASE | re.DOTALL,
    )
    RE_PRIMARY_KEY = re.compile(r"PRIMARY\s+KEY\s*\((.*?)\)", re.IGNORECASE)
    RE_CREATE_INDEX = re.compile(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+[A-Za-z0-9_]+\s+ON\s+([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)", re.IGNORECASE)

    RE_DEFINE_CLUSTER = re.compile(
        r"DEFINE\s+CLUSTER\s*\(\s*NAME\s*\(\s*([A-Za-z0-9#@$._-]+)\s*\)(.*?)\)",
        re.IGNORECASE | re.DOTALL,
    )

    def _split_columns(self, body: str) -> List[str]:
        parts = []
        current = []
        depth = 0
        for char in body:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current).strip())
        return [p for p in parts if p]

    def parse_db2_ddl(self, ddl_text: str) -> Dict[str, DatabaseTable]:
        tables: Dict[str, DatabaseTable] = {}

        # Find tables
        for m in self.RE_CREATE_TABLE.finditer(ddl_text):
            full_table_name = m.group(1).upper()
            body = m.group(2)

            schema = "DB2"
            tname = full_table_name
            if "." in full_table_name:
                schema, tname = full_table_name.split(".", 1)

            # Extract columns and primary keys
            definitions = self._split_columns(body)
            columns = []
            pk_cols = []

            for item in definitions:
                u_item = item.strip().upper()
                if u_item.startswith(("PRIMARY", "FOREIGN", "CONSTRAINT", "KEY", "CHECK")):
                    pk_m = self.RE_PRIMARY_KEY.search(item)
                    if pk_m:
                        raw_keys = pk_m.group(1)
                        pk_cols = [k.strip().upper() for k in re.findall(r"[A-Za-z0-9_]+", raw_keys)]
                else:
                    parts = item.split()
                    if parts:
                        col_name = parts[0].strip().upper()
                        if col_name and not col_name.startswith(("-", "/")):
                            columns.append(col_name)

            has_pk = bool(pk_cols) or bool(self.RE_PRIMARY_KEY.search(body))

            tables[tname] = DatabaseTable(
                table_name=tname,
                schema_name=schema,
                columns_count=max(1, len(columns)),
                columns=columns,
                has_primary_key=has_pk,
                primary_key=pk_cols,
                indexes_count=1 if has_pk else 0,
                is_relational=True,
            )

        # Count additional indexes
        for im in self.RE_CREATE_INDEX.finditer(ddl_text):
            target = im.group(1).upper()
            tname = target.split(".", 1)[1] if "." in target else target
            if tname in tables:
                tables[tname].indexes_count += 1

        return tables

    def parse_ddl_text(self, ddl_text: str, file_path: Optional[str] = None) -> List[DatabaseTable]:
        return list(self.parse_db2_ddl(ddl_text).values())

    def parse_vsam_idcams(self, idcams_text: str) -> Dict[str, VsamDataset]:
        vsams: Dict[str, VsamDataset] = {}

        for m in self.RE_DEFINE_CLUSTER.finditer(idcams_text):
            cluster_name = m.group(1).upper()
            params = m.group(2).upper()

            # Determine VSAM type
            if "INDEXED" in params:
                vtype = VsamType.KSDS
            elif "NONINDEXED" in params:
                vtype = VsamType.ESDS
            elif "NUMBERED" in params:
                vtype = VsamType.RRDS
            elif "LINEAR" in params:
                vtype = VsamType.LDS
            else:
                vtype = VsamType.KSDS

            # Extract record length
            rec_len = 80
            rec_m = re.search(r"RECORDSIZE\s*\(\s*([0-9]+)\s+([0-9]+)\s*\)", params)
            if rec_m:
                rec_len = int(rec_m.group(2))

            # Extract keys
            key_len = 0
            key_off = 0
            key_m = re.search(r"KEYS\s*\(\s*([0-9]+)\s+([0-9]+)\s*\)", params)
            if key_m:
                key_len = int(key_m.group(1))
                key_off = int(key_m.group(2))

            # Share options
            share_m = re.search(r"SHAREOPTIONS\s*\(\s*([0-9,\s]+)\s*\)", params)
            share_opts = f"({share_m.group(1).replace(' ', '')})" if share_m else "(2,3)"

            has_aix = "AIX" in cluster_name or "ALTERNATEINDEX" in idcams_text.upper()

            vsams[cluster_name] = VsamDataset(
                cluster_name=cluster_name,
                vsam_type=vtype,
                record_length=rec_len,
                key_length=key_len,
                key_offset=key_off,
                share_options=share_opts,
                has_alternate_index=has_aix,
            )

        return vsams
