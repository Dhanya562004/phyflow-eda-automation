"""
Domain Models for PHYFlow Framework.

Provides strongly typed dataclasses, enums, and structured data objects for:
- Design specifications & corners
- Tool execution results & logs
- EDA metrics (Timing WNS/TNS, Area, Power, SPICE convergence)
- Flow stages, Jobs, Regressions & Storage metadata
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class DesignType(str, Enum):
    RTL = "RTL"
    CUSTOM_CELL = "CUSTOM_CELL"
    MACRO = "MACRO"


class Corner(str, Enum):
    SS = "SS"  # Slow-Slow (1.62V, 125C / 100C)
    TT = "TT"  # Typical-Typical (1.80V, 25C)
    FF = "FF"  # Fast-Fast (1.98V, -40C)


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"


class StageName(str, Enum):
    VALIDATION = "VALIDATION"
    SYNTHESIS = "SYNTHESIS"
    FLOORPLAN = "FLOORPLAN"
    PLACE_ROUTE = "PLACE_ROUTE"
    STA = "STA"
    SPICE_VALIDATION = "SPICE_VALIDATION"
    PARSING = "PARSING"
    THRESHOLD_CHECK = "THRESHOLD_CHECK"
    REPORTING = "REPORTING"


class FailureType(str, Enum):
    NONE = "NONE"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    PROCESS_FAILURE = "PROCESS_FAILURE"
    TIMEOUT = "TIMEOUT"
    INVALID_INPUT = "INVALID_INPUT"
    PARSE_FAILURE = "PARSE_FAILURE"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    SPICE_FAILURE = "SPICE_FAILURE"


@dataclass
class Cell:
    name: str
    pin_count: int
    area_um2: float = 0.0
    leakage_power_nw: float = 0.0


@dataclass
class Design:
    name: str
    design_type: DesignType
    source_files: List[str]
    top_module: str
    sdc_file: Optional[str] = None
    spice_file: Optional[str] = None
    spice_testbench: Optional[str] = None
    description: str = ""


@dataclass
class FlowConfig:
    design_name: str
    corner: Corner = Corner.TT
    output_dir: str = "runs"
    timeout_sec: int = 300
    max_retries: int = 2
    synthesis_tool: str = "Yosys"
    pnr_tool: str = "OpenROAD"
    sta_tool: str = "OpenSTA"
    spice_tool: str = "ngspice"
    thresholds: Dict[str, Any] = field(default_factory=dict)
    mock_mode: bool = False


@dataclass
class FlowStage:
    name: StageName
    description: str
    enabled: bool = True


@dataclass
class ToolResult:
    tool_name: str
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str
    duration_sec: float
    artifacts: List[str] = field(default_factory=list)
    status: JobStatus = JobStatus.PENDING
    error_message: Optional[str] = None


@dataclass
class TimingResult:
    wns_ns: float = 0.0
    tns_ns: float = 0.0
    fmax_mhz: float = 0.0
    critical_path: str = ""
    violations: int = 0


@dataclass
class AreaResult:
    total_area_um2: float = 0.0
    gate_count: int = 0
    utilization_pct: float = 0.0
    cell_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class PowerResult:
    internal_power_mw: float = 0.0
    switching_power_mw: float = 0.0
    leakage_power_mw: float = 0.0
    total_power_mw: float = 0.0


@dataclass
class SpiceValidationResult:
    cell_name: str
    logic_correct: bool = True
    spice_converged: bool = True
    rise_delay_ps: float = 0.0
    fall_delay_ps: float = 0.0
    voh_v: float = 1.8
    vol_v: float = 0.0
    details: str = ""


@dataclass
class ValidationResult:
    passed: bool
    stage_statuses: Dict[str, JobStatus] = field(default_factory=dict)
    timing: Optional[TimingResult] = None
    area: Optional[AreaResult] = None
    power: Optional[PowerResult] = None
    spice: Optional[SpiceValidationResult] = None
    violations: List[str] = field(default_factory=list)


@dataclass
class Job:
    job_id: str
    design_name: str
    corner: Corner
    stages: List[StageName]
    status: JobStatus = JobStatus.PENDING
    attempt: int = 0
    max_retries: int = 2


@dataclass
class JobResult:
    job_id: str
    design_name: str
    corner: Corner
    status: JobStatus
    duration_sec: float
    stage_tool_results: Dict[str, ToolResult] = field(default_factory=dict)
    validation_result: Optional[ValidationResult] = None
    failure_type: FailureType = FailureType.NONE
    error_details: str = ""


@dataclass
class RegressionResult:
    total_jobs: int = 0
    passed_jobs: int = 0
    failed_jobs: int = 0
    skipped_jobs: int = 0
    total_duration_sec: float = 0.0
    job_results: List[JobResult] = field(default_factory=list)
    matrix: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RunMetadata:
    run_id: str
    timestamp: str
    design_name: str
    corner: str
    status: str
    runtime_sec: float
    tools_detected: Dict[str, str]
    execution_mode: str
    artifact_dir: str
