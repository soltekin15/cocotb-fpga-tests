import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_simple_fifo(dut):
    """Basit FIFO test"""

    # Parametreleri oku
    try:
        data_width = dut.DATA_WIDTH.value
        depth = dut.DEPTH.value
        dut._log.info(f"FIFO parametreleri: WIDTH={data_width}, DEPTH={depth}")
    except:
        data_width = 8
        depth = 4
        dut._log.info("Varsayılan parametreler kullanılıyor")

    # Clock oluştur (100 MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    await Timer(50, units="ns")
    
    # Reset sonrası kontrol
    dut._log.info(f"Reset sonrası: full={dut.full.value}, empty={dut.empty.value}")
    assert dut.full.value == 0 and dut.empty.value == 1, f"Reset hatası: full={dut.full.value}, empty={dut.empty.value}"
    
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # ===== TEST 1: 3 Veri Yazma =====
    test_data = [0xAA, 0xBB, 0xCC]
    dut._log.info("=== TEST 1: 3 Veri Yazma ===")

    for i in range(len(test_data)):
        # Write işlemi öncesi durum
        dut._log.info(f"Write öncesi {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        dut.wr_en.value = 1
        dut.wr_data.value = test_data[i]
        await RisingEdge(dut.clk)
        dut.wr_en.value = 0
        
        # Write işlemi sonrası durum
        await Timer(1, units="ns")
        dut._log.info(f"Yazılan veri: 0x{test_data[i]:02X}")
        dut._log.info(f"Write sonrası {i}: full={dut.full.value}, empty={dut.empty.value}")

    # ===== TEST 2: 3 Veri Okuma =====
    dut._log.info("=== TEST 2: 3 Veri Okuma ===")
    
    for i in range(len(test_data)):
        # Read işlemi öncesi durum
        dut._log.info(f"Read öncesi {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        dut.rd_en.value = 0
        
        # Read işlemi sonrası durum
        await Timer(1, units="ns")
        okunan_deger = int(dut.rd_data.value)
        dut._log.info(f"Okunan veri: 0x{okunan_deger:02X} (Beklenen: 0x{test_data[i]:02X})")
        dut._log.info(f"Read sonrası {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        assert okunan_deger == test_data[i], f"Veri uyuşmazlığı: okunan=0x{okunan_deger:02X}, beklenen=0x{test_data[i]:02X}"

    # Empty kontrolü
    assert dut.empty.value == 1, f"FIFO boş olmalıydı: empty={dut.empty.value}"
    dut._log.info("✅ Test 1 başarılı!")

    # ===== TEST 3: 4 Veri Yazma (Full Test) =====
    test_data = [0x11, 0x22, 0x33, 0x44]
    dut._log.info("=== TEST 3: 4 Veri Yazma (Full Test) ===")

    for i in range(len(test_data)):
        # Write işlemi öncesi durum
        dut._log.info(f"Write öncesi {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        dut.wr_en.value = 1
        dut.wr_data.value = test_data[i]
        await RisingEdge(dut.clk)
        dut.wr_en.value = 0
        
        # Write işlemi sonrası durum
        await Timer(1, units="ns")
        dut._log.info(f"Yazılan veri: 0x{test_data[i]:02X}")
        dut._log.info(f"Write sonrası {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        # Full flag kontrolü
        if i == 3:  # Son veri yazıldı
            assert dut.full.value == 1, f"FIFO dolu olmalıydı: full={dut.full.value}"
        else:
            assert dut.full.value == 0, f"FIFO henüz dolu olmamalı: full={dut.full.value}"

    # ===== TEST 4: 4 Veri Okuma =====
    dut._log.info("=== TEST 4: 4 Veri Okuma ===")
    
    for i in range(len(test_data)):
        # Read işlemi öncesi durum
        dut._log.info(f"Read öncesi {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        dut.rd_en.value = 0
        
        # Read işlemi sonrası durum
        await Timer(1, units="ns")
        okunan_deger = int(dut.rd_data.value)
        dut._log.info(f"Okunan veri: 0x{okunan_deger:02X} (Beklenen: 0x{test_data[i]:02X})")
        dut._log.info(f"Read sonrası {i}: full={dut.full.value}, empty={dut.empty.value}")
        
        assert okunan_deger == test_data[i], f"Veri uyuşmazlığı: okunan=0x{okunan_deger:02X}, beklenen=0x{test_data[i]:02X}"

    # Final empty kontrolü
    assert dut.empty.value == 1, f"FIFO boş olmalıydı: empty={dut.empty.value}"
    dut._log.info("✅ Tüm testler başarılı!")