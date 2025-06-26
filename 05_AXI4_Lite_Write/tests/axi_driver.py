import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import TestFailure

class AXI4LiteDriver:
    def __init__(self, dut):
        self.dut = dut
        self.clock = dut.aclk
        self._init_signals()
        
    def _init_signals(self):
        # Write channels
        self.dut.awvalid.value = 0
        self.dut.awaddr.value = 0
        self.dut.wvalid.value = 0
        self.dut.wdata.value = 0
        self.dut.wstrb.value = 0
        self.dut.bready.value = 1
        
        # Read channels
        self.dut.arvalid.value = 0
        self.dut.araddr.value = 0
        self.dut.rready.value = 1
        
    async def reset(self, cycles=10):
        print("🔄 Starting reset...")
        self.dut.aresetn.value = 0
        self._init_signals()
        
        for i in range(cycles):
            await RisingEdge(self.clock)
            print(f"  Reset cycle {i+1}/{cycles}")
            
        self.dut.aresetn.value = 1
        await RisingEdge(self.clock)
        
        # DEBUG: Reset sonrası tüm sinyalleri kontrol et
        print("✅ Reset completed. Checking signals:")
        print(f"  awready = {self.dut.awready.value}")
        print(f"  wready = {self.dut.wready.value}")
        print(f"  bvalid = {self.dut.bvalid.value}")
        print(f"  bresp = {self.dut.bresp.value}")
        print(f"  arready = {self.dut.arready.value}")
        print(f"  rvalid = {self.dut.rvalid.value}")
        print(f"  rresp = {self.dut.rresp.value}")
        print(f"  rdata = {self.dut.rdata.value}")
        
    async def write(self, address, data, strobe=0xF):
        print(f"\n📝 Starting write: addr=0x{address:08x}, data=0x{data:08x}")
        
        # Address phase
        print("  📍 Address Phase:")
        self.dut.awaddr.value = address
        self.dut.awvalid.value = 1
        print(f"    Set awvalid=1, awaddr=0x{address:08x}")
        
        # Wait for awready
        for cycle in range(100):
            await RisingEdge(self.clock)
            awready_val = self.dut.awready.value
            print(f"    Cycle {cycle}: awready={awready_val}")
            
            if awready_val == 1:
                print("    ✅ Address handshake completed!")
                break
        else:
            raise TestFailure("Address timeout")
            
        self.dut.awvalid.value = 0
        
        # Data phase
        print("  📦 Data Phase:")
        self.dut.wdata.value = data
        self.dut.wstrb.value = strobe
        self.dut.wvalid.value = 1
        print(f"    Set wvalid=1, wdata=0x{data:08x}, wstrb=0x{strobe:x}")
        
        # Wait for wready
        for cycle in range(100):
            await RisingEdge(self.clock)
            wready_val = self.dut.wready.value
            print(f"    Cycle {cycle}: wready={wready_val}")
            
            if wready_val == 1:
                print("    ✅ Data handshake completed!")
                break
        else:
            raise TestFailure("Data timeout")
            
        self.dut.wvalid.value = 0
        
        # Response phase
        print("  📨 Response Phase:")
        for cycle in range(100):
            await RisingEdge(self.clock)
            bvalid_val = self.dut.bvalid.value
            bresp_val = self.dut.bresp.value
            print(f"    Cycle {cycle}: bvalid={bvalid_val}, bresp={bresp_val}")
            
            if bvalid_val == 1:
                print(f"    ✅ Response received: bresp={bresp_val}")
                # X değeri kontrolü
                try:
                    bresp_int = int(bresp_val)
                    print(f"    ✅ bresp converted to int: {bresp_int}")
                    return bresp_int
                except ValueError as e:
                    print(f"    ❌ ERROR: Cannot convert bresp to int: {e}")
                    print(f"    ❌ bresp raw value: {bresp_val}")
                    raise TestFailure(f"X value in bresp: {bresp_val}")
        else:
            raise TestFailure("Response timeout")
                
    async def read(self, address):
        print(f"\n📖 Starting read: addr=0x{address:08x}")
        
        # Address phase
        self.dut.araddr.value = address
        self.dut.arvalid.value = 1
        print(f"  Set arvalid=1, araddr=0x{address:08x}")
        
        # Wait for arready
        for cycle in range(100):
            await RisingEdge(self.clock)
            arready_val = self.dut.arready.value
            print(f"  Cycle {cycle}: arready={arready_val}")
            
            if arready_val == 1:
                print("  ✅ Read address accepted!")
                break
        else:
            raise TestFailure("Read address timeout")
            
        self.dut.arvalid.value = 0
        
        # Data phase
        for cycle in range(100):
            await RisingEdge(self.clock)
            rvalid_val = self.dut.rvalid.value
            
            if rvalid_val == 1:
                rdata_val = self.dut.rdata.value
                rresp_val = self.dut.rresp.value
                print(f"  ✅ Read data: rdata={rdata_val}, rresp={rresp_val}")
                
                try:
                    rdata_int = int(rdata_val)
                    rresp_int = int(rresp_val)
                    return rdata_int, rresp_int
                except ValueError as e:
                    print(f"  ❌ ERROR: Cannot convert read values: {e}")
                    raise TestFailure(f"X value in read response")
        else:
            raise TestFailure("Read data timeout")