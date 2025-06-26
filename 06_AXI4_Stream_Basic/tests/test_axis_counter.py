import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from axis_driver import AXISDriver

@cocotb.test()
async def test_basic_packet(dut):
    """Test 1: Basit packet transfer"""
    
    # Clock başlat
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Driver oluştur
    axis = AXISDriver(dut)
    await axis.reset(10)
    
    dut._log.info("🎯 Test 1: Basic packet transfer")
    
    # Transfer başlat
    await axis.start_transfer()
    
    # Packet receive et
    received_data = await axis.receive_packet(expected_size=4)
    
    # Done bekle
    await axis.wait_done()
    
    # Stop transfer
    await axis.stop_transfer()
    
    # Validate data
    expected_data = [1, 2, 3, 4]
    assert received_data == expected_data, f"Data mismatch: got {received_data}, expected {expected_data}"
    
    dut._log.info("✅ Basic packet test PASSED")





@cocotb.test()
async def test_backpressure(dut):
    """Test 2: Backpressure handling - FINAL"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    axis = AXISDriver(dut)
    await axis.reset(10)
    
    dut._log.info("🎯 Test 2: Backpressure test")
    
    # Transfer başlat
    await axis.start_transfer()
    
    # İlk data'yı hemen al (data=1)
    await RisingEdge(dut.clk)
    while not (dut.m_axis_tvalid.value and dut.m_axis_tready.value):
        await RisingEdge(dut.clk)
    
    first_data = int(dut.m_axis_tdata.value)
    dut._log.info(f"📊 First data: {first_data}")
    
    # Backpressure uygula (sonraki transfer için)
    dut.m_axis_tready.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut._log.info("🔒 Applied 3-cycle backpressure")
    
    # Backpressure'ı kaldır ve kalan data'ları al
    dut.m_axis_tready.value = 1
    remaining_data = []
    
    for cycle in range(10):
        await RisingEdge(dut.clk)
        
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            tdata = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            
            remaining_data.append(tdata)
            dut._log.info(f"📊 Received: data={tdata}, tlast={tlast}")
            
            if tlast:
                break
    
    await axis.wait_done()
    await axis.stop_transfer()
    
    # Combine all data
    all_data = [first_data] + remaining_data
    expected_data = [1, 2, 3, 4]
    
    dut._log.info(f"📋 Total received: {all_data}")
    assert all_data == expected_data, f"Backpressure test failed: got {all_data}, expected {expected_data}"
    
    dut._log.info("✅ Backpressure test PASSED")





@cocotb.test()
async def test_multiple_packets(dut):
    """Test 3: Çoklu packet transfer"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    axis = AXISDriver(dut)
    await axis.reset(10)
    
    dut._log.info("🎯 Test 3: Multiple packets")
    
    # İlk packet
    await axis.start_transfer()
    packet1 = await axis.receive_packet(expected_size=4)
    await axis.wait_done()
    await axis.stop_transfer()
    
    # Biraz bekle
    for _ in range(5):
        await RisingEdge(dut.clk)
    
    # İkinci packet
    await axis.start_transfer()
    packet2 = await axis.receive_packet(expected_size=4)
    await axis.wait_done()
    await axis.stop_transfer()
    
    # Validate
    expected1 = [1, 2, 3, 4]
    expected2 = [5, 6, 7, 8]  # Counter devam ediyor
    
    assert packet1 == expected1, f"Packet 1: {packet1}"
    assert packet2 == expected2, f"Packet 2: {packet2}"
    
    dut._log.info("✅ Multiple packets test PASSED")