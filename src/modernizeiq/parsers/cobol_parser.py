"""Enterprise COBOL parser and static analysis engine."""

from __future__ import annotations
import math
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from ..models.artifacts import CobolProgram, CobolDialect, ProgramType, CicsStatePattern


# Regular expressions for COBOL structural elements
RE_PROGRAM_ID = re.compile(r"\bPROGRAM-ID\.\s+([A-Za-z0-9_-]+)", re.IGNORECASE)
RE_DIVISION = re.compile(r"\b(IDENTIFICATION|ENVIRONMENT|DATA|PROCEDURE)\s+DIVISION\b", re.IGNORECASE)
RE_SECTION = re.compile(r"^\s*([A-Za-z0-9_-]+)\s+SECTION\b", re.IGNORECASE)
RE_PARAGRAPH = re.compile(r"^\s*([A-Za-z0-9_-]+)\.\s*$", re.IGNORECASE)

# Invocations and Dependencies
RE_COPY = re.compile(r"\bCOPY\s+([A-Za-z0-9_-]+)(?:\s+REPLACING\s+.*?)?\.?", re.IGNORECASE)
RE_STATIC_CALL = re.compile(r"\bCALL\s+['\"]([A-Za-z0-9_-]+)['\"]", re.IGNORECASE)
RE_DYNAMIC_CALL = re.compile(r"\bCALL\s+([A-Za-z0-9_-]+)(?!\s*['\"])", re.IGNORECASE)

# CICS Statements
RE_EXEC_CICS = re.compile(r"EXEC\s+CICS\s+(.*?)\s+END-EXEC", re.IGNORECASE | re.DOTALL)
RE_CICS_LINK = re.compile(r"\bLINK\s+PROGRAM\s*\(\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*\)", re.IGNORECASE)
RE_CICS_XCTL = re.compile(r"\bXCTL\s+PROGRAM\s*\(\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*\)", re.IGNORECASE)
RE_CICS_START = re.compile(r"\bSTART\s+TRANSID\s*\(\s*['\"]?([A-Za-z0-9_-]+)['\"]?\s*\)", re.IGNORECASE)
RE_CICS_COMMAREA = re.compile(r"\bCOMMAREA\s*\(\s*([A-Za-z0-9_-]+)\s*\)", re.IGNORECASE)
RE_CICS_LENGTH = re.compile(r"\bLENGTH\s*\(\s*([0-9]+|[A-Za-z0-9_-]+)\s*\)", re.IGNORECASE)

# SQL Statements
RE_EXEC_SQL = re.compile(r"EXEC\s+SQL\s+(.*?)\s+END-EXEC", re.IGNORECASE | re.DOTALL)
RE_SQL_TABLE = re.compile(r"\b(?:FROM|INTO|UPDATE|TABLE)\s+([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)", re.IGNORECASE)

# Anti-patterns
RE_ALTER = re.compile(r"\bALTER\s+([A-Za-z0-9_-]+)\s+TO\s+PROCEED\s+TO\b", re.IGNORECASE)
RE_COMPUTED_GOTO = re.compile(r"\bGO\s+TO\s+([A-Za-z0-9_\s-]+)\s+DEPENDING\s+ON\b", re.IGNORECASE)


