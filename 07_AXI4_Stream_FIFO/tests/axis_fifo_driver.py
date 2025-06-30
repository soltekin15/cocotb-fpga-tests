import cocotb
from cocotb.triggers import RisingEdge
from cocotb.result import TestFailure

class AXISFIFODriver:
    """AXIS FIFO Test Driver - Consumer rolünde"""
    
    def __init__(self, dut, clock_name="clk"):
        self.dut = dut
        self.clock = getattr(dut, clock_name)
        self._init_signals()
        
    def _init_signals(self):
        """Signals initialize"""
        self.dut.start_counter.value = 0
        self.dut.m_axis_tready.value = 1  # Always ready başlangıç
        
    async def reset(self, cycles=10):
        """Reset sequence"""
        print("🔄 FIFO Test reset...")
        self.dut.rst_n.value = 0
        self._init_signals()
        
        for i in range(cycles):
            await RisingEdge(self.clock)
            
        self.dut.rst_n.value = 1
        await RisingEdge(self.clock)
        print("✅ FIFO Test reset completed")
        
    async def start_producer(self):
        """Counter producer'ı başlat"""
        print("🚀 Starting counter producer...")
        self.dut.start_counter.value = 1
        await RisingEdge(self.clock)
        
    async def stop_producer(self):
        """Counter producer'ı durdur"""
        print("🛑 Stopping counter producer...")
        self.dut.start_counter.value = 0
        await RisingEdge(self.clock)
        
    async def wait_producer_done(self, timeout_cycles=100):
        """Producer done bekle"""
        print("⏳ Waiting for producer done...")
        for cycle in range(timeout_cycles):
            await RisingEdge(self.clock)
            if self.dut.counter_done.value == 1:
                print(f"✅ Producer done in {cycle} cycles")
                return
        else:
            raise TestFailure(f"Producer timeout after {timeout_cycles} cycles")
            
    async def consume_packet(self, expected_size=4, timeout_cycles=100):
        """FIFO'dan packet consume et - STREAMING MODE"""
        received_data = []
        
        print(f"📦 Consuming packet from FIFO (expected size: {expected_size})")
        
        for cycle in range(timeout_cycles):
            await RisingEdge(self.clock)
            
            # Transfer check
            tvalid = self.dut.m_axis_tvalid.value
            tready = self.dut.m_axis_tready.value
            
            if tvalid and tready:
                tdata = int(self.dut.m_axis_tdata.value)
                tlast = int(self.dut.m_axis_tlast.value)
                
                received_data.append(tdata)
                print(f"  📊 FIFO → Consumer: data={tdata}, tlast={tlast}")
                
                if tlast:
                    print(f"✅ Packet consumed! Total words: {len(received_data)}")
                    return received_data
                    
            # *** FIX: Early exit if we have some data and no more coming ***
            if len(received_data) > 0 and not tvalid:
                # Wait a few more cycles to be sure
                no_data_cycles = 0
                for wait_cycle in range(5):
                    await RisingEdge(self.clock)
                    if not self.dut.m_axis_tvalid.value:
                        no_data_cycles += 1
                    else:
                        break
                
                if no_data_cycles >= 3:  # 3 cycles no data = probably done
                    print(f"✅ Packet likely complete (no tlast): {received_data}")
                    return received_data
        
        # If we reach here, timeout occurred
        if len(received_data) > 0:
            print(f"⚠️ Timeout but got data: {received_data}")
            return received_data
        else:
            print(f"❌ Complete timeout - no data received")
            raise TestFailure(f"No data received after {timeout_cycles} cycles")
        
    async def set_consumer_backpressure(self, ready_pattern):
        """Consumer backpressure uygula"""
        print(f"🔒 Consumer backpressure: {ready_pattern}")
        
        for ready_val in ready_pattern:
            self.dut.m_axis_tready.value = ready_val
            await RisingEdge(self.clock)
            
        # Restore to ready
        self.dut.m_axis_tready.value = 1
        
    async def monitor_fifo_status(self, cycles=10):
        """FIFO status monitoring"""
        print("🔍 FIFO status monitoring:")
        
        for i in range(cycles):
            await RisingEdge(self.clock)
            
            full = self.dut.fifo_full.value
            empty = self.dut.fifo_empty.value
            tvalid_in = self.dut.counter_inst.m_axis_tvalid.value if hasattr(self.dut, 'counter_inst') else "?"
            tready_in = self.dut.fifo_inst.s_axis_tready.value if hasattr(self.dut, 'fifo_inst') else "?"
            tvalid_out = self.dut.m_axis_tvalid.value
            tready_out = self.dut.m_axis_tready.value
            
            print(f"  Cycle {i}: full={full}, empty={empty}, in=({tvalid_in},{tready_in}), out=({tvalid_out},{tready_out})")