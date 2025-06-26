import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import TestFailure

class AXISDriver:
    """AXI4-Stream Driver - Sink (Consumer) rolünde"""
    
    def __init__(self, dut, clock_name="clk"):
        self.dut = dut
        self.clock = getattr(dut, clock_name)
        self._init_signals()
        
    def _init_signals(self):
        """Slave sinyallerini initialize et"""
        self.dut.start.value = 0
        self.dut.m_axis_tready.value = 1  # Always ready (başlangıç)
        
    async def reset(self, cycles=10):
        """Reset sequence"""
        print("🔄 Starting reset...")
        self.dut.rst_n.value = 0
        self._init_signals()
        
        for i in range(cycles):
            await RisingEdge(self.clock)
            print(f"  Reset cycle {i+1}/{cycles}")
            
        self.dut.rst_n.value = 1
        await RisingEdge(self.clock)
        print("✅ Reset completed")
        
    async def start_transfer(self):
        """Counter'ı başlat"""
        print("🚀 Starting transfer...")
        self.dut.start.value = 1
        await RisingEdge(self.clock)
        
    async def stop_transfer(self):
        """Counter'ı durdur"""
        print("🛑 Stopping transfer...")
        self.dut.start.value = 0
        await RisingEdge(self.clock)
        
    async def wait_done(self, timeout_cycles=100):
        """Done sinyalini bekle"""
        print("⏳ Waiting for done...")
        for cycle in range(timeout_cycles):
            await RisingEdge(self.clock)
            if self.dut.done.value == 1:
                print(f"✅ Transfer completed in {cycle} cycles")
                return
        else:
            raise TestFailure(f"Done timeout after {timeout_cycles} cycles")
            
    async def receive_packet(self, expected_size=4, timeout_cycles=100):
        """Packet receive et ve validate et"""
        received_data = []
        tlast_seen = False
        
        print(f"📦 Receiving packet (expected size: {expected_size})")
        
        for cycle in range(timeout_cycles):
            await RisingEdge(self.clock)
            
            # Transfer check
            tvalid = self.dut.m_axis_tvalid.value
            tready = self.dut.m_axis_tready.value
            
            if tvalid and tready:
                tdata = int(self.dut.m_axis_tdata.value)
                tlast = int(self.dut.m_axis_tlast.value)
                
                received_data.append(tdata)
                print(f"  📊 Received: data={tdata}, tlast={tlast}")
                
                if tlast:
                    tlast_seen = True
                    print(f"✅ Packet end detected! Total words: {len(received_data)}")
                    break
        else:
            raise TestFailure(f"Packet receive timeout after {timeout_cycles} cycles")
            
        # Validate packet
        if not tlast_seen:
            raise TestFailure("tlast never seen!")
            
        if len(received_data) != expected_size:
            raise TestFailure(f"Packet size mismatch: expected {expected_size}, got {len(received_data)}")
            
        return received_data
        
    async def set_backpressure(self, ready_pattern):
        """Backpressure simulation
        ready_pattern: list of 0/1 values for tready
        """
        print(f"🔒 Applying backpressure: {ready_pattern}")
        
        for ready_val in ready_pattern:
            self.dut.m_axis_tready.value = ready_val
            await RisingEdge(self.clock)
            
        # Restore to always ready
        self.dut.m_axis_tready.value = 1
        
    async def monitor_signals(self, cycles=10):
        """Debug için sinyal monitoring"""
        print("🔍 Signal monitoring:")
        
        for i in range(cycles):
            await RisingEdge(self.clock)
            
            tvalid = self.dut.m_axis_tvalid.value
            tready = self.dut.m_axis_tready.value
            tdata = self.dut.m_axis_tdata.value if tvalid else "X"
            tlast = self.dut.m_axis_tlast.value if tvalid else "X"
            state = self.dut.current_state.value
            
            print(f"  Cycle {i}: tvalid={tvalid}, tready={tready}, tdata={tdata}, tlast={tlast}, state={state}")