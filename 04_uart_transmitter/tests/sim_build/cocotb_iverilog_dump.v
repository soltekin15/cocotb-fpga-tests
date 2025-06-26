module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/uart_transmitter.fst");
    $dumpvars(0, uart_transmitter);
end
endmodule
