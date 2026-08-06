import json
import requests

def load_config(config_path="loads.json"):
    """Betölti a célpontok konfigurációját a JSON fájlból."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Hiba: A(z) {config_path} fájl nem található.")
        return {"targets": []}
    except json.JSONDecodeError:
        print("[!] Hiba: Nem megfelelő JSON formátum a konfigurációs fájlban.")
        return {"targets": []}

def check_email_login(target, email):
    """
    Bejelentkezési kísérletet szimulál egy hamis jelszóval, 
    hogy e-mail küldés nélkül határozza meg a fiók létezését.
    """
    url = target.get("url")
    method = target.get("method", "POST").upper()
    
    # Adatok összeállítása
    payload = {
        target.get("email_field", "email"): email,
        target.get("password_field", "password"): target.get("dummy_password", "DummyPass123")
    }
    
    # Alapvető böngészős fejlécek a blokkolások elkerülésére
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "hu-HU,hu;q=0.9,en;q=0.8"
    }

    try:
        if method == "POST":
            response = requests.post(url, data=payload, headers=headers, timeout=10, allow_redirects=True)
        else:
            response = requests.get(url, params=payload, headers=headers, timeout=10, allow_redirects=True)
        
        body = response.text
        exists_kw = target.get("exists_keyword", "")
        not_exists_kw = target.get("not_exists_keyword", "")
        
        # Válasz elemzése kulcsszavak alapján
        if exists_kw and exists_kw in body:
            return {"status": "EXISTS", "details": f"A fiók létezik (Kulcsszó találat: '{exists_kw}')"}
        elif not_exists_kw and not_exists_kw in body:
            return {"status": "NOT_EXISTS", "details": f"A fiók nem létezik (Kulcsszó találat: '{not_exists_kw}')"}
        else:
            return {"status": "UNKNOWN", "details": f"Nem egyértelmű válasz. HTTP Státusz: {response.status_code}"}
            
    except requests.RequestException as e:
        return {"status": "ERROR", "details": f"Hálózati hiba: {str(e)}"}

def main():
    config = load_config()
    targets = config.get("targets", [])
    
    if not targets:
        print("[!] Nincsenek betöltött célpontok a konfigban.")
        return

    email_to_check = input("Add meg az ellenőrizendő e-mail címet: ").strip()
    print(f"\n[i] Vizsgálat indítása a következő címre: {email_to_check}\n" + "-"*50)

    for target in targets:
        print(f"[*] Célpont vizsgálata: {target.get('name', 'Ismeretlen')}...")
        result = check_email_login(target, email_to_check)
        
        # Eredmény színezett/kifejezett kiírása
        status = result['status']
        if status == "EXISTS":
            print(f"    [+] EREDMÉNY: LÉTEZIK -> {result['details']}")
        elif status == "NOT_EXISTS":
            print(f"    [-] EREDMÉNY: NINCS REGISZTRÁCIÓ -> {result['details']}")
        else:
            print(f"    [?] EREDMÉNY: {status} -> {result['details']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
