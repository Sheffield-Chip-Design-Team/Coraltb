// Adder module for testing 


module adder (
  input wire [WIDTH-1 :0] a,
  input wire [WIDTH-1 :0] b,
  output wire [WIDTH*2-1:0] c
);

  localparam  WIDTH = 4;  
  assign c = a+b;  

endmodule