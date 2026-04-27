"""
Tests for the Catamount Processing Unit disassembler, including round-trip
(assemble --> disassemble --> reassemble) verification against all *.asm
sources.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

import glob
import os

import pytest

from assembler import assemble
from disassembler import disassemble

_ASM_DIR = os.path.join(os.path.dirname(__file__), "asm")
_ASM_FILES = sorted(glob.glob(os.path.join(_ASM_DIR, "*.asm")))


class TestDisassemblerUnits:
    def test_halt(self):
        assert any("HALT" in line for line in disassemble(assemble(["HALT"])))

    def test_ret(self):
        assert any("RET" in line for line in disassemble(assemble(["RET"])))

    def test_loadi(self):
        assert any(
            "LOADI R3, #42" in line for line in disassemble(assemble(["LOADI R3, #42"]))
        )

    def test_lui(self):
        # 0xFF is 255 -- disassembler emits the integer, not the hex literal
        assert any(
            "LUI R1, #255" in line for line in disassemble(assemble(["LUI R1, #0xFF"]))
        )

    def test_add(self):
        assert any(
            "ADD R1, R2, R3" in line
            for line in disassemble(assemble(["ADD R1, R2, R3"]))
        )

    def test_sub(self):
        assert any(
            "SUB R4, R5, R6" in line
            for line in disassemble(assemble(["SUB R4, R5, R6"]))
        )

    def test_and(self):
        assert any(
            "AND R0, R1, R2" in line
            for line in disassemble(assemble(["AND R0, R1, R2"]))
        )

    def test_or(self):
        assert any(
            "OR R7, R6, R5" in line for line in disassemble(assemble(["OR R7, R6, R5"]))
        )

    def test_xor(self):
        assert any(
            "XOR R2, R3, R4" in line
            for line in disassemble(assemble(["XOR R2, R3, R4"]))
        )

    def test_shft(self):
        assert any(
            "SHFT R1, R2, R3" in line
            for line in disassemble(assemble(["SHFT R1, R2, R3"]))
        )

    def test_addi_positive(self):
        assert any(
            "ADDI R1, R2, #5" in line
            for line in disassemble(assemble(["ADDI R1, R2, #5"]))
        )

    def test_addi_negative(self):
        assert any(
            "ADDI R1, R2, #-1" in line
            for line in disassemble(assemble(["ADDI R1, R2, #-1"]))
        )

    def test_load_positive_offset(self):
        assert any(
            "LOAD R1, [R2 + #3]" in line
            for line in disassemble(assemble(["LOAD R1, [R2 + #3]"]))
        )

    def test_load_negative_offset(self):
        assert any(
            "LOAD R1, [R2 + #-3]" in line
            for line in disassemble(assemble(["LOAD R1, [R2 + #-3]"]))
        )

    def test_load_zero_offset(self):
        assert any(
            "LOAD R1, [R2 + #0]" in line
            for line in disassemble(assemble(["LOAD R1, [R2 + #0]"]))
        )

    def test_store(self):
        assert any(
            "STORE R1, [R2 + #0]" in line
            for line in disassemble(assemble(["STORE R1, [R2 + #0]"]))
        )

    def test_synthetic_label_at_forward_target(self):
        # BEQ TARGET (pc=0) --> target=2; label inserted before HALT at pc=2
        words = assemble(["BEQ TARGET", "LOADI R0, #0", "TARGET:", "HALT"])
        assert "L_0002:" in disassemble(words)

    def test_synthetic_label_at_backward_target(self):
        words = assemble(["LOOP:", "LOADI R0, #0", "BNE LOOP"])
        assert "L_0000:" in disassemble(words)

    def test_beq(self):
        words = assemble(["BEQ TARGET", "LOADI R0, #0", "TARGET:", "HALT"])
        assert any("BEQ L_0002" in line for line in disassemble(words))

    def test_bne(self):
        words = assemble(["BNE TARGET", "LOADI R0, #0", "TARGET:", "HALT"])
        assert any("BNE L_0002" in line for line in disassemble(words))

    def test_blt(self):
        words = assemble(["BLT TARGET", "LOADI R0, #0", "TARGET:", "HALT"])
        assert any("BLT L_0002" in line for line in disassemble(words))

    def test_bge(self):
        words = assemble(["BGE TARGET", "LOADI R0, #0", "TARGET:", "HALT"])
        assert any("BGE L_0002" in line for line in disassemble(words))

    def test_b_forward(self):
        words = assemble(["B TARGET", "TARGET:", "HALT"])
        assert any("B L_0001" in line for line in disassemble(words))

    def test_b_backward(self):
        words = assemble(["LOOP:", "LOADI R0, #0", "B LOOP"])
        lines = disassemble(words)
        assert "L_0000:" in lines
        assert any("B L_0000" in line for line in lines)

    def test_call_and_ret(self):
        words = assemble(["CALL FOO", "HALT", "FOO:", "RET"])
        lines = disassemble(words)
        assert any("CALL L_0002" in line for line in lines)
        assert any("RET" in line for line in lines)

    def test_mov_becomes_addi_zero(self):
        # MOV is a pseudo-instruction; disassembler emits the underlying ADDI Rd, Ra, #0
        words = assemble(["MOV R3, R1"])
        assert any("ADDI R3, R1, #0" in line for line in disassemble(words))


@pytest.mark.parametrize(
    "asm_path", _ASM_FILES, ids=[os.path.basename(p) for p in _ASM_FILES]
)
def test_round_trip(asm_path):
    """
    Round-trip: assemble --> disassemble --> reassemble.
    The re-assembled binary must be bit-for-bit identical to the original.
    """
    with open(asm_path) as f:
        src = f.readlines()
    original = assemble(src)
    roundtripped = assemble(disassemble(original))
    assert original == roundtripped, (
        f"Round-trip mismatch for {os.path.basename(asm_path)}\n"
        f"Original:     {[f'0x{w:04X}' for w in original]}\n"
        f"Round-tripped:{[f'0x{w:04X}' for w in roundtripped]}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
