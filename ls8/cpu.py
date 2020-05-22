"""CPU functionality."""

import sys, re

class CPU:
    def __init__(self):
        self.ram = [0] * 256     #RAM 00-FF
        self.reg = [0] * 8       #Registers
        self.pc = 7              #Program counter location
        self.sp = 6              #Stack pointer location
        self.fl = 5              #Flag status location
        self.reg[self.pc] = 0    #Init program counter
        self.reg[self.sp] = 0xF4 #Init stack pointer
        self.reg[self.fl] = 0    #Init flag status

        self.halted = False

        self.instruction = {
            0x01: (self.HLT, 1),
            0x82: (self.LDI, 3),
            0x47: (self.PRN, 2),
            0x45: (self.PUSH, 2),
            0x46: (self.POP, 2),
            0x50: (self.CALL, 0),
            0x11: (self.RET, 0),
            #Math
            0xA0: (lambda: self.alu('ADD'), 3),
            0xA1: (lambda: self.alu('SUB'), 3),
            0xA2: (lambda: self.alu('MUL'), 3),
            0xA3: (lambda: self.alu('DIV'), 3),
            0x65: (lambda: self.alu('INC'), 2),
            0x66: (lambda: self.alu('DEC'), 2),
            #Sprint instructions
            0xA7: (lambda: self.alu('CMP'), 3),
            0x54: (self.JMP, 0),
            0x55: (lambda: self.alu('JEQ'), 0),
            0x56: (lambda: self.alu('JNE'), 0),
        }

    def load(self, program):
        with open(f'examples/{program}.ls8', 'r') as punchcard:
            address = 0
            for line in punchcard:
                instruction = re.match(r'(\d+)(?=\D)', line) if re.match(r"(\d+)(?=\D)", line) else None
                if instruction:
                    self.ram_write(address, int(instruction[0], 2))
                    address += 1


    def ram_read(self, MAR): #memory address register
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, operation):
        #We doin math
        def ADD():
            self.reg[self.ram_read(self.reg[self.pc]+1)] += self.reg[self.ram_read(self.reg[self.pc]+2)]
        def SUB():
            self.reg[self.ram_read(self.reg[self.pc]+1)] -= self.reg[self.ram_read(self.reg[self.pc]+2)]
        def MUL():
            self.reg[self.ram_read(self.reg[self.pc]+1)] *= self.reg[self.ram_read(self.reg[self.pc]+2)]
        def DIV():
            self.reg[self.ram_read(self.reg[self.pc]+1)] /= self.reg[self.ram_read(self.reg[self.pc]+2)]
        def INC():
            self.reg[self.ram_read(self.reg[self.pc]+1)] += 1
        def DEC():
            self.reg[self.ram_read(self.reg[self.pc]+1)] -= 1
        def CMP():
            if self.reg[self.ram_read(self.reg[self.pc]+1)] == self.reg[self.ram_read(self.reg[self.pc]+2)]: self.reg[self.fl] = 0x01
            elif self.reg[self.ram_read(self.reg[self.pc]+1)] < self.reg[self.ram_read(self.reg[self.pc]+2)]: self.reg[self.fl] = 0x04
            else: self.reg[self.fl] = 0x02

        #Not math
        def JEQ(): #If equals flag is true, jump to address stored in given register
            if self.reg[self.fl] == 0x01: self.reg[self.pc] = self.reg[self.ram_read(self.reg[self.pc]+1)]
            else: self.reg[self.pc] += 2
        def JNE(): #If equals flag is false, jump to address stored in given register
            if self.reg[self.fl] != 0x01: self.reg[self.pc] = self.reg[self.ram_read(self.reg[self.pc]+1)]
            else: self.reg[self.pc] += 2

        #Run the thing
        operations = {
            'ADD': ADD,
            'SUB': SUB,
            'MUL': MUL,
            'DIV': DIV,
            'INC': INC,
            'DEC': DEC,
            'CMP': CMP,
            'JEQ': JEQ,
            'JNE': JNE,
        }

        try:
            operations[operation]()
        except:
            raise Exception("Unsupported ALU operation")

    #Having fun being a computer
    def LDI(self):
        self.reg[self.ram_read(self.reg[self.pc]+1)] = self.ram_read(self.reg[self.pc]+2)

    def PRN(self):
       print(self.reg[self.ram_read(self.reg[self.pc]+1)])

    def HLT(self):
        self.halted = True

    def PUSH(self, MDR = None):
        self.reg[self.sp] -= 1
        data = MDR if MDR else self.reg[self.ram[self.reg[self.pc]+1]]
        self.ram_write(self.reg[self.sp], data)

    def POP(self):
        self.reg[self.ram_read(self.reg[self.pc]+1)] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        
    def CALL(self):
        self.PUSH(self.reg[self.pc]+2)
        self.reg[self.pc] = self.reg[self.ram_read(self.reg[self.pc]+1)]

    def RET(self):
        self.reg[self.pc] = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def JMP(self):
        self.reg[self.pc] = self.reg[self.ram_read(self.reg[self.pc]+1)]

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02i | %03i %03i %03i |" % (
            self.reg[self.pc]+1,
            self.ram_read(self.reg[self.pc]),
            self.ram_read(self.reg[self.pc] + 1),
            self.ram_read(self.reg[self.pc] + 2)
        ), end='')
        for i in range(8): print(" %03i" % self.reg[i], end='')
        print()

    def run(self):
        while not self.halted:
            IR = self.ram_read(self.reg[self.pc])
            self.instruction[IR][0]()
            self.reg[self.pc] += self.instruction[IR][1]