"""
OpenROAD Log Parser.
Extracts floorplan utilization, placement density, routed wirelength, and DRC status.
"""

import re
from typing import Dict, Any


def parse_openroad_log(log_content: str) -> Dict[str, Any]:
    """
    Parses stdout log content from OpenROAD physical design execution.
    """
    utilization_pct = 0.0
    total_area_um2 = 0.0
    wirelength_um = 0.0
    drc_violations = 0

    for line in log_content.splitlines():
        line_clean = line.strip()

        # Design utilization match: "Design area 150 u^2 45.5% utilization."
        util_match = re.search(r"(\d+(?:\.\d+)?)\s*u\^2\s+([\d\.]+)\%\s+utilization", line_clean)
        if util_match:
            total_area_um2 = float(util_match.group(1))
            utilization_pct = float(util_match.group(2))

        # Direct percentage match: "Utilization: 52.3 %"
        util_match2 = re.search(r"[Uu]tilization:\s*([\d\.]+)\s*\%", line_clean)
        if util_match2:
            utilization_pct = float(util_match2.group(1))

        # Wirelength match: "Total wire length = 1245 um"
        wl_match = re.search(r"Total wire length\s*=\s*([\d\.]+)", line_clean)
        if wl_match:
            wirelength_um = float(wl_match.group(1))

        # DRC violations match: "Found 0 DRC violations"
        drc_match = re.search(r"Found\s+(\d+)\s+DRC violations", line_clean)
        if drc_match:
            drc_violations = int(drc_match.group(1))

    return {
        "utilization_pct": utilization_pct,
        "total_area_um2": total_area_um2,
        "wirelength_um": wirelength_um,
        "drc_violations": drc_violations,
        "pnr_success": drc_violations == 0
    }
