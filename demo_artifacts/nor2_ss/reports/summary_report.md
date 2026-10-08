# PHYFlow Engineering Execution Report
**Job ID:** `nor2_ss`  
**Design:** `nor2` | **Corner:** `SS`  
**Overall Status:** `FAILED` | **Runtime:** `0.24 s`  

## 1. Flow Stage Breakdown

| Stage | Status | Duration (s) | Exit Code |
|---|---|---|---|
| VALIDATION | `PASSED` | 0.01 | 0 |
| SYNTHESIS | `PASSED` | 0.05 | 0 |
| PLACE_ROUTE | `PASSED` | 0.05 | 0 |
| STA | `PASSED` | 0.05 | 0 |
| SPICE_VALIDATION | `PASSED` | 0.05 | 0 |

## 2. Key Parsed EDA Metrics

### Static Timing Analysis (OpenSTA)
- **WNS (Worst Negative Slack):** `-0.040 ns`
- **TNS (Total Negative Slack):** `-0.120 ns`
- **Estimated FMax:** `99.60 MHz`
- **Critical Path:** `reg_out/D (rising edge clock clk)`

### Physical Area & Placement (OpenROAD / Yosys)
- **Total Area:** `450.00 µm²`
- **Gate / Cell Count:** `48`
- **Core Utilization:** `65.2%`

### Custom-Cell SPICE Simulation (ngspice)
- **SPICE Convergence:** `PASS`
- **Logic Functionality:** `PASS`
- **Rise Delay (50%-50%):** `24.5 ps`
- **Fall Delay (50%-50%):** `21.5 ps`
- **VOH / VOL:** `1.80 V` / `0.00 V`

## 3. Validation Threshold Checks

> [!WARNING]
> **Validation Violations Identified:**
- Timing WNS Violation: WNS = -0.040 ns (Threshold >= 0.000 ns)
- Timing TNS Violation: TNS = -0.120 ns (Threshold >= 0.000 ns)

---
*Report generated automatically by PHYFlow Framework.*