import json
import requests

# 1. Beolvassuk a konfigurációt a loads.json-ből
def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_osint_check(email_to_check):
    config_list = load_config("loads.json")
    
    # Létrehozunk egy Session objektumot, ami megőrzi a sütiket és a munkamenetet
    session = requests.Session()

    for item in config_list:
        name = item.get("name")
        url = item.get("url")
        method = item.get("method", "POST").upper()
        headers = item.get("headers", {})
        
        # Alapértelmezett User-Agent, ha nincs a JSON-ben
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Különleges kezelés a Gyakorikerdesek platformhoz:
        # Először lekérjük a fő/bejelentkezési oldalt, hogy a szerver beállítsa a sütiket (Session)
        if "gyakorikerdesek.php" in url or "gyakorikerdesek" in name.lower():
            try:
                session.get("https://www.gyakorikerdesek.hu/belepes", headers=headers)
            except Exception as e:
                print(f"[{name}] Hiba a munkamenet indításakor: {e}")
                continue

        # Dinamikusan kicseréljük a {email} helyőrzőt a vizsgált e-mail címre
        raw_data = item.get("data", {})
        payload = {}
        for key, value in raw_data.items():
            if isinstance(value, str):
                payload[key] = value.replace("{email}", email_to_check)
            else:
                payload[key] = value

        print(f"[*] Ellenőrzés itt: {name} ({email_to_check})...")

        try:
            if method == "POST":
                response = session.post(url, data=payload, headers=headers)
            elif method == "GET":
                response = session.get(url, params=payload, headers=headers)
            else:
                print(f"[{name}] Nem támogatott metódus: {method}")
                continue

            # Szabályok ellenőrzése (Rule evaluation)
            rule = item.get("rule", {})
            rule_type = rule.get("type")
            expected_status = rule.get("status")
            expected_contains = rule.get("contains")

            status_ok = (response.status_code == expected_status) if expected_status else True
            text_ok = (expected_contains in response.text) if expected_contains else True

            # Eredmény kiértékelése
            if rule_type == "status_and_text":
                if status_ok and text_ok:
                    print(f"[+] [{name}] Találat / Megfelel a feltételnek (A fiók valószínűleg létezik vagy a válasz azonos).")
                    print(f"Válasz részlet: {response.text[:150]}...")
                else:
                    print(f"[-] [{name}] Nincs találat vagy eltérő válasz. Státusz: {response.status_code}")
            else:
                print(f"[?] [{name}] Ismeretlen rule típus: {rule_type}")

        except requests.exceptions.RequestException as e:
            print(f"[!] [{name}] Hálózati hiba történt: {e}")

if __name__ == "__main__":
    # Teszt e-mail cím megadása
    target_email = input("Add meg az ellenőrizendő e-mail címet: ").strip()
    run_osint_check(target_email)
