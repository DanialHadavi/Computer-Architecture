"""CPU functionality."""

import sys

LDI = 0b10000010  # Load Immediate
PRN = 0b01000111  # Print
HLT = 0b00000001  # Halt
MUL = 0b10100010  # Multiply
ADD = 0b10100000  # Addition
SUB = 0b10100001  # Subtraction
DIV = 0b10100011  # Division
SP = 7  # Stack Pointer
POP = 0b01000110
PUSH = 0b01000101
RET = 0b00010001
CALL = 0b01010000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.fl = 0
        self.running = False
        self.reg[SP] = 0xF4

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py examples/filename")
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#", 1)[0].strip()
                        if line == "":
                            continue
                        else:
                            self.ram[address] = int(line, 2)
                            address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.load()
        running = True
        while running:
            inst = self.ram[self.pc]
            reg_num = self.ram[self.pc+1]
            value = self.ram[self.pc+2]

            if inst == LDI:
                """ `LDI`: load "immediate", store a value in a register, or "set this register to
                this value"."""
                self.reg[reg_num] = value
                self.pc += 3
            elif inst == MUL:
                self.reg[reg_num] *= self.reg[value]
                self.pc += 3
            elif inst == PRN:
                """ `PRN`: a pseudo-instruction that prints the numeric value stored in a
                register."""
                print(self.reg[reg_num])
                self.pc += 2
            elif inst == HLT:
                """ `HLT`: halt the CPU and exit the emulator."""
                running = False
            elif inst == PUSH:  # push
                self.reg[SP] -= 1
                value = self.reg[reg_num]
                address_to_push = self.reg[SP]
                self.ram[address_to_push] = value
                self.pc += 2
            elif inst == POP:  # pop
                address_to_pop = self.reg[SP]
                value = self.ram[address_to_pop]
                self.reg[reg_num] = value
                self.reg[SP] += 1
                self.pc += 2
            elif inst == CALL:  # call
                return_addr = self.pc + 2
                self.reg[SP] -= 1
                address_to_push = self.reg[SP]
                self.ram[address_to_push] = return_addr
                reg_num = self.ram[self.pc+1]
                sub_addr = self.reg[reg_num]
                self.pc = sub_addr

            elif inst == RET:  # return
                address_to_pop = self.reg[SP]
                return_addr = self.ram[address_to_pop]
                self.reg[SP] += 1
                self.pc = return_addr
            elif inst == ADD:
                self.alu("ADD", reg_num, value)
                self.pc += 3

            else:
                print(f'Unkown instruction {inst} at address {self.pc}')
                sys.exit(1)
