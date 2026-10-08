"""
LSF (Load Sharing Facility) Scheduler Adapter for PHYFlow.
Provides LSF-compatible job submission script construction and bsub command generation.

Note: PHYFlow provides an LSF-compatible submission abstraction for demonstrating batch scheduling concepts;
actual LSF execution requires an LSF cluster environment.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional


class LSFCommandAdapter:
    """Generates IBM Spectrum LSF (bsub) batch submission commands and job scripts."""

    def __init__(self, queue: str = "normal", cores: int = 2, memory_mb: int = 4096):
        self.queue = queue
        self.cores = cores
        self.memory_mb = memory_mb

    def build_bsub_command(
        self,
        job_name: str,
        command_str: str,
        log_file: Path,
        project: str = "phyflow_eda"
    ) -> List[str]:
        """
        Constructs bsub CLI argument array.
        Example: bsub -J job_inv -q normal -n 2 -R "rusage[mem=4096]" -o /path/to/log "phyflow run..."
        """
        return [
            "bsub",
            "-J", job_name,
            "-q", self.queue,
            "-n", str(self.cores),
            "-P", project,
            "-R", f"rusage[mem={self.memory_mb}]",
            "-o", str(log_file),
            command_str
        ]

    def generate_batch_script(self, job_name: str, commands: List[str], output_script: Path) -> Path:
        """Generates a POSIX shell script containing #BSUB headers for batch submission."""
        lines = [
            "#!/bin/bash",
            f"#BSUB -J {job_name}",
            f"#BSUB -q {self.queue}",
            f"#BSUB -n {self.cores}",
            f"#BSUB -R \"rusage[mem={self.memory_mb}]\"",
            f"#BSUB -o {job_name}_%J.log",
            "",
            "# Auto-generated PHYFlow LSF Batch Job Script",
            "set -e",
            ""
        ] + commands

        with open(output_script, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return output_script
