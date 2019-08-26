#! /usr/bin/env python3
import cgi
import re
import os
import json

PROG_DIR = "../programs"
TOKEN_FILE = "../config/tokens.json"

def atomic_write(fname, data):
    temp = fname + ".tmp"
    with open(temp, "w") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.rename(temp, fname)

print("Content-Type: text/html\n")

form = cgi.FieldStorage()

print('<html><head><link rel="stylesheet" type="text/css" href="/style.css" /></head><body>')

if "program" not in form:
    print("Error: no program submitted!")
    print("</body></html>")
    exit(0)
program = form["program"].value
program = re.sub('[^a-fA-F0-9]', "", program)

token_config = None
with open(TOKEN_FILE, 'r') as f:
    token_config = json.loads(f.read())

token = form.getvalue("token", "")
user_tokens = {a['token'] : (a['name'], a['file']) for a in token_config}
if token not in user_tokens:
    print("Error: invalid token!")
    print("</body></html>")
    exit(0)
user, fname = user_tokens[token]

maps = [x for x in ["A", "B", "C"] if form.getvalue("map"+x, "") == "on"]
if len(maps) == 0:
    print("Error: no maps selected!")
    exit(0)

for m in maps:
    atomic_write(f"{PROG_DIR}/{fname}.{m}.bin", program)
    
print(f"<p>Succesfully submitted a program for user {user} and maps {maps}.</p>")
print(f"<h3>Program</h3>")
print(f"<pre>{program}</pre>")
print('<p><a href="../submit.html">Nazad</a></p>')
print("</body></html>")
