"""Parser for Mainframe JCL (Job Control Language) job streams and batch workflows."""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from ..models.artifacts import JclJob, JclStep, JclDatasetRef


RE_JOB_CARD = re.compile(r"^//([A-Za-z0-9#@$]+)\s+JOB\b", re.IGNORECASE)
RE_EXEC_STMT = re.compile(r"^//([A-Za-z0-9#@$]+)\s+EXEC\s+(?:PGM=([A-Za-z0-9#@$]+)|PROC=([A-Za-z0-9#@$]+)|([A-Za-z0-9#@$]+))", re.IGNORECASE)
RE_DD_STMT = re.compile(r"^//([A-Za-z0-9#@$]+)\s+DD\s+(.*)$", re.IGNORECASE)
RE_DSN = re.compile(r"DSN=([A-Za-z0-9#@$.\(\)+-]+)", re.IGNORECASE)
RE_DISP = re.compile(r"DISP=\((.*?)\)", re.IGNORECASE)
RE_COND = re.compile(r"COND=\((.*?)\)", re.IGNORECASE)

KNOWN_UTILITIES = {
    "SORT", "DFSORT", "SYNCSORT", "IDCAMS", "IEBGENER", "IEBCOPY",
    "IEBDG", "IEBEDIT", "IEBUPDTE", "IEHLIST", "IKJEFT01", "DSNTIAR"
}


class JclParser:
    """Parses JCL streams to extract job topologies, data lineage, and step orchestration."""

    def parse_code(self, jcl_text: str, file_path: Optional[str] = None) -> JclJob:
        lines = jcl_text.splitlines()
        job_name = "UNKNOWN_JOB"
        steps: List[JclStep] = []
        current_step: Optional[JclStep] = None
        has_gdg = False
        has_conditional = False
        has_checkpoint = False

        for raw_line in lines:
            line = raw_line.strip()
            # Ignore JCL comments
            if line.startswith("//*") or not line.startswith("//"):
                continue

            # 1. Match JOB Card
            job_match = RE_JOB_CARD.match(line)
            if job_match:
                job_name = job_match.group(1).upper()
                continue

            # 2. Match EXEC Statement
            exec_match = RE_EXEC_STMT.match(line)
            if exec_match:
                step_name = exec_match.group(1).upper()
                pgm = exec_match.group(2)
                proc = exec_match.group(3)
                default_target = exec_match.group(4)

                target_name = (pgm or proc or default_target or "UNKNOWN").upper()
                is_proc = bool(proc) or (not pgm and bool(default_target))

                # Check COND codes
                cond_match = RE_COND.search(line)
                cond_val = cond_match.group(1) if cond_match else None
                cond_codes_list = [cond_val] if cond_val else []
                if cond_val:
                    has_conditional = True

                is_util = target_name in KNOWN_UTILITIES

                current_step = JclStep(
                    step_name=step_name,
                    program_executed=target_name,
                    is_proc=is_proc,
                    cond_codes=cond_codes_list,
                    is_utility=is_util,
                )
                steps.append(current_step)
                continue

            # 3. Match DD Statement
            dd_match = RE_DD_STMT.match(line)
            if dd_match and current_step is not None:
                dd_name = dd_match.group(1).upper()
                dd_params = dd_match.group(2)

                dsn_match = RE_DSN.search(dd_params)
                if dsn_match:
                    dsn = dsn_match.group(1).upper()
                    # Check for GDG generation notation, e.g. DSN=PROD.GDG(+1) or (0)
                    is_gdg = "(+" in dsn or "(-" in dsn or "(0)" in dsn
                    if is_gdg:
                        has_gdg = True

                    disp_match = RE_DISP.search(dd_params)
                    disp_str = disp_match.group(1).upper() if disp_match else ""

                    current_step.datasets.append(JclDatasetRef(dsn=dsn, is_gdg=is_gdg, disp=disp_str))

                    if "NEW" in disp_str or "MOD" in disp_str:
                        current_step.output_datasets.append(dsn)
                    else:
                        current_step.input_datasets.append(dsn)

                    if "SHR" in disp_str:
                        current_step.disposition_share = True

                # Check for checkpoint/restart DDs
                if dd_name in ("SYSCHK", "SYSCKEOV"):
                    has_checkpoint = True

        if job_name == "UNKNOWN_JOB" and file_path:
            job_name = Path(file_path).stem.upper()

        return JclJob(
            job_name=job_name,
            file_path=file_path,
            steps=steps,
            has_gdg=has_gdg,
            has_conditional_steps=has_conditional,
            has_checkpoint_restart=has_checkpoint,
            estimated_runtime_minutes=max(10, len(steps) * 15),
        )

    def parse_text(self, jcl_text: str, file_path: Optional[str] = None) -> JclJob:
        return self.parse_code(jcl_text, file_path=file_path)

    def parse_file(self, file_path: str) -> JclJob:
        content = Path(file_path).read_text(encoding="latin-1", errors="replace")
        return self.parse_code(content, file_path=file_path)
