// NOR2 Custom Cell Verilog Representation
module nor2 (
    input wire A,
    input wire B,
    output wire Y
);
    assign Y = ~(A | B);
endmodule
