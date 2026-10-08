# OpenROAD Placement & Routing Automation Script for PHYFlow

puts "=== PHYFlow Tcl Automation: Starting OpenROAD Placement & Routing ==="

# Read LEF Physical Library
read_lef libs/lef/sky130_fd_sc_hd.lef

# Initialize Floorplan
initialize_floorplan -utilization 50 -aspect_ratio 1.0 -core_space 10.0

# Global & Detailed Placement
global_placement
detailed_placement

# Global & Detailed Routing
global_route
detailed_route

# Check Design Rule Checks (DRC)
check_placement
check_antennas

puts "=== OpenROAD Placement & Routing Completed ==="
