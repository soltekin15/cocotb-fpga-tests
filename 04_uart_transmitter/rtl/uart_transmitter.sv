module uart_transmitter #(
    parameter CLOCK_FREQ = 100_000_000,  // 100MHz
    parameter BAUD_RATE = 9600           // 9600 baud
)(
    input  wire       clk,
    input  wire       rst_n,
    
    // Data interface
    input  wire [7:0] tx_data,
    input  wire       tx_valid,
    output reg        tx_ready,
    
    // UART output
    output reg        uart_tx
);

// Baud rate generator
localparam BAUD_TICKS = CLOCK_FREQ / BAUD_RATE;
reg [$clog2(BAUD_TICKS)-1:0] baud_counter;
reg baud_tick;

// State machine
typedef enum reg [2:0] {
    IDLE    = 3'b000,
    START   = 3'b001,
    DATA    = 3'b010,
    STOP    = 3'b011
} state_t;

state_t state, next_state;
reg [7:0] shift_reg;
reg [2:0] bit_counter;

// Baud rate generator
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        baud_counter <= 0;
        baud_tick <= 0;
    end else begin
        if (baud_counter == BAUD_TICKS - 1) begin
            baud_counter <= 0;
            baud_tick <= 1;
        end else begin
            baud_counter <= baud_counter + 1;
            baud_tick <= 0;
        end
    end
end

// State machine - next state logic
always @(*) begin
    case (state)
        IDLE: begin
            if (tx_valid)
                next_state = START;
            else
                next_state = IDLE;
        end
        
        START: begin
            if (baud_tick)
                next_state = DATA;
            else
                next_state = START;
        end
        
        DATA: begin
            if (baud_tick && bit_counter == 7)
                next_state = STOP;
            else
                next_state = DATA;
        end
        
        STOP: begin
            if (baud_tick)
                next_state = IDLE;
            else
                next_state = STOP;
        end
        
        default: next_state = IDLE;
    endcase
end

// State machine - state register
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state <= IDLE;
    end else begin
        state <= next_state;
    end
end

// Data path
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        shift_reg <= 8'h00;
        bit_counter <= 0;
        tx_ready <= 1;
        uart_tx <= 1;
    end else begin
        case (state)
            IDLE: begin
                tx_ready <= 1;
                uart_tx <= 1;
                if (tx_valid) begin
                    shift_reg <= tx_data;
                    tx_ready <= 0;
                end
            end
            
            START: begin
                uart_tx <= 0;  // Start bit
                tx_ready <= 0;
            end
            
            DATA: begin
                if (baud_tick) begin
                    uart_tx <= shift_reg[0];
                    shift_reg <= {1'b0, shift_reg[7:1]};
                    bit_counter <= bit_counter + 1;
                end
                tx_ready <= 0;
            end
            
            STOP: begin
                uart_tx <= 1;  // Stop bit
                tx_ready <= 0;
                if (baud_tick) begin
                    bit_counter <= 0;
                end
            end
        endcase
    end
end

endmodule