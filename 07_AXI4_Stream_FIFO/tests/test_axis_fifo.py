import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from axis_fifo_driver import AXISFIFODriver

@cocotb.test()
async def test_basic_fifo_flow(dut):
    """Test 1: Basit FIFO flow - Counter → FIFO → Consumer"""
    
    # Clock başlat
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Driver oluştur
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 1: Basic FIFO flow")
    
    # Producer başlat
    await fifo_driver.start_producer()
    
    # *** BASIT STREAMING CONSUME (working version) ***
    received_data = []
    
    for cycle in range(15):  # Yeterli cycle
        await RisingEdge(dut.clk)
        
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            tdata = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            received_data.append(tdata)
            dut._log.info(f"📊 Received: {tdata}, tlast={tlast}")
            
            if tlast:
                dut._log.info(f"✅ Packet complete: {received_data}")
                break
    
    await fifo_driver.stop_producer()
    
    # Validate
    expected_data = [1, 2, 3, 4]
    assert received_data == expected_data, f"Data mismatch: got {received_data}, expected {expected_data}"
    
    dut._log.info("✅ Basic FIFO flow test PASSED")

@cocotb.test()
async def test_fifo_backpressure_consumer(dut):
    """Test 2: Consumer backpressure - Basit streaming"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 2: Consumer backpressure")
    
    # Producer başlat
    await fifo_driver.start_producer()
    
    # Streaming with backpressure - Manual control
    received_data = []
    backpressure_applied = False
    
    for cycle in range(20):  # Yeterli cycle
        await RisingEdge(dut.clk)
        
        # Backpressure logic: 2 data aldıktan sonra 3 cycle durdur
        if len(received_data) == 2 and not backpressure_applied:
            dut._log.info("🔒 Applying backpressure for 3 cycles...")
            
            # 3 cycle backpressure
            dut.m_axis_tready.value = 0
            await RisingEdge(dut.clk)
            await RisingEdge(dut.clk) 
            await RisingEdge(dut.clk)
            dut.m_axis_tready.value = 1
            
            backpressure_applied = True
            dut._log.info("✅ Backpressure released")
            continue  # Skip this cycle's data check
        
        # Normal data collection
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            tdata = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            received_data.append(tdata)
            dut._log.info(f"📊 Received: {tdata}, tlast={tlast}")
            
            if tlast:
                dut._log.info(f"✅ Packet complete: {received_data}")
                break
    
    await fifo_driver.stop_producer()
    
    # Validate
    expected_data = [1, 2, 3, 4]
    assert received_data == expected_data, f"Backpressure test failed: got {received_data}, expected {expected_data}"
    
    dut._log.info("✅ Consumer backpressure test PASSED")

@cocotb.test()
async def test_fifo_backpressure_consumer(dut):
    """Test 2: Streaming backpressure - Working approach"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 2: Consumer backpressure")
    
    # Producer başlat
    await fifo_driver.start_producer()
    
    # *** ORIGINAL WORKING APPROACH: Manual streaming consume ***
    received_data = []
    
    # Consume first data
    await RisingEdge(dut.clk)
    while not (dut.m_axis_tvalid.value and dut.m_axis_tready.value):
        await RisingEdge(dut.clk)
    first_data = int(dut.m_axis_tdata.value)
    received_data.append(first_data)
    dut._log.info(f"📊 First data: {first_data}")
    
    # Apply backpressure for next data
    dut._log.info("🔒 Applying backpressure...")
    dut.m_axis_tready.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.m_axis_tready.value = 1
    dut._log.info("✅ Backpressure released")
    
    # Continue consuming
    for cycle in range(10):
        await RisingEdge(dut.clk)
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            data = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            received_data.append(data)
            dut._log.info(f"📊 Received: {data}, tlast={tlast}")
            if tlast:
                break
    
    await fifo_driver.stop_producer()
    
    # Validate - Expected behavior for streaming FIFO
    dut._log.info(f"📋 Total received: {received_data}")
    
    # For streaming FIFO, we expect all data to be received
    assert len(received_data) == 4, f"Expected 4 data, got {len(received_data)}: {received_data}"
    assert received_data == [1, 2, 3, 4], f"Data order issue: {received_data}"
    
    dut._log.info("✅ Consumer backpressure test PASSED")

@cocotb.test()
async def test_fifo_status_flags(dut):
    """Test 3: FIFO status in streaming mode"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 3: FIFO status flags")
    
    # Initial empty check
    await RisingEdge(dut.clk)
    assert dut.fifo_empty.value == 1, "FIFO should be empty initially"
    assert dut.fifo_full.value == 0, "FIFO should not be full initially"
    dut._log.info("✅ Initial empty state confirmed")
    
    # Start streaming
    await fifo_driver.start_producer()
    
    # Monitor during streaming
    received_data = []
    max_count_seen = 0
    
    for cycle in range(10):
        await RisingEdge(dut.clk)
        
        empty = dut.fifo_empty.value
        full = dut.fifo_full.value
        count = int(dut.fifo_inst.count.value) if hasattr(dut.fifo_inst, 'count') else 0
        
        max_count_seen = max(max_count_seen, count)
        
        # Data collection
        if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
            tdata = int(dut.m_axis_tdata.value)
            tlast = int(dut.m_axis_tlast.value)
            received_data.append(tdata)
            
            if tlast:
                break
    
    await fifo_driver.stop_producer()
    
    # Validate streaming behavior
    dut._log.info(f"📊 Max FIFO count during streaming: {max_count_seen}")
    dut._log.info(f"📊 Received data: {received_data}")
    
    # In perfect streaming, FIFO rarely gets deep
    assert max_count_seen <= 2, f"Streaming FIFO shouldn't get deep: {max_count_seen}"
    assert received_data == [1, 2, 3, 4], f"Data mismatch: {received_data}"
    
    dut._log.info("✅ FIFO status streaming test PASSED")

@cocotb.test()
async def test_multiple_packets_through_fifo(dut):
    """Test 4: Multiple packets streaming"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    fifo_driver = AXISFIFODriver(dut)
    await fifo_driver.reset(10)
    
    dut._log.info("🎯 Test 4: Multiple packets streaming")
    
    all_packets = []
    
    # 3 packets back-to-back streaming
    for packet_num in range(3):
        dut._log.info(f"📦 Packet {packet_num + 1}/3")
        
        # Start producer
        await fifo_driver.start_producer()
        
        # Stream consume
        packet_data = []
        for cycle in range(10):
            await RisingEdge(dut.clk)
            
            if dut.m_axis_tvalid.value and dut.m_axis_tready.value:
                tdata = int(dut.m_axis_tdata.value)
                tlast = int(dut.m_axis_tlast.value)
                packet_data.append(tdata)
                
                if tlast:
                    break
        
        all_packets.append(packet_data)
        await fifo_driver.stop_producer()
        
        # Small gap between packets
        for _ in range(3):
            await RisingEdge(dut.clk)
    
    # Validate
    expected_packets = [
        [1, 2, 3, 4],
        [5, 6, 7, 8], 
        [9, 10, 11, 12]
    ]
    
    assert all_packets == expected_packets, f"Multi-packet failed: {all_packets}"
    
    dut._log.info("✅ Multiple packets streaming test PASSED")