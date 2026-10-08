# PHYFlow Engineering Execution Report
**Job ID:** `inverter_ff`  
**Design:** `inverter` | **Corner:** `FF`  
**Overall Status:** `PASSED` | **Runtime:** `0.24 s`  

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
- **WNS (Worst Negative Slack):** `0.350 ns`
- **TNS (Total Negative Slack):** `0.000 ns`
- **Estimated FMax:** `103.63 MHz`
- **Critical Path:** `reg_out/D (rising edge clock clk)`

### Physical Area & Placement (OpenROAD / Yosys)
- **Total Area:** `150.00 µm²`
- **Gate / Cell Count:** `12`
- **Core Utilization:** `42.5%`

### Custom-Cell SPICE Simulation (ngspice)
- **SPICE Convergence:** `PASS`
- **Logic Functionality:** `PASS`
- **Rise Delay (50%-50%):** `12.1 ps`
- **Fall Delay (50%-50%):** `9.1 ps`
- **VOH / VOL:** `1.80 V` / `0.00 V`

## 3. Validation Threshold Checks

> [!NOTE]
> All design validation threshold constraints PASSED successfully.

---
*Report generated automatically by PHYFlow Framework.*