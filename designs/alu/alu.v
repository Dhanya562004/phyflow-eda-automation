// 4-bit Arithmetic Logic Unit (ALU) Verilog Representation
module alu (
    input wire [3:0] A,
    input wire [3:0] B,
    input wire [1:0] opcode,
    output reg [3:0] result,
    output wire zero
);
    always @(*) begin
        case (opcode)
            2'b00: result = A + B;   // ADD
            2'b01: result = A - B;   // SUB
            2'b10: result = A & B;   // AND
            2'b11: result = A | B;   // OR
            default: result = 4'b0000;
        endcase
    end

    assign zero = (result == 4'b0000);
endmodule
