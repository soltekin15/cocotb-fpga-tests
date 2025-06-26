import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_uart_transmitter(dut):
    """UART Trasnmitter Test"""

    # Clock oluştur (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    #Reset
    dut.rst_n.value = 0
    await Timer(50, units="ns")

    # Reset sonrası kontrol
    dut._log.info(f"Reset sonrası: full={dut.tx_ready.value}, empty={dut.uart_tx.value}")
    assert dut.tx_ready.value == 1 and dut.uart_tx.value == 1, f"Reset hatası: full={dut.tx_ready.value}, empty={dut.uart_tx.value}"

    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # ====== TEST 1: Single Byte Transmission ======

    # 0x55 byte'ını gönder
    test_byte = 0x55
    dut.tx_data.value = test_byte
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0

    dut._log.info(f"0x{test_byte:02X} gönderildi")
    
    # State machine'in tepki vermesi için biraz bekle
    await Timer(1, units="ns")
    
    # tx_ready'nin 0 olmasını kontrol et (busy)
    assert dut.tx_ready.value == 0, f"tx_ready busy olmalı: {dut.tx_ready.value}"
    dut._log.info("UART busy - transmission başladı")

    # Transmission time hesapla ve bekle
    # 1 start + 8 data + 1 stop = 10 bit
    # 9600 baud = her bit 104,167 ns
    bit_time_ns = int((1 / 9600) * 1_000_000_000)  # 104167 ns
    frame_time_ns = bit_time_ns * 10                # 1041670 ns

    dut._log.info(f"Transmission süresi: {frame_time_ns} ns bekliyor...")
    await Timer(frame_time_ns, units="ns")

    # tx_ready'nin 1 olmasını kontrol et (transmission bitti)
    assert dut.tx_ready.value == 1, f"Transmission bittikten sonra tx_ready=1 olmalı: {dut.tx_ready.value}"
    dut._log.info("✅ Single byte transmission testi başarılı!")


    # ====== TEST 2: UART Frame Bit Kontrolü ======

    # Beklenen bit sequence (LSB first):
    test_byte = 0x55
    expected_pattern = "0101010101"  # START + LSB first + STOP

    dut.tx_data.value = test_byte
    dut.tx_valid.value = 1
    await RisingEdge(dut.clk)
    dut.tx_valid.value = 0

    # UART'ın başlamasını bekle
    await Timer(10000, units="ns")  # 10µs bekle, kesin başlamış olur

    # Pattern'i kontrol et - sadece birkaç bit
    for i in range(3):  # İlk 3 bit: START, D0, D1
        uart_bit = int(dut.uart_tx.value)
        expected_bit = int(expected_pattern[i])
        dut._log.info(f"Bit {i}: expected={expected_bit}, actual={uart_bit}")
        await Timer(bit_time_ns, units="ns")