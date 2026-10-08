# OpenSTA Static Timing Analysis Script for PHYFlow

puts "=== PHYFlow Tcl Automation: Starting OpenSTA Timing Analysis ==="

# Read Liberty Library
read_liberty libs/liberty/sky130_fd_sc_hd__tt_025C_1v80.lib

# Link Design
link_design inverter

# Define Clock Constraint (100 MHz target, 10.0 ns period)
create_clock -name clk -period 10.0 [get_ports A]

# Report Timing Slack & WNS/TNS
report_checks -digits 3
report_wns
report_tns

puts "=== OpenSTA Timing Analysis Completed ==="
