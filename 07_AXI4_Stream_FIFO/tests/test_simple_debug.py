import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from axis_fifo_driver import AXISFIFODriver

@cocotb.test()
async def test_backpressure_streaming(dut):
    """Test 2: Real streaming backpressure"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 2: Streaming backpressure")
    
    # Producer başlat
    await fifo_driver.start_producer()
    
    # İlk data'yı al (stream mode)
    await RisingEdge(dut.clk)
    while not (dut.m_axis_tvalid.value and dut.m_axis_tready.value):
        await RisingEdge(dut.clk)
    first_data = int(dut.m_axis_tdata.value)
    dut._log.info(f"📊 First data: {first_data}")
    
    # Backpressure uygula
    dut.m_axis_tready.value = 0
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.m_axis_tready.value = 1
    
    # Kalan data'ları al
    remaining_data = []
    for _ in range(10):
        await RisingEdge(dut.clk)
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            data = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            remaining_data.append(data)
            dut._log.info(f"📊 Received: {data}, tlast={tlast}")
            if tlast:
                break
    
    await fifo_driver.stop_producer()
    
    # Validate
    total_data = [first_data] + remaining_data
    expected_data = [1, 2, 3, 4]
    assert total_data == expected_data, f"Got {total_data}, expected {expected_data}"
    
    dut._log.info("✅ Streaming backpressure test PASSED")