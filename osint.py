import json
import os
import requests

def load_configurations():
    """Beolvassa a loads.json és cookies.json fájtokat."""
    loads = {}
    cookies = {}
    
    if os.path.exists("loads.json"):
        with open("loads.json", "r", encoding="utf-8") as f:
            try:
                loads = json.load(f)
            except Exception as e:
                print(f"Hiba a loads.json beolvasásakor: {e}")
                
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding="utf-8") as f:
            try:
                cookies = json.load(f)
            except Exception as e:
                print(f"Hiba a cookies.json beolvasásakor: {e}")
                
    return loads, cookies

def check_gyakorikerdesek(email: str, config: dict, cookies: dict) -> str:
    """
    Gyakorikerdesek.hu ellenőrzése hagyományos requests alapon.
    """
    url = config.get("url")
    if not url:
        return "[hiba] Hiányzik az URL a loads.json-ból!"
        
    method = config.get("method", "POST").upper()
    
    # Cookie-k átalakítása szótárrá, függetlenül attól, hogy listaként vagy szótárként vannak tárolva
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
            return f"[válasz érkezett] Státusz: 200 OK | Tartalom hossza: {len(response.text)} karakter"
        else:
            return f"[hiba] Státusz kód: {response.status_code}"
            
    except Exception as e:
        return f"[hiba] {str(e)}"

def main():
    loads, cookies = load_configurations()
    target_email = loads.get("target_email", "teszt@pelda.hu")
    
    print(f"Cél e-mail ellenőrzése: {target_email}\n" + "---" * 20)

    # Konfiguráció kinyerése a loads.json-ból (kezelve azt is, ha külön blokkban vagy közvetlenül van)
    gyk_config = loads.get("gyakorikerdesek", loads)
    
    print("[*] Gyakorikerdesek.hu ellenőrzése (Requests)...")
    result = check_gyakorikerdesek(target_email, gyk_config, cookies)
    print(f"Eredmény: {result}\n")

if __name__ == "__main__":
    main()
