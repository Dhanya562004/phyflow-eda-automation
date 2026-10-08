"""
OpenSTA EDA Tool Adapter.
Handles Static Timing Analysis (STA).
"""

from pathlib import Path
from typing import List, Dict, Any

from phyflow.tools.base import ToolAdapter
from phyflow.parsers.opensta_parser import parse_opensta_log


class OpenSTAAdapter(ToolAdapter):
    def __init__(self):
        super().__init__(binary_name="opensta", name="OpenSTA")

    def build_command(self, script_path: Path, config: Dict[str, Any], output_dir: Path) -> List[str]:
        """Build OpenSTA timing analysis command array."""
        tcl_script = script_path if script_path.exists() else output_dir / "sta.tcl"
        return [self.binary_name, "-exit", str(tcl_script)]

    def parse_result(self, log_content: str) -> Dict[str, Any]:
        """Parse OpenSTA timing report log."""
        return parse_opensta_log(log_content)
