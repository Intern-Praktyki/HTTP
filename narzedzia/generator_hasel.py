# -*- coding: utf-8 -*-
"""
Narzędzie: Generator i audytor haseł.

Robi dwie proste, przydatne dla każdego rzeczy:
  1) generuje mocne, losowe hasło,
  2) ocenia, jak silne jest hasło, które już masz.

Działa w 100% offline -- nic nie wysyła do internetu.
Kod celowo prosty i obficie komentowany.
"""

# secrets -> losowanie BEZPIECZNE kryptograficznie (lepsze do haseł niż "random").
import secrets
# string -> gotowe zestawy znaków (litery, cyfry), żeby nie wypisywać ich ręcznie.
import string
# argparse -> obsługa argumentów w trybie CLI.
import argparse


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "hasla"
TYTUL = "Generator i audytor haseł"
OPIS = "Tworzy mocne hasła i ocenia, jak silne jest Twoje hasło."


# Krótka lista najpopularniejszych, łatwych do złamania haseł.
# Jeśli ktoś poda takie hasło -> od razu ostrzegamy. Trzymamy małymi literami.
NAJCZESTSZE_HASLA = {
    "123456", "123456789", "12345678", "111111", "000000", "qwerty",
    "password", "haslo", "admin", "iloveyou", "qwerty123", "zaq12wsx",
    "1q2w3e4r", "polska", "abc123", "qwerty1", "monkey", "dragon",
}


def generuj_haslo(dlugosc=16, uzyj_znakow_specjalnych=True):
    """
    Tworzy losowe hasło o zadanej długości.

    Używamy modułu secrets, bo jest bezpieczny kryptograficznie -- w odróżnieniu
    od zwykłego "random" nie da się przewidzieć, co wylosuje.
    """
    # Budujemy "pulę" znaków, z których losujemy.
    # ascii_letters to a-z i A-Z, digits to 0-9.
    pula = string.ascii_letters + string.digits
    if uzyj_znakow_specjalnych:
        # Dokładamy znaki specjalne, jeśli użytkownik ich chce.
        pula = pula + "!@#$%^&*()-_=+?"

    # secrets.choice losuje jeden bezpieczny znak; robimy to tyle razy, ile trzeba.
    # "".join(...) skleja pojedyncze znaki w jedno hasło.
    return "".join(secrets.choice(pula) for _ in range(dlugosc))


def ocen_haslo(haslo):
    """
    Ocenia siłę hasła w prosty sposób i zwraca słownik z wynikiem oraz
    listą podpowiedzi, co poprawić. Nie udajemy pełnego audytu -- to ma być
    zrozumiałe dla każdego.
    """
    uwagi = []   # tu zbieramy podpowiedzi dla użytkownika
    punkty = 0   # im więcej punktów, tym lepsze hasło

    # 1) Długość -- najważniejszy czynnik. Liczymy znaki funkcją len().
    if len(haslo) >= 12:
        punkty += 2
    elif len(haslo) >= 8:
        punkty += 1
        uwagi.append("Wydłuż hasło do co najmniej 12 znaków.")
    else:
        uwagi.append("Hasło jest za krótkie -- użyj co najmniej 12 znaków.")

    # 2) Różnorodność znaków. any(...) sprawdza, czy JAKIKOLWIEK znak spełnia warunek.
    if any(z.islower() for z in haslo):
        punkty += 1
    else:
        uwagi.append("Dodaj małe litery.")

    if any(z.isupper() for z in haslo):
        punkty += 1
    else:
        uwagi.append("Dodaj wielkie litery.")

    if any(z.isdigit() for z in haslo):
        punkty += 1
    else:
        uwagi.append("Dodaj cyfry.")

    # Znak specjalny = taki, który nie jest literą ani cyfrą.
    if any(not z.isalnum() for z in haslo):
        punkty += 1
    else:
        uwagi.append("Dodaj znak specjalny (np. ! ? # @).")

    # 3) Czy to jedno z najpopularniejszych haseł? To natychmiastowa czerwona flaga.
    if haslo.lower() in NAJCZESTSZE_HASLA:
        punkty = 0
        uwagi = ["To jedno z najczęściej używanych haseł -- zmień je natychmiast."]

    # Zamieniamy punkty na czytelną ocenę słowną.
    if punkty >= 5:
        ocena = "Mocne"
    elif punkty >= 3:
        ocena = "Średnie"
    else:
        ocena = "Słabe"

    return {"ocena": ocena, "punkty": punkty, "maks": 6, "uwagi": uwagi}


