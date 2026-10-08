"""
Configuration Loader & Parser for PHYFlow.
Loads YAML configuration files into strongly typed FlowConfig instances.
"""

from pathlib import Path
from typing import Dict, Any, Union, Optional
import yaml

from phyflow.models import FlowConfig, Corner
from phyflow.validation.thresholds import ValidationThresholds


def load_yaml_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Loads raw YAML file into dictionary."""
    p = Path(config_path)
    if not p.exists():
        raise FileNotFoundError(f"Configuration file not found: {p}")

    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data


def create_flow_config(
    design_name: str,
    corner: Corner = Corner.TT,
    config_file: Optional[Union[str, Path]] = None,
    mock_mode: bool = False
) -> FlowConfig:
    """Constructs strongly-typed FlowConfig object with optional YAML overrides."""
    base_data: Dict[str, Any] = {
        "design_name": design_name,
        "corner": corner,
        "output_dir": "runs",
        "timeout_sec": 300,
        "max_retries": 2,
        "mock_mode": mock_mode
    }

    if config_file:
        yaml_data = load_yaml_config(config_file)
        if "flow" in yaml_data:
            base_data.update(yaml_data["flow"])
        if "thresholds" in yaml_data:
            base_data["thresholds"] = yaml_data["thresholds"]

    # Convert corner string to Enum if necessary
    if isinstance(base_data.get("corner"), str):
        base_data["corner"] = Corner(base_data["corner"].upper())

    return FlowConfig(
        design_name=base_data["design_name"],
        corner=base_data["corner"],
        output_dir=base_data.get("output_dir", "runs"),
        timeout_sec=base_data.get("timeout_sec", 300),
        max_retries=base_data.get("max_retries", 2),
        synthesis_tool=base_data.get("synthesis_tool", "Yosys"),
        pnr_tool=base_data.get("pnr_tool", "OpenROAD"),
        sta_tool=base_data.get("sta_tool", "OpenSTA"),
        spice_tool=base_data.get("spice_tool", "ngspice"),
        thresholds=base_data.get("thresholds", {}),
        mock_mode=base_data.get("mock_mode", mock_mode)
    )
