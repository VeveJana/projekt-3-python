# Elections Scraper

## Popis projektu
Elections Scraper je program pro extrakci volebních dat parlamentních voleb 2017 z webových stránek Českého statistického úřadu. Program získává data o výsledcích hlasování v jednotlivých obcích ve vybraném územním celku a ukládá je do CSV souboru pro další analýzu.

Program extrahuje následující údaje:
- Kód obce
- Název obce
- Počet registrovaných voličů
- Počet vydaných obálek
- Počet platných hlasů
- Výsledky všech politických stran a hnutí (počet hlasů)

## Instalace

### Postup instalace

1. Naklonujte repozitář nebo stáhněte zdrojový kód
2. Vytvořte virtuální prostředí:
   python -m venv venv
3. Aktivujte virtuální prostředí:
   - Windows:
   venv\Scripts\activate
   - macOS/Linux:
   source venv/bin/activate
4. Nainstalujte potřebné knihovny:
   pip install -r requirements.txt

## Spuštění projektu

Program se spouští z příkazové řádky a vyžaduje dva povinné argumenty:

python main.py <URL_adresa> <nazev_vystupniho_souboru>

### Argumenty:
- <URL_adresa> - URL adresa stránky s odkazy na výsledky voleb v jednotlivých obcích
- <nazev_vystupniho_souboru> - Název výstupního CSV souboru (musí končit příponou .csv)

### Příklad použití:

python main.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_olomoucko.csv"

## Ukázka projektu

### Argumenty:
1. URL adresa: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
2. Název výstupního souboru: vysledky_olomoucko.csv

### Výstup v terminálu:
Stahuji data z: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
Ukladam do souboru: vysledky_olomoucko.csv
Stahuji data z URL: https://volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec=589268&xvyber=7103
...
Ukládám do souboru: vysledky_olomoucko.csv
Ukončuji Elections Scraper

### Částečný výstup (ukázka obsahu CSV souboru):
code;name;registered_voters;envelopes;valid_votes;Občanská demokratická strana;Řád národa - Vlastenecká unie;CESTA ODPOVĚDNÉ SPOLEČNOSTI;...
506761;Alojzov;205;145;144;29;0;0;...
589268;Bedihošť;834;527;524;34;0;0;...
552631;Bílovice-Lutotín;431;279;275;24;0;0;...
...

## Autor
Jana Veverková  
Email: sevcik.jana@gmail.com
