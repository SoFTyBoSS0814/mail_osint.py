import json
import sys
import requests
import re
from urllib.parse import urlparse

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
        
    for item in config_list:
        name = item.get("name")
        url = item.get("url")
        method = item.get("method", "POST").upper()
        headers = item.get("headers", {})
        pre_get_url = item.get("pre_get_url")
        check_type = item.get("check_type", "baseline")
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        parsed_url = urlparse(url)
        domain = parsed_url.hostname
        raw_data = item.get("data", {})

        # Segédfüggvény, ami minden egyes híváshoz új sessiont indít és lekéri a friss tokent
        def make_request(email_val):
            session = requests.Session()
            site_cookies = all_cookies.get(name, {})
            for cookie_name, cookie_value in site_cookies.items():
                session.cookies.set(cookie_name, cookie_value, domain=domain)

            extracted_tokens = {}
            if pre_get_url:
                try:
                    pre_resp = session.get(pre_get_url, headers=headers)
                    for match in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', pre_resp.text):
                        tag = match.group(0)
                        name_match = re.search(r'name=["\']([^"\']+)["\']', tag)
                        val_match = re.search(r'value=["\']([^"\']*)["\']', tag)
                        if name_match:
                            val = val_match.group(1) if val_match else ""
                            extracted_tokens[name_match.group(1)] = val
                except Exception:
                    pass

            payload = {}
            for key, value in raw_data.items():
                if key in extracted_tokens and (value == "" or value is None):
                    payload[key] = extracted_tokens[key]
                elif isinstance(value, str):
                    payload[key] = value.replace("{email}", email_val)
                else:
                    payload[key] = value
            
            for tk, tv in extracted_tokens.items():
                if tk not in payload:
                    payload[tk] = tv

            if method == "POST":
                return session.post(url, data=payload, headers=headers)
            else:
                return session.get(url, params=payload, headers=headers)

        try:
            if check_type == "baseline":
                # 1. Fiktív kérés teljesen friss, független sessionnel és tokennel
                fake_email = "nonexistent_test_account_9988776655@gmail.com"
                fake_response = make_request(fake_email)

                # 2. Valódi kérés szintén külön, friss sessionnel és tokennel
                target_response = make_request(email_to_check)

                resp_text = target_response.text

                if "Túl sok sikertelen" in resp_text or "túl sok" in resp_text.lower():
                    print(f"[!] [{name}] Rate-limit / túl sok kérés észlelve!")
                elif fake_response.text == target_response.text:
                    print(f"[-] [{name}] A válasz megegyezik a fiktív címmel -> A fiók NEM LÉTEZIK.")
                else:
                    print(f"[+] [{name}] Eltérő válasz a fiktívhez képest -> A fiók LÉTEZIK (vagy eltérő státusz).")

            elif check_type == "keyword":
                response = make_request(email_to_check)
                response_text = response.text
                keyword = item.get("keyword", "")
                if keyword and keyword in response_text:
                    print(f"[+] [{name}] Kulcsszó megtalálva: '{keyword}'")
                else:
                    print(f"[-] [{name}] Nincs találat vagy eltérő válasz.")

        except requests.exceptions.RequestException:
            print(f"[!] Hálózati hiba történt a(z) {name} ellenőrzése közben.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python3 osint.py <email_cim>")
        sys.exit(1)
      
    target_email = sys.argv[1].strip()
    run_osint_check(target_email)
