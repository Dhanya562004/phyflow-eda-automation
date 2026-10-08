// 2:1 Multiplexer Verilog Representation
module mux2 (
    input wire I0,
    input wire I1,
    input wire S,
    output wire Y
);
    assign Y = S ? I1 : I0;
endmodule
