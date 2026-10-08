"""
Unit tests for Validation Engine.
"""

from phyflow.models import TimingResult, AreaResult, PowerResult, SpiceValidationResult, JobStatus
from phyflow.validation.thresholds import ValidationThresholds
from phyflow.validation.validators import FlowValidator


def test_validator_pass():
    thresholds = ValidationThresholds(min_wns_ns=0.0, max_area_um2=500.0)
    validator = FlowValidator(thresholds)

    stage_statuses = {"SYNTHESIS": JobStatus.PASSED, "STA": JobStatus.PASSED}
    timing = TimingResult(wns_ns=0.15, tns_ns=0.0)
    area = AreaResult(total_area_um2=150.0, gate_count=10)
    power = PowerResult(total_power_mw=0.01)
    spice = SpiceValidationResult(cell_name="inverter", rise_delay_ps=18.0, fall_delay_ps=14.0)

    val_res = validator.validate_stage_results("inverter", stage_statuses, timing, area, power, spice)
    assert val_res.passed is True
    assert len(val_res.violations) == 0


def test_validator_timing_violation():
    thresholds = ValidationThresholds(min_wns_ns=0.0)
    validator = FlowValidator(thresholds)

    stage_statuses = {"SYNTHESIS": JobStatus.PASSED}
    timing = TimingResult(wns_ns=-0.05, tns_ns=-0.15)
    area = AreaResult(total_area_um2=150.0)
    power = PowerResult()

    val_res = validator.validate_stage_results("inverter", stage_statuses, timing, area, power, None)
    assert val_res.passed is False
    assert any("Timing WNS Violation" in v for v in val_res.violations)