class CobolParser:
    """Parser and complexity analyzer for mainframe COBOL programs."""

    COBOL_OPERATORS = {
        "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE", "MOVE", "SET",
        "PERFORM", "CALL", "IF", "ELSE", "EVALUATE", "WHEN", "GO", "GOTO",
        "READ", "WRITE", "REWRITE", "DELETE", "START", "OPEN", "CLOSE",
        "STOP", "GOBACK", "EXIT", "SEARCH", "STRING", "UNSTRING", "INSPECT",
        "INITIALIZE", "CONTINUE", "EXEC", "END-EXEC", "RETURN", "ACCEPT", "DISPLAY"
    }

    DECISION_KEYWORDS = [
        r"\bIF\b",
        r"\bEVALUATE\b",
        r"\bWHEN\b(?!\s+OTHER)",
        r"\bPERFORM\s+.*?\bUNTIL\b",
        r"\bPERFORM\s+.*?\bVARYING\b",
        r"\bSEARCH\b",
        r"\bAT\s+END\b",
        r"\bNOT\s+AT\s+END\b",
        r"\bON\s+SIZE\s+ERROR\b",
        r"\bINVALID\s+KEY\b",
    ]

    def parse_code(self, source_code: str, file_path: Optional[str] = None) -> CobolProgram:
        """Parse raw COBOL source code and extract metrics and metadata."""
        lines = source_code.splitlines()
        total_lines = len(lines)
        cleaned_lines: List[str] = []
        comment_lines = 0
        blank_lines = 0
        raw_comments: List[str] = []

        # 1. Clean and normalize lines (handling fixed 80-column and free format)
        for line in lines:
            if not line.strip():
                blank_lines += 1
                continue

            # Standard fixed format: column 7 is indicator
            if len(line) >= 7 and line[6] in ("*", "/"):
                comment_lines += 1
                raw_comments.append(line[7:].strip())
                continue
            elif line.strip().startswith("*") or line.strip().startswith("//"):
                comment_lines += 1
                raw_comments.append(line.strip().lstrip("*/ "))
                continue

            # Distinguish fixed 80-column punch-card format vs free format
            # In fixed format, line is at least 7 characters and cols 1-6 are numeric sequence digits
            if len(line) >= 7 and line[:6].isdigit():
                content = line[7:72].rstrip() if len(line) > 72 else line[7:].rstrip()
            elif len(line) > 80:
                content = line[:72].strip()
            else:
                content = line.strip()

            if content.strip():
                cleaned_lines.append(content)

        clean_text = "\n".join(cleaned_lines)
        loc = len(cleaned_lines)

        # 2. Extract Program ID
        prog_match = RE_PROGRAM_ID.search(clean_text)
        program_id = prog_match.group(1).upper() if prog_match else "UNKNOWN_PROG"
        if file_path and program_id == "UNKNOWN_PROG":
            program_id = Path(file_path).stem.upper()

        # 3. Detect Divisions, Sections, Paragraphs
        divisions = [m.group(1).upper() for m in RE_DIVISION.finditer(clean_text)]
        sections = [m.group(1).upper() for m in RE_SECTION.finditer(clean_text)]
        
        # Paragraphs: usually inside PROCEDURE DIVISION
        paragraphs: List[str] = []
        proc_idx = clean_text.upper().find("PROCEDURE DIVISION")
        proc_text = clean_text[proc_idx:] if proc_idx != -1 else clean_text

        for p_line in proc_text.splitlines():
            pm = RE_PARAGRAPH.match(p_line)
            if pm:
                p_name = pm.group(1).strip().upper()
                if not any(k in p_name for k in ("DIVISION", "SECTION", "EXIT")):
                    paragraphs.append(p_name)

        # 4. Extract COPYBOOKS
        copybooks: Set[str] = set()
        for m in RE_COPY.finditer(clean_text):
            cb_name = m.group(1).upper()
            if cb_name not in ("MEMBER", "OF", "IN"):
                copybooks.add(cb_name)

        include_matches = re.findall(r"EXEC\s+SQL\s+INCLUDE\s+([A-Za-z0-9_-]+)\s+END-EXEC", clean_text, re.IGNORECASE)
        for inc in include_matches:
            copybooks.add(inc.upper())

        # 5. Extract Program Calls (Static & Dynamic)
        static_calls: Set[str] = set()
        for m in RE_STATIC_CALL.finditer(clean_text):
            static_calls.add(m.group(1).upper())

        dynamic_calls: Set[str] = set()
        for m in RE_DYNAMIC_CALL.finditer(clean_text):
            target = m.group(1).upper()
            # Filter out non-variable keywords
            if target not in ("USING", "RETURNING", "ON", "OVERFLOW", "EXCEPTION", "IDENTIFIER"):
                dynamic_calls.add(target)

        # 6. Analyze CICS Statements
        cics_blocks = RE_EXEC_CICS.findall(clean_text)
        has_cics = len(cics_blocks) > 0
        cics_links: Set[str] = set()
        cics_xctls: Set[str] = set()
        cics_starts: Set[str] = set()
        has_tsq = False
        has_tdq = False
        has_syncpoint = False
        has_syncpoint_rollback = False
        has_receive = False
        has_return_transid = False
        has_shared_getmain = False
        commarea_size = 0

        for block in cics_blocks:
            upper_block = block.upper()
            if "LINK" in upper_block:
                lm = RE_CICS_LINK.search(upper_block)
                if lm:
                    cics_links.add(lm.group(1).upper())
            if "XCTL" in upper_block:
                xm = RE_CICS_XCTL.search(upper_block)
                if xm:
                    cics_xctls.add(xm.group(1).upper())
            if "START" in upper_block:
                sm = RE_CICS_START.search(upper_block)
                if sm:
                    cics_starts.add(sm.group(1).upper())
            if "WRITEQ TS" in upper_block or "READQ TS" in upper_block:
                has_tsq = True
            if "WRITEQ TD" in upper_block or "READQ TD" in upper_block:
                has_tdq = True
            if "SYNCPOINT" in upper_block:
                has_syncpoint = True
                if "ROLLBACK" in upper_block:
                    has_syncpoint_rollback = True
            if "RECEIVE" in upper_block:
                has_receive = True
            if "RETURN" in upper_block and "TRANSID" in upper_block:
                has_return_transid = True
            if "GETMAIN" in upper_block and "SHARED" in upper_block:
                has_shared_getmain = True
            if "COMMAREA" in upper_block:
                len_m = RE_CICS_LENGTH.search(upper_block)
                if len_m and len_m.group(1).isdigit():
                    commarea_size = max(commarea_size, int(len_m.group(1)))
                elif commarea_size == 0:
                    commarea_size = 100  # Default nominal size if unspecified

        # Determine CICS State Pattern
        if not has_cics:
            state_pattern = CicsStatePattern.STATELESS
        elif has_shared_getmain:
            state_pattern = CicsStatePattern.SHARED_MEMORY
        elif has_receive and not has_return_transid:
            state_pattern = CicsStatePattern.CONVERSATIONAL
        elif has_return_transid or commarea_size > 0:
            state_pattern = CicsStatePattern.PSEUDO_CONVERSATIONAL
        else:
            state_pattern = CicsStatePattern.STATELESS

        # 7. Analyze SQL Statements
        sql_blocks = RE_EXEC_SQL.findall(clean_text)
        has_sql = len(sql_blocks) > 0
        sql_tables: Set[str] = set()
        sql_ops: Dict[str, int] = {"SELECT": 0, "INSERT": 0, "UPDATE": 0, "DELETE": 0}
        has_cursors = False
        has_stored_procedure_calls = False

        for block in sql_blocks:
            upper_sql = block.upper()
            for op in sql_ops:
                if re.search(rf"\b{op}\b", upper_sql):
                    sql_ops[op] += 1
            if "DECLARE" in upper_sql and "CURSOR" in upper_sql:
                has_cursors = True
            if "CALL" in upper_sql:
                has_stored_procedure_calls = True
            for tm in RE_SQL_TABLE.finditer(upper_sql):
                tbl = tm.group(1).upper()
                if tbl not in ("SQLCA", "SET", "WHERE", "VALUES", "SELECT"):
                    sql_tables.add(tbl)

        # 8. Detect VSAM file access in COBOL (SELECT ASSIGN TO / READ / WRITE)
        vsam_files: Set[str] = set()
        vsam_matches = re.findall(r"SELECT\s+([A-Za-z0-9_-]+)\s+ASSIGN\s+TO\s+([A-Za-z0-9_-]+)", clean_text, re.IGNORECASE)
        for f_internal, f_dd in vsam_matches:
            vsam_files.add(f_dd.upper())

        # 9. Anti-Patterns & Quality Checks
        alter_matches = len(RE_ALTER.findall(clean_text))
        has_alter_goto = alter_matches > 0
        has_computed_goto = bool(RE_COMPUTED_GOTO.search(clean_text))
        has_embedded_assembler = "CALL 'ILBO" in clean_text.upper() or "EXEC CICS LINK PROGRAM('DFH" in clean_text.upper() or "ENTRY 'ASM" in clean_text.upper()

        # 10. Complexity Metrics Computation
        # Cyclomatic Complexity
        cc = 1
        for kw_pattern in self.DECISION_KEYWORDS:
            matches = len(re.findall(kw_pattern, proc_text, re.IGNORECASE))
            cc += matches

        # Halstead Metrics
        words = re.findall(r"[A-Za-z0-9_-]+", proc_text)
        operators: List[str] = []
        operands: List[str] = []

        for w in words:
            uw = w.upper()
            if uw in self.COBOL_OPERATORS:
                operators.append(uw)
            else:
                operands.append(uw)

        n1 = max(1, len(set(operators)))  # distinct operators
        n2 = max(1, len(set(operands)))   # distinct operands
        N1 = max(1, len(operators))       # total operators
        N2 = max(1, len(operands))        # total operands

        vocabulary = n1 + n2
        length = N1 + N2
        halstead_vol = length * math.log2(vocabulary) if vocabulary > 0 else 0.0
        halstead_diff = (n1 / 2.0) * (N2 / float(n2)) if n2 > 0 else 1.0
        halstead_eff = halstead_vol * halstead_diff

        # Maintainability Index (MI) = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
        # Scaled to 0-100
        safe_loc = max(1, loc)
        safe_vol = max(1.0, halstead_vol)
        try:
            raw_mi = 171.0 - (5.2 * math.log(safe_vol)) - (0.23 * cc) - (16.2 * math.log(safe_loc))
            maintainability_idx = max(0.0, min(100.0, (raw_mi * 100.0 / 171.0)))
        except Exception:
            maintainability_idx = 50.0

        # Program Type Classification
        if has_cics:
            prog_type = ProgramType.ONLINE_CICS
        elif vsam_files and "SORT" in clean_text.upper():
            prog_type = ProgramType.BATCH
        elif not has_cics and not vsam_files and not has_sql:
            prog_type = ProgramType.SUBPROGRAM
        else:
            prog_type = ProgramType.BATCH

        # Business summary from comments
        business_summary = " ".join(raw_comments[:10]) if raw_comments else None

        # Dead / Unreferenced Paragraphs
        unreferenced_paragraphs: List[str] = []
        for p in paragraphs:
            if paragraphs and p == paragraphs[0]:
                continue
            pattern = rf"\b(?:PERFORM|GO\s+TO|GOTO|THRU|THROUGH)\s+(?:[A-Za-z0-9_-]+\s+THRU\s+)?{re.escape(p)}\b"
            if not re.search(pattern, proc_text, re.IGNORECASE):
                unreferenced_paragraphs.append(p)

        return CobolProgram(
            program_id=program_id,
            file_path=file_path,
            dialect=CobolDialect.ENTERPRISE_COBOL,
            program_type=prog_type,
            lines_of_code=loc,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            divisions_present=divisions,
            paragraphs=paragraphs,
            sections=sections,
            cyclomatic_complexity=cc,
            halstead_volume=round(halstead_vol, 2),
            halstead_difficulty=round(halstead_diff, 2),
            halstead_effort=round(halstead_eff, 2),
            maintainability_index=round(maintainability_idx, 2),
            copybooks_used=sorted(list(copybooks)),
            static_calls=sorted(list(static_calls)),
            dynamic_calls=sorted(list(dynamic_calls)),
            cics_links=sorted(list(cics_links)),
            cics_xctls=sorted(list(cics_xctls)),
            cics_starts=sorted(list(cics_starts)),
            has_cics=has_cics,
            cics_commands_count=len(cics_blocks),
            cics_state_pattern=state_pattern,
            commarea_size_bytes=commarea_size,
            has_tsq=has_tsq,
            has_tdq=has_tdq,
            has_syncpoint=has_syncpoint,
            has_syncpoint_rollback=has_syncpoint_rollback,
            has_sql=has_sql,
            sql_tables_accessed=sorted(list(sql_tables)),
            sql_operations=sql_ops,
            has_cursors=has_cursors,
            has_stored_procedure_calls=has_stored_procedure_calls,
            vsam_files_accessed=sorted(list(vsam_files)),
            has_alter_goto=has_alter_goto,
            alter_statements_count=alter_matches,
            has_computed_goto=has_computed_goto,
            has_embedded_assembler=has_embedded_assembler,
            dead_paragraphs_count=len(unreferenced_paragraphs),
            unreferenced_paragraphs=unreferenced_paragraphs,
            business_summary=business_summary,
        )

    def parse_text(self, text: str, file_path: Optional[str] = None) -> CobolProgram:
        """Alias for parse_code."""
        return self.parse_code(text, file_path=file_path)

    def parse_file(self, file_path: str) -> CobolProgram:
        """Read and parse a COBOL program file."""
        path = Path(file_path)
        content = path.read_text(encoding="latin-1", errors="replace")
        return self.parse_code(content, file_path=str(path))
