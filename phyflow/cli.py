"""
Professional Command Line Interface (CLI) for PHYFlow.
Built with argparse supporting tool detection, single flow runs, multi-corner runs,
parallel regression testing, run history inspection, and reporting.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from phyflow import __version__
from phyflow.models import Corner, Design, DesignType, JobStatus
from phyflow.config import create_flow_config, load_yaml_config
from phyflow.flow.flow_manager import FlowManager
from phyflow.execution.scheduler import LocalScheduler
from phyflow.storage.run_store import RunStore
from phyflow.validation.regression import build_regression_matrix, evaluate_regression_results
from phyflow.utils.tool_detection import check_all_tools
from phyflow.reporting.summary import format_tool_check_table, format_run_summary_terminal
from phyflow.reporting.report_generator import generate_run_report_md, generate_regression_report_md
from phyflow.utils.filesystem import clean_directory
from phyflow.utils.logging import setup_logger

logger = setup_logger("phyflow.cli")


# Standard Design Catalog
KNOWN_DESIGNS = {
    "inverter": Design(
        name="inverter",
        design_type=DesignType.CUSTOM_CELL,
        source_files=["designs/inverter/inverter.v"],
        top_module="inverter",
        spice_file="designs/inverter/inverter.sp",
        spice_testbench="designs/inverter/inverter_tb.sp",
        description="Single-stage CMOS Inverter Custom Cell"
    ),
    "nand2": Design(
        name="nand2",
        design_type=DesignType.CUSTOM_CELL,
        source_files=["designs/nand2/nand2.v"],
        top_module="nand2",
        spice_file="designs/nand2/nand2.sp",
        spice_testbench="designs/nand2/nand2_tb.sp",
        description="2-Input NAND Custom Cell"
    ),
    "nor2": Design(
        name="nor2",
        design_type=DesignType.CUSTOM_CELL,
        source_files=["designs/nor2/nor2.v"],
        top_module="nor2",
        spice_file="designs/nor2/nor2.sp",
        spice_testbench="designs/nor2/nor2_tb.sp",
        description="2-Input NOR Custom Cell"
    ),
    "xor2": Design(
        name="xor2",
        design_type=DesignType.RTL,
        source_files=["designs/xor2/xor2.v"],
        top_module="xor2",
        description="2-Input XOR RTL Gate"
    ),
    "mux2": Design(
        name="mux2",
        design_type=DesignType.RTL,
        source_files=["designs/mux2/mux2.v"],
        top_module="mux2",
        description="2:1 Multiplexer RTL Module"
    ),
    "alu": Design(
        name="alu",
        design_type=DesignType.RTL,
        source_files=["designs/alu/alu.v"],
        top_module="alu",
        description="4-bit Arithmetic Logic Unit (ALU)"
    ),
}


def cmd_check_tools(args: argparse.Namespace) -> int:
    """Execute 'phyflow check-tools' command."""
    tools = check_all_tools()
    table_output = format_tool_check_table(tools)
    print("\nPHYFlow EDA & System Environment Tool Audit:\n")
    print(table_output)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Execute 'phyflow run' command for a design."""
    design_name = args.design.lower()
    if design_name not in KNOWN_DESIGNS:
        print(f"Error: Unknown design '{design_name}'. Available: {list(KNOWN_DESIGNS.keys())}", file=sys.stderr)
        return 3

    design = KNOWN_DESIGNS[design_name]
    corners_to_run = [Corner.SS, Corner.TT, Corner.FF] if args.all_corners else [Corner(args.corner.upper())]

    overall_exit_code = 0

    for c in corners_to_run:
        config = create_flow_config(
            design_name=design_name,
            corner=c,
            config_file=args.config,
            mock_mode=args.mock
        )

        manager = FlowManager(config)
        res = manager.run_flow(design)

        violations = res.validation_result.violations if res.validation_result else []
        summary_str = format_run_summary_terminal(
            job_id=res.job_id,
            design=res.design_name,
            corner=res.corner.value,
            status=res.status.value,
            duration=res.duration_sec,
            violations=violations
        )
        print(summary_str)

        if res.status != JobStatus.PASSED:
            overall_exit_code = 1

    return overall_exit_code


def cmd_regression(args: argparse.Namespace) -> int:
    """Execute 'phyflow regression' command."""
    cfg_file = args.config or "configs/regression.yaml"
    cfg_data = load_yaml_config(cfg_file) if Path(cfg_file).exists() else {}

    matrix_cfg = cfg_data.get("matrix", {})
    designs_list = matrix_cfg.get("designs", ["inverter", "nand2", "nor2", "xor2", "mux2", "alu"])
    corners_raw = matrix_cfg.get("corners", ["SS", "TT", "FF"])
    corners_list = [Corner(c.upper()) for c in corners_raw]

    workers = args.workers or cfg_data.get("scheduler", {}).get("workers", 4)

    matrix = build_regression_matrix(designs_list, corners_list)
    print(f"\nInitiating Parallel Regression Matrix: {len(matrix)} total jobs using {workers} workers...\n")

    def run_job_item(item: dict):
        d_name = item["design"]
        c_val = item["corner"]
        design = KNOWN_DESIGNS.get(d_name, KNOWN_DESIGNS["inverter"])
        flow_cfg = create_flow_config(design_name=d_name, corner=c_val, config_file=args.config, mock_mode=args.mock)
        manager = FlowManager(flow_cfg)
        return manager.run_flow(design)

    scheduler = LocalScheduler(max_workers=workers)
    reg_result = scheduler.run_jobs(run_job_item, matrix)

    rep_md = generate_regression_report_md(reg_result)
    print(rep_md)

    return 0 if reg_result.failed_jobs == 0 else 1


