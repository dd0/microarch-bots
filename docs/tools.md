% Alati

## Arena

Da bi pokrenuli partiju sa robotima čiji programi su `robot1.hex`,
`robot2.hex` i `robot3.hex`, i sačuvali log partije u `log.txt`:

~~~ {.bash}
python run.py robot1.hex robot2.hex robot3.hex -o log.txt
~~~

Takođe su na raspolaganju parametri `--seed SEED` (da bi dobili
konzistentne partije) i `-m tip-mape` koji bira generator mapa (jedan
od `empty`, `blocks`, `cave`).

## Asembler

Da bi lakše počeli, na raspolaganju je program `asm.py`, koji od fajla
koji sadrži kod u asembleru za kontroler robota generiše program koji
arena čita. Da bi fajl `program.S` asemblirali u `robot.hex`:

~~~ {.bash}
python asm.py -i program.S -o robot.hex
~~~

Ukoliko jedan od ova dva parametra nedostaje, program čita sa
standardnog ulaza, odnosno piše na standardni izlaz. Dodatno,
parametrom `--format` se može odabrati alternativni format izlaza:
binarni fajl (`--format raw`) ili niz brojeva (`--format array`),
ukoliko vam je to korisno kao među-format za dalje procesiranje.

## Server

Da bi imali pristup vizuelizacijama prethodnih partija, neophodno je
da pokrenete kopiju servera iz direktorijuma `frontend`:

~~~ {.bash}
cd frontend
python -m http.server --cgi
~~~

Serveru možete pristupiti na <http://localhost:8000>. Da bi se partija
pojavila u spisku prošlih partija, potrebno je staviti log fajl u
`frontend/logs/` (napravite direktorijum ako ne postoji).

[Nazad](../index.html)
