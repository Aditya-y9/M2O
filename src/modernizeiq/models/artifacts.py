"""Legacy mainframe artifact metamodels aligned with OMG KDM (Knowledge Discovery Metamodel)."""

from __future__ import annotations
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class CobolDialect(str, Enum):
    ENTERPRISE_COBOL = "Enterprise COBOL for z/OS"
    OS_VS_COBOL = "OS/VS COBOL"
    COBOL_II = "VS COBOL II"
    MICRO_FOCUS = "Micro Focus COBOL"
    UNKNOWN = "Unknown"


class ProgramType(str, Enum):
    ONLINE_CICS = "Online CICS"
    BATCH = "Batch"
    SUBPROGRAM = "Shared Subprogram"
    HYBRID = "Hybrid Online/Batch"
    UTILITY = "Utility"


class VsamType(str, Enum):
    KSDS = "KSDS"  # Key-Sequenced (indexed)
    ESDS = "ESDS"  # Entry-Sequenced (sequential/append-only)
    RRDS = "RRDS"  # Relative Record (slot-based)
    LDS = "LDS"    # Linear (byte stream)


class CicsStatePattern(str, Enum):
    STATELESS = "Stateless (Immediate return, externalized state)"
    PSEUDO_CONVERSATIONAL = "Pseudo-Conversational (COMMAREA or Container)"
    CONVERSATIONAL = "Conversational (Retains task across terminal think-time)"
    SHARED_MEMORY = "Shared Memory (GETMAIN SHARED / CWA / TWA)"


class CobolProgram(BaseModel):
    """Metamodel for a single COBOL program unit."""
    program_id: str
    file_path: Optional[str] = None
    dialect: CobolDialect = CobolDialect.ENTERPRISE_COBOL
    program_type: ProgramType = ProgramType.ONLINE_CICS
    lines_of_code: int = 0
    comment_lines: int = 0
    blank_lines: int = 0

    # Architecture & Structural Metrics
    divisions_present: List[str] = Field(default_factory=list)
    paragraphs: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)

    # Complexity Metrics
    cyclomatic_complexity: int = 1
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    maintainability_index: float = 100.0

    # Dependencies & Interactions
    copybooks_used: List[str] = Field(default_factory=list)
    static_calls: List[str] = Field(default_factory=list)
    dynamic_calls: List[str] = Field(default_factory=list)
    cics_links: List[str] = Field(default_factory=list)
    cics_xctls: List[str] = Field(default_factory=list)
    cics_starts: List[str] = Field(default_factory=list)

    # CICS & Transaction Patterns
    has_cics: bool = False
    cics_commands_count: int = 0
    cics_state_pattern: CicsStatePattern = CicsStatePattern.STATELESS
    commarea_size_bytes: int = 0
    has_tsq: bool = False
    has_tdq: bool = False
    has_syncpoint: bool = False
    has_syncpoint_rollback: bool = False

    # Database & Data Store Access
    has_sql: bool = False
    sql_tables_accessed: List[str] = Field(default_factory=list)
    sql_operations: Dict[str, int] = Field(default_factory=dict)  # SELECT, INSERT, UPDATE, DELETE
    has_cursors: bool = False
    has_stored_procedure_calls: bool = False
    vsam_files_accessed: List[str] = Field(default_factory=list)
    mq_queues_accessed: List[str] = Field(default_factory=list)

    # Legacy Anti-Patterns & Modernization Blockers
    has_alter_goto: bool = False
    alter_statements_count: int = 0
    has_computed_goto: bool = False
    has_embedded_assembler: bool = False
    has_hardcoded_file_paths: bool = False
    dead_paragraphs_count: int = 0
    unreferenced_paragraphs: List[str] = Field(default_factory=list)

    # Semantic extraction (comments, business intent)
    description: Optional[str] = None
    business_summary: Optional[str] = None
    extracted_business_rules: List[str] = Field(default_factory=list)

    @property
    def mccabe_cyclomatic_complexity(self) -> int:
        return self.cyclomatic_complexity

    @property
    def copybooks(self) -> List[str]:
        return self.copybooks_used

    @property
    def cics_count(self) -> int:
        return self.cics_commands_count

    @property
    def sql_count(self) -> int:
        return sum(self.sql_operations.values()) if self.sql_operations else (len(self.sql_tables_accessed) if self.has_sql else 0)

    @property
    def anti_patterns(self) -> List[str]:
        ap = []
        if self.has_alter_goto or self.alter_statements_count > 0:
            ap.append("ALTER")
        if self.has_computed_goto:
            ap.append("COMPUTED_GOTO")
        if self.has_embedded_assembler:
            ap.append("EMBEDDED_ASSEMBLER")
        if self.has_hardcoded_file_paths:
            ap.append("HARDCODED_FILE_PATHS")
        return ap

    @property
    def is_cics_program(self) -> bool:
        return self.has_cics or self.program_type == ProgramType.ONLINE_CICS

    @property
    def is_batch_program(self) -> bool:
        return self.program_type == ProgramType.BATCH

    @property
    def sql_queries_count(self) -> int:
        return self.sql_count

    @property
    def cics_syncpoints_count(self) -> int:
        return 1 if self.has_syncpoint else 0

    @property
    def is_conversational(self) -> bool:
        return self.cics_state_pattern == CicsStatePattern.CONVERSATIONAL

    @property
    def total_loc(self) -> int:
        return self.lines_of_code


