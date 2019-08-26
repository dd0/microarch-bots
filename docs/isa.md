% Mikrokontroler

# Procesor

Roboti koje programirate pokreće jednostavan procesor, sa arhitekturom
koja je pomalo slična mikrokontrolerima, ali sa nekoliko bitnih
razlika (na primer, stek je odvojen od ostatka memorije). Procesor
radi sa 16-bitnim vrednostima (kako memorijskim adresama, tako i
vrednostima).

Memorija se sastoji od dva dela:

* glavna" memorija, koja sadrži program koji se izvršava i podatke, i
  kojoj se može pristupati putem `LOAD` i `STORE` instrukcija, i 
* stek, koji je potpuno odvojen od glavne memorije i kojem se pristupa
  putem `PUSH` i `POP`.

Procesor ima osam registara: šest registara opšte namene (`R0` do
`R6`), "stack pointer" `SP` koji sadrži broj vrednosti na steku, i
"program counter" `PC` koji sadrži adresu instrukcije koja se trenutno
izvršava.

Na početku partije, vaš program se učitava u memoriju počev od adrese
`0`. Ostatak memorije i registri se inicijalizuju na 0 (uključujući
`PC`) i počinje izvršavanje programa.

## Vreme

Partija je podeljena u poteze, koje svi roboti igraju istovremeno i
tokom kojih izvršavaju instrukcije. Svaki potez se izvršava fiksan
broj instrukcija (100), sa izuzetkom prvog poteza u kom je ovo
ograničenje značajno veće.

Instrukcije za interagovanje sa svetom su izuzetak od ovoga i mogu
koštati više (brojati se kao nekoliko instrukcija). Ukoliko procesor
izvrši instrukciju koja bi premašila broj dozvoljenih instrukcija za
ovaj potez, ostatak "neplaćenog" vremena će se oduzeti od narednih
poteza.

Dodatno, instrukcije za kretanje uvek završavaju potez.

# Instrukcije

## Format

Instrukcije su u memoriji predstavljene kao 16-bitni brojevi. Prvih
pet bita gledano sa leva (najtežih) predstavljaju kod instrukcije, dok
su u ostalih 11 zapisani parametri. Parametri su zapisani redom kojim
su dati u opisu instrukcije. Registri su predstavljeni sa tri bita
(`R0` kao 0, `R1` kao 1, ..., `SP` kao 6 i `PC` kao 7). Ukoliko je
poslednji parametar instrukcije broj, svi preostali biti se koriste za
njega.

Napomena: instrukcije koje imaju tri registra kao parametre imaju dva
bita "viška" na kraju, koje procesor ignoriše.

Operacija uslovnog skoka `B.cond` je izuzetak od ovog formata, i
detaljnije je opisana dole.

## Spisak instrukcija

U sledećoj tabeli je dat spisak podržanih instrukcija i njihovih
kodova. U tabeli, `Rx` predstavlja proizvoljan registar, a `imm` broj.

Kod  Instrukcija        Efekat
---  -----------        ------
  0  MOV Rd, Ra         Rd = Ra
  1  MOV Rd, imm        Rd = imm
  2  ADD Rd, Ra, Rb     Rd = Ra + Rb
  3  ADD Rd, Ra, imm    Rd = Ra + imm
  4  SUB Rd, Ra, Rb     Rd = Ra - Rb
  5  SUB Rd, Ra, imm    Rd = Ra - imm
  6  SHL Rd, Ra, Rb     Rd = Ra << Rb
  7  SHL Rd, Ra, imm    Rd = Ra << imm
  8  SHR Rd, Ra, Rb     Rd = Ra >> Rb
  9  SHR Rd, Ra, imm    Rd = Ra >> imm
 10  AND Rd, Ra, Rb     Rd = Ra & Rb
 11  AND Rd, Ra, imm    Rd = Ra & imm
 12  OR Rd, Ra, Rb      Rd = Ra | Rb
 13  OR Rd, Ra, imm     Rd = Ra | imm
 14  XOR Rd, Ra, Rb     Rd = Ra ^ Rb
 15  XOR Rd, Ra, imm    Rd = Ra | imm
 16  LOAD Rd, Ra, Rb    Rd = mem[Ra + Rb]
 17  LOAD Rd, Ra, imm   Rd = mem[Ra + imm]
 18  STORE Rs, Ra, Rb   mem[Ra + Rb] = Rs
 19  STORE Rs, Ra, imm  mem[Ra + imm] = Rs
 20  PUSH Rs            push(Rs)
 21  PUSH imm           push(imm)
 22  POP Rd             Rd = pop()
 23  CMP Ra, Rb         utiče na ponašanje `B.cond` (videti dole)
 24  CMP Ra, imm        isto
 25  B.cond imm         uslovni skok
 26  B imm              bezuslovni skok
 27  SYSCALL Rx, imm    interakcija sa svetom

