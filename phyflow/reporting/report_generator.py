"""
Engineering Report Generator for PHYFlow.
Generates comprehensive Markdown reports for individual runs and regression matrices.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from phyflow.models import JobResult, RegressionResult, JobStatus


def generate_run_report_md(job_result: JobResult) -> str:
    """Generates detailed Markdown report for a single run."""
    val = job_result.validation_result
    lines = []
    lines.append(f"# PHYFlow Engineering Execution Report")
    lines.append(f"**Job ID:** `{job_result.job_id}`  ")
    lines.append(f"**Design:** `{job_result.design_name}` | **Corner:** `{job_result.corner.value}`  ")
    lines.append(f"**Overall Status:** `{job_result.status.value}` | **Runtime:** `{job_result.duration_sec:.2f} s`  \n")

    lines.append("## 1. Flow Stage Breakdown\n")
    lines.append("| Stage | Status | Duration (s) | Exit Code |")
    lines.append("|---|---|---|---|")
    for s_name, t_res in job_result.stage_tool_results.items():
        lines.append(f"| {s_name} | `{t_res.status.value}` | {t_res.duration_sec:.2f} | {t_res.exit_code} |")

    lines.append("\n## 2. Key Parsed EDA Metrics\n")

    if val:
        if val.timing:
            lines.append("### Static Timing Analysis (OpenSTA)")
            lines.append(f"- **WNS (Worst Negative Slack):** `{val.timing.wns_ns:.3f} ns`")
            lines.append(f"- **TNS (Total Negative Slack):** `{val.timing.tns_ns:.3f} ns`")
            lines.append(f"- **Estimated FMax:** `{val.timing.fmax_mhz:.2f} MHz`")
            lines.append(f"- **Critical Path:** `{val.timing.critical_path or 'N/A'}`\n")

        if val.area:
            lines.append("### Physical Area & Placement (OpenROAD / Yosys)")
            lines.append(f"- **Total Area:** `{val.area.total_area_um2:.2f} µm²`")
            lines.append(f"- **Gate / Cell Count:** `{val.area.gate_count}`")
            lines.append(f"- **Core Utilization:** `{val.area.utilization_pct:.1f}%`\n")

        if val.spice:
            lines.append("### Custom-Cell SPICE Simulation (ngspice)")
            lines.append(f"- **SPICE Convergence:** `{'PASS' if val.spice.spice_converged else 'FAIL'}`")
            lines.append(f"- **Logic Functionality:** `{'PASS' if val.spice.logic_correct else 'FAIL'}`")
            lines.append(f"- **Rise Delay (50%-50%):** `{val.spice.rise_delay_ps:.1f} ps`")
            lines.append(f"- **Fall Delay (50%-50%):** `{val.spice.fall_delay_ps:.1f} ps`")
            lines.append(f"- **VOH / VOL:** `{val.spice.voh_v:.2f} V` / `{val.spice.vol_v:.2f} V`\n")

        lines.append("## 3. Validation Threshold Checks\n")
        if val.passed:
            lines.append("> [!NOTE]\n> All design validation threshold constraints PASSED successfully.")
        else:
            lines.append("> [!WARNING]\n> **Validation Violations Identified:**")
            for v in val.violations:
                lines.append(f"- {v}")

    lines.append("\n---\n*Report generated automatically by PHYFlow Framework.*")
    return "\n".join(lines)


def generate_regression_report_md(reg_result: RegressionResult) -> str:
    """Generates detailed Markdown report for a multi-job regression suite."""
    lines = []
    lines.append("# PHYFlow Regression Suite Report\n")
    lines.append(f"- **Total Executed Jobs:** {reg_result.total_jobs}")
    lines.append(f"- **PASSED:** {reg_result.passed_jobs} | **FAILED:** {reg_result.failed_jobs} | **SKIPPED:** {reg_result.skipped_jobs}")
    lines.append(f"- **Total Wall Time:** {reg_result.total_duration_sec:.2f} s\n")

    lines.append("## Job Execution Matrix\n")
    lines.append("| Job ID | Design | Corner | Status | Duration (s) | Error Details |")
    lines.append("|---|---|---|---|---|---|")

    for item in reg_result.matrix:
        err = item.get("error", "")
        lines.append(f"| `{item['job_id']}` | {item['design']} | `{item['corner']}` | `{item['status']}` | {item['duration_sec']:.2f} | {err} |")

    lines.append("\n---\n*Report generated automatically by PHYFlow Regression Engine.*")
    return "\n".join(lines)
