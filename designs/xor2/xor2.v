// XOR2 Cell Verilog Representation
module xor2 (
    input wire A,
    input wire B,
    output wire Y
);
    assign Y = A ^ B;
endmodule
