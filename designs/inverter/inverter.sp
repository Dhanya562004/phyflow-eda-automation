* SPICE Subcircuit for Inverter (INV_X1)
.subckt inverter A Y VDD VSS
M1 Y A VDD VDD pmos w=1.0u l=0.15u
M2 Y A VSS VSS nmos w=0.5u l=0.15u
.ends inverter
