import json
import os
import requests
import traceback
from playwright.sync_api import sync_playwright

def load_configurations():
    """Beolvassa a loads.json és cookies.json fájtokat biztonságosan."""
    loads = {}
    cookies = {}
    
    if os.path.exists("loads.json"):
        try:
            with open("loads.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    loads = data
                else:
                    print("[!] Hiba: A loads.json fájlnak szótárral ({} jelöléssel) kell kezdődnie!")
        except Exception as e:
            print(f"[!] Hiba a loads.json elemzésekor: {e}")
            
    if os.path.exists("cookies.json"):
        try:
            with open("cookies.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, (dict, list)):
                    cookies = data
        except Exception as e:
            print(f"[!] Hiba a cookies.json elemzésekor: {e}")
            
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
            page.wait_for_timeout(4000)

            page.wait_for_selector("input[name='email']", timeout=10000)
            page.fill("input[name='email']", email)

            try:
                page.click("button:has-text('Jelszó küldése'), input[type='submit']")
            except:
                page.click("text=Jelszó küldése")

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
    
    # Cookie formátum biztonságos kezelése (ha lista vagy dict)
    if isinstance(cookies, list):
        cookie_dict = {c.get('name'): c.get('value') for c in cookies if 'name' in c and 'value' in c}
    else:
        cookie_dict = cookies
    
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
    try:
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
            
    except Exception as e:
        print("[!] Kritikus hiba lépett fel a futtatás során:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
