// NAND2 Custom Cell Verilog Representation
module nand2 (
    input wire A,
    input wire B,
    output wire Y
);
    assign Y = ~(A & B);
endmodule
