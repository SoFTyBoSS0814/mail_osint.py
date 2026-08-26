import json

def adatgyujto():
    print("--- Скрипт сбора личных данных ---")
    print("Пожалуйста, введите запрашиваемые данные (если каких-то нет, оставьте поле пустым и нажмите Enter):\n")

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

    print(f"\n[+] Данные успешно сохранены в файл '{fajlnev}'!")

if __name__ == "__main__":
    adatgyujto()
