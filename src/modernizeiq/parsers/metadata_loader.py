"""Unified Application Portfolio Ingestion and Artifact Linker."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, Any

from ..models.artifacts import (
    ApplicationPortfolio,
    CobolProgram,
    Copybook,
    JclJob,
    CicsTransaction,
    BmsMapset,
    DatabaseTable,
    VsamDataset,
    SecurityProfile,
    NonFunctionalRequirements,
)
from .cobol_parser import CobolParser
from .jcl_parser import JclParser
from .bms_parser import BmsParser, CicsCsdParser
from .data_parser import DataParser
from .security_parser import SecurityParser


class MetadataLoader:
    """Loads and links mainframe application portfolios from directories or JSON metadata."""

    def __init__(self):
        self.cobol_parser = CobolParser()
        self.jcl_parser = JclParser()
        self.bms_parser = BmsParser()
        self.csd_parser = CicsCsdParser()
        self.data_parser = DataParser()
        self.security_parser = SecurityParser()

    def load_from_directory(self, app_dir: str) -> ApplicationPortfolio:
        """Scan a folder structure, parse all mainframe artifacts, and link relationships."""
        root = Path(app_dir)
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Application directory not found: {app_dir}")

        app_id = root.name.upper()
        app_name = root.name.replace("_", " ").title()
        description = f"Legacy mainframe application portfolio: {app_name}"
        domain = "General Enterprise"
        owner_team = "Mainframe Core Services"
        security = SecurityProfile()
        nfrs = NonFunctionalRequirements()

        programs: Dict[str, CobolProgram] = {}
        copybooks: Dict[str, Copybook] = {}
        jobs: Dict[str, JclJob] = {}
        transactions: Dict[str, CicsTransaction] = {}
        mapsets: Dict[str, BmsMapset] = {}
        tables: Dict[str, DatabaseTable] = {}
        vsam_files: Dict[str, VsamDataset] = {}

        # 1. Check for portfolio.json, metadata.json or app_profile.json
        meta_file = root / "portfolio.json"
        if not meta_file.exists():
            meta_file = root / "metadata.json"
        if not meta_file.exists():
            meta_file = root / "app_profile.json"

        if meta_file.exists():
            try:
                meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
                app_id = meta_data.get("app_id", app_id)
                app_name = meta_data.get("app_name", app_name)
                description = meta_data.get("description", description)
                domain = meta_data.get("business_domain", domain)
                owner_team = meta_data.get("owner_team", owner_team)

                if "security" in meta_data:
                    security = SecurityProfile(**meta_data["security"])
                elif "racf_profiles" in meta_data:
                    res_classes = list({p.get("resource_class", "FACILITY") for p in meta_data["racf_profiles"] if isinstance(p, dict)})
                    security = SecurityProfile(esm_type="RACF", resource_classes_used=res_classes)

                nfr_dict = meta_data.get("nfrs") or meta_data.get("nfr")
                if nfr_dict and isinstance(nfr_dict, dict):
                    # Clean SLA if string with %
                    sla_val = nfr_dict.get("availability_sla", 99.95)
                    if isinstance(sla_val, str):
                        try:
                            sla_val = float(sla_val.replace("%", "").strip())
                        except ValueError:
                            sla_val = 99.95
                    tps = nfr_dict.get("peak_throughput_tps") or nfr_dict.get("target_tps") or 500
                    lat = nfr_dict.get("target_latency_p99_ms") or nfr_dict.get("max_latency_p99_ms") or 50.0
                    batch_w = nfr_dict.get("batch_window_hours") or nfr_dict.get("daily_batch_window_hours") or 4.0
                    nfrs = NonFunctionalRequirements(
                        peak_throughput_tps=int(tps),
                        target_latency_p99_ms=float(lat),
                        availability_sla=float(sla_val),
                        batch_window_hours=float(batch_w),
                        rto_minutes=int(nfr_dict.get("rto_minutes", 60)),
                        rpo_minutes=int(nfr_dict.get("rpo_minutes", 15)),
                    )

                # In case metadata provides pre-defined entities
                if "tables" in meta_data:
                    for t_name, t_val in meta_data["tables"].items():
                        tables[t_name] = DatabaseTable(**t_val)
                if "vsam_files" in meta_data:
                    for v_name, v_val in meta_data["vsam_files"].items():
                        vsam_files[v_name] = VsamDataset(**v_val)
                if "transactions" in meta_data:
                    for tx_id, tx_val in meta_data["transactions"].items():
                        transactions[tx_id] = CicsTransaction(**tx_val)
            except Exception as e:
                print(f"Warning loading metadata from {meta_file.name}: {e}")

        # 2. Parse COBOL programs
        cobol_exts = {".cbl", ".cob", ".cobol", ".pco"}
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix.lower() in cobol_exts or "cobol" in str(f.parent).lower()):
                try:
                    prog = self.cobol_parser.parse_file(str(f))
                    programs[prog.program_id] = prog
                except Exception as e:
                    print(f"Error parsing COBOL file {f}: {e}")

        # 3. Parse Copybooks
        cpy_exts = {".cpy", ".copybook", ".cpb"}
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix.lower() in cpy_exts or "copybook" in str(f.parent).lower()):
                try:
                    cb_name = f.stem.upper()
                    text = f.read_text(encoding="latin-1", errors="replace")
                    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith(("*", "/"))]
                    copybooks[cb_name] = Copybook(
                        name=cb_name,
                        file_path=str(f),
                        field_count=len(lines),
                        total_length_bytes=len(lines) * 10,
                        has_occurs="OCCURS" in text.upper(),
                        has_redefines="REDEFINES" in text.upper(),
                    )
                except Exception as e:
                    print(f"Error parsing Copybook {f}: {e}")

        # 4. Parse JCL Jobs
        jcl_exts = {".jcl", ".job", ".prc", ".proc"}
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix.lower() in jcl_exts or "jcl" in str(f.parent).lower()):
                try:
                    job = self.jcl_parser.parse_file(str(f))
                    jobs[job.job_name] = job
                except Exception as e:
                    print(f"Error parsing JCL file {f}: {e}")

        # 5. Parse BMS Screens
        bms_exts = {".bms", ".map"}
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix.lower() in bms_exts or "bms" in str(f.parent).lower()):
                try:
                    mapset = self.bms_parser.parse_file(str(f))
                    mapsets[mapset.mapset_name] = mapset
                except Exception as e:
                    print(f"Error parsing BMS file {f}: {e}")

        # 6. Parse DDL / IDCAMS
        sql_exts = {".sql", ".ddl", ".idcams"}
        for f in root.rglob("*"):
            if f.is_file() and (f.suffix.lower() in sql_exts or "ddl" in str(f.parent).lower()):
                try:
                    content = f.read_text(encoding="latin-1", errors="replace")
                    if "CREATE TABLE" in content.upper():
                        parsed_tbls = self.data_parser.parse_db2_ddl(content)
                        tables.update(parsed_tbls)
                    if "DEFINE CLUSTER" in content.upper():
                        parsed_vsam = self.data_parser.parse_vsam_idcams(content)
                        vsam_files.update(parsed_vsam)
                except Exception as e:
                    print(f"Error parsing DDL/IDCAMS {f}: {e}")

        # 7. Cross-Artifact Relationship Linkage
        # Link copybooks to programs
        for prog in programs.values():
            for cb in prog.copybooks_used:
                if cb in copybooks:
                    if prog.program_id not in copybooks[cb].referenced_by_programs:
                        copybooks[cb].referenced_by_programs.append(prog.program_id)
                else:
                    # Register implicit copybook if not found as file
                    copybooks[cb] = Copybook(
                        name=cb,
                        field_count=10,
                        referenced_by_programs=[prog.program_id],
                    )

            # Link DB2 tables to programs
            for tbl in prog.sql_tables_accessed:
                if tbl in tables:
                    if prog.program_id not in tables[tbl].accessed_by_programs:
                        tables[tbl].accessed_by_programs.append(prog.program_id)
                else:
                    tables[tbl] = DatabaseTable(
                        table_name=tbl,
                        accessed_by_programs=[prog.program_id],
                    )

            # Link VSAM files to programs
            for vf in prog.vsam_files_accessed:
                if vf in vsam_files:
                    if prog.program_id not in vsam_files[vf].accessed_by_programs:
                        vsam_files[vf].accessed_by_programs.append(prog.program_id)
                else:
                    vsam_files[vf] = VsamDataset(
                        cluster_name=vf,
                        accessed_by_programs=[prog.program_id],
                    )

        # Link BMS mapsets to programs
        for mapset in mapsets.values():
            for prog_id, prog in programs.items():
                if mapset.mapset_name in prog.copybooks_used or mapset.mapset_name in prog.cics_links:
                    if prog_id not in mapset.associated_programs:
                        mapset.associated_programs.append(prog_id)

        # Build portfolio
        portfolio = ApplicationPortfolio(
            app_id=app_id,
            app_name=app_name,
            description=description,
            business_domain=domain,
            owner_team=owner_team,
            programs=programs,
            copybooks=copybooks,
            jobs=jobs,
            transactions=transactions,
            mapsets=mapsets,
            tables=tables,
            vsam_files=vsam_files,
            security=security,
            nfrs=nfrs,
        )

        return portfolio

    def load_from_json(self, json_path_or_str: str) -> ApplicationPortfolio:
        """Load portfolio directly from a serialized JSON file or string."""
        path = Path(json_path_or_str)
        if path.exists() and path.is_file():
            raw_text = path.read_text(encoding="utf-8")
        else:
            raw_text = json_path_or_str

        data = json.loads(raw_text)
        return ApplicationPortfolio(**data)