### Bezuslovni skok

Instrukcija bezuslovnog skoka `B imm` skače na adresu `imm`, tako da
je sledeća instrukcija koja će biti izvršena ona na adresi `imm`.

### Uslovni skok

Instrukcije `CMP` i `B.cond` služe za uslovne skokove: prvo je
potrebno izvršiti `CMP` da bi se uporedila dva registra, čiji će se
rezultat dalje koristiti da bi se odlučilo da li će skok `B.cond imm`
skočiti na lokaciju `imm` ili ne. 

Instrukcija uslovnog skoka je predstavljena kao pet bita sa kodom
(25), zatim četiri bita koji opisuju uslov koji treba ispuniti da bi
do skoka došlo, i na kraju adresu. Neki korisni uslovi su:

* `0000`: Ra == Rb
* `0001`: Ra != Rb
* `1010`: Ra >= Rb
* `1011`: Ra < Rb
* `1100`: Ra > Rb
* `1101`: Ra <= Rb

### Interakcija sa svetom

Instrukcija `SYSCALL Rx, imm` služi za interakciju sa ostatkom sveta
(van robota). Parametar `imm` bira vrstu interakcije, a `Rx` se
koristi za ulazni, ondosno izlazni parametar -- ako interakcija
očekuje parametar treba ga upisati u `Rx`, a ako vraća vrednost ona će
biti upisana u `Rx`.

Na raspolaganju su sledeće operacije:

* Pročitaj svoje koordinate (`imm = 0`): u `Rx` zapisuje trenutnu
  poziciju robota. Cena: 50 instrukcija.
* Pronađi najbližeg robota datoj poziciji (`imm = 1`): u `Rx` zapisuje
  poziciju robota najbližeg poziciji datoj u `Rx`. Cena: 10
  instrukcija.
* Pronađi najbližeg tuđeg robota datoj poziciji (`imm = 2`): u `Rx`
  zapisuje poziciju robota najbližeg poziciji datoj u `Rx`, ne
  računajući sebe. Cena: 10 instrukcija.
* Pročitaj poziciju poena (`imm = 3`): u `Rx` zapisuje poziciju poena
  sa indeksom datim u `Rx`. Ukoliko nema dovoljno poena, vraća
  nevalidnu poziciju (`1<<12`). Cena: 5 instrukcija.
* Proveri stanje polja (`imm = 4`): u `Rx` zapisuje 0 ukoliko je polje
  na poziciji datoj u `Rx` prohodno, a u suprotnom 1. Cena: 25
  instrukcija, osim tokom prvog poteza, tokom kog je cena 1
  instrukcija.
* Pomeri se (`imm = 5`): pomera robota jedno polje u pravcu datom u
  `Rx` (gore: 0, dole: 1, levo: 2, desno: 3). Cena: 200
  instrukcija, **završava potez**.
* Završi potez (`imm = 6`).
* Debug (`imm = 7`): u "debug-registar" zapisuje vrednost u `Rx`. Ovo
  nije pravi registar, već izlazna vrednost koja se može videti tokom
  vizuelizacije (gde se prikazuje samo poslednja vrednost upisana
  tokom poteza). Cena: 1 instrukcija.

Za operacije koje čitaju ili vraćaju poziciju, pozicija je opisana kao
12-bitni broj, gde gornjih šest bita predstavlja red, a donjih šest
kolonu.

[Nazad](../index.html)
