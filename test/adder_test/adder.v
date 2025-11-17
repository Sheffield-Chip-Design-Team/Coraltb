// Adder module for testing 

module adder #(parameter WIDTH = 4) (
  input wire [WIDTH-1 :0] a,
  input wire [WIDTH-1 :0] b,
  output wire [WIDTH*2-1:0] c
);

  assign c = a+b;  

endmodule