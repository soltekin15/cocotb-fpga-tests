import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from axi_driver import AXI4LiteDriver

@cocotb.test()
async def test_basic_write(dut):
    """Test 1: Basit write işlemi"""
    
    # Clock başlat
    clock = Clock(dut.aclk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Driver oluştur
    axi = AXI4LiteDriver(dut)
    await axi.reset(10)
    
    # Test
    test_addr = 0x04
    test_data = 0xCAFEBABE
    
    dut._log.info(f"Writing 0x{test_data:08x} to 0x{test_addr:02x}")
    
    # Write
    bresp = await axi.write(test_addr, test_data)
    assert bresp == 0, f"Write failed: bresp={bresp}"
    
    # Read back
    rdata, rresp = await axi.read(test_addr)
    assert rresp == 0, f"Read failed: rresp={rresp}"
    assert rdata == test_data, f"Data mismatch: got 0x{rdata:08x}"
    
    dut._log.info("✅ Basic write test PASSED")

@cocotb.test()
async def test_multiple_writes(dut):
    """Test 2: Çoklu write işlemi"""
    
    clock = Clock(dut.aclk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    axi = AXI4LiteDriver(dut)
    await axi.reset(10)
    
    # Test cases
    test_cases = [
        (0x00, 0x11111111),
        (0x04, 0x22222222),
        (0x08, 0x33333333),
        (0x0C, 0x44444444),
    ]
    
    # Write all
    for addr, data in test_cases:
        bresp = await axi.write(addr, data)
        assert bresp == 0
        
    # Read all
    for addr, expected in test_cases:
        rdata, rresp = await axi.read(addr)
        assert rresp == 0
        assert rdata == expected
        dut._log.info(f"✅ 0x{addr:02x} = 0x{rdata:08x}")
    
    dut._log.info("✅ Multiple writes PASSED")

@cocotb.test()
async def test_byte_enable(dut):
    """Test 3: Byte enable test"""
    
    clock = Clock(dut.aclk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    axi = AXI4LiteDriver(dut)
    await axi.reset(10)
    
    addr = 0x10
    
    # Clear register
    await axi.write(addr, 0x00000000, strobe=0xF)
    
    # Write only byte 0
    await axi.write(addr, 0xDEADBEEF, strobe=0x1)
    rdata, _ = await axi.read(addr)
    assert rdata == 0x000000EF
    dut._log.info(f"Byte 0: 0x{rdata:08x}")
    
    # Write byte 1
    await axi.write(addr, 0xDEADBEEF, strobe=0x2)
    rdata, _ = await axi.read(addr)
    assert rdata == 0x0000BEEF
    dut._log.info(f"Byte 1: 0x{rdata:08x}")
    
    dut._log.info("✅ Byte enable PASSED")