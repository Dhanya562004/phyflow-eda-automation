"""
Unit tests for EDA Log Parsers (Yosys, OpenROAD, OpenSTA, ngspice).
"""

from phyflow.parsers.yosys_parser import parse_yosys_log
from phyflow.parsers.openroad_parser import parse_openroad_log
from phyflow.parsers.opensta_parser import parse_opensta_log
from phyflow.parsers.ngspice_parser import parse_ngspice_log


def test_yosys_parser():
    sample_log = """
Yosys 0.33
Printing statistics.
=== inverter ===
   Number of cells:                 12
     sky130_fd_sc_hd__inv_1         12
   Chip area for module '\\inverter': 15.200000
"""
    res = parse_yosys_log(sample_log)
    assert res["gate_count"] == 12
    assert res["total_area_um2"] == 15.2
    assert res["synthesis_success"] is True


def test_openroad_parser():
    sample_log = """
OpenROAD v2.0
Design area 150 u^2 45.5% utilization.
Total wire length = 1245 um
Found 0 DRC violations
"""
    res = parse_openroad_log(sample_log)
    assert res["total_area_um2"] == 150.0
    assert res["utilization_pct"] == 45.5
    assert res["drc_violations"] == 0
    assert res["pnr_success"] is True


def test_opensta_parser():
    sample_log = """
OpenSTA 2.4.0
Endpoint: reg_out/D (rising edge clock clk)
slack (MET) 0.120
wns 0.120
tns 0.000
0 timing violations
"""
    res = parse_opensta_log(sample_log)
    assert res["wns_ns"] == 0.120
    assert res["tns_ns"] == 0.000
    assert res["timing_pass"] is True


def test_ngspice_parser():
    sample_log = """
****** ngspice-39
trise = 1.850000e-11
tfall = 1.420000e-11
voh = 1.800000e+00
vol = 0.000000e+00
Simulation finished successfully.
"""
    res = parse_ngspice_log(sample_log)
    assert res["spice_converged"] is True
    assert res["rise_delay_ps"] == 18.5
    assert res["fall_delay_ps"] == 14.2
    assert res["logic_correct"] is True
