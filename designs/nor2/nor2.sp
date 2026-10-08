* SPICE Subcircuit for NOR2
.subckt nor2 A B Y VDD VSS
M1 N1 A VDD VDD pmos w=2.0u l=0.15u
M2 Y  B N1  VDD pmos w=2.0u l=0.15u
M3 Y  A VSS VSS nmos w=0.5u l=0.15u
M4 Y  B VSS VSS nmos w=0.5u l=0.15u
.ends nor2
