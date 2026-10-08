"""
Console & Summary Formatter for PHYFlow.
Renders clean ASCII tables, PASS/FAIL status indicators, and summary metrics.
"""

from typing import List, Dict, Any
from phyflow.utils.tool_detection import ToolStatus


def format_tool_check_table(tools: List[ToolStatus]) -> str:
    """Renders formatted ASCII table of EDA tool availability."""
    lines = []
    lines.append("=" * 75)
    lines.append(f"{'Tool Name':<12} | {'Status':<10} | {'Version / Notes':<45}")
    lines.append("=" * 75)

    for t in tools:
        status_str = "AVAILABLE" if t.available else "NOT FOUND"
        version_str = t.version if t.available else t.install_guide[:45]
        lines.append(f"{t.name:<12} | {status_str:<10} | {version_str:<45}")

    lines.append("=" * 75)
    return "\n".join(lines)


def format_run_summary_terminal(job_id: str, design: str, corner: str, status: str, duration: float, violations: List[str]) -> str:
    """Renders single run execution summary banner for CLI stdout."""
    lines = []
    lines.append("\n" + "=" * 65)
    lines.append(f" PHYFLOW RUN SUMMARY: {job_id}")
    lines.append("=" * 65)
    lines.append(f" Design Name : {design}")
    lines.append(f" Corner      : {corner}")
    lines.append(f" Overall Status: {status}")
    lines.append(f" Runtime     : {duration:.2f} s")
    if violations:
        lines.append("-" * 65)
        lines.append(" VIOLATIONS / ERRORS:")
        for v in violations:
            lines.append(f"  [!] {v}")
    lines.append("=" * 65 + "\n")
    return "\n".join(lines)
