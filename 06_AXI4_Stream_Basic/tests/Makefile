# Simulator
SIM ?= icarus

# Language
TOPLEVEL_LANG ?= verilog

# Sources
VERILOG_SOURCES += $(PWD)/../rtl/axis_counter.sv

# Top module
TOPLEVEL = axis_counter

# Test module
MODULE = test_axis_counter

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