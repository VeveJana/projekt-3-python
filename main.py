"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

authorka: Jana Veverková
email: sevcik.jana@gmail.com
"""
"""
Elections Scraper - Program pro extrakci volebních dat parlamentních voleb 2017
z webových stránek Českého statistického úřadu.
Použití:
    python main.py <URL_adresa> <nazev_vystupniho_souboru>
Příklad:
    python main.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_olomoucko.csv"
"""
import sys
import csv
import requests
from bs4 import BeautifulSoup

def check_arguments():
    """
    Zkontroluje správnost vstupních argumentů.
    
    Returns:
        tuple: (URL, output_file) - dvojice obsahující URL adresu a název výstupního souboru
    
    Raises:
        ValueError: Pokud je počet argumentů nesprávný nebo URL není validní
    """
    if len(sys.argv) != 3:
        raise ValueError("Chyba: Program vyžaduje přesně dva argumenty: URL adresu a název výstupního souboru.")
    
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    # Ověření formátu URL
    if not url.startswith("https://volby.cz/pls/ps2017nss/"):
        raise ValueError("Chyba: URL adresa musí pocházet z domény volby.cz pro parlamentní volby 2017.")
    
    # Ověření formátu výstupního souboru
    if not output_file.endswith(".csv"):
        raise ValueError("Chyba: Výstupní soubor musí mít příponu .csv")
    
    return url, output_file

def get_html_content(url):
    """
    Získá HTML obsah ze zadané URL adresy.
    
    Args:
        url (str): URL adresa stránky
    
    Returns:
        str: HTML obsah stránky
    
    Raises:
        Exception: Při problému se stažením stránky
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.text
    except requests.RequestException as e:
        raise Exception(f"Chyba při stahování stránky {url}: {e}")

