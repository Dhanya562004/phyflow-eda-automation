"""
Flow Dependency Graph for PHYFlow stage validation.
"""

from typing import List, Dict
from phyflow.models import StageName


class FlowGraph:
    """Directed Dependency Graph for validating EDA flow stage execution order."""

    DEPENDENCIES: Dict[StageName, List[StageName]] = {
        StageName.VALIDATION: [],
        StageName.SYNTHESIS: [StageName.VALIDATION],
        StageName.FLOORPLAN: [StageName.SYNTHESIS],
        StageName.PLACE_ROUTE: [StageName.FLOORPLAN],
        StageName.STA: [StageName.SYNTHESIS],
        StageName.SPICE_VALIDATION: [StageName.VALIDATION],
        StageName.PARSING: [StageName.SYNTHESIS],
        StageName.THRESHOLD_CHECK: [StageName.PARSING],
        StageName.REPORTING: [StageName.THRESHOLD_CHECK]
    }

    @classmethod
    def validate_execution_sequence(cls, stages: List[StageName]) -> bool:
        """Validates that all prerequisites for requested stages are satisfied."""
        executed = set()
        for stage in stages:
            deps = cls.DEPENDENCIES.get(stage, [])
            for d in deps:
                if d not in executed and d in stages:
                    return False
            executed.add(stage)
        return True
