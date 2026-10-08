"""
Regression Suite Matrix Builder & Analysis for PHYFlow.
"""

from typing import List, Dict, Any
from phyflow.models import Corner, RegressionResult, JobResult, JobStatus


def build_regression_matrix(designs: List[str], corners: List[Corner]) -> List[Dict[str, Any]]:
    """Build job matrix for all combinations of designs and corners."""
    matrix = []
    for d in designs:
        for c in corners:
            matrix.append({
                "job_id": f"{d}_{c.value.lower()}",
                "design": d,
                "corner": c
            })
    return matrix


def evaluate_regression_results(job_results: List[JobResult], duration_sec: float) -> RegressionResult:
    """Aggregate individual job execution results into a full RegressionResult summary."""
    total = len(job_results)
    passed = sum(1 for r in job_results if r.status == JobStatus.PASSED)
    failed = sum(1 for r in job_results if r.status == JobStatus.FAILED)
    skipped = sum(1 for r in job_results if r.status == JobStatus.SKIPPED)

    matrix_summary = [
        {
            "job_id": r.job_id,
            "design": r.design_name,
            "corner": r.corner.value,
            "status": r.status.value,
            "duration_sec": r.duration_sec,
            "error": r.error_details if r.status != JobStatus.PASSED else ""
        }
        for r in job_results
    ]

    return RegressionResult(
        total_jobs=total,
        passed_jobs=passed,
        failed_jobs=failed,
        skipped_jobs=skipped,
        total_duration_sec=duration_sec,
        job_results=job_results,
        matrix=matrix_summary
    )
