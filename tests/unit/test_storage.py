"""
Unit tests for RunStore and SQLite storage.
"""

from pathlib import Path
from phyflow.models import JobResult, JobStatus, Corner, FailureType
from phyflow.storage.run_store import RunStore


def test_sqlite_run_store(tmp_path: Path):
    store = RunStore(runs_dir=tmp_path / "runs", db_path=tmp_path / "test.db")

    job_res = JobResult(
        job_id="test_inv_tt",
        design_name="inverter",
        corner=Corner.TT,
        status=JobStatus.PASSED,
        duration_sec=0.5,
        failure_type=FailureType.NONE
    )

    run_path = store.save_run(job_res, tools_detected={"Yosys": "Installed"})
    assert run_path.exists()
    assert (run_path / "metadata.json").exists()
    assert (run_path / "results.json").exists()

    history = store.list_history()
    assert len(history) == 1
    assert history[0]["run_id"] == "test_inv_tt"
