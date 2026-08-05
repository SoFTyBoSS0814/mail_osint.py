import json
import requests

# 1. Beolvassuk a konfigurációt a loads.json-ből
def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_osint_check(email_to_check):
    config_list = load_config("loads.json")
    
    # Létrehozunk egy Session objektumot a sütik kezeléséhez
    session = requests.Session()

    for item in config_list:
        name = item.get("name")
        url = item.get("url")
        method = item.get("method", "POST").upper()
        headers = item.get("headers", {})
        
        # Alapértelmezett User-Agent beállítása, ha hiányzik
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # Munkamenet indítása a Gyakorikerdesek oldalán a sütikért
        if "gyakorikerdesek" in name.lower() or "gyakorikerdesek.hu" in url:
            try:
                session.get("https://www.gyakorikerdesek.hu/belepes", headers=headers)
            except Exception as e:
                print(f"[{name}] Hiba a munkamenet indításakor: {e}")
                continue

        # Dinamikus e-mail cserélés a payloadban
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

            # DEBUG: Kiíratjuk a szerver valós válaszát, hogy lássuk mi történik a háttérben
            print(f"[DEBUG] Státusz kód: {response.status_code}")
            print(f"[DEBUG] Válasz szövege:\n{response.text[:400]}")
            print("-" * 50)

            # Szabályok ellenőrzése
            rule = item.get("rule", {})
            expected_status = rule.get("status")
            expected_contains = rule.get("contains")

            status_ok = (response.status_code == expected_status) if expected_status else True
            text_ok = (expected_contains in response.text) if expected_contains else True

            if status_ok and text_ok:
                print(f"[+] [{name}] Feltétel teljesül (Találat / Megfelelő válasz).")
            else:
                print(f"[-] [{name}] A válasz nem felel meg a feltételnek.")

        except requests.exceptions.RequestException as e:
            print(f"[!] [{name}] Hálózati hiba történt: {e}")

if __name__ == "__main__":
    target_email = input("Add meg az ellenőrizendő e-mail címet: ").strip()
    run_osint_check(target_email)
