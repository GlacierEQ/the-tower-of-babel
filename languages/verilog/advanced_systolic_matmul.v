// Verilog — Advanced Example: Systolic Array Matrix Multiply Unit (TPU-Style)
// What: 4x4 systolic array performing pipelined matrix multiplication.
// Where: AI/ML hardware accelerators, tensor processing units, FPGA inference.
// When: Deploying custom neural network inference at the hardware level.
// Why: Systolic arrays achieve maximum data reuse with minimal memory bandwidth.
// How: Weight-stationary dataflow where activations flow right and partial sums flow down.

module systolic_pe (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [15:0] a_in,        // Activation input (flows right)
    input  wire [15:0] b_in,        // Weight (stationary, loaded once)
    input  wire [31:0] sum_in,      // Partial sum input (flows down)
    input  wire        weight_load, // Load weight signal
    output reg  [15:0] a_out,       // Activation output to right neighbor
    output reg  [31:0] sum_out      // Partial sum output to bottom neighbor
);
    reg [15:0] weight;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            weight  <= 16'b0;
            a_out   <= 16'b0;
            sum_out <= 32'b0;
        end else begin
            if (weight_load)
                weight <= b_in;

            // MAC: multiply-accumulate
            a_out   <= a_in;
            sum_out <= sum_in + (a_in * weight);
        end
    end
endmodule

module systolic_array_4x4 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        weight_load,
    input  wire [15:0] a_row [0:3],     // 4 activation inputs
    input  wire [15:0] b_col [0:3],     // 4 weight columns
    output wire [31:0] result [0:3]     // 4 accumulated outputs
);
    wire [15:0] a_wire [0:3][0:4];  // Horizontal activation wires
    wire [31:0] s_wire [0:4][0:3];  // Vertical partial sum wires

    genvar r, c;
    generate
        for (r = 0; r < 4; r = r + 1) begin : row_gen
            assign a_wire[r][0] = a_row[r];
            for (c = 0; c < 4; c = c + 1) begin : col_gen
                if (r == 0)
                    assign s_wire[0][c] = 32'b0;

                systolic_pe pe_inst (
                    .clk(clk),
                    .rst_n(rst_n),
                    .a_in(a_wire[r][c]),
                    .b_in(b_col[c]),
                    .sum_in(s_wire[r][c]),
                    .weight_load(weight_load),
                    .a_out(a_wire[r][c+1]),
                    .sum_out(s_wire[r+1][c])
                );
            end
        end
    endgenerate

    // Output: bottom row of partial sums
    generate
        for (c = 0; c < 4; c = c + 1) begin : out_gen
            assign result[c] = s_wire[4][c];
        end
    endgenerate
endmodule

// Testbench
module systolic_array_tb;
    reg         clk, rst_n, weight_load;
    reg  [15:0] a_row [0:3];
    reg  [15:0] b_col [0:3];
    wire [31:0] result [0:3];

    systolic_array_4x4 uut (
        .clk(clk), .rst_n(rst_n), .weight_load(weight_load),
        .a_row(a_row), .b_col(b_col), .result(result)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        rst_n = 0; weight_load = 0;
        a_row[0] = 0; a_row[1] = 0; a_row[2] = 0; a_row[3] = 0;
        b_col[0] = 0; b_col[1] = 0; b_col[2] = 0; b_col[3] = 0;

        #20 rst_n = 1;

        // Load weights
        weight_load = 1;
        b_col[0] = 16'd1; b_col[1] = 16'd2; b_col[2] = 16'd3; b_col[3] = 16'd4;
        #10 weight_load = 0;

        // Stream activations
        a_row[0] = 16'd1; a_row[1] = 16'd2; a_row[2] = 16'd3; a_row[3] = 16'd4;
        #100;

        $display("Result[0]=%0d [1]=%0d [2]=%0d [3]=%0d",
                 result[0], result[1], result[2], result[3]);
        $finish;
    end
endmodule
