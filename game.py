#! /usr/bin/env python3
from cpu import BotCPU
import random

class Bot:
    def __init__(self, code, pos):
        self.pos = pos
        self.cpu = BotCPU()
        self.cpu.load_code(code)
        self.energy = 0

        
    def add_energy(self, delta):
        self.energy += delta


    def tick(self, handler):
        def syscall_handler(imm, param):
            res, cost, ends_turn = handler(imm, param)
            self.energy -= cost - 1  # last 1 paid anyway
            if ends_turn and self.energy > 0:
                self.energy = 0
            return res

        while self.energy > 0:
            self.cpu.step(handler)
            self.energy -= 1


    def get_pos(self):
        return self.pos


    def move(self, d):
        DI = [-1, 1, 0, 0]
        DJ = [0, 0, -1, 1]
        if d < 0 or d >= len(DI):
            return

        i, j = self.pos
        ii, jj = i + DI[d], j + DJ[d]

        # check for out-of-bounds is World's responsibility
        self.pos = ii, jj


    def kill(self):
        self.pos = (-1, -1)
        self.energy = -1e10


class World:
    SIZE = 64
    ENERGY_PER_TURN = 100
    
    def __init__(self, codes, seed=None):
        self.r = random.Random(seed)
        self.board = [[' ' for j in range(World.SIZE)] for i in range(World.SIZE)]
        self.bots = []
        
        for code in codes:
            self.bots.append(Bot(code, self.random_empty()))


    def random_empty(self):
        while True:
            i, j = self.r.randrange(World.SIZE), random.randrange(World.SIZE)
            ok = self.board[i][j] == ' '
            for bot in self.bots:
                if (i, j) == bot.get_pos():
                    ok = False
            if ok:
                return i, j

    def encode_pos(p):
        i, j = p
        return (i << 6) | j


    def decode_pos(p):
        return p >> 6, p & 63


    def is_blocked(self, pos):
        i, j = pos
        if i < 0 or j < 0 or i >= World.SIZE or j >= World.SIZE:
            return True
        
        # Collision, ugly hack
        if len([b for b in self.bots if b.get_pos() == pos]) > 1:
            return False
        
        return self.board[i][j] == '#'
    
    
    def tick(self):
        pending_moves = [None for _ in self.bots]
        
        def make_handler(me):
            def handler(imm, param):
                print('SYSCALL', imm, param)
                
                if imm >= len(BotCPU.SYSCALLS):
                    # Nonexistent call, end turn as penalty
                    return 0, 0, True
            
                name = BotCPU.SYSCALLS[imm][0]

                if name == 'GET-POS':
                    res = World.encode_pos(self.bots[me].get_pos())
                if name == 'GET-CLOSEST':
                    res = World.encode_pos(World.closest(World.decode_pos(param),
                                                         [b.get_pos() for b in self.bots]))
                if name == 'GET-CLOSEST-OTHER':
                    res =  World.encode_pos(World.closest(World.decode_pos(param),
                                                        [b.get_pos() for i, b in enumerate(self.bots) if i != me]))
                if name == 'GET-CLOSEST-POINT':
                    res = 0
                if name == 'GET-TILE':
                    i, j = World.decode_pos(param)
                    res = 0 if self.board[i][j] == ' ' else 1
                if name == 'MOVE':
                    pending_moves[me] = param
                    res = 0
                if name == 'YIELD':
                    res = 0  # do nothing, but end tick

                return res, BotCPU.SYSCALLS[imm][1], BotCPU.SYSCALLS[imm][2]
                
            return handler

        for bot in self.bots:
            bot.add_energy(World.ENERGY_PER_TURN)
            
        for i, bot in enumerate(self.bots):
            bot.tick(make_handler(i))

        for move, bot in zip(pending_moves, self.bots):
            if move:
                bot.move(move)

        for bot in self.bots:
            if self.is_blocked(bot.get_pos()):
                bot.kill()

        for bot in self.bots:
            print(bot.get_pos())

        

code = [2053, 2308, 4868, 608, 55808]
world = World([code, code])
world.tick()