class Copybook(BaseModel):
    """Metamodel for a COBOL COPY member (shared data structure)."""
    name: str
    file_path: Optional[str] = None
    field_count: int = 0
    level_01_name: Optional[str] = None
    total_length_bytes: int = 0
    has_occurs: bool = False
    has_redefines: bool = False
    referenced_by_programs: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class JclDatasetRef(BaseModel):
    """Reference to a dataset within a JCL DD statement."""
    dsn: str
    is_gdg: bool = False
    disp: Optional[str] = None


class JclStep(BaseModel):
    """A step within a JCL batch job."""
    step_name: str
    program_executed: str
    is_proc: bool = False
    cond_codes: List[str] = Field(default_factory=list)
    input_datasets: List[str] = Field(default_factory=list)
    output_datasets: List[str] = Field(default_factory=list)
    datasets: List[JclDatasetRef] = Field(default_factory=list)
    disposition_share: bool = False
    is_utility: bool = False  # SORT, IDCAMS, IEBGENER, etc.

    @property
    def program_name(self) -> str:
        return self.program_executed

    @property
    def has_cond_logic(self) -> bool:
        return len(self.cond_codes) > 0


class JclJob(BaseModel):
    """Metamodel for a JCL batch job."""
    job_name: str
    file_path: Optional[str] = None
    job_class: Optional[str] = None
    steps: List[JclStep] = Field(default_factory=list)
    has_gdg: bool = False
    has_conditional_steps: bool = False
    has_checkpoint_restart: bool = False
    estimated_runtime_minutes: int = 0
    scheduler_dependencies: List[str] = Field(default_factory=list)  # CA-7/TWS upstream jobs

    @property
    def gdg_datasets_count(self) -> int:
        count = sum(1 for step in self.steps for ds in step.datasets if ds.is_gdg)
        return count if count > 0 else (1 if self.has_gdg else 0)


class CicsTransaction(BaseModel):
    """CICS transaction definition."""
    trans_id: str
    initial_program: str
    description: Optional[str] = None
    priority: int = 1
    is_restartable: bool = True
    tw_size: int = 0
    bms_mapset: Optional[str] = None

    @property
    def program_name(self) -> str:
        return self.initial_program


class BmsMap(BaseModel):
    """An individual 3270 screen map within a BMS mapset."""
    map_name: str
    has_cursor_positioning: bool = False
    modified_data_tags: bool = False
    fields_count: int = 0


class BmsMapset(BaseModel):
    """3270 BMS Mapset definition."""
    mapset_name: str
    file_path: Optional[str] = None
    maps_count: int = 1
    maps: List[BmsMap] = Field(default_factory=list)
    total_fields: int = 0
    has_cursor_logic: bool = False
    has_mdt_logic: bool = False
    pf_keys_used: List[str] = Field(default_factory=list)
    associated_programs: List[str] = Field(default_factory=list)

    @property
    def total_fields_count(self) -> int:
        return self.total_fields or sum(m.fields_count for m in self.maps)


class DatabaseTable(BaseModel):
    """Relational (DB2) or hierarchical (IMS) data entity."""
    table_name: str
    schema_name: Optional[str] = "DB2"
    columns_count: int = 0
    columns: List[str] = Field(default_factory=list)
    has_primary_key: bool = True
    primary_key: List[str] = Field(default_factory=list)
    indexes_count: int = 1
    estimated_row_count: int = 0
    accessed_by_programs: List[str] = Field(default_factory=list)
    is_relational: bool = True  # False for IMS DB

    @property
    def column_count(self) -> int:
        return self.columns_count or len(self.columns)