def parse_municipality_list(html_content, base_url="https://volby.cz/pls/ps2017nss/"):
    """
    Parsuje seznam obcí z HTML obsahu.
    
    Args:
        html_content (str): HTML obsah stránky se seznamem obcí
        base_url (str): Základní URL adresa pro sestavení absolutních odkazů
    
    Returns:
        list: Seznam slovníků obsahujících kód obce, název obce a URL s detaily
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    municipalities = []
    
    # Najdeme všechny tabulky s daty
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Přeskočíme hlavičku tabulky
            cells = row.find_all('td')
            
            # Přeskočíme řádky s nedostatkem buněk
            if len(cells) <= 1:
                continue
                        
            # Zkontrolujeme, zda první buňka obsahuje číslo (kód obce)
            first_cell_text = cells[0].text.strip()
            if not first_cell_text or not first_cell_text[0].isdigit():
                continue
            
            # Získáme kód obce (první buňka)
            code = first_cell_text
            
            # Získáme název obce (druhá buňka)
            name = cells[1].text.strip() if len(cells) > 1 else ""
            
            # Hledáme odkaz na detaily - může být v první nebo třetí buňce
            link = None
            for cell_index in [0, 2]:
                if cell_index < len(cells):
                    link = cells[cell_index].find('a')
                    if link:
                        break
            
            if link:
                # Sestavíme absolutní URL adresu
                href = link.get('href')
                if href:
                    detail_url = base_url + href
                    
                    municipalities.append({
                        'code': code,
                        'name': name,
                        'url': detail_url
                    })
    
    return municipalities

def get_voter_data(detail_html):
    """
    Extrahuje základní volební data (voliči, obálky, platné hlasy) z HTML detailu obce.
    
    Args:
        detail_html (str): HTML obsah stránky s detaily voleb v obci
    
    Returns:
        dict: Slovník obsahující počet voličů, vydaných obálek a platných hlasů
    """
    soup = BeautifulSoup(detail_html, 'html.parser')
    
    # Inicializujeme slovník
    voter_data = {'registered_voters': '', 'envelopes': '', 'valid_votes': ''}
    
    try:
        # Zkusíme najít tabulku s ID 'ps311_t1'
        summary_table = soup.find('table', id='ps311_t1')
        
        # Pokud není nalezena, zkusíme hledat první tabulku, která obsahuje potřebná data
        if not summary_table:
            # Hledáme tabulky, které mají v textu "Voliči v seznamu" nebo podobné
            for table in soup.find_all('table'):
                if 'Voliči' in table.text:
                    summary_table = table
                    break
        
        # Pokud stále nemáme tabulku, zkusíme najít jinou cestu
        if not summary_table:
            # Hledáme tabulku podle struktury - tabulka s 3 čísly v samostatných buňkách
            for table in soup.find_all('table'):
                cells = table.find_all('td')
                if len(cells) >= 3 and all(cell.text.strip().replace('\xa0', '').isdigit() for cell in cells[:3]):
                    voter_data['registered_voters'] = cells[0].text.strip().replace('\xa0', '')
                    voter_data['envelopes'] = cells[1].text.strip().replace('\xa0', '')
                    voter_data['valid_votes'] = cells[2].text.strip().replace('\xa0', '')
                    return voter_data
        
        # Pokud jsme našli tabulku, extrahujeme data
        if summary_table:
            # Najdeme první řádek s daty (přeskočíme hlavičku)
            rows = summary_table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                # Hledáme řádek, který obsahuje data o voličích, obálkách a hlasech
                if len(cells) >= 3:
                    # Zkontrolujeme, zda všechny buňky obsahují čísla
                    if all(cell.text.strip().replace('\xa0', '').replace(' ', '').isdigit() for cell in cells[:3]):
                        voter_data['registered_voters'] = cells[0].text.strip().replace('\xa0', '')
                        voter_data['envelopes'] = cells[1].text.strip().replace('\xa0', '')
                        voter_data['valid_votes'] = cells[2].text.strip().replace('\xa0', '')
                        break
        
        # Pokud stále nemáme data, zkusíme konkrétní rozložení stránky pro okres
        if not any(voter_data.values()):
            # Najdeme všechny td s třídou 'cislo'
            number_cells = soup.find_all('td', class_='cislo')
            
            # Pokud máme alespoň 3 buňky s čísly
            if len(number_cells) >= 3:
                voter_data['registered_voters'] = number_cells[0].text.strip().replace('\xa0', '')
                voter_data['envelopes'] = number_cells[1].text.strip().replace('\xa0', '')
                voter_data['valid_votes'] = number_cells[2].text.strip().replace('\xa0', '')
    
    except Exception as e:
        print(f"Chyba při extrakci volebních dat: {e}")
    
    return voter_data

def get_party_results(detail_html):
    """
    Extrahuje výsledky jednotlivých stran z HTML detailu obce.
    
    Args:
        detail_html (str): HTML obsah stránky s detaily voleb v obci
    
    Returns:
        dict: Slovník, kde klíčem je název strany a hodnotou počet hlasů
    """
    soup = BeautifulSoup(detail_html, 'html.parser')
    
    # Najde všechny tabulky s výsledky stran
    tables = soup.find_all('table')
    
    party_results = {}
    
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Přeskočí hlavičky
            cells = row.find_all('td')
            
            # Přeskočí prázdné řádky
            if len(cells) <= 1:
                continue
            
            # Pokud řádek obsahuje název strany a počet hlasů
            if len(cells) >= 3:
                # Získá název strany (obvykle ve druhém sloupci)
                party_name = cells[1].text.strip()
                
                # Získá počet hlasů (obvykle ve třetím sloupci, ale odstranit netisknutelné znaky)
                votes = cells[2].text.strip().replace('\xa0', '')
                
                # Přidá pouze pokud jsme našli neprázný název strany
                if party_name and votes.isdigit():
                    party_results[party_name] = votes
    
    return party_results

def process_municipality(municipality, all_parties):
    """
    Zpracuje data jedné obce a aktualizuje set názvů všech stran.
    
    Args:
        municipality (dict): Slovník s informacemi o obci
        all_parties (set): Set názvů všech stran
    
    Returns:
        dict: Kompletní data o obci včetně výsledků voleb
    """
    print(f"Stahuji data z URL: {municipality['url']}")
    
    detail_html = get_html_content(municipality['url'])
    
    # Získá základní volební data
    voter_data = get_voter_data(detail_html)
    
    # Získá výsledky stran
    party_results = get_party_results(detail_html)
    
    # Aktualizuje set všech stran
    all_parties.update(party_results.keys())
    
    # Vytvoří výsledný objekt
    result = {
        'code': municipality['code'],
        'name': municipality['name'],
        'registered_voters': voter_data.get('registered_voters', ''),
        'envelopes': voter_data.get('envelopes', ''),
        'valid_votes': voter_data.get('valid_votes', ''),
        'party_results': party_results
    }
    
    return result

def save_to_csv(data, all_parties, output_file):
    """
    Uloží výsledky do CSV souboru.
    
    Args:
        data (list): Seznam slovníků s daty obcí
        all_parties (set): Set názvů všech stran
        output_file (str): Název výstupního souboru
    """
    print(f"Ukládám do souboru: {output_file}")
    
    # Seřadí strany abecedně
    sorted_parties = sorted(all_parties)
    
    # Připraví hlavičky
    headers = ['code', 'name', 'registered_voters', 'envelopes', 'valid_votes'] + sorted_parties
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Použijeme středník jako oddělovač místo čárky pro lepší kompatibilitu s českým Excelem
            writer = csv.writer(f, delimiter=';')
            
            # Zapíše hlavičku
            writer.writerow(headers)
            
            # Zapíše data pro každou obec
            for municipality_data in data:
                row = [
                    municipality_data['code'],
                    municipality_data['name'],
                    municipality_data['registered_voters'],
                    municipality_data['envelopes'],
                    municipality_data['valid_votes']
                ]
                
                # Přidá výsledky stran
                for party in sorted_parties:
                    row.append(municipality_data['party_results'].get(party, ''))
                
                writer.writerow(row)
    except IOError as e:
        raise Exception(f"Chyba při zápisu do CSV souboru: {e}")

def main():
    """
    Hlavní funkce programu.
    """
    try:
        # Zkontroluje argumenty
        url, output_file = check_arguments()
        
        print(f"Stahuji data z: {url}")
        print(f"Ukladam do souboru: {output_file}")
        
        # Získá obsah hlavní stránky
        html_content = get_html_content(url)
        
        # Parsuje seznam obcí
        municipalities = parse_municipality_list(html_content)
        
        if not municipalities:
            raise ValueError("Nebyla nalezena žádná obec na zadané URL adrese. Zkontrolujte zadané URL.")
        
        # Set pro ukládání názvů všech stran
        all_parties = set()
        
        # Zpracuje data pro každou obec
        results = []
        for municipality in municipalities:
            municipality_data = process_municipality(municipality, all_parties)
            results.append(municipality_data)
        
        # Uloží výsledky do CSV
        save_to_csv(results, all_parties, output_file)
        
        print("Ukončuji Elections Scraper")
        
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Došlo k neočekávané chybě: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
