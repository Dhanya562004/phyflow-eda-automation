"""
ngspice EDA Tool Adapter.
Handles SPICE transient simulations and custom-cell functional validation.
"""

from pathlib import Path
from typing import List, Dict, Any

from phyflow.tools.base import ToolAdapter
from phyflow.parsers.ngspice_parser import parse_ngspice_log


class NGSpiceAdapter(ToolAdapter):
    def __init__(self):
        super().__init__(binary_name="ngspice", name="ngspice")

    def build_command(self, script_path: Path, config: Dict[str, Any], output_dir: Path) -> List[str]:
        """Build ngspice batch execution command array."""
        circuit_file = script_path if script_path.exists() else output_dir / "testbench.sp"
        return [self.binary_name, "-b", "-o", str(output_dir / "ngspice.log"), str(circuit_file)]

    def parse_result(self, log_content: str) -> Dict[str, Any]:
        """Parse ngspice transient analysis log for timing and convergence."""
        return parse_ngspice_log(log_content)