def cmd_list_runs(args: argparse.Namespace) -> int:
    """Execute 'phyflow list-runs' command."""
    store = RunStore()
    history = store.list_history(limit=50)

    if not history:
        print("No historical PHYFlow runs recorded in SQLite DB.")
        return 0

    print("\n" + "=" * 95)
    print(f"{'Run ID':<18} | {'Timestamp':<20} | {'Design':<10} | {'Corner':<6} | {'Status':<8} | {'Runtime(s)':<10} | {'WNS(ns)':<8}")
    print("=" * 95)

    for r in history:
        print(f"{r['run_id']:<18} | {r['timestamp'][:19]:<20} | {r['design_name']:<10} | {r['corner']:<6} | {r['status']:<8} | {r['runtime_sec']:<10.2f} | {r['wns_ns']:<8.3f}")

    print("=" * 95 + "\n")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    """Execute 'phyflow inspect' command for a run_id."""
    store = RunStore()
    data = store.load_run(args.run_id)

    if not data:
        print(f"Error: Run ID '{args.run_id}' not found in runs storage.", file=sys.stderr)
        return 3

    print(f"\n--- Run Details: {args.run_id} ---")
    print(f"Artifact Path: {data['path']}")
    print("\nMetadata:")
    for k, v in data.get("metadata", {}).items():
        print(f"  {k}: {v}")
    print("\nResults:")
    for k, v in data.get("results", {}).items():
        print(f"  {k}: {v}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Execute 'phyflow report' command."""
    store = RunStore()
    data = store.load_run(args.run_id)

    if not data:
        print(f"Error: Run ID '{args.run_id}' not found.", file=sys.stderr)
        return 3

    rep_path = Path(data['path']) / "reports" / "summary_report.md"
    if rep_path.exists():
        with open(rep_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(f"Report not found at {rep_path}")

    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Execute 'phyflow clean' command."""
    clean_directory("runs")
    print("Cleaned local PHYFlow runs directory and SQLite database.")
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Execute 'phyflow version' command."""
    print(f"PHYFlow Framework Version {__version__}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build ArgParse CLI command parser."""
    parser = argparse.ArgumentParser(
        prog="phyflow",
        description="PHYFlow — EDA Automation & Custom-Cell Validation Framework CLI"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available PHYFlow commands")

    # check-tools
    p_check = subparsers.add_parser("check-tools", help="Audit installed EDA and system tools")
    p_check.set_defaults(func=cmd_check_tools)

    # run
    p_run = subparsers.add_parser("run", help="Run EDA flow for a specified design")
    p_run.add_argument("--design", required=True, help="Design name (inverter, nand2, nor2, xor2, mux2, alu)")
    p_run.add_argument("--corner", default="tt", choices=["ss", "tt", "ff", "SS", "TT", "FF"], help="Process Corner")
    p_run.add_argument("--all-corners", action="store_true", help="Run design across all corners (SS, TT, FF)")
    p_run.add_argument("--config", help="Optional YAML config path")
    p_run.add_argument("--mock", action="store_true", help="Force mock/demo execution mode")
    p_run.set_defaults(func=cmd_run)

    # regression
    p_reg = subparsers.add_parser("regression", help="Run parallel regression matrix")
    p_reg.add_argument("--config", default="configs/regression.yaml", help="Path to regression YAML matrix")
    p_reg.add_argument("--workers", type=int, default=4, help="Number of parallel worker threads")
    p_reg.add_argument("--mock", action="store_true", help="Force mock execution mode")
    p_reg.set_defaults(func=cmd_regression)

    # list-runs
    p_list = subparsers.add_parser("list-runs", help="List historical runs from SQLite database")
    p_list.set_defaults(func=cmd_list_runs)

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect details of a specific run")
    p_insp.add_argument("--run-id", required=True, help="Run ID string")
    p_insp.set_defaults(func=cmd_inspect)

    # report
    p_rep = subparsers.add_parser("report", help="Generate/display Markdown report for a run")
    p_rep.add_argument("--run-id", required=True, help="Run ID string")
    p_rep.set_defaults(func=cmd_report)

    # clean
    p_clean = subparsers.add_parser("clean", help="Clean local run artifacts")
    p_clean.set_defaults(func=cmd_clean)

    # version
    p_ver = subparsers.add_parser("version", help="Print framework version")
    p_ver.set_defaults(func=cmd_version)

    return parser


def main() -> None:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Support 'python -m phyflow cli ...' or 'python -m phyflow ...'
    if sys.argv[1] == "cli":
        sys.argv.pop(1)

    args = parser.parse_args()
    if hasattr(args, "func"):
        try:
            exit_code = args.func(args)
            sys.exit(exit_code)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(4)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
