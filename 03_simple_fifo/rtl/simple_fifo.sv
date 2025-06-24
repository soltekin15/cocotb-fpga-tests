module simple_fifo #(
    parameter DATA_WIDTH = 8,
    parameter DEPTH = 4
)(
    input  wire                    clk,
    input  wire                    rst_n,
    
    // Write interface
    input  wire                    wr_en,
    input  wire [DATA_WIDTH-1:0]   wr_data,
    output wire                    full,
    
    // Read interface  
    input  wire                    rd_en,
    output reg  [DATA_WIDTH-1:0]   rd_data,
    output wire                    empty
);

reg [DATA_WIDTH-1:0] memory [0:DEPTH-1];
reg [2:0] wr_ptr, rd_ptr;
reg [2:0] count;

// Status flags
assign full = (count == DEPTH);
assign empty = (count == 0);

// FIFO operation (tek always bloğunda)
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        wr_ptr <= 0;
        rd_ptr <= 0;
        count <= 0;
        rd_data <= 8'h00;  // rd_data'yı da reset et
    end else begin
        // Count update
        case ({wr_en && !full, rd_en && !empty})
            2'b10: count <= count + 1;  // Sadece write
            2'b01: count <= count - 1;  // Sadece read
            2'b11: count <= count;      // Write + read (aynı anda)
            2'b00: count <= count;      // Hiçbiri
        endcase
        
        // Write operation
        if (wr_en && !full) begin
            memory[wr_ptr] <= wr_data;
            wr_ptr <= (wr_ptr + 1) % DEPTH;
        end
        
        // Read operation
        if (rd_en && !empty) begin
            rd_data <= memory[rd_ptr];
            rd_ptr <= (rd_ptr + 1) % DEPTH;
        end
    end
end

endmodule