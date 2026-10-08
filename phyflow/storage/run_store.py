"""
RunStore Manager for PHYFlow.
Handles filesystem run artifact serialization, SQLite metadata sync,
and automatic fallback scanning of JSON reference artifacts for cloud deployment.
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
    """Orchestrates saving and retrieving execution runs from filesystem, SQLite DB, or demo artifacts."""

    def __init__(self, runs_dir: Path = Path("runs"), db_path: Path = Path("runs/phyflow_history.db")):
        self.runs_dir = Path(runs_dir)
        self.db_path = Path(db_path)
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

        try:
            self.db.record_run(meta, wns_ns=wns_ns, area_um2=area_um2, gate_count=gate_count)
        except Exception:
            pass

        return run_path

    def scan_artifact_dir(self, target_dir: Path) -> List[Dict[str, Any]]:
        """Scans directory for run folders containing metadata.json/results.json directly."""
        runs = []
        if not target_dir.exists():
            return runs

        for entry in target_dir.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                meta_file = entry / "metadata.json"
                res_file = entry / "results.json"
                if meta_file.exists() or res_file.exists():
                    meta = {}
                    res = {}
                    if meta_file.exists():
                        try:
                            with open(meta_file, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                        except Exception:
                            pass
                    if res_file.exists():
                        try:
                            with open(res_file, "r", encoding="utf-8") as f:
                                res = json.load(f)
                        except Exception:
                            pass

                    run_id = meta.get("run_id") or res.get("job_id") or entry.name
                    timestamp = meta.get("timestamp") or "2026-10-08T00:00:00"
                    design_name = meta.get("design_name") or res.get("design") or run_id.split("_")[0]
                    corner = meta.get("corner") or res.get("corner") or "TT"
                    status = meta.get("status") or res.get("status") or "PASSED"
                    runtime_sec = meta.get("runtime_sec") or res.get("duration_sec") or 0.0
                    exec_mode = meta.get("execution_mode") or "Demo Mode"

                    val = res.get("validation", {}) or {}
                    timing = val.get("timing", {}) or {}
                    area = val.get("area", {}) or {}

                    wns_ns = timing.get("wns_ns", 0.0) if timing else 0.0
                    area_um2 = area.get("total_area_um2", 0.0) if area else 0.0
                    gate_count = area.get("gate_count", 0) if area else 0

                    runs.append({
                        "run_id": run_id,
                        "timestamp": timestamp,
                        "design_name": design_name,
                        "corner": corner,
                        "status": status,
                        "runtime_sec": float(runtime_sec),
                        "execution_mode": exec_mode,
                        "wns_ns": float(wns_ns),
                        "area_um2": float(area_um2),
                        "gate_count": int(gate_count)
                    })
        runs.sort(key=lambda x: x["timestamp"], reverse=True)
        return runs

    def list_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch run history summary from SQLite, falling back to direct JSON scan if empty or unreadable."""
        try:
            db_runs = self.db.list_runs(limit=limit)
            if db_runs:
                return db_runs
        except Exception:
            pass

        # Fallback 1: scan self.runs_dir
        scanned = self.scan_artifact_dir(self.runs_dir)
        if scanned:
            return scanned[:limit]

        # Fallback 2: scan demo_artifacts
        scanned_demo = self.scan_artifact_dir(Path("demo_artifacts"))
        return scanned_demo[:limit]

    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load full metadata and results for a run_id searching runs_dir and demo_artifacts."""
        possible_paths = [
            self.runs_dir / run_id,
            Path("runs") / run_id,
            Path("demo_artifacts") / run_id
        ]
        run_path = None
        for p in possible_paths:
            if p.exists() and p.is_dir():
                run_path = p
                break

        if not run_path:
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
