"""
Yosys EDA Tool Adapter.
Handles RTL synthesis using Yosys.
"""

from pathlib import Path
from typing import List, Dict, Any

from phyflow.tools.base import ToolAdapter
from phyflow.parsers.yosys_parser import parse_yosys_log


class YosysAdapter(ToolAdapter):
    def __init__(self):
        super().__init__(binary_name="yosys", name="Yosys")

    def build_command(self, script_path: Path, config: Dict[str, Any], output_dir: Path) -> List[str]:
        """Build Yosys synthesis execution command array."""
        tcl_script = script_path if script_path.exists() else output_dir / "synthesis.tcl"
        return [self.binary_name, "-s", str(tcl_script)]

    def parse_result(self, log_content: str) -> Dict[str, Any]:
        """Parse Yosys synthesis output log."""
        return parse_yosys_log(log_content)
