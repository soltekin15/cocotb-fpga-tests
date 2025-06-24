import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_counter_2bit(dut):
    """2-bit counter testi"""

    #Clock olustur(100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    #Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    await Timer(50, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    #Reset Kontrolu
    assert dut.rst_n == 1, f"dut.rst_n == 0 olmamali"
    dut._log.info("Reset Testi Gecti")

    await Timer(10, units="ns")
    dut.enable.value = 1

    #5 cycle say 
    for i in range(5):
        await RisingEdge(dut.clk)
        expected = i % 4
        actual = int(dut.count.value)
        assert expected == actual, f"False ==> Cycle:{i + 1} -> expected: {expected} , actual: {actual}"
        dut._log.info(f"True ==> Cycle:{i + 1} -> expected: {expected} , actual: {actual}")

    await Timer(1,units="ns")
    dut.enable.value = 0
    current_count = int(dut.count.value)
    
    for i in range(3):
        await RisingEdge(dut.clk)
        assert current_count == dut.count.value
        dut._log.info("Deger Degismedi enable = 0 iken")
    

