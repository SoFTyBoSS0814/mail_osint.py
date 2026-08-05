import json
import requests

def load_config():
    """Betölti a loads.json és cookies.json konfigurációs fájlokat."""
    try:
        with open('loads.json', 'r', encoding='utf-8') as f:
            loads = json.load(f)
    except Exception as e:
        print(f"Hiba a loads.json betöltésekor: {e}")
        loads = []

    try:
        with open('cookies.json', 'r', encoding='utf-8') as f:
            cookies = json.load(f)
    except Exception as e:
        print(f"Hiba a cookies.json betöltésekor: {e}")
        cookies = {}
        
    return loads, cookies

def main():
    email_to_test = input("Add meg a tesztelni kívánt e-mail címet: ").strip()
    loads, cookies_config = load_config()

    if not loads:
        print("Nincsenek betölthető célpontok a loads.json fájlban.")
        return

    for target in loads:
        name = target.get("name")
        url = target.get("url")
        method = target.get("method", "POST").upper()
        headers = target.get("headers", {})
        data_template = target.get("data", {})
        rule = target.get("rule", {})

        # Az {email} helykitöltő cseréje a megadott címre
        data = {k: v.replace("{email}", email_to_test) for k, v in data_template.items()}

        # Az adott célponthoz tartozó sütik lekérése
        target_cookies = cookies_config.get(name, {})

        print(f"\n" + "="*50)
        print(f"Célpont vizsgálata: {name}")
        print(f"URL: {url}")
        print("="*50)

        try:
            if method == "POST":
                response = requests.post(url, headers=headers, data=data, cookies=target_cookies, timeout=10)
            elif method == "GET":
                response = requests.get(url, headers=headers, params=data, cookies=target_cookies, timeout=10)
            else:
                print(f"Ismeretlen HTTP metódus: {method}")
                continue

            # --- DEBUG INFORMÁCIÓK ---
            print(f"[DEBUG] HTTP Státuszkód: {response.status_code}")
            print(f"[DEBUG] Szerver nyers válasza:\n{response.text}\n")
            print("-" * 50)

            # Szabályok ellenőrzése
            expected_status = rule.get("status")
            contains_text = rule.get("contains")

            status_ok = (response.status_code == expected_status) if expected_status else True
            contains_ok = (contains_text in response.text) if contains_text else True

            if status_ok and contains_ok:
                print(f"Eredményértékelés: A megadott szabály (tartalmazza: '{contains_text}') **TELJESÜLT**. A fiók valószínűleg **NEM LÉTEZIK**.")
            else:
                print(f"Eredményértékelés: A szabály **NEM TELJESÜLT**. Lehet, hogy a fiók **LÉTEZIK**, vagy a szerver eltérő választ adott (pl. rate-limit / anti-enumeration védelem).")

        except requests.exceptions.RequestException as e:
            print(f"Hálózati hiba történt a {name} hívásakor: {e}")

if __name__ == "__main__":
    main()
