"""
Catamount Processing Unit
A toy 16-bit Harvard architecture CPU.

CS 2210 Computer Organization
Clayton Cafiero <cbcafier@uvm.edu>

Raine Geary and Lee Ericson
"""

from alu import Alu
from constants import STACK_TOP
from instruction_set import Instruction
from memory import DataMemory, InstructionMemory
from register_file import RegisterFile


class Cpu:
    """
    Catamount Processing Unit
    """

    def __init__(self, *, alu, regs, d_mem, i_mem):
        """
        Constructor
        """
        self._i_mem = i_mem
        self._d_mem = d_mem
        self._regs = regs
        self._alu = alu
        self._pc = 0  # program counter
        self._ir = 0  # instruction register
        self._sp = STACK_TOP  # stack pointer
        self._decoded = Instruction()
        self._halt = False

    @property
    def running(self):
        return not self._halt

    @property
    def pc(self):
        return self._pc

    @property
    def sp(self):
        return self._sp

    @property
    def ir(self):
        return self._ir

    @property
    def decoded(self):
        return self._decoded

    def get_reg(self, r):
        """
        Public accessor (getter) for single register value.
        """
        return self._regs.execute(ra=r)[0]

    def tick(self):
        """
        Fetch-decode-execute
        """
        if not self._halt:
            self._fetch()
            self._decode()

            # execute...
            match self._decoded.mnem:
                case "LOADI":
                    # Load an immediate value into rd (destinitation register)
                    rd = self._decoded.rd
                    imm = self.sext(self._decoded.imm, 8)
                    self._regs.execute(rd=rd, data=imm, write_enable=True)
                case "LUI":
                    # Load upper immediate (shifted left by 8 bits)
                    rd = self._decoded.rd
                    upper = self._decoded.imm << 8
                    lower, _ = self._regs.execute(ra=rd)
                    lower &= 0x00FF  # clear upper bits
                    data = upper | lower
                    self._regs.execute(rd=rd, data=data, write_enable=True)
                case "LOAD":
                    # Load a value from memory to a register 
                    rd = self._decoded.rd
                    addr, _ = self._regs.execute(ra=self._decoded.ra)
                    offset = self.sext(value=self._decoded.addr, bits=6) 
                    data = self._d_mem.read(addr + offset) 
                    self._regs.execute(rd=rd, data=data, write_enable = True)
                case "STORE": #use d_mem
                    # Store a value from ra to rb + offset in d_MEM
                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    addr = self._decoded.addr
                    print(addr)
                    offset = self.sext(value=addr, bits=6)
                    addr, _ = self._regs.execute(ra=rb)
                    addr += offset                    
                    data, _ = self._regs.execute(ra=ra)
                    self._d_mem.write_enable(True)
                    self._d_mem.write(addr=addr, value=data)  #should automatically reset write enable
                    print(self._d_mem.read(addr=5))
                case "ADDI":
                    self._alu.set_op("ADD")
                    ra = self._decoded.ra
                    rd = self._decoded.rd
                    op_b = self.sext(self._decoded.imm, 6)
                    op_a, _ = self._regs.execute(ra=ra)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data = result, write_enable=True)
                case "ADD":
                    self._alu.set_op("ADD")
                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    rd = self._decoded.rd   #destinitaion
                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "SUB":
                    self._alu.set_op("SUB")

                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    rd = self._decoded.rd

                    op_a , op_b = self._regs.execute(ra=ra, rb=rb) 
                    result = self._alu.execute(op_a,op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "AND":
                    self._alu.set_op("AND")

                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    rd = self._decoded.rd

                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "OR":
                    self._alu.set_op("OR")

                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    rd = self._decoded.rd

                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "XOR":
                    self._alu.set_op("XOR")
                    
                    ra = self._decoded.ra
                    rb = self._decoded.rb
                    rd = self._decoded.rd

                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "SHFT":
                    self._alu.set_op("SHFT")

                    rd = self._decoded.rd
                    ra = self._decoded.ra
                    rb = self._decoded.rb

                    op_a, op_b = self._regs.execute(ra=ra, rb=rb)
                    result = self._alu.execute(op_a, op_b)
                    self._regs.execute(rd=rd, data=result, write_enable=True)
                case "BEQ":
                    if self._alu.zero:
                        offset = self.sext(self._decoded.imm, 8)
                        self._pc += offset  # take branch
                case "BNE":
                    # branch if not equal
                    if not self._alu.zero:
                        offset = self.sext(self._decoded.imm, 8)
                        self._pc += offset
                case "BLT":
                    # branch if less than; if negative flag is set
                    if self._alu.negative:
                        offset = self.sext(self._decoded.imm, 8)
                        self._pc += offset
                case "BGE":
                    if not self._alu.negative:
                        offset = self.sext(self._decoded.imm, 8)
                        self._pc += offset
                case "B":
                    offset = self.sext(self._decoded.imm, 8)
                    self._pc += offset
                case "CALL":
                    self._sp -= 1  # grow stack downward
                    # PC is incremented immediately upon fetch so already
                    # pointing to next instruction, which is return address.
                    ret_addr = self._pc  # explicit
                    self._d_mem.write_enable(True)
                    # push return address...
                    self._d_mem.write(self._sp, ret_addr, from_stack=True)
                    offset = self._decoded.imm
                    self._pc += self.sext(offset, 8)  # jump to target
                case "RET":
                    if self._sp == STACK_TOP:
                        raise RuntimeError("Stack underflow")
                    # Get return address from memory via SP
                    ret_addr = self._d_mem.read(self._sp)
                    # Increment SP
                    self._sp += 1
                    # Update PC
                    self._pc = ret_addr
                    
                case "HALT":
                    self._halt = True
                case _:  # default
                    raise ValueError(
                        "Unknown mnemonic: " + str(self._decoded) + "\n" + str(self._ir)
                    )

            return True
        return False

    def _decode(self):
        """
        We're effectively delegating decoding to the Instruction class.
        """
        self._decoded = Instruction(raw=self._ir)

    def _fetch(self):
        # Use address in program counter (PC) to fetch next instruction
        next_instruction = self._i_mem.read(addr=self._pc)
        # Store instruction in instruction register
        self._ir = next_instruction
        # increment the program counter.
        self._pc += 1

    def load_program(self, prog):
        self._i_mem.load_program(prog)

    @staticmethod
    def sext(value, bits=16):
        mask = (1 << bits) - 1
        value &= mask
        sign_bit = 1 << (bits - 1)
        return (value ^ sign_bit) - sign_bit


# Helper function
def make_cpu(prog=None):
    alu = Alu()
    d_mem = DataMemory()
    i_mem = InstructionMemory()
    if prog:
        i_mem.load_program(prog)
    regs = RegisterFile()
    return Cpu(alu=alu, d_mem=d_mem, i_mem=i_mem, regs=regs)
