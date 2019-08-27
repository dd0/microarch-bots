#! /usr/bin/env python
from cpu import BotCPU
import sys
import struct
import argparse


def asm_instruction(line):
    instr = line.split()[0]
    params = ''.join(line.split()[1:]).split(',')

    cond = None
    if '.' in instr:
        instr, cond = instr.split('.')

    opcode, fmt = None, None
    
    if instr == 'B':
        opcode, fmt = (25, 'C') if cond else (26, 'O')
    elif instr == 'BR':
        opcode, fmt = (28, 'C') if cond else (29, 'O')
    else:
        candidates = [(i, x[1]) for i, x in enumerate(BotCPU.OPERATIONS) if x[0] == instr]
        if len(candidates) == 0:
            raise Exception("Unknown instruction " + instr)
        elif len(candidates) == 1:
            opcode, fmt = candidates[0]
        elif not params[-1].isnumeric():
            opcode, fmt = candidates[0][0], 'R'
        else:
            opcode, fmt = candidates[0][0] + 1, ('I' if instr in ['CMP', 'MOV'] else 'D')

    def encode(lens, vals):
        res = 0
        for l, v in zip(lens, vals):
            res = (res << l) | (v & (2**l - 1))
        return res

    #print(line)
    #print(instr, opcode, params, fmt)

    regs = {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'SP': 6, 'PC': 7}
    params = [int(regs.get(p, p)) for p in params]

    #print(instr, opcode, params, fmt)
    
    if fmt == 'R':
        while len(params) < 3: params.append(0)
        return encode([5, 3, 3, 3, 2], [opcode, params[0], params[1], params[2], 0])
    elif fmt == 'D':
        return encode([5, 3, 3, 5], [opcode, params[0], params[1], params[2]])
    elif fmt == 'I':
        return encode([5, 3, 8], [opcode, params[0], params[1]])
    elif fmt == 'C':
        cond_map = {x[0]: i for i, x in enumerate(BotCPU.COND)}
        cond_code = cond_map[cond]
        return encode([5, 4, 7], [opcode, cond_code, params[0]])
    elif fmt == 'O':
        return encode([5, 11], [opcode, params[0]])
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-o', '--output', type=argparse.FileType('wb'), default=sys.stdout.buffer)
    parser.add_argument('--format', choices=['hex', 'raw', 'array'], default='hex')
    args = parser.parse_args()
    
    code = []
    for line in args.input:
        code.append(asm_instruction(line.strip()))

    output = None
    if args.format == 'hex':
        output = ''.join('%04x' % c for c in code).encode('utf-8')
    elif args.format == 'raw':
        output = struct.pack('<%dH' % len(code), *code)
    elif args.format == 'array':
        output = str(code).encode('utf-8')

    output += b'\n'

    args.output.write(output)
        
    
if __name__ == '__main__':
    main()
