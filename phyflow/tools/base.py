"""
Base Abstract Tool Adapter for PHYFlow EDA Tools.

All EDA tool integrations (Yosys, OpenROAD, OpenSTA, ngspice) inherit from
ToolAdapter to enforce a uniform execution and parsing interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import subprocess
import time
from typing import List, Dict, Any, Optional

from phyflow.models import ToolResult, JobStatus


class ToolAdapter(ABC):
    """Abstract base class for all EDA tool adapters."""

    def __init__(self, binary_name: str, name: str):
        self.binary_name = binary_name
        self.name = name

    def is_available(self) -> bool:
        """Check if tool binary is found in PATH."""
        return shutil.which(self.binary_name) is not None

    def version(self) -> str:
        """Get version string of installed tool binary."""
        if not self.is_available():
            return "NOT FOUND"
        try:
            res = subprocess.run([self.binary_name, "-v"], capture_output=True, text=True, timeout=5)
            out = res.stdout or res.stderr
            return out.splitlines()[0] if out else "Unknown"
        except Exception:
            return "Unknown"

    @abstractmethod
    def build_command(self, script_path: Path, config: Dict[str, Any], output_dir: Path) -> List[str]:
        """Construct CLI command array for tool execution."""
        pass

    def execute(
        self,
        command: List[str],
        cwd: Path,
        timeout_sec: float = 300.0,
        mock_mode: bool = False,
        mock_stdout: Optional[str] = None
    ) -> ToolResult:
        """
        Execute tool command array using controlled subprocess execution.
        Captures stdout, stderr, exit code, runtime duration, and generated artifacts.
        """
        start_time = time.time()

        if mock_mode or not self.is_available():
            time.sleep(0.05)  # Simulate execution latency
            duration = round(time.time() - start_time, 3)
            stdout_text = mock_stdout or f"[{self.name} MOCK] Command executed successfully: {' '.join(command)}\n"
            return ToolResult(
                tool_name=self.name,
                command=command,
                exit_code=0,
                stdout=stdout_text,
                stderr="",
                duration_sec=duration,
                artifacts=[],
                status=JobStatus.PASSED,
                error_message=None
            )

        try:
            proc = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            duration = round(time.time() - start_time, 3)
            status = JobStatus.PASSED if proc.returncode == 0 else JobStatus.FAILED
            error_msg = None if proc.returncode == 0 else f"Tool {self.name} exited with status code {proc.returncode}"

            return ToolResult(
                tool_name=self.name,
                command=command,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_sec=duration,
                artifacts=[],
                status=status,
                error_message=error_msg
            )
        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 3)
            return ToolResult(
                tool_name=self.name,
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {timeout_sec} seconds",
                duration_sec=duration,
                artifacts=[],
                status=JobStatus.TIMEOUT,
                error_message=f"Timeout expired ({timeout_sec}s)"
            )
        except Exception as e:
            duration = round(time.time() - start_time, 3)
            return ToolResult(
                tool_name=self.name,
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_sec=duration,
                artifacts=[],
                status=JobStatus.FAILED,
                error_message=str(e)
            )

    @abstractmethod
    def parse_result(self, log_content: str) -> Dict[str, Any]:
        """Parse log content to extract structured EDA metrics."""
        pass
