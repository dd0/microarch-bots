#! /usr/bin/env python
import os

print("Content-Type: text/html\n")

print('<html><head><link rel="stylesheet" type="text/css" href="/style.css" /></head><body>')

print("<h1>Partije</h1>")
print("<table><tr><th>Naziv</th><th>Rezultat</th></tr>")
for game in os.listdir("logs"):
    print(f"<tr><td><a href=../visualiser.html?{game}>{game}</a></td><td>...</td></tr>")
print("</table>")

print("<p><a href=../index.html>Nazad</a></p>")
    
print("</body></html>")
