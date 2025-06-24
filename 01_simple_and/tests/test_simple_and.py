import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge,Timer

@cocotb.test()
async def test_simple_and(dut):
    """Basit AND testi"""
    
    test_count = 0
    dut.a.value = 0
    dut.b.value = 0
    await Timer(1, units="ns")  # ← Bu satırı ekleyin
    assert dut.y.value == 0, f"Sonuc yanlis cikti a = {dut.a.value}, b = {dut.b.value} ==>  y = {dut.y.value}"
    dut._log.info(f"{test_count + 1}. Test gecti")
    await Timer(50, units="ns")

    test_count = test_count + 1
    dut.a.value = 0
    dut.b.value = 1
    await Timer(1, units="ns")  # ← Bu satırı ekleyin
    assert dut.y.value == 0, f"Sonuc yanlis cikti a = {dut.a.value}, b = {dut.b.value} ==>  y = {dut.y.value}"
    dut._log.info(f"{test_count + 1}. Test gecti")
    await Timer(50, units="ns")

    test_count = test_count + 1
    dut.a.value = 1
    dut.b.value = 0
    await Timer(1, units="ns")  # ← Bu satırı ekleyin
    assert dut.y.value == 0, f"Sonuc yanlis cikti a = {dut.a.value}, b = {dut.b.value} ==>  y = {dut.y.value}"
    dut._log.info(f"{test_count + 1}. Test gecti")
    await Timer(50, units="ns")

    test_count = test_count + 1
    dut.a.value = 1
    dut.b.value = 1
    await Timer(1, units="ns")  # ← Bu satırı ekleyin
    assert dut.y.value == 1, f"Sonuc yanlis cikti a = {dut.a.value}, b = {dut.b.value} ==>  y = {dut.y.value}"
    dut._log.info(f"{test_count + 1}. Test gecti")
    await Timer(50, units="ns")

    dut._log.info("AND testi Basarili  ")