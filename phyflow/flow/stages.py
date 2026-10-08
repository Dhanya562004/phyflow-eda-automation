"""
Flow Stage definitions for PHYFlow pipeline.
"""

from typing import List
from phyflow.models import StageName, FlowStage


def get_default_flow_stages(is_custom_cell: bool = False) -> List[FlowStage]:
    """Returns standard 8-stage EDA pipeline definition."""
    stages = [
        FlowStage(StageName.VALIDATION, "Validate design input files, SDC constraints, and directory layout"),
        FlowStage(StageName.SYNTHESIS, "RTL logic synthesis and gate mapping (Yosys)"),
        FlowStage(StageName.FLOORPLAN, "Floorplanning and power grid initialization (OpenROAD)"),
        FlowStage(StageName.PLACE_ROUTE, "Cell placement and clock/signal routing (OpenROAD)"),
        FlowStage(StageName.STA, "Static Timing Analysis & Slack calculation (OpenSTA)"),
    ]

    if is_custom_cell:
        stages.append(FlowStage(StageName.SPICE_VALIDATION, "Custom-Cell SPICE transient simulation (ngspice)"))

    stages.extend([
        FlowStage(StageName.PARSING, "Parse tool logs and extract WNS, area, and SPICE delays"),
        FlowStage(StageName.THRESHOLD_CHECK, "Apply data-driven pass/fail validation thresholds"),
        FlowStage(StageName.REPORTING, "Generate run summary reports, metadata, and SQLite entry")
    ])

    return stages
