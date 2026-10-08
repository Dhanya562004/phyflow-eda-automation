"""
RunStore Manager for PHYFlow.
Handles filesystem run artifact serialization and SQLite metadata sync.
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from phyflow.models import RunMetadata, JobResult
from phyflow.storage.sqlite_store import SQLiteRunStore
from phyflow.utils.filesystem import create_run_directory


class RunStore:
    """Orchestrates saving and retrieving execution runs from filesystem and SQLite DB."""

    def __init__(self, runs_dir: Path = Path("runs"), db_path: Path = Path("runs/phyflow_history.db")):
        self.runs_dir = Path(runs_dir)
        self.db = SQLiteRunStore(db_path)

    def save_run(
        self,
        job_result: JobResult,
        tools_detected: Dict[str, str],
        execution_mode: str = "Real EDA Mode"
    ) -> Path:
        """Serializes job execution results, logs, and metadata into a run directory and SQLite DB."""
        run_id = job_result.job_id
        timestamp = datetime.now().isoformat()

        run_path = create_run_directory(self.runs_dir, run_id)

        # 1. Save metadata.json
        meta = RunMetadata(
            run_id=run_id,
            timestamp=timestamp,
            design_name=job_result.design_name,
            corner=job_result.corner.value,
            status=job_result.status.value,
            runtime_sec=job_result.duration_sec,
            tools_detected=tools_detected,
            execution_mode=execution_mode,
            artifact_dir=str(run_path.resolve())
        )

        with open(run_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(asdict(meta), f, indent=2)

        # 2. Save results.json
        results_data = {
            "job_id": job_result.job_id,
            "design": job_result.design_name,
            "corner": job_result.corner.value,
            "status": job_result.status.value,
            "duration_sec": job_result.duration_sec,
            "failure_type": job_result.failure_type.value,
            "error_details": job_result.error_details,
            "validation": asdict(job_result.validation_result) if job_result.validation_result else None
        }

        with open(run_path / "results.json", "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2)

        # 3. Save logs per stage
        logs_dir = run_path / "logs"
        for stage_name, t_res in job_result.stage_tool_results.items():
            stage_log_file = logs_dir / f"{stage_name.lower()}.log"
            with open(stage_log_file, "w", encoding="utf-8") as f:
                f.write(f"=== STAGE: {stage_name} ===\n")
                f.write(f"Command: {' '.join(t_res.command)}\n")
                f.write(f"Status: {t_res.status.value} (Exit code: {t_res.exit_code})\n")
                f.write(f"Duration: {t_res.duration_sec} s\n\n")
                f.write("--- STDOUT ---\n")
                f.write(t_res.stdout or "(None)\n")
                f.write("\n--- STDERR ---\n")
                f.write(t_res.stderr or "(None)\n")

        # Extract summary metrics for SQLite record
        wns_ns = 0.0
        area_um2 = 0.0
        gate_count = 0
        if job_result.validation_result:
            if job_result.validation_result.timing:
                wns_ns = job_result.validation_result.timing.wns_ns
            if job_result.validation_result.area:
                area_um2 = job_result.validation_result.area.total_area_um2
                gate_count = job_result.validation_result.area.gate_count

        self.db.record_run(meta, wns_ns=wns_ns, area_um2=area_um2, gate_count=gate_count)
        return run_path

    def list_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch run history summary from SQLite."""
        return self.db.list_runs(limit=limit)

    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load full metadata and results for a run_id."""
        run_path = self.runs_dir / run_id
        if not run_path.exists():
            return None

        meta_file = run_path / "metadata.json"
        results_file = run_path / "results.json"

        data: Dict[str, Any] = {"run_id": run_id, "path": str(run_path)}
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                data["metadata"] = json.load(f)
        if results_file.exists():
            with open(results_file, "r", encoding="utf-8") as f:
                data["results"] = json.load(f)

        return data
