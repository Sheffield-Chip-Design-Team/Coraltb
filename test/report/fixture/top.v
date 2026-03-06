module top (
    input clk,
    input rst,
    output reg [3:0] counter,
    output wire result1,
    output wire result2
);

sub sub1(
.counter(counter),
.result(result1)
);

sub sub2(
    .counter(counter),
    .result(result2)
);


always @(posedge clk)begin
    if (~rst) begin
        counter <= counter + 1;
    end else begin
        counter <= 0;
    end
end

endmodule

