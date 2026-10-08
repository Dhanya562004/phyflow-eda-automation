# OpenROAD Floorplanning Automation Script for PHYFlow

puts "=== PHYFlow Tcl Automation: Starting OpenROAD Floorplanning ==="

# Read LEF & Technology Files
read_lef libs/lef/sky130_fd_sc_hd.lef

# Initialize Floorplan (Die Area & Core Utilization)
initialize_floorplan -utilization 45 -aspect_ratio 1.0 -core_space 10.0

# Place IO Pins
place_pins -hor_layers met3 -ver_layers met2

puts "=== OpenROAD Floorplanning Completed ==="
