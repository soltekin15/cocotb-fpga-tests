module counter_2bit (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enable,
    output reg  [1:0] count
);

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        count <= 2'b00;
    end else if (enable) begin
        count <= count + 1;
    end
end

endmodule