* SPICE Testbench for Inverter Custom-Cell Validation
.include "../../libs/spice/sky130_fd_sc_hd.spice"
.include "inverter.sp"

VVDD VDD 0 DC 1.8V
VVSS VSS 0 DC 0.0V
VA A 0 PULSE(0 1.8 1ns 50ps 50ps 5ns 10ns)

X1 A Y VDD VSS inverter

.tran 10ps 15ns
.meas tran trise TRIG v(Y) VAL=0.18 RISE=1 TARG v(Y) VAL=1.62 RISE=1
.meas tran tfall TRIG v(Y) VAL=1.62 FALL=1 TARG v(Y) VAL=0.18 FALL=1
.meas tran voh MAX v(Y)
.meas tran vol MIN v(Y)

.control
run
quit
.endc
.end
