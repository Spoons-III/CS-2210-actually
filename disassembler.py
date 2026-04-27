"""
Catamount Processing Unit -- Disassembler

Converts 16-bit instruction words back to reassembleable assembly source.
Synthetic labels (L_XXXX) are generated for all branch targets so that the
output can be fed directly back into the assembler for round-trip testing.

MOV pseudo-instructions are not reconstructed; the equivalent
    ADDI Rd, Ra, #0
is emitted instead (assembles to identical binary).

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>
"""

import glob
import os

from instruction_set import Instruction

_BRANCH_MNEMS = {"BEQ", "BNE", "BLT", "BGE", "B", "CALL"}


def _sign_extend(value, bits):
    """Sign-extend 'value' (treated as 'bits'-wide) to a Python int."""
    mask = (1 << bits) - 1
    value &= mask
    sign_bit = 1 << (bits - 1)
    return (value ^ sign_bit) - sign_bit


def _branch_target(pc, imm8):
    """Absolute word address of a branch target (all branch types are PC+1-relative)."""
    return pc + 1 + _sign_extend(imm8, 8)


def disassemble(words):
    """
    Disassemble a list of 16-bit words.

    Returns a list of assembly source lines with synthetic labels inserted at
    branch targets.  Output is valid input to the assembler (round-trippable).
    """
    n = len(words)

    # Pass 1: decode all words and collect branch target addresses.
    instructions = []
    targets = set()
    for pc, word in enumerate(words):
        inst = Instruction(raw=word)
        instructions.append(inst)
        if inst.mnem in _BRANCH_MNEMS:
            target = _branch_target(pc, inst.imm)
            if 0 <= target < n:
                targets.add(target)

    # Pass 2: emit assembly text, inserting synthetic labels at targets.
    lines = []
    for pc, inst in enumerate(instructions):
        if pc in targets:
            lines.append(f"L_{pc:04X}:")
        mnem = inst.mnem
        if mnem in ("ADD", "SUB", "AND", "OR", "XOR", "SHFT"):
            lines.append(f"    {mnem} R{inst.rd}, R{inst.ra}, R{inst.rb}")
        elif mnem in ("LOADI", "LUI"):
            lines.append(f"    {mnem} R{inst.rd}, #{inst.imm}")
        elif mnem == "ADDI":
            sx = _sign_extend(inst.imm, 6)
            lines.append(f"    ADDI R{inst.rd}, R{inst.ra}, #{sx}")
        elif mnem == "LOAD":
            disp = _sign_extend(inst.addr, 6)
            lines.append(f"    LOAD R{inst.rd}, [R{inst.ra} + #{disp}]")
        elif mnem == "STORE":
            disp = _sign_extend(inst.addr, 6)
            lines.append(f"    STORE R{inst.ra}, [R{inst.rb} + #{disp}]")
        elif mnem in ("BEQ", "BNE", "BLT", "BGE"):
            target = _branch_target(pc, inst.imm)
            lines.append(f"    {mnem} L_{target:04X}")
        elif mnem == "B":
            target = _branch_target(pc, inst.imm)
            lines.append(f"    B L_{target:04X}")
        elif mnem == "CALL":
            target = _branch_target(pc, inst.imm)
            lines.append(f"    CALL L_{target:04X}")
        elif mnem == "RET":
            lines.append("    RET")
        elif mnem == "HALT":
            lines.append("    HALT")
        else:
            lines.append(f"    .word 0x{inst.raw:04X}  ; unhandled {mnem}")
    return lines


if __name__ == "__main__":
    from assembler import assemble

    directory_path = "asm"
    for filename in sorted(glob.glob(os.path.join(directory_path, "*.asm"))):
        basename = os.path.basename(os.path.normpath(filename))
        print(f"=== {basename} ===")
        with open(filename) as f:
            src = f.readlines()
        words = assemble(src)
        for line in disassemble(words):
            print(line)
        print()