class VsamDataset(BaseModel):
    """VSAM file cluster definition."""
    cluster_name: str
    vsam_type: VsamType = VsamType.KSDS
    record_length: int = 80
    key_length: int = 0
    key_offset: int = 0
    share_options: str = "(2,3)"
    has_alternate_index: bool = False
    accessed_by_programs: List[str] = Field(default_factory=list)

    @property
    def organization(self) -> VsamType:
        return self.vsam_type


class SecurityManagerEnum(str, Enum):
    RACF = "RACF"
    ACF2 = "ACF2"
    TOP_SECRET = "TopSecret"
    NONE = "NONE"


class SecurityProfile(BaseModel):
    """Mainframe ESM (RACF/ACF2/TopSecret) security requirements."""
    esm_type: str = "RACF"
    resource_classes_used: List[str] = Field(default_factory=list)  # FACILITY, DATASET, CICS
    has_saf_exits: bool = False
    has_surrogate_security: bool = False
    compliance_frameworks: List[str] = Field(default_factory=list)  # PCI-DSS, SOX, HIPAA
    custom_exits: List[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def populate_defaults(self) -> "SecurityProfile":
        if self.has_saf_exits and not self.custom_exits:
            self.custom_exits = ["ICHHEX01"]
        return self

    @property
    def security_manager(self) -> SecurityManagerEnum:
        val = (self.esm_type or "RACF").upper()
        if "ACF2" in val:
            return SecurityManagerEnum.ACF2
        elif "TOP" in val or "SECRET" in val:
            return SecurityManagerEnum.TOP_SECRET
        return SecurityManagerEnum.RACF

    @property
    def resource_classes(self) -> List[str]:
        return self.resource_classes_used

    @property
    def uses_surrogate(self) -> bool:
        return self.has_surrogate_security or any("SURROGAT" in r.upper() for r in self.resource_classes_used)


class NonFunctionalRequirements(BaseModel):
    """Operational dependencies and NFR constraints."""
    peak_throughput_tps: int = 500
    target_latency_p99_ms: float = 50.0
    availability_sla: float = 99.95  # e.g., 99.999%
    batch_window_hours: float = 4.0
    rto_minutes: int = 60
    rpo_minutes: int = 15
    data_volume_gb: float = 50.0
    is_customer_facing: bool = True
    audit_logging_required: bool = True
    business_criticality: str = "Tier 1 - Mission Critical"

    # Optional alias fields
    target_response_time_ms_val: Optional[float] = Field(default=None, alias="target_response_time_ms")
    availability_percentage_val: Optional[float] = Field(default=None, alias="availability_percentage")
    peak_transactions_per_sec_val: Optional[int] = Field(default=None, alias="peak_transactions_per_sec")

    model_config = {"populate_by_name": True}

    @property
    def target_response_time_ms(self) -> float:
        return self.target_response_time_ms_val if self.target_response_time_ms_val is not None else self.target_latency_p99_ms

    @property
    def availability_percentage(self) -> float:
        return self.availability_percentage_val if self.availability_percentage_val is not None else self.availability_sla

    @property
    def peak_transactions_per_sec(self) -> int:
        return self.peak_transactions_per_sec_val if self.peak_transactions_per_sec_val is not None else self.peak_throughput_tps


class ApplicationPortfolio(BaseModel):
    """Complete application package submitted for modernization assessment."""
    app_id: str
    app_name: str
    description: str
    business_domain: str
    owner_team: Optional[str] = None
    programs: Dict[str, CobolProgram] = Field(default_factory=dict)
    copybooks: Dict[str, Copybook] = Field(default_factory=dict)
    jobs: Dict[str, JclJob] = Field(default_factory=dict)
    transactions: Dict[str, CicsTransaction] = Field(default_factory=dict)
    mapsets: Dict[str, BmsMapset] = Field(default_factory=dict)
    tables: Dict[str, DatabaseTable] = Field(default_factory=dict)
    vsam_files: Dict[str, VsamDataset] = Field(default_factory=dict)
    security: SecurityProfile = Field(default_factory=SecurityProfile)
    nfrs: NonFunctionalRequirements = Field(default_factory=NonFunctionalRequirements)

    @property
    def cobol_programs(self) -> Dict[str, CobolProgram]:
        return self.programs

    @property
    def jcl_jobs(self) -> Dict[str, JclJob]:
        return self.jobs

    @property
    def bms_mapsets(self) -> Dict[str, BmsMapset]:
        return self.mapsets

    @property
    def db2_tables(self) -> Dict[str, DatabaseTable]:
        return self.tables

    @property
    def racf_profiles(self) -> List[str]:
        return self.security.resource_classes_used
