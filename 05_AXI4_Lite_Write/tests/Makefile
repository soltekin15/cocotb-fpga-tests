# Simulator
SIM ?= icarus

# Language
TOPLEVEL_LANG ?= verilog

# Sources
VERILOG_SOURCES += $(PWD)/../rtl/axi_lite_slave.sv

# Top module
TOPLEVEL = axi_lite_slave

# Test module
MODULE = test_axi_write

# Flags
COMPILE_ARGS += -g2012

# Include cocotb
include $(shell cocotb-config --makefiles)/Makefile.sim

# Custom targets
.PHONY: waves
waves:
	@echo "Running with waves..."
	$(MAKE) sim

.PHONY: clean_all
clean_all: clean
	rm -f *.vcd *.fst