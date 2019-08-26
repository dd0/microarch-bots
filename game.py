#! /usr/bin/env python3
from cpu import BotCPU
import random

class Bot:
    def __init__(self, code, pos):
        self.pos = pos
        self.cpu = BotCPU()
        self.cpu.load_code(code)
        self.energy = 0
        self.killed = False
        self.points = 0
        self.debug = 0

        
    def add_energy(self, delta):
        self.energy += delta


    def tick(self, handler):
        if not self.alive():
            return
            
        def syscall_handler(imm, param):
            res, cost, ends_turn = handler(imm, param)
            self.energy -= cost - 1  # last 1 paid anyway
            if ends_turn and self.energy > 0:
                self.energy = 0
            return res

        while self.energy > 0:
            self.cpu.step(syscall_handler)
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
        self.pos = -1, -1
        self.killed = True


    def alive(self):
        return not self.killed


    def get_points(self):
        return self.points

    def score_point(self):
        self.points += 1


class World:
    SIZE = 64
    ENERGY_PER_TURN = 100
    INVALID_POS = SIZE - 1, SIZE
    
    def __init__(self, codes, map_class, seed=None):
        self.r = random.Random(seed)

        map_generator = map_class(World.SIZE, seed)
        self.board = map_generator.generate()
        
        self.points = []
        self.bots = []

        # This must be a loop to avoid missing checks for overlapping points
        for _ in range(10):
            self.points.append(self.random_empty())
        
        for code in codes:
            self.bots.append(Bot(code, self.random_empty()))

        self.current_tick = 0


    def random_empty(self):
        while True:
            i, j = self.r.randrange(World.SIZE), random.randrange(World.SIZE)
            ok = self.board[i][j] == ' '
            for bot in self.bots:
                if (i, j) == bot.get_pos():
                    ok = False
            ok = ok and not any((i, j) == p for p in self.points)
            if ok:
                return i, j


    def state(self):
        res = {}
        res['bots'] = [{'pos': bot.get_pos(), 'alive': bot.alive(), 'points': bot.get_points(), 'energy': bot.energy, 'pc': bot.cpu.pc(), 'debug': bot.debug} for bot in self.bots]
        res['points'] = self.points
        return res
        
            
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
            return True
        
        return self.board[i][j] == '#'
    

    def closest(me, others):
        def dist(a, b):
            i, j = a
            ii, jj = b

            return abs(i - ii) + abs(j - jj)
            
        if len(others) == 0:
            return World.INVALID_POS

        res = others[0]
        for o in others[1:]:
            if dist(me, res) > dist(me, o):
                res = o
        return res

    
    def tick(self):
        self.current_tick += 1
        pending_moves = [None for _ in self.bots]
        
        def make_handler(me):
            def handler(imm, param):
                if imm >= len(BotCPU.SYSCALLS):
                    # Nonexistent call, end turn as penalty
                    return 0, 0, True
            
                name = BotCPU.SYSCALLS[imm][0]

                if name == 'GET-POS':
                    res = World.encode_pos(self.bots[me].get_pos())
                if name == 'GET-CLOSEST':
                    res = World.encode_pos(World.closest(World.decode_pos(param),
                                                         [b.get_pos() for b in self.bots if b.alive()]))
                if name == 'GET-CLOSEST-OTHER':
                    res =  World.encode_pos(World.closest(World.decode_pos(param),
                                                        [b.get_pos() for i, b in enumerate(self.bots) if i != me and b.alive()]))
                if name == 'GET-CLOSEST-POINT':
                    res = World.encode_pos(World.closest(World.decode_pos(param), self.points))
                if name == 'GET-TILE':
                    i, j = World.decode_pos(param)
                    res = 0 if self.board[i][j] == ' ' else 1
                if name == 'MOVE':
                    pending_moves[me] = param
                    res = param  # do not change
                if name == 'YIELD':
                    res = param  # do nothing, but end tick
                if name == 'DEBUG':
                    self.bots[me].debug = param
                    res = param

                return res, BotCPU.SYSCALLS[imm][1], BotCPU.SYSCALLS[imm][2]
                
            return handler

        for bot in self.bots:
            bot.add_energy(World.ENERGY_PER_TURN)
            
        for i, bot in enumerate(self.bots):
            bot.tick(make_handler(i))

        for move, bot in zip(pending_moves, self.bots):
            if move is not None:
                bot.move(move)

        for bot in self.bots:
            if self.is_blocked(bot.get_pos()):
                bot.kill()
                
        for bot in self.bots:
            for point in self.points:
                if bot.get_pos() == point:
                    bot.score_point()

        self.points = [p for p in self.points if not any(p == bot.pos for bot in self.bots)]


    def run_with_log(self, n_ticks, meta={}):
        out = '{ "meta": ' + str(meta) + ', "board": ' + str(self.board) + ', "turns": ['
        out += str(self.state())
        for _ in range(n_ticks):
            self.tick();
            out += ', ' + str(self.state())
        out += ']}'
        return out
