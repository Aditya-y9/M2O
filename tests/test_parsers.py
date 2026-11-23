"""Tests for legacy artifact parsers."""

import pytest
from pathlib import Path
from modernizeiq.parsers.cobol_parser import CobolParser
from modernizeiq.parsers.jcl_parser import JclParser
from modernizeiq.parsers.bms_parser import BmsParser
from modernizeiq.parsers.data_parser import DataParser
from modernizeiq.parsers.metadata_loader import MetadataLoader


def test_cobol_parser():
    sample_cobol = """
    IDENTIFICATION DIVISION.
    PROGRAM-ID. TESTPGM.
    ENVIRONMENT DIVISION.
    DATA DIVISION.
    WORKING-STORAGE SECTION.
    COPY TESTREC.
    PROCEDURE DIVISION.
    0000-MAIN.
        IF WS-A > 10
            EXEC SQL SELECT BAL INTO :WS-BAL FROM ACCT WHERE ID = :WS-ID END-EXEC
        ELSE
            EXEC CICS RETURN END-EXEC
        END-IF.
        ALTER ROUTE-PARAGRAPH TO PROCEED TO NEW-PARAGRAPH.
    """
    parser = CobolParser()
    prog = parser.parse_text(sample_cobol, "TESTPGM.cbl")

    assert prog.program_id == "TESTPGM"
    assert "TESTREC" in prog.copybooks
    assert prog.cics_count >= 1
    assert prog.sql_count >= 1
    assert "ALTER" in prog.anti_patterns
    assert prog.mccabe_cyclomatic_complexity >= 2


def test_jcl_parser():
    sample_jcl = """
    //TESTJOB  JOB (1234),'TEST JOB',CLASS=A
    //STEP1    EXEC PGM=PROGA
    //DD1      DD DSN=DATA.FILE(+1),DISP=(NEW,CATLG)
    //STEP2    EXEC PGM=PROGB,COND=(0,NE,STEP1)
    """
    parser = JclParser()
    job = parser.parse_text(sample_jcl, "TESTJOB.jcl")

    assert job.job_name == "TESTJOB"
    assert len(job.steps) == 2
    assert job.steps[0].program_name == "PROGA"
    assert job.steps[0].datasets[0].is_gdg is True
    assert "STEP1" in job.steps[1].cond_codes[0]


def test_bms_parser():
    sample_bms = """
    TESTSET  DFHMSD TYPE=&SYSPARM,MODE=INOUT,STORAGE=AUTO
    TESTMAP  DFHMDI SIZE=(24,80)
    FLDA     DFHMDF POS=(1,10),LENGTH=20,ATTRB=(UNPROT,IC,FSET)
    TESTSET  DFHMSD TYPE=FINAL
             END
    """
    parser = BmsParser()
    mapset = parser.parse_text(sample_bms, "TESTSET.bms")

    assert mapset.mapset_name == "TESTSET"
    assert len(mapset.maps) == 1
    assert mapset.maps[0].has_cursor_positioning is True
    assert mapset.maps[0].modified_data_tags is True


def test_data_parser():
    sample_ddl = """
    CREATE TABLE TEST_TBL (
        ID DECIMAL(10, 0) NOT NULL,
        NAME VARCHAR(50),
        PRIMARY KEY (ID)
    );
    CREATE INDEX IX_TEST ON TEST_TBL(NAME);
    """
    parser = DataParser()
    tables = parser.parse_ddl_text(sample_ddl, "SCHEMA.sql")

    assert len(tables) == 1
    assert tables[0].table_name == "TEST_TBL"
    assert tables[0].primary_key == ["ID"]
    assert len(tables[0].columns) == 2


def test_metadata_loader_core_banking():
    loader = MetadataLoader()
    portfolio = loader.load_from_directory("data/sample_portfolios/core_banking_deposit")

    assert portfolio.app_id == "CORE-BNK-DEP"
    assert len(portfolio.cobol_programs) >= 3
    assert len(portfolio.copybooks) >= 2
    assert len(portfolio.jcl_jobs) >= 1
    assert len(portfolio.bms_mapsets) >= 1
    assert len(portfolio.db2_tables) >= 2
