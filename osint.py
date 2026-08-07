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
        check_type = item.get("check_type", "keyword")
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        parsed_url = urlparse(url)
        domain = parsed_url.hostname
        raw_data = item.get("data", {})

        try:
            session = requests.Session()
            site_cookies = all_cookies.get(name, {})
            for cookie_name, cookie_value in site_cookies.items():
                session.cookies.set(cookie_name, cookie_value, domain=domain)

            extracted_tokens = {}
            if pre_get_url:
                pre_resp = session.get(pre_get_url, headers=headers)
                for match in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', pre_resp.text):
                    tag = match.group(0)
                    name_match = re.search(r'name=["\']([^"\']+)["\']', tag)
                    val_match = re.search(r'value=["\']([^"\']*)["\']', tag)
                    if name_match:
                        val = val_match.group(1) if val_match else ""
                        extracted_tokens[name_match.group(1)] = val

            payload = {}
            for key, value in raw_data.items():
                if key in extracted_tokens and (value == "" or value is None):
                    payload[key] = extracted_tokens[key]
                elif isinstance(value, str):
                    payload[key] = value.replace("{email}", email_to_check)
                else:
                    payload[key] = value
            
            for tk, tv in extracted_tokens.items():
                if tk not in payload:
                    payload[tk] = tv

            if method == "POST":
                response = session.post(url, data=payload, headers=headers)
            else:
                response = session.get(url, params=payload, headers=headers)

            response_text = response.text

            # Ellenőrzési logika
            if "Túl sok sikertelen" in response_text or "túl sok" in response_text.lower():
                print(f"[!] [{name}] Rate-limit / túl sok kérés észlelve!")
            elif check_type == "keyword":
                keyword = item.get("keyword", "")
                if keyword and keyword in response_text:
                    print(f"[+] [{name}] A fiók LÉTEZIK (A kulcsszó megtalálható: '{keyword}').")
                else:
                    print(f"[-] [{name}] A fiók NEM LÉTEZIK (A kulcsszó nem található).")
            elif check_type == "not_found_keyword":
                not_found_kw = item.get("not_found_keyword", "")
                if not_found_kw and not_found_kw in response_text:
                    print(f"[-] [{name}] A fiók NEM LÉTEZIK (A szerver szerint nincs ilyen e-mail).")
                else:
                    print(f"[+] [{name}] A fiók LÉTEZIK (A hibaüzenet nem jelentkezett).")
            else:
                print(f"[?] [{name}] Ismeretlen check_type: {check_type}")

        except requests.exceptions.RequestException:
            print(f"[!] Hálózati hiba történt a(z) {name} ellenőrzése közben.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python3 osint.py <email_cim>")
        sys.exit(1)
      
    target_email = sys.argv[1].strip()
    run_osint_check(target_email)
