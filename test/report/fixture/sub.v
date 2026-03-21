module sub (
    input [3:0] counter,
    output wire result
);

assign result = counter[3] & counter[2];

endmodule