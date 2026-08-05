import json
import os
import requests
from playwright.sync_api import sync_playwright

def load_configurations():
    """Beolvassa a loads.json és cookies.json fájtokat."""
    loads = {}
    cookies = {}
    
    if os.path.exists("loads.json"):
        with open("loads.json", "r", encoding="utf-8") as f:
            loads = json.load(f)
            
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
            
    return loads, cookies

def check_goldengate(email: str, config: dict) -> str:
    """
    GoldenGate.hu ellenőrzése Playwright-tal a Cloudflare Turnstile kezeléséhez.
    """
    url = config.get("url", "https://www.goldengate.hu/felhasznalo/elfelejtett_jelszo")
    
    with sync_playwright() as p:
        # A headless=True a háttérben futtatja, ha látni akarod a böngészőt, állítsd False-ra
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Navigáció az oldalra
            page.goto(url, timeout=60000)
            
            # 2. Várás a Cloudflare Turnstile betöltődésére
            page.wait_for_timeout(3000)

            # 3. E-mail mező kitöltése
            page.fill("input[name='email']", email)

            # 4. Küldés gomb megnyomása
            page.click("input[name='forgotten_password'], button[type='submit']")

            # 5. Válasz megvárása és elemzése
            page.wait_for_selector("form, .alert, body", timeout=10000)
            content = page.content()

            if "Nincs ilyen e-mail megadva" in content:
                return "[negatív] Az e-mail cím nincs regisztrálva."
            elif "Sikeres" in content or "levél" in content:
                return "[pozitív] Az e-mail cím regisztrálva van."
            else:
                return "[ismeretlen] A szerver válasza nemértelmezhető."

        except Exception as e:
            return f"[hiba] Hiba történt a folyamat során: {str(e)}"
        
        finally:
            browser.close()

def check_gyakorikerdesek(email: str, config: dict, cookies: dict) -> str:
    """
    Gyakorikerdesek.hu ellenőrzése hagyományos requests alapon (meglévő logika).
    """
    url = config.get("url")
    method = config.get("method", "POST").upper()
    
    # Cookiek konvertálása a requests számára, ha szükséges
    cookie_dict = {c['name']: c['value'] for c in cookies} if isinstance(cookies, list) else cookies
    
    # Itt a loads.json-ban megadott adatstruktúra szerint küldöd a kérést
    data = config.get("data", {})
    # Cseréljük be az e-mail címet a konfigurációban megjelölt helyre
    for key, value in data.items():
        if value == "{email}":
            data[key] = email

    try:
        if method == "POST":
            response = requests.post(url, data=data, cookies=cookie_dict, timeout=10)
        else:
            response = requests.get(url, params=data, cookies=cookie_dict, timeout=10)
            
        # Ide jön a Gyakorikerdesek válaszértékelő logikája
        if response.status_code == 200:
            return f"[válasz érkezett] Státusz: 200 OK"
        else:
            return f"[hiba] Státusz kód: {response.status_code}"
            
    except Exception as e:
        return f"[hiba] {str(e)}"

def main():
    loads, cookies = load_configs()
    target_email = loads.get("target_email", "teszt@pelda.hu")
    
    print(د "Cél e-mail ellenőrzése: {target_email}\n" + "---" * 20)

    # 1. GoldenGate ellenőrzés futtatása
    if "goldengate" in loads:
        print("[*] GoldenGate.hu ellenőrzése (Playwright)...")
        gg_result = check_goldengate(target_email, loads["goldengate"])
        print(f"Eredmény: {gg_result}\n")

    # 2. Gyakorikerdesek ellenőrzés futtatása
    if "gyakorikerdesek" in loads:
        print("[*] Gyakorikerdesek.hu ellenőrzése (Requests)...")
        gyk_result = check_gyakorikerdesek(target_email, loads["gyakorikerdesek"], cookies)
        print(f"Eredmény: {gyk_result}\n")

if __name__ == "__main__":
    main()
