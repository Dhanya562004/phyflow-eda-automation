# PHYFlow Engineering Execution Report
**Job ID:** `mux2_tt`  
**Design:** `mux2` | **Corner:** `TT`  
**Overall Status:** `PASSED` | **Runtime:** `0.19 s`  

## 1. Flow Stage Breakdown

| Stage | Status | Duration (s) | Exit Code |
|---|---|---|---|
| VALIDATION | `PASSED` | 0.01 | 0 |
| SYNTHESIS | `PASSED` | 0.05 | 0 |
| PLACE_ROUTE | `PASSED` | 0.05 | 0 |
| STA | `PASSED` | 0.05 | 0 |

## 2. Key Parsed EDA Metrics

### Static Timing Analysis (OpenSTA)
- **WNS (Worst Negative Slack):** `0.120 ns`
- **TNS (Total Negative Slack):** `0.000 ns`
- **Estimated FMax:** `101.21 MHz`
- **Critical Path:** `reg_out/D (rising edge clock clk)`

### Physical Area & Placement (OpenROAD / Yosys)
- **Total Area:** `450.00 µm²`
- **Gate / Cell Count:** `48`
- **Core Utilization:** `65.2%`

## 3. Validation Threshold Checks

> [!NOTE]
> All design validation threshold constraints PASSED successfully.

---
*Report generated automatically by PHYFlow Framework.*