#! /usr/bin/env python

class BotCPU:
    # Configuration
    MEM_SIZE = 2**16
    STACK_SIZE = 2**12

    # Register names
    SP = 6
    PC = 7
    
    def __init__(self):
        self.memory = [0 for _ in range(BotCPU.MEM_SIZE)]
        self.stack = [0 for _ in range(BotCPU.STACK_SIZE)]
        self.regs = [0 for _ in range(8)]
        self.flags = False, False, False, False

    def load_code(self, data):
        for i, d in enumerate(data):
            self.memory[i] = d
        # Start execution from first instruction
        self.regs[BotCPU.PC] = 0


    def pc(self):
        return self.regs[BotCPU.PC]


    # Pairs of (name, encoding), where encoding is one of:
    #   R: Rdest, R1, R2
    #   D: Rdest, R, imm
    #   I: Rdest, imm
    #   C: cond, imm
    #   O: imm only
    OPERATIONS = [
        ('MOV', 'R'),
        ('MOV', 'I'),
        ('ADD', 'R'),
        ('ADD', 'D'),
        ('SUB', 'R'),
        ('SUB', 'D'),
        ('SHL', 'R'),
        ('SHL', 'D'),
        ('SHR', 'R'),
        ('SHR', 'D'),
        ('AND', 'R'),
        ('AND', 'D'),
        ('OR', 'R'),
        ('OR', 'D'),
        ('XOR', 'R'),
        ('XOR', 'D'),
        ('LOAD', 'R'),
        ('LOAD', 'D'),
        ('STORE', 'R'),
        ('STORE', 'D'),
        ('PUSH', 'R'),
        ('PUSH', 'O'),
        ('POP', 'R'),
        ('CMP', 'R'),
        ('CMP', 'I'),
        ('B', 'C'),
        ('B', 'O'),
        ('SYSCALL', 'I')
    ]

    ARITH = {
        'ADD': lambda x, y: x + y,
        'SUB': lambda x, y: x - y,
        'SHL': lambda x, y: x << y,
        'SHR': lambda x, y: x >> y,
        'AND': lambda x, y: x & y,
        'OR': lambda x, y: x | y,
        'XOR': lambda x, y: x ^ y
    }

    COND = [
        ('EQ', lambda n, z, c, v: z),
        ('NE', lambda n, z, c, v: not z),
        ('CS', lambda n, z, c, v: c),
        ('CC', lambda n, z, c, v: not c),
        ('MI', lambda n, z, c, v: n),
        ('PL', lambda n, z, c, v: not n),
        ('VS', lambda n, z, c, v: v),
        ('VC', lambda n, z, c, v: not v),
        ('HI', lambda n, z, c, v: c and not z),
        ('LS', lambda n, z, c, v: not c or z),
        ('GE', lambda n, z, c, v: n == v),
        ('LT', lambda n, z, c, v: n != v),
        ('GT', lambda n, z, c, v: not z and (n == v)),
        ('LE', lambda n, z, c, v: z or (n != v)),
        ('AL', lambda n, z, c, v: True),
        ('NV', lambda n, z, c, v: False),
    ]

    # (name, cost, ends turn?)
    SYSCALLS = [
        ('GET-POS', 50, False),
        ('GET-CLOSEST', 10, False),
        ('GET-CLOSEST-OTHER', 10, False),
        ('GET-POINT', 5, False),
        ('GET-TILE', 25, False),
        ('MOVE', 100, True),
        ('YIELD', 0, True),
        ('DEBUG', 0, False)
    ]
    
    def decode(instr):
        def field(off, L):
            return (instr >> off) & (2**L - 1)
        
        opcode = field(11, 5)
        R, imm, cond = None, None, None

        fmt = BotCPU.OPERATIONS[opcode][1]

        if fmt == 'R':
            R, imm = [field(8, 3), field(5, 3), field(2, 3)], None
        elif fmt == 'D':
            R, imm = [field(8, 3), field(5, 3)], field(0, 5)
        elif fmt == 'I':
            R, imm = [field(8, 3)], field(0, 8)
        elif fmt == 'C':
            R, imm, cond = [field(4, 3)], field(0, 7), field(7, 4)
        elif fmt == 'O':
            R, imm = [], field(0, 11)

        return opcode, R, imm, cond


    def set_reg(self, r, x):
        if r < 0 or r > 7:
            raise "Register out of range"
        self.regs[r] = x & 0xFFFF


    def get_mem(self, i):
        if i < 0 or i >= len(self.memory):
            return 0
        return self.memory[i]


    def set_mem(self, i, val):
        if i < 0 or i >= len(self.memory):
            return
        self.memory[i] = val


    def push(self, x):
        self.set_reg(BotCPU.SP, (self.regs[BotCPU.SP] + 1) % len(self.stack))
        self.stack[self.regs[BotCPU.SP]] = x


    def pop(self):
        res = self.stack[self.regs[BotCPU.SP]]
        self.set_reg(BotCPU.SP, (self.regs[BotCPU.SP] - 1) % len(self.stack))
        return res

    
    def step(self, syscall_handler):
        # Decode
        instr = self.get_mem(self.pc())
        opcode, R, imm, cond = BotCPU.decode(instr)

        name, fmt = BotCPU.OPERATIONS[opcode]
        params = None

        if fmt == 'R':
            params = self.regs[R[1]], self.regs[R[2]]
        elif fmt == 'D':
            params = self.regs[R[1]], imm
        elif fmt == 'I':
            params = [imm]

        #print(name, R, imm)

        # Execute
        if name in BotCPU.ARITH:
            self.set_reg(R[0], BotCPU.ARITH[name](*params))
        elif name == 'MOV':
            self.set_reg(R[0], self.regs[R[1]] if fmt == 'R' else imm)
        elif name == 'LOAD':
            self.set_reg(R[0], self.get_mem(params[0] + params[1]))
        elif name == 'STORE':
            self.set_mem(params[0] + params[1], self.regs[R[0]])
        elif name == 'PUSH':
            self.push(self.regs[R[0]] if fmt == 'R' else imm)
        elif name == 'POP':
            self.set_reg(R[0], self.pop())
        elif name == 'CMP':
            # flags are NZCV
            res = self.regs[R[0]] - params[0]
            self.flags = res < 0, res == 0, res > 0xFFFF, res > 0x7FFF
        elif name == 'B':
            should_jump = BotCPU.COND[cond][1](*self.flags) if fmt == 'C' else True
            if should_jump:
                # set two bytes before jump target since we will increment PC (note: cells are 2-byte)
                self.set_reg(BotCPU.PC, imm - 1)
        elif name == 'SYSCALL':
            self.regs[R[0]] = syscall_handler(imm, self.regs[R[0]])
        else:
            raise "Unknown instruction " + name

        # next instruction
        self.set_reg(BotCPU.PC, self.pc() + 1)
        #print(self.regs)
