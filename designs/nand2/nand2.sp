* SPICE Subcircuit for NAND2
.subckt nand2 A B Y VDD VSS
M1 Y A VDD VDD pmos w=1.0u l=0.15u
M2 Y B VDD VDD pmos w=1.0u l=0.15u
M3 Y A N1  VSS nmos w=1.0u l=0.15u
M4 N1 B VSS VSS nmos w=1.0u l=0.15u
.ends nand2