def _wypisz_ocene(haslo):
    """Wypisuje czytelnie wynik oceny hasła. Wspólne dla CLI i menu."""
    wynik = ocen_haslo(haslo)
    print("Ocena hasła: " + wynik["ocena"]
          + " (" + str(wynik["punkty"]) + "/" + str(wynik["maks"]) + ")")
    if wynik["uwagi"]:
        print("Co poprawić:")
        for uwaga in wynik["uwagi"]:
            print("  - " + uwaga)
    else:
        print("Świetnie -- to hasło wygląda solidnie!")


def uruchom_cli(argv):
    """
    Tryb CLI. Przykłady:
      python3 main.py hasla generuj
      python3 main.py hasla generuj --dlugosc 24 --bez-znakow
      python3 main.py hasla sprawdz "MojeHaslo123!"
    """
    parser = argparse.ArgumentParser(prog="main.py " + NAZWA, description=OPIS)
    # "akcja" decyduje, co robimy. choices ogranicza dozwolone wartości.
    parser.add_argument("akcja", choices=["generuj", "sprawdz"],
                        help="'generuj' tworzy hasło, 'sprawdz' ocenia podane hasło.")
    # nargs="?" -> ten argument jest opcjonalny (potrzebny tylko przy 'sprawdz').
    parser.add_argument("haslo", nargs="?",
                        help="Hasło do sprawdzenia (dla akcji 'sprawdz').")
    parser.add_argument("--dlugosc", type=int, default=16,
                        help="Długość generowanego hasła (domyślnie 16).")
    parser.add_argument("--bez-znakow", action="store_true",
                        help="Generuj bez znaków specjalnych (same litery i cyfry).")
    argumenty = parser.parse_args(argv)

    if argumenty.akcja == "generuj":
        haslo = generuj_haslo(argumenty.dlugosc, not argumenty.bez_znakow)
        print(haslo)
        return 0

    # Tutaj akcja == "sprawdz".
    if not argumenty.haslo:
        print("Podaj hasło do sprawdzenia, np.: main.py hasla sprawdz \"twoje-haslo\"")
        return 1
    _wypisz_ocene(argumenty.haslo)
    return 0


def uruchom_interaktywnie():
    """Tryb z menu głównego: pyta, czy wygenerować hasło, czy ocenić istniejące."""
    print("")
    print(TYTUL)
    print("  1) Wygeneruj mocne hasło")
    print("  2) Sprawdź siłę mojego hasła")
    wybor = input("Wybierz (1/2): ").strip()

    if wybor == "1":
        # Pytamy o długość; pusta odpowiedź -> używamy domyślnej 16.
        tekst = input("Długość hasła (Enter = 16): ").strip()
        dlugosc = int(tekst) if tekst.isdigit() else 16
        odp = input("Dodać znaki specjalne? (T/n): ").strip().lower()
        znaki = odp not in ("n", "nie", "no")
        print("\nTwoje nowe hasło:")
        print("  " + generuj_haslo(dlugosc, znaki))
        return 0

    if wybor == "2":
        haslo = input("Wpisz hasło do sprawdzenia: ")
        print("")
        _wypisz_ocene(haslo)
        return 0

    print("Nie rozpoznano wyboru.")
    return 1
