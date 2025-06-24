module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/counter_2bit.fst");
    $dumpvars(0, counter_2bit);
end
endmodule
