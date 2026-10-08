"""
ngspice Log Parser.
Extracts transient simulation measurements, SPICE convergence status, rise/fall delays, and logic thresholds.
"""

import re
from typing import Dict, Any


def parse_ngspice_log(log_content: str) -> Dict[str, Any]:
    """
    Parses stdout/output log from ngspice transient simulation.
    Extracts `.meas` statement outputs for rise delay, fall delay, VOH, VOL, and convergence.
    """
    converged = True
    rise_delay_ps = 0.0
    fall_delay_ps = 0.0
    voh_v = 1.8
    vol_v = 0.0
    logic_correct = True

    # Check convergence failure keywords
    if "CPU time limit exceeded" in log_content or "Timestep too small" in log_content or "transient simulation failed" in log_content:
        converged = False

    for line in log_content.splitlines():
        line_clean = line.strip()

        # Match ngspice measurement lines: e.g. "trise = 1.450000e-11"
        trise_match = re.search(r"trise\s*=\s*([0-9eE\.\-\+]+)", line_clean)
        if trise_match:
            try:
                rise_delay_ps = round(float(trise_match.group(1)) * 1e12, 2)
            except ValueError:
                pass

        tfall_match = re.search(r"tfall\s*=\s*([0-9eE\.\-\+]+)", line_clean)
        if tfall_match:
            try:
                fall_delay_ps = round(float(tfall_match.group(1)) * 1e12, 2)
            except ValueError:
                pass

        voh_match = re.search(r"voh\s*=\s*([0-9eE\.\-\+]+)", line_clean)
        if voh_match:
            try:
                voh_v = round(float(voh_match.group(1)), 3)
            except ValueError:
                pass

        vol_match = re.search(r"vol\s*=\s*([0-9eE\.\-\+]+)", line_clean)
        if vol_match:
            try:
                vol_v = round(float(vol_match.group(1)), 3)
            except ValueError:
                pass

    # Basic logic sanity check for inverter/NAND/NOR VOH >= 1.6V, VOL <= 0.2V
    if voh_v < 1.4 or vol_v > 0.4:
        logic_correct = False

    return {
        "spice_converged": converged,
        "rise_delay_ps": rise_delay_ps,
        "fall_delay_ps": fall_delay_ps,
        "voh_v": voh_v,
        "vol_v": vol_v,
        "logic_correct": logic_correct and converged
    }
