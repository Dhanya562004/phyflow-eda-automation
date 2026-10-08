# Yosys Synthesis Automation Script for PHYFlow
# Orchestrated by Python FlowManager

if {[info exists env(DESIGN_NAME)]} {
    set design $env(DESIGN_NAME)
} else {
    set design "inverter"
}

puts "=== PHYFlow Tcl Automation: Starting Yosys Synthesis for $design ==="

# Read Verilog Source
read_verilog designs/$design/$design.v

# Elaborate Hierarchy
hierarchy -top $design

# Perform Generic Synthesis Pass
synth -top $design

# Read Technology Liberty File
read_liberty -lib libs/liberty/sky130_fd_sc_hd__tt_025C_1v80.lib

# Technology Mapping
abc -liberty libs/liberty/sky130_fd_sc_hd__tt_025C_1v80.lib

# Clean up
opt_clean -purge

# Report Statistics
stat -liberty libs/liberty/sky130_fd_sc_hd__tt_025C_1v80.lib

puts "=== Yosys Synthesis Automation Completed ==="
