#! /usr/bin/env python3
import cgi
import re
import os

PROG_DIR = "programs"

def atomic_write(fname, data):
    temp = fname + ".tmp"
    with open(temp, "w") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.rename(temp, fname)

print("Content-Type: text/html\n")

form = cgi.FieldStorage()

if "program" not in form:
    print("Error: no program submitted!")
    exit(0)
program = form["program"].value
program = re.sub('[^a-fA-F0-9]', "", program)

token = form.getvalue("token", "")
user_tokens = {"test": "player1", "token_2": "player2"}
if token not in user_tokens:
    print("Error: invalid token!")
    exit(0)
user = user_tokens[token]

maps = [x for x in ["A", "B", "C"] if form.getvalue("map"+x, "") == "on"]
if len(maps) == 0:
    print("Error: no maps selected!")
    exit(0)

for m in maps:
    atomic_write(f"{PROG_DIR}/{user}.{m}.S", program)
    
print(f"<p>Succesfully submitted a program for user {user} and maps {maps}.</p>")
print(f"<h3>Program</h3>")
print(f"<pre>{program}</pre>")
print('<p><a href="../submit.html">Nazad</a></p>')
