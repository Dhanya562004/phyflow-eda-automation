"""
Unit tests for PHYFlow Domain Models.
"""

from phyflow.models import Design, DesignType, Corner, FlowConfig, JobStatus, FailureType


def test_design_model():
    d = Design(
        name="inverter",
        design_type=DesignType.CUSTOM_CELL,
        source_files=["designs/inverter/inverter.v"],
        top_module="inverter"
    )
    assert d.name == "inverter"
    assert d.design_type == DesignType.CUSTOM_CELL


def test_flow_config_defaults():
    cfg = FlowConfig(design_name="inverter")
    assert cfg.corner == Corner.TT
    assert cfg.synthesis_tool == "Yosys"
    assert cfg.max_retries == 2


def test_enums():
    assert Corner.SS.value == "SS"
    assert JobStatus.PASSED.value == "PASSED"
    assert FailureType.SPICE_FAILURE.value == "SPICE_FAILURE"
