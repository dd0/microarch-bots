#! /usr/bin/env python
import random

class Map:
    def __init__(self, n, seed=None):
        self.R = random.Random(seed)
        self.n = n
        self.board = [[' ' for _ in range(n)] for _ in range(n)]


    def generate(self):
        while True:
            self.build()
            self.remove_holes()
            if self.check():
                break
        return self.board


    def build(self):
        pass  # overwritten by subclasses


    def get_components(self):
        self.component = [[None for _ in row] for row in self.board]
        self.n_components = 0

        def flood_component(start_i, start_j, colour):
            stack = [(start_i, start_j)]
            while len(stack) > 0:
                i, j = stack.pop()
                if i < 0 or j < 0 or i >= self.n or j >= self.n:
                    continue
                if self.board[i][j] != ' ' or self.component[i][j] is not None:
                    continue
                self.component[i][j] = colour
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    stack.append((i + di, j + dj))
        
        for i, row in enumerate(self.board):
            for j, tile in enumerate(row):
                if tile == ' ' and self.component[i][j] is None:
                    self.n_components += 1
                    flood_component(i, j, self.n_components)

    
    def remove_holes(self):
        self.get_components()
        component_size = {i: 0 for i in range(1, self.n_components + 1)}
        for row in self.component:
            for c in row:
                if c is not None:
                    component_size[c] += 1

        largest = max((j,i) for (i,j) in component_size.items())[1]
        for i in range(self.n):
            for j in range(self.n):
                if self.component[i][j] != largest:
                    self.board[i][j] = '#'

        
    def check(self):
        n_empty = sum(sum(1 for x in row if x == ' ') for row in self.board)
        return n_empty >= self.n * self.n // 5


