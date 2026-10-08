"""
Command Runner & Subprocess Executor for PHYFlow.
Provides safe command execution, stream capturing, timeout enforcement, and failure classification.
"""

import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple

from phyflow.models import ToolResult, JobStatus, FailureType


def classify_failure(exit_code: int, stderr: str, stdout: str) -> FailureType:
    """Classifies subprocess execution failure into strongly typed FailureType."""
    if exit_code == -1 or "timed out" in stderr.lower():
        return FailureType.TIMEOUT
    if "command not found" in stderr.lower() or "no such file" in stderr.lower():
        return FailureType.TOOL_NOT_FOUND
    if "spice" in stderr.lower() or "timestep too small" in stdout.lower() or "convergence" in stdout.lower():
        return FailureType.SPICE_FAILURE
    if "syntax error" in stdout.lower() or "syntax error" in stderr.lower():
        return FailureType.INVALID_INPUT
    return FailureType.PROCESS_FAILURE


def run_command_safe(
    cmd: List[str],
    cwd: Path,
    timeout_sec: float = 300.0,
    env: Optional[dict] = None
) -> Tuple[int, str, str, float]:
    """
    Executes a shell command array cleanly using subprocess without shell=True for security.
    Returns (exit_code, stdout, stderr, duration_sec).
    """
    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env
        )
        duration = round(time.time() - start_time, 3)
        return proc.returncode, proc.stdout, proc.stderr, duration
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start_time, 3)
        return -1, "", f"Command timed out after {timeout_sec} seconds", duration
    except Exception as e:
        duration = round(time.time() - start_time, 3)
        return -1, "", str(e), duration
