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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=60000)
            
            # Várkód a Cloudflare-re és az elemek betöltődésére
            page.wait_for_timeout(4000)

            # E-mail mező kitöltése (biztosítva, hogy létezik)
            page.wait_for_selector("input[name='email']", timeout=10000)
            page.fill("input[name='email']", email)

            # Küldés gomb megnyomása (szöveg vagy típus alapján)
            # A GoldenGate-en a gomb felirata "Jelszó küldése"
            try:
                page.click("button:has-text('Jelszó küldése'), input[type='submit']")
            except:
                # Alternatív kattintási kísérlet, ha az első nem találja
                page.click("text=Jelszó küldése")

            # Válasz megvárása
            page.wait_for_timeout(3000)
            content = page.content()

            if "Nincs ilyen e-mail megadva" in content:
                return "[negatív] Az e-mail cím nincs regisztrálva."
            elif "Sikeres" in content or "levél" in content:
                return "[pozitív] Az e-mail cím regisztrálva van."
            else:
                return "[ismeretlen] A szerver válasza nem értelmezhető (lehet, hogy a Cloudflare blokkolta)."

        except Exception as e:
            return f"[hiba] Playwright hiba: {str(e)}"
        
        finally:
            browser.close()

def check_gyakorikerdesek(email: str, config: dict, cookies: dict) -> str:
    """
    Gyakorikerdesek.hu ellenőrzése hagyományos requests alapon.
    """
    url = config.get("url")
    if not url:
        return "[hiba] Hiányzik a Gyakorikerdesek URL a loads.json-ból!"
        
    method = config.get("method", "POST").upper()
    
    cookie_dict = {c['name']: c['value'] for c in cookies} if isinstance(cookies, list) else cookies
    
    data = config.get("data", {}).copy()
    for key, value in data.items():
        if value == "{email}":
            data[key] = email

    try:
        if method == "POST":
            response = requests.post(url, data=data, cookies=cookie_dict, timeout=10)
        else:
            response = requests.get(url, params=data, cookies=cookie_dict, timeout=10)
            
        if response.status_code == 200:
            return f"[válasz érkezett] Státusz: 200 OK"
        else:
            return f"[hiba] Státusz kód: {response.status_code}"
            
    except Exception as e:
        return f"[hiba] Requests hiba: {str(e)}"

def main():
    loads, cookies = load_configurations()
    target_email = loads.get("target_email", "teszt@pelda.hu")
    
    print(f"Cél e-mail ellenőrzése: {target_email}\n" + "---" * 20)

    if "goldengate" in loads:
        print("[*] GoldenGate.hu ellenőrzése (Playwright)...")
        gg_result = check_goldengate(target_email, loads["goldengate"])
        print(f"Eredmény: {gg_result}\n")

    if "gyakorikerdesek" in loads:
        print("[*] Gyakorikerdesek.hu ellenőrzése (Requests)...")
        gyk_result = check_gyakorikerdesek(target_email, loads["gyakorikerdesek"], cookies)
        print(f"Eredmény: {gyk_result}\n")

if __name__ == "__main__":
    main()
