"""
OpenSTA Timing Log Parser.
Extracts Worst Negative Slack (WNS), Total Negative Slack (TNS), FMax, and Critical Path.
"""

import re
from typing import Dict, Any


def parse_opensta_log(log_content: str) -> Dict[str, Any]:
    """
    Parses OpenSTA timing analysis reports.
    Extracts WNS (Worst Negative Slack), TNS (Total Negative Slack), and Critical Path.
    """
    wns_ns = 0.0
    tns_ns = 0.0
    fmax_mhz = 0.0
    critical_path = ""
    violations = 0

    for line in log_content.splitlines():
        line_clean = line.strip()

        # Match WNS: "wns -0.05" or "Worst Negative Slack: -0.05 ns"
        wns_match = re.search(r"(?:wns|Worst Negative Slack:?)\s*(-?[\d\.]+)", line_clean, re.IGNORECASE)
        if wns_match:
            wns_ns = float(wns_match.group(1))

        # Match TNS: "tns -0.15" or "Total Negative Slack: -0.15 ns"
        tns_match = re.search(r"(?:tns|Total Negative Slack:?)\s*(-?[\d\.]+)", line_clean, re.IGNORECASE)
        if tns_match:
            tns_ns = float(tns_match.group(1))

        # Match Slack line: "slack (VIOLATED) -0.05"
        slack_match = re.search(r"slack\s+\([A-Z]+\)\s+(-?[\d\.]+)", line_clean)
        if slack_match:
            val = float(slack_match.group(1))
            if val < 0 and wns_ns == 0.0:
                wns_ns = val

        # Match violations count
        viol_match = re.search(r"(\d+)\s+timing violations", line_clean, re.IGNORECASE)
        if viol_match:
            violations = int(viol_match.group(1))

        # Critical path endpoint match: "Endpoint: reg_out (rising edge clock clk)"
        ep_match = re.search(r"Endpoint:\s*(.+)", line_clean)
        if ep_match:
            critical_path = ep_match.group(1).strip()

    # Calculate approximate FMax if WNS is available (assuming target 100MHz / 10ns period baseline)
    target_period_ns = 10.0
    effective_period = target_period_ns - wns_ns
    if effective_period > 0:
        fmax_mhz = round(1000.0 / effective_period, 2)

    if wns_ns < 0:
        violations = max(1, violations)

    return {
        "wns_ns": wns_ns,
        "tns_ns": tns_ns,
        "fmax_mhz": fmax_mhz,
        "critical_path": critical_path,
        "violations": violations,
        "timing_pass": wns_ns >= 0.0
    }
