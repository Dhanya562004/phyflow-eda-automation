"""
OpenROAD EDA Tool Adapter.
Handles physical floorplanning, placement, and routing.
"""

from pathlib import Path
from typing import List, Dict, Any

from phyflow.tools.base import ToolAdapter
from phyflow.parsers.openroad_parser import parse_openroad_log


class OpenROADAdapter(ToolAdapter):
    def __init__(self):
        super().__init__(binary_name="openroad", name="OpenROAD")

    def build_command(self, script_path: Path, config: Dict[str, Any], output_dir: Path) -> List[str]:
        """Build OpenROAD execution command array."""
        tcl_script = script_path if script_path.exists() else output_dir / "pnr.tcl"
        return [self.binary_name, "-exit", str(tcl_script)]

    def parse_result(self, log_content: str) -> Dict[str, Any]:
        """Parse OpenROAD output log for area, density, and routing metrics."""
        return parse_openroad_log(log_content)
