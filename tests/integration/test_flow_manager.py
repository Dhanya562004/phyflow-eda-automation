"""
Integration tests for FlowManager pipeline execution.
"""

from pathlib import Path
from phyflow.config import create_flow_config
from phyflow.flow.flow_manager import FlowManager
from phyflow.cli import KNOWN_DESIGNS
from phyflow.models import Corner, JobStatus


def test_flow_manager_mock_execution(tmp_path: Path):
    design = KNOWN_DESIGNS["inverter"]
    config = create_flow_config(design_name="inverter", corner=Corner.TT, mock_mode=True)

    manager = FlowManager(config, runs_dir=tmp_path / "runs")
    res = manager.run_flow(design)

    assert res.job_id == "inverter_tt"
    assert res.status == JobStatus.PASSED
    assert res.validation_result is not None
    assert res.validation_result.timing.wns_ns > 0.0
