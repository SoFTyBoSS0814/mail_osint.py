import json
import sys
import requests

def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Hiba: A(z) {file_path} fájl nem található.")
        sys.exit(1)

def run_osint_check(email_to_check):
    config_list = load_json("loads.json")
    
    try:
        all_cookies = load_json("cookies.json")
    except Exception:
        all_cookies = {}
        
    session = requests.Session()

    for item in config_list:
        name = item.get("name")
        url = item.get("url")
        method = item.get("method", "POST").upper()
        headers = item.get("headers", {})
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        site_cookies = all_cookies.get(name, {})
        for cookie_name, cookie_value in site_cookies.items():
            session.cookies.set(cookie_name, cookie_value, domain="www.gyakorikerdesek.hu")

        if "gyakorikerdesek" in name.lower() or "gyakorikerdesek.hu" in url:
            try:
                session.get("https://www.gyakorikerdesek.hu/belepes", headers=headers)
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
                response = session.post(url, data=payload, headers=headers, allow_redirects=True)
            elif method == "GET":
                response = session.get(url, params=payload, headers=headers, allow_redirects=True)
            else:
                continue

            response_text = response.text

            # Eredmény elemzése a belepes.php válaszai alapján
            if "Túl sok sikertelen" in response_text or "túl sok" in response_text.lower():
                print(f"[!] [{name}] Nem sikerült a lekérdezés rate-limit / védelem miatt.")
            elif "A megadott usernév/jelszó párosítás nem megfelelő" in response_text:
                print(f"[+] [{name}] A fiók LÉTEZIK (A megadott e-mail regisztrálva van).")
            else:
                print(f"[?] [{name}] Ismeretlen válasz. HTTP Státusz: {response.status_code}")
                print(f"    Válasz szövege (részlet): {response.text[:300].strip().replace(chr(10), ' ')}")

        except requests.exceptions.RequestException as e:
            print(f"[!] Hálózati hiba történt a(z) {name} ellenőrzése közben: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python3 osint.py <email_cim>")
        sys.exit(1)
      
    target_email = sys.argv[1].strip()
    run_osint_check(target_email)
