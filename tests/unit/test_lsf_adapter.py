"""
Unit tests for LSF Command Adapter.
"""

from pathlib import Path
from phyflow.execution.lsf_adapter import LSFCommandAdapter


def test_lsf_bsub_command_building():
    adapter = LSFCommandAdapter(queue="normal", cores=4, memory_mb=8192)
    cmd = adapter.build_bsub_command(
        job_name="inv_tt",
        command_str="phyflow run --design inverter",
        log_file=Path("inv_tt.log")
    )
    assert cmd[0] == "bsub"
    assert "-J" in cmd
    assert "inv_tt" in cmd
    assert "-n" in cmd
    assert "4" in cmd


def test_lsf_batch_script_generation(tmp_path: Path):
    adapter = LSFCommandAdapter()
    script = adapter.generate_batch_script(
        job_name="job_demo",
        commands=["phyflow run --design inverter --all-corners"],
        output_script=tmp_path / "job_demo.sh"
    )
    assert script.exists()
    content = script.read_text()
    assert "#BSUB -J job_demo" in content
