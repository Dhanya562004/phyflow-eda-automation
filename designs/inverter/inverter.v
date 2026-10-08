// Inverter Custom Cell Verilog Representation
module inverter (
    input wire A,
    output wire Y
);
    assign Y = ~A;
endmodule
