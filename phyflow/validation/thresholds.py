"""
Thresholds configuration for PHYFlow validation engine.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ValidationThresholds:
    min_wns_ns: float = 0.0
    min_tns_ns: float = 0.0
    max_area_um2: float = 50000.0
    max_utilization_pct: float = 85.0
    max_drc_violations: int = 0
    require_spice_convergence: bool = True
    max_rise_delay_ps: float = 500.0
    max_fall_delay_ps: float = 500.0
    min_voh_v: float = 1.4
    max_vol_v: float = 0.4

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationThresholds":
        """Build thresholds from dictionary (e.g. YAML config)."""
        valid_keys = {k: v for k, v in data.items() if hasattr(cls, k)}
        return cls(**valid_keys)
