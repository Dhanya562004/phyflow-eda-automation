"""
Tool detection utility for PHYFlow.
Checks presence, version, and execution environment of EDA tools & system utilities.
"""

import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ToolStatus:
    name: str
    available: bool
    version: str
    install_guide: str


TOOLS_TO_CHECK = {
    "Yosys": {
        "binary": "yosys",
        "version_flag": "-V",
        "install_guide": "Install via APT: `sudo apt-get install yosys` or build from github.com/YosysHQ/yosys"
    },
    "OpenROAD": {
        "binary": "openroad",
        "version_flag": "-version",
        "install_guide": "Install from OpenROAD Project: github.com/The-OpenROAD-Project/OpenROAD"
    },
    "OpenSTA": {
        "binary": "opensta",
        "version_flag": "-version",
        "install_guide": "Build OpenSTA: github.com/The-OpenROAD-Project/OpenSTA"
    },
    "ngspice": {
        "binary": "ngspice",
        "version_flag": "-v",
        "install_guide": "Install via APT: `sudo apt-get install ngspice` or source distribution"
    },
    "Bash": {
        "binary": "bash",
        "version_flag": "--version",
        "install_guide": "Standard Unix POSIX shell required (available on Linux / WSL / macOS)"
    },
    "Tcl": {
        "binary": "tclsh",
        "version_flag": "echo exit | tclsh",
        "install_guide": "Install via APT: `sudo apt-get install tcl tcl-dev`"
    }
}


def detect_tool(tool_name: str) -> ToolStatus:
    """Detect presence and version of a specific tool binary."""
    config = TOOLS_TO_CHECK.get(tool_name)
    if not config:
        return ToolStatus(
            name=tool_name,
            available=False,
            version="N/A",
            install_guide="Unknown tool binary specification"
        )

    binary = config["binary"]
    executable = shutil.which(binary)

    if not executable:
        return ToolStatus(
            name=tool_name,
            available=False,
            version="NOT FOUND",
            install_guide=config["install_guide"]
        )

    # Try running version command
    try:
        flag = config["version_flag"]
        if tool_name == "Tcl":
            # tclsh doesn't take --version standardly, inspect tcl_version in shell or binary existence
            proc = subprocess.run([binary], input="puts [info patchlevel]; exit\n", text=True, capture_output=True, timeout=5)
            version_str = proc.stdout.strip() if proc.returncode == 0 else "Installed"
        else:
            proc = subprocess.run([binary, flag], capture_output=True, text=True, timeout=5)
            output = proc.stdout or proc.stderr
            lines = [l.strip() for l in output.splitlines() if l.strip()]
            version_str = lines[0] if lines else "Installed"

        return ToolStatus(
            name=tool_name,
            available=True,
            version=version_str[:60],  # Truncate long banners
            install_guide="Available on system"
        )
    except Exception as e:
        return ToolStatus(
            name=tool_name,
            available=True,
            version=f"Installed (Version check error: {e})",
            install_guide="Available on system"
        )


def check_all_tools() -> List[ToolStatus]:
    """Check all configured EDA and system tools."""
    return [detect_tool(name) for name in TOOLS_TO_CHECK.keys()]


def get_tool_availability_dict() -> Dict[str, str]:
    """Return dictionary mapping tool name to version or NOT FOUND."""
    return {status.name: status.version if status.available else "NOT FOUND" for status in check_all_tools()}
