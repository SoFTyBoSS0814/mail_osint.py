import json
import sys
import requests
import re
import random
from urllib.parse import urlparse, urljoin

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
        pre_get_url = item.get("pre_get_url")
        fallback_url = item.get("url")
        method = item.get("method", "POST").upper()
        check_type = item.get("check_type", "keyword")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://moly.hu",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        }

        parsed_url = urlparse(pre_get_url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        raw_data = item.get("data", {})

        try:
            session = requests.Session()
            site_cookies = all_cookies.get(name, {})
            for cookie_name, cookie_value in site_cookies.items():
                session.cookies.set(cookie_name, cookie_value, domain=parsed_url.hostname)

            extracted_tokens = {}
            target_post_url = fallback_url

            if pre_get_url:
                headers["Referer"] = pre_get_url
                pre_resp = session.get(pre_get_url, headers=headers)
                
                forms = re.findall(r'(<form.*?</form>)', pre_resp.text, re.DOTALL | re.IGNORECASE)
                for form_html in forms:
                    if 'user[email]' in form_html or 'user[login]' in form_html:
                        action_match = re.search(r'action=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
                        if action_match:
                            action_path = action_match.group(1)
                            target_post_url = urljoin(domain, action_path)
                            break

                token_match = re.search(r'name=["\']authenticity_token["\'][^>]*value=["\']([^"\']+)["\']', pre_resp.text, re.IGNORECASE)
                if not token_match:
                    token_match = re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']authenticity_token["\']', pre_resp.text, re.IGNORECASE)
                
                if token_match:
                    extracted_tokens["authenticity_token"] = token_match.group(1)
                
                meta_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', pre_resp.text)
                if meta_match and "authenticity_token" not in extracted_tokens:
                    extracted_tokens["authenticity_token"] = meta_match.group(1)

            headers["Referer"] = pre_get_url

            # Egyedi véletlenszám generálása ehhez a futtatáshoz
            rand_suffix = str(random.randint(100000, 999999))

            payload = {}
            for key, value in raw_data.items():
                if key in extracted_tokens and (value == "" or value is None):
                    payload[key] = extracted_tokens[key]
                elif isinstance(value, str):
                    val = value.replace("{email}", email_to_check)
                    val = val.replace("{random}", rand_suffix)
                    payload[key] = val
                else:
                    payload[key] = value
            
            for tk, tv in extracted_tokens.items():
                if tk not in payload:
                    payload[tk] = tv

            if method == "POST":
                response = session.post(target_post_url, data=payload, headers=headers)
            else:
                response = session.get(target_post_url, params=payload, headers=headers)

            response_text = response.text

            print(f"[DEBUG] [{name}] Végleges POST URL: {target_post_url} | HTTP Státusz: {response.status_code}")

            if "Túl sok sikertelen" in response_text or "túl sok" in response_text.lower():
                print(f"[!] [{name}] Rate-limit / túl sok kérés észlelve!")
            elif check_type == "keyword":
                keyword = item.get("keyword", "")
                if keyword and keyword in response_text:
                    print(f"[+] [{name}] A fiók LÉTEZIK (A kulcsszó megtalálható: '{keyword}').")
                else:
                    print(f"[-] [{name}] A fiók NEM LÉTEZIK (A kulcsszó nem található).")
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
