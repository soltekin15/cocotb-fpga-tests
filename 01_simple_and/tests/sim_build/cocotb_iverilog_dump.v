module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/simple_and.fst");
    $dumpvars(0, simple_and);
end
endmodule
