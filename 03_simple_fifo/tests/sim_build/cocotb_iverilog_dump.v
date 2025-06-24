module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/simple_fifo.fst");
    $dumpvars(0, simple_fifo);
end
endmodule
