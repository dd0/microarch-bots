#! /usr/bin/env python
from game import World
import argparse
import sys
import map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('players', nargs='+')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-m', '--map', choices=['empty', 'blocks', 'cave'], default='empty')
    args = parser.parse_args()

    bots = []
    for player in args.players:
        with open(player, 'r') as f:
            code = f.read()
            parsed = []
            for i in range(0, len(code), 4):
                parsed.append(int(code[i:i+4], 16))
            bots.append(parsed)

    map_generator = map.Map if args.map == 'empty' \
        else map.RocksMap if args.map == 'blocks' \
        else map.CaveMap
    world = World(bots, map_generator, args.seed)

    meta = {'players': args.players, 'seed': args.seed if args.seed is not None else -1, 'map': args.map}
        
    args.output.write(world.run_with_log(1000, meta))
    
if __name__ == '__main__':
    main()
