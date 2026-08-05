import json
import sys
import requests

def load_config(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Hiba: A(z) {file_path} fájl nem található.")
        sys.exit(1)

def run_osint_check(email_to_check):
    config_list = load_config("loads.json")
    session = requests.Session()

    for item in config_list:
        name = item.get("name")
        url = item.get("url")
        method = item.get("method", "POST").upper()
        headers = item.get("headers", {})
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # GDPR / Süti fal megkerülése a Gyakorikerdesekhez
        if "gyakorikerdesek" in name.lower() or "gyakorikerdesek.hu" in url:
            try:
                session.get("https://www.gyakorikerdesek.hu/belepes", headers=headers)
                session.cookies.set("cookieok", "1", domain="www.gyakorikerdesek.hu")
            except Exception:
                pass

        raw_data = item.get("data", {})
        payload = {}
        for key, value in raw_data.items():
            if isinstance(value, str):
                payload[key] = value.replace("{email}", email_to_check)
            else:
                payload[key] = value

        try:
            if method == "POST":
                response = session.post(url, data=payload, headers=headers)
            elif method == "GET":
                response = session.get(url, params=payload, headers=headers)
            else:
                continue

            rule = item.get("rule", {})
            expected_contains = rule.get("contains", "")

            # Eredmény kiértékelése
            if expected_contains and expected_contains in response.text:
                print(f"[-] [{name}] A fiók NEM létezik (Nincs regisztráció ezzel a címmel).")
            else:
                print(f"[+] [{name}] A fiók LÉTEZIK (vagy érvényes regisztrált e-mail cím).")

        except requests.exceptions.RequestException:
            print(f"[!] Hálózati hiba történt a(z) {name} ellenőrzése közben.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python3 osint.py <email_cim>")
        sys.exit(1)
    
    target_email = sys.argv[1].strip()
    run_osint_check(target_email)
