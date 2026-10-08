"""
Regression tests verifying parser robustness against known good and malformed log fixtures.
"""

from phyflow.parsers.yosys_parser import parse_yosys_log
from phyflow.parsers.opensta_parser import parse_opensta_log
from phyflow.parsers.ngspice_parser import parse_ngspice_log


def test_malformed_yosys_log():
    log = "ERROR: Could not read Verilog file syntax error at line 45"
    res = parse_yosys_log(log)
    assert res["gate_count"] == 0
    assert res["synthesis_success"] is False


def test_malformed_sta_log():
    log = "FATAL: Liberty library not found"
    res = parse_opensta_log(log)
    assert res["timing_pass"] is True
    assert res["violations"] == 0


def test_spice_convergence_failure_log():
    log = "CPU time limit exceeded. Timestep too small in transient simulation."
    res = parse_ngspice_log(log)
    assert res["spice_converged"] is False
    assert res["logic_correct"] is False
