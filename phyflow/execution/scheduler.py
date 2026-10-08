"""
Parallel Job Scheduler for PHYFlow.
Provides bounded concurrent execution of EDA flows across designs and corners using concurrent.futures.
"""

from abc import ABC, abstractmethod
import concurrent.futures
import time
from typing import List, Callable, Dict, Any, Optional

from phyflow.models import Job, JobResult, JobStatus, RegressionResult
from phyflow.validation.regression import evaluate_regression_results
from phyflow.utils.logging import setup_logger

logger = setup_logger("phyflow.scheduler")


class BaseScheduler(ABC):
    """Abstract Job Scheduler interface."""

    @abstractmethod
    def run_jobs(self, job_fn: Callable[[Dict[str, Any]], JobResult], job_configs: List[Dict[str, Any]]) -> RegressionResult:
        pass


class LocalScheduler(BaseScheduler):
    """
    Local multi-threaded job scheduler.
    Executes independent design/corner jobs concurrently with configurable worker thread pool.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max(1, max_workers)

    def run_jobs(
        self,
        job_fn: Callable[[Dict[str, Any]], JobResult],
        job_configs: List[Dict[str, Any]]
    ) -> RegressionResult:
        """
        Submits job_configs list to ThreadPoolExecutor pool and deterministically aggregates results.
        """
        start_time = time.time()
        results: List[JobResult] = []

        logger.info(f"Starting Parallel Scheduler with {self.max_workers} worker threads for {len(job_configs)} jobs...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map job_fn across job_configs list
            future_to_config = {
                executor.submit(job_fn, cfg): cfg for cfg in job_configs
            }

            for future in concurrent.futures.as_completed(future_to_config):
                cfg = future_to_config[future]
                job_id = cfg.get("job_id", f"{cfg.get('design')}_{cfg.get('corner')}")
                try:
                    res = future.result()
                    results.append(res)
                    logger.info(f"Job finished: {job_id} -> Status: {res.status.value}")
                except Exception as e:
                    logger.error(f"Unhandled Exception in Job {job_id}: {e}")
                    # Construct failed JobResult entry on exception
                    failed_res = JobResult(
                        job_id=job_id,
                        design_name=cfg.get("design", "unknown"),
                        corner=cfg.get("corner"),
                        status=JobStatus.FAILED,
                        duration_sec=0.0,
                        error_details=str(e)
                    )
                    results.append(failed_res)

        total_duration = round(time.time() - start_time, 3)
        # Ensure deterministic result order based on job_configs order
        config_order = {cfg.get("job_id", ""): i for i, cfg in enumerate(job_configs)}
        results.sort(key=lambda r: config_order.get(r.job_id, 999))

        return evaluate_regression_results(results, total_duration)
