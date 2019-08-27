#! /usr/bin/env python
import os
import json

players = {}

print('<html><head><link rel="stylesheet" type="text/css" href="/style.css" /></head><body>')

print('<table>')
print('<tr><th>Partija</th><th>EJOI ekipica</th><th>Infinity</th><th>Inspekcija</th></tr>')

LOG_DIR = 'frontend/logs'
for game in sorted(os.listdir(LOG_DIR)):
    with open(LOG_DIR + '/' + game, 'r') as f:
        raw = f.read()
        data = eval(raw)
        scores = [x['points'] for x in data['turns'][-1]['bots']]
        print(f'<tr><td>{game}</td>', end='')
        for s in scores:
            print(f'<td>{s}</td>', end='')
        print('</tr>')
        
print('</table></body></html>')
