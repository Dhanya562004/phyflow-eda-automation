"""
Unit tests for Parallel Scheduler.
"""

from phyflow.models import Corner, JobResult, JobStatus, FailureType
from phyflow.execution.scheduler import LocalScheduler
from phyflow.validation.regression import build_regression_matrix


def dummy_job(cfg: dict) -> JobResult:
    return JobResult(
        job_id=cfg["job_id"],
        design_name=cfg["design"],
        corner=cfg["corner"],
        status=JobStatus.PASSED,
        duration_sec=0.01,
        failure_type=FailureType.NONE
    )


def test_local_scheduler():
    matrix = build_regression_matrix(["inverter", "nand2"], [Corner.TT, Corner.FF])
    scheduler = LocalScheduler(max_workers=2)
    reg_result = scheduler.run_jobs(dummy_job, matrix)

    assert reg_result.total_jobs == 4
    assert reg_result.passed_jobs == 4
    assert reg_result.failed_jobs == 0
