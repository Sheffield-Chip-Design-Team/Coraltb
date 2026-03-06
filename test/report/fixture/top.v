module top (
    input clk,
    input rst,
    output reg [3:0] counter
);

always @(posedge clk)begin
    if (~rst) begin
        counter <= counter + 2;
    end else begin
        counter <= 0;
    end
end

endmodule
