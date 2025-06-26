module axis_counter #(
    parameter DATA_WIDTH = 32,
    parameter PACKET_SIZE = 4
)(
    input  logic                    clk,
    input  logic                    rst_n,
    
    // Control interface
    input  logic                    start,
    output logic                    done,
    
    // AXI Stream Master (Source)
    output logic                    m_axis_tvalid,
    input  logic                    m_axis_tready,
    output logic [DATA_WIDTH-1:0]   m_axis_tdata,
    output logic                    m_axis_tlast
);

// Internal counters
logic [$clog2(PACKET_SIZE):0] word_count;
logic [DATA_WIDTH-1:0] data_counter;
logic [DATA_WIDTH-1:0] current_tdata;  // *** FIX: Registered output ***

// State machine
typedef enum logic [1:0] {
    IDLE,
    SENDING,
    DONE_STATE
} state_t;

state_t current_state;

// State machine
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        current_state <= IDLE;
        word_count <= 0;
        data_counter <= 0;
        current_tdata <= 0;     // *** FIX: Initialize registered output ***
        done <= 0;
    end else begin
        case (current_state)
            IDLE: begin
                done <= 0;
                if (start) begin
                    current_state <= SENDING;
                    word_count <= 0;
                    data_counter <= data_counter + 1;      // Next global counter
                    current_tdata <= data_counter + 1;     // *** FIX: Prepare first data ***
                end
            end
            
            SENDING: begin
                // *** FIX: Only update on successful handshake ***
                if (m_axis_tvalid && m_axis_tready) begin
                    word_count <= word_count + 1;
                    
                    if (word_count == PACKET_SIZE - 1) begin
                        // Last word transferred, go to done
                        current_state <= DONE_STATE;
                    end else begin
                        // Prepare next data for next transfer
                        data_counter <= data_counter + 1;
                        current_tdata <= data_counter + 1;  // *** FIX: Next data ***
                    end
                end
                // *** IMPORTANT: When tready=0, current_tdata stays stable ***
            end
            
            DONE_STATE: begin
                done <= 1;
                if (!start) begin
                    current_state <= IDLE;
                end
            end
        endcase
    end
end

// Output assignments
assign m_axis_tvalid = (current_state == SENDING);
assign m_axis_tdata  = current_tdata;   // *** FIX: Use registered output ***
assign m_axis_tlast  = (word_count == PACKET_SIZE - 1) && (current_state == SENDING);

// Debug dump
initial begin
    $dumpfile("axis_waves.vcd");
    $dumpvars(0, axis_counter);
end

endmodule