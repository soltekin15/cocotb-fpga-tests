# Simulator
SIM ?= icarus

# Language
TOPLEVEL_LANG ?= verilog

# Sources
VERILOG_SOURCES += $(PWD)/../rtl/fifo_test_top.sv
VERILOG_SOURCES += $(PWD)/../rtl/axis_fifo.sv
VERILOG_SOURCES += $(PWD)/../rtl/axis_counter.sv

# Top module
TOPLEVEL = fifo_test_top

# Test module
MODULE = test_axis_fifo

# Flags
COMPILE_ARGS += -g2012

# Include cocotb
include $(shell cocotb-config --makefiles)/Makefile.sim

# ========================================
# SELECTIVE TEST TARGETS
# ========================================

.PHONY: test1
test1:
	@echo "🎯 Running Test 1: Basic FIFO flow"
	$(MAKE) sim TESTCASE=test_basic_fifo_flow

.PHONY: test2
test2:
	@echo "🎯 Running Test 2: Backpressure"
	$(MAKE) sim TESTCASE=test_fifo_backpressure_consumer

.PHONY: test3
test3:
	@echo "🎯 Running Test 3: Status flags"
	$(MAKE) sim TESTCASE=test_fifo_status_flags

.PHONY: test4
test4:
	@echo "🎯 Running Test 4: Multiple packets"
	$(MAKE) sim TESTCASE=test_multiple_packets_through_fifo

.PHONY: test_13
test_13:
	@echo "🎯 Running Tests 1 & 3"
	$(MAKE) sim TESTCASE=test_basic_fifo_flow,test_fifo_status_flags

.PHONY: test_24
test_24:
	@echo "🎯 Running Tests 2 & 4"
	$(MAKE) sim TESTCASE=test_fifo_backpressure_consumer,test_multiple_packets_through_fifo

.PHONY: test_all
test_all:
	@echo "🎯 Running ALL tests"
	$(MAKE) sim

.PHONY: waves
waves:
	@echo "Running with waves..."
	$(MAKE) sim

.PHONY: clean_all
clean_all: clean
	rm -f *.vcd *.fst

.PHONY: help_tests
help_tests:
	@echo "Available test targets:"
	@echo "  test1      - Run only Test 1 (Basic flow)"
	@echo "  test2      - Run only Test 2 (Backpressure)"  
	@echo "  test3      - Run only Test 3 (Status flags)"
	@echo "  test4      - Run only Test 4 (Multiple packets)"
	@echo "  test_13    - Run Tests 1 & 3"
	@echo "  test_24    - Run Tests 2 & 4"
	@echo "  test_all   - Run ALL tests"
	@echo "  waves      - Run with waveforms"
	@echo ""
	@echo "Examples:"
	@echo "  make test1"
	@echo "  make test_13"
	@echo "  make test_all"