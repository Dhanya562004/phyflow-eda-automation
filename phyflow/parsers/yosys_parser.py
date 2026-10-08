"""
Yosys Log Parser.
Extracts cell count, total area, chip gate breakdown, and synthesis statistics.
"""

import re
from typing import Dict, Any


def parse_yosys_log(log_content: str) -> Dict[str, Any]:
    """
    Parses stdout log content from Yosys synthesis execution.
    Tolerates small format variations and returns structured data.
    """
    cell_count = 0
    total_area = 0.0
    cell_breakdown: Dict[str, int] = {}

    # Example Yosys summary patterns:
    #   Number of cells:                 12
    #   Chip area for module '\inverter': 15.200000
    #     sky130_fd_sc_hd__inv_1        12

    for line in log_content.splitlines():
        line_clean = line.strip()

        # Match total cells
        cell_match = re.search(r"Number of cells:\s+(\d+)", line_clean)
        if cell_match:
            cell_count = int(cell_match.group(1))

        # Match chip area
        area_match = re.search(r"Chip area for module.*:\s+([\d\.]+)", line_clean)
        if area_match:
            total_area = float(area_match.group(1))

        # Match individual cell counts (e.g., "sky130_fd_sc_hd__inv_1 5")
        cell_type_match = re.match(r"^([A-Za-z0-9_]+)\s+(\d+)$", line_clean)
        if cell_type_match:
            cell_name = cell_type_match.group(1)
            count = int(cell_type_match.group(2))
            if cell_name not in ["Number", "Chip", "Printing", "=== design"]:
                cell_breakdown[cell_name] = count

    return {
        "gate_count": cell_count,
        "total_area_um2": total_area,
        "cell_breakdown": cell_breakdown,
        "synthesis_success": "Printing statistics." in log_content or cell_count > 0 or "Chip area" in log_content
    }
