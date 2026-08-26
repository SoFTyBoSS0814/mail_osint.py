import json

def adatgyujto():
    print("--- Személyes Adatgyűjtő Szkript ---")
    print("Kérlek add meg a kért adatokat (ha valamelyik nincs, hagyd üresen és nyomj Entert):\n")

    adatok = {
        "Neve": input("Neve: ").strip(),
        "Kora": input("Kora: ").strip(),
        "Indok": input("Indok: ").strip(),
        "Mail": input("Mail: ").strip(),
        "Lakcim": input("Lakcim: ").strip(),
        "Telefonszam": input("Telefonszam: ").strip(),
        "Facebook": input("Facebook: ").strip(),
        "Instagram": input("Instagram: ").strip(),
        "Snapchat": input("Snapchat: ").strip(),
        "Tiktok": input("Tiktok: ").strip(),
        "Anyja neve": input("Anyja neve: ").strip(),
        "Apja neve": input("Apja neve: ").strip(),
        "Lánytestvér Neve": input("Lánytestvér Neve: ").strip(),
        "Fiútestvér Neve": input("Fiútestvér Neve: ").strip(),
        "Nagymama Neve": input("Nagymama Neve: ").strip(),
        "Nagypapa Neve": input("Nagypapa Neve: ").strip(),
        "Anyja Facebook Fiókja": input("Anyja Facebook Fiókja: ").strip(),
        "Apja facebook fiókja": input("Apja facebook fiókja: ").strip(),
        "anyja telefonszáma": input("anyja telefonszáma: ").strip(),
        "apja telefonszáma": input("apja telefonszáma: ").strip(),
        "testvére facebook fiókja": input("testvére facebook fiókja: ").strip(),
    }

    # Mentés JSON fájlba
    fajlnev = "profil.json"
    with open(fajlnev, "w", encoding="utf-8") as f:
        json.dump(adatok, f, ensure_ascii=False, indent=4)

    print(f"\n[+] Az adatok sikeresen elmentve a(z) '{fajlnev}' fájlba!")

if __name__ == "__main__":
    adatgyujto()
