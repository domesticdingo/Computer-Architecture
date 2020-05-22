"""CPU functionality."""

import sys, re

class CPU:
    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.halted = False
        self.instruction = {
            0x01: self.HLT,
            0x82: self.LDI,
            0x47: self.PRN,
            0xA2: self.MUL,
            0x45: self.PUSH,
            0x46: self.POP,
            0x50: self.CALL,
            0x11: self.RET,
            0xA0: self.ADD,
        }

    def load(self, program):
        instructions = []
        address = 0
        with open(f'examples/{program}.ls8', 'r') as punchcard:
            for line in punchcard:
                instruction = re.match(r'(\d+)(?=\D)', line) if re.match(r"(\d+)(?=\D)", line) else None
                if instruction:
                    self.ram_write(address, int(instruction[0], 2))
                    address += 1


    def ram_read(self, MAR): #memory address register
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def LDI(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
        self.pc += 3

    def PRN(self):
        print(self.reg[self.ram_read(self.pc+1)])
        self.pc += 2

    def HLT(self):
        self.halted = True
        self.pc += 1

    def ADD(self):
        self.alu('ADD', self.ram_read(self.pc+1),self.ram_read(self.pc+2))
        self.pc += 3

    def MUL(self):
        reg_a = self.ram_read(self.pc+1)
        reg_b = self.ram_read(self.pc+2)
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    def PUSH(self, MDR = None):
        self.reg[self.sp] -= 1
        data = MDR if MDR else self.reg[self.ram[self.pc+1]]
        self.ram_write(self.reg[self.sp], data)
        self.pc += 2

    def POP(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.reg[self.sp])
        self.pc += 2
        self.reg[self.sp] += 1
        
    def CALL(self):
        self.PUSH(self.pc+2)
        self.pc = self.reg[self.ram_read(self.pc-1)]

    def RET(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        
    def run(self):
        while not self.halted:
            IR = self.ram_read(self.pc)
            self.instruction[IR]()