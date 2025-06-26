module axi_lite_slave (
    input  logic        aclk,
    input  logic        aresetn,
    
    // Write Address Channel
    input  logic        awvalid,
    output logic        awready,
    input  logic [31:0] awaddr,
    
    // Write Data Channel  
    input  logic        wvalid,
    output logic        wready,
    input  logic [31:0] wdata,
    input  logic [3:0]  wstrb,
    
    // Write Response Channel
    output logic        bvalid,
    input  logic        bready,
    output logic [1:0]  bresp,
    
    // Read Address Channel
    input  logic        arvalid,
    output logic        arready,
    input  logic [31:0] araddr,
    
    // Read Data Channel
    output logic        rvalid,
    input  logic        rready,
    output logic [31:0] rdata,
    output logic [1:0]  rresp
);

// Register bank
logic [31:0] registers [16];

// Debug sinyalleri
wire [31:0] debug_reg0 = registers[0];
wire [31:0] debug_reg1 = registers[1];
wire [31:0] debug_reg2 = registers[2];
wire [31:0] debug_reg3 = registers[3];
wire [31:0] debug_reg4 = registers[4];
wire [31:0] debug_reg5 = registers[5];

// Write FSM
typedef enum logic [1:0] {
    W_IDLE, W_WAIT_DATA, W_RESP
} write_state_t;

write_state_t write_state;
logic [31:0] write_addr_reg;

// *** FIX: Registered outputs instead of combinational ***
logic [1:0] bresp_reg;
logic [1:0] rresp_reg;
logic [31:0] rdata_reg;

// Write Logic
always_ff @(posedge aclk or negedge aresetn) begin
    if (!aresetn) begin
        write_state <= W_IDLE;
        awready <= 1'b1;       // *** FIX: Start ready ***
        wready <= 1'b0;
        bvalid <= 1'b0;
        write_addr_reg <= 32'h0;
        bresp_reg <= 2'b00;    // *** FIX: Initialize bresp ***
        
        for (int i = 0; i < 16; i++) registers[i] <= 32'h0;
    end else begin
        case (write_state)
            W_IDLE: begin
                awready <= 1'b1;
                if (awvalid && awready) begin
                    write_addr_reg <= awaddr;
                    write_state <= W_WAIT_DATA;
                    awready <= 1'b0;
                    wready <= 1'b1;
                    // *** FIX: Set bresp early ***
                    bresp_reg <= (awaddr[5:2] < 16) ? 2'b00 : 2'b10;
                end
            end
            
            W_WAIT_DATA: begin
                if (wvalid && wready) begin
                    // Perform write
                    if (write_addr_reg[5:2] < 16) begin
                        for (int i = 0; i < 4; i++) begin
                            if (wstrb[i])
                                registers[write_addr_reg[5:2]][i*8 +: 8] <= wdata[i*8 +: 8];
                        end
                    end
                    write_state <= W_RESP;
                    wready <= 1'b0;
                    bvalid <= 1'b1;
                end
            end 
            
            W_RESP: begin
                if (bvalid && bready) begin
                    bvalid <= 1'b0;
                    write_state <= W_IDLE;
                end
            end
        endcase
    end
end

// Read Logic  
always_ff @(posedge aclk or negedge aresetn) begin
    if (!aresetn) begin
        arready <= 1'b1;
        rvalid <= 1'b0;
        rresp_reg <= 2'b00;     // *** FIX: Initialize rresp ***
        rdata_reg <= 32'h0;    // *** FIX: Initialize rdata ***
    end else begin
        if (arvalid && arready) begin
            // *** FIX: Capture read data immediately ***
            rdata_reg <= (araddr[5:2] < 16) ? registers[araddr[5:2]] : 32'hDEADBEEF;
            rresp_reg <= (araddr[5:2] < 16) ? 2'b00 : 2'b10;
            arready <= 1'b0;
            rvalid <= 1'b1;
        end else if (rvalid && rready) begin
            rvalid <= 1'b0;
            arready <= 1'b1;
        end
    end
end

// *** FIX: Use registered outputs ***
assign bresp = bresp_reg;
assign rresp = rresp_reg;
assign rdata = rdata_reg;


initial begin
    $dumpfile("axi_waves.vcd");
    $dumpvars(0, axi_lite_slave);



end


endmodule