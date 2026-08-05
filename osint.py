import requests
import sys
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def evaluate_rule(response, rule):
    """
    Dinamikusan kiértékeli a JSON-ben megadott szabályt a válaszra.
    """
    rule_type = rule.get("type")
    
    if rule_type == "status_and_text":
        expected_status = rule.get("status", 200)
        contains_text = rule.get("contains", "")
        return response.status_code == expected_status and contains_text in response.text
        
    elif rule_type == "status_only":
        return response.status_code == rule.get("status", 200)
        
    return False

def check_target(target, email):
    # Dinamikusan behelyettesítjük az e-mail címet a data mezőkbe
    url = target["url"]
    method = target["method"].upper()
    headers = target["headers"]
    
    # Adatok előkészítése (ha a data egy dictionary, átalakítjuk sztringgé a helyettesítéshez, majd vissza)
    data_str = json.dumps(target["data"]).replace("{email}", email)
    data = json.loads(data_str)

    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'GET':
            response = requests.get(url, headers=headers, params=data, timeout=10)
        else:
            return "UNKNOWN", "Nem támogatott HTTP metódus"

        if evaluate_rule(response, target["rule"]):
            return "FOUND", f"Regisztrálva / Létezik (Status: {response.status_code})"
        else:
            return "NOT_FOUND", f"Nincs regisztrálva (Status: {response.status_code})"

    except requests.exceptions.RequestException as e:
        return "ERROR", f"Hálózati hiba: {str(e)}"

def run_email_check(email, config_file="loads.json"):
    print(f"\n{Colors.BOLD}[*] E-mail cím vizsgálata: {email}{Colors.RESET}\n")
    print("-" * 50)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            targets = json.load(f)
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Hiba: A(z) {config_file} fájl nem található!{Colors.RESET}")
        return

    for target in targets:
        status, message = check_target(target, email)
        name = target["name"]

        if status == "FOUND":
            print(f"[{Colors.GREEN}+{Colors.RESET}] {name}: {Colors.GREEN}{message}{Colors.RESET}")
        elif status == "NOT_FOUND":
            print(f"[{Colors.RED}-{Colors.RESET}] {name}: {Colors.YELLOW}{message}{Colors.RESET}")
        else:
            print(f"[{Colors.BOLD}?{Colors.RESET}] {name}: {message}")

    print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Használat: python {sys.argv[0]} <email_cim>")
        sys.exit(1)

    target_email = sys.argv[1]
    run_email_check(target_email)
