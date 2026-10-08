"""
Validation Engine for PHYFlow.
Applies data-driven quality and constraint checks to parsed EDA stage metrics.
"""

from typing import Dict, Any, List
from phyflow.models import (
    ValidationResult, TimingResult, AreaResult, PowerResult,
    SpiceValidationResult, JobStatus
)
from phyflow.validation.thresholds import ValidationThresholds


class FlowValidator:
    """Evaluates parsed EDA metrics against configurable design thresholds."""

    def __init__(self, thresholds: ValidationThresholds):
        self.thresholds = thresholds

    def validate_stage_results(
        self,
        design_name: str,
        stage_statuses: Dict[str, JobStatus],
        timing: TimingResult,
        area: AreaResult,
        power: PowerResult,
        spice: SpiceValidationResult
    ) -> ValidationResult:
        """
        Evaluates design performance metrics against validation thresholds.
        Returns a structured ValidationResult with violation details.
        """
        violations: List[str] = []

        # 1. Stage status check
        for stage, status in stage_statuses.items():
            if status != JobStatus.PASSED:
                violations.append(f"Stage '{stage}' status is {status.value}")

        # 2. Timing Threshold Checks
        if timing:
            if timing.wns_ns < self.thresholds.min_wns_ns:
                violations.append(
                    f"Timing WNS Violation: WNS = {timing.wns_ns:.3f} ns (Threshold >= {self.thresholds.min_wns_ns:.3f} ns)"
                )
            if timing.tns_ns < self.thresholds.min_tns_ns:
                violations.append(
                    f"Timing TNS Violation: TNS = {timing.tns_ns:.3f} ns (Threshold >= {self.thresholds.min_tns_ns:.3f} ns)"
                )

        # 3. Area & Physical DRC Checks
        if area:
            if area.total_area_um2 > self.thresholds.max_area_um2:
                violations.append(
                    f"Area Exceeded: {area.total_area_um2:.1f} um² (Max limit = {self.thresholds.max_area_um2:.1f} um²)"
                )
            if area.utilization_pct > self.thresholds.max_utilization_pct:
                violations.append(
                    f"Utilization High: {area.utilization_pct:.1f}% (Max limit = {self.thresholds.max_utilization_pct:.1f}%)"
                )

        # 4. Custom-Cell SPICE Simulation Checks
        if spice:
            if self.thresholds.require_spice_convergence and not spice.spice_converged:
                violations.append("SPICE Validation Failed: Transient simulation failed to converge")
            if not spice.logic_correct:
                violations.append(
                    f"SPICE Logic Failure: VOH={spice.voh_v}V, VOL={spice.vol_v}V out of expected thresholds"
                )
            if spice.rise_delay_ps > self.thresholds.max_rise_delay_ps:
                violations.append(
                    f"Rise Delay Violation: {spice.rise_delay_ps:.1f} ps (Threshold <= {self.thresholds.max_rise_delay_ps:.1f} ps)"
                )
            if spice.fall_delay_ps > self.thresholds.max_fall_delay_ps:
                violations.append(
                    f"Fall Delay Violation: {spice.fall_delay_ps:.1f} ps (Threshold <= {self.thresholds.max_fall_delay_ps:.1f} ps)"
                )

        passed = len(violations) == 0
        return ValidationResult(
            passed=passed,
            stage_statuses=stage_statuses,
            timing=timing,
            area=area,
            power=power,
            spice=spice,
            violations=violations
        )
