module processing_element #(
  parameter WIDTH = 16,
  parameter ACC_WIDTH = 40
) (
  input logic clk,
  input logic reset_n,
  input logic signed [WIDTH-1:0] a_in,
  input logic signed [WIDTH-1:0] b_in,
  input logic valid_in,
  output logic signed [WIDTH-1:0] a_out,
  output logic signed [WIDTH-1:0] b_out,
  output logic signed [ACC_WIDTH-1:0] accumulator,
  output logic valid_out
);
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      a_out <= '0; b_out <= '0; accumulator <= '0; valid_out <= 1'b0;
    end else begin
      a_out <= a_in;
      b_out <= b_in;
      valid_out <= valid_in;
      if (valid_in) accumulator <= accumulator + a_in * b_in;
    end
  end

  property accumulation_requires_valid;
    @(posedge clk) disable iff (!reset_n)
      !valid_in |=> $stable(accumulator);
  endproperty
  assert property (accumulation_requires_valid);
endmodule

module systolic_array (
  input logic clk,
  input logic reset_n,
  input logic signed [15:0] a,
  input logic signed [15:0] b,
  input logic valid,
  output logic signed [39:0] result
);
  logic signed [15:0] unused_a, unused_b;
  logic unused_valid;
  processing_element pe(
    .clk, .reset_n, .a_in(a), .b_in(b), .valid_in(valid),
    .a_out(unused_a), .b_out(unused_b), .accumulator(result), .valid_out(unused_valid)
  );
endmodule
