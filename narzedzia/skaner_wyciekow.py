# -*- coding: utf-8 -*-
"""
Narzędzie: Detektyw haseł (sprawdzanie wycieków).

Sprawdza, czy podane hasło pojawiło się w znanych wyciekach danych --
korzystając z oficjalnego, darmowego API "Have I Been Pwned: Pwned Passwords".

PRYWATNOŚĆ (bardzo ważne):
  Używamy modelu k-anonimowości. Liczymy skrót SHA-1 hasła, ale do serwera
  wysyłamy TYLKO jego 5 pierwszych znaków. Pełne hasło ani pełny skrót NIGDY
  nie opuszczają Twojego komputera. Serwer odsyła listę pasujących końcówek,
  a porównania dokonujemy lokalnie.

Kod celowo prosty i obficie komentowany.
"""

# hashlib -> liczenie skrótu SHA-1 hasła (lokalnie, na naszym komputerze).
import hashlib
# getpass -> bezpieczne wczytanie hasła (nie pokazuje go na ekranie podczas pisania).
import getpass
# argparse -> obsługa argumentów w trybie CLI.
import argparse

# requests -> jedyna zewnętrzna zależność; tutaj odpytujemy publiczne API.
import requests


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "wycieki"
TYTUL = "Detektyw haseł (sprawdzanie wycieków)"
OPIS = "Sprawdza, czy hasło wyciekło, nie wysyłając go (model k-anonimowości)."

# Adres oficjalnego, darmowego API. Doklejamy do niego 5 znaków skrótu.
API_URL = "https://api.pwnedpasswords.com/range/"


def sprawdz_haslo(haslo, timeout=10):
    """
    Zwraca liczbę wystąpień hasła w wyciekach (0 = nie znaleziono).
    Może rzucić wyjątek requests, jeśli nie uda się połączyć -- łapiemy go wyżej.
    """
    # 1) Liczymy skrót SHA-1 hasła i zapisujemy go WIELKIMI literami
    #    (API zwraca końcówki wielkimi literami, więc ujednolicamy).
    skrot = hashlib.sha1(haslo.encode("utf-8")).hexdigest().upper()

    # 2) Dzielimy skrót na 5-znakowy prefiks i resztę (suffix).
    #    Do serwera wyślemy WYŁĄCZNIE prefiks -- to jest właśnie k-anonimowość.
    prefiks = skrot[:5]
    reszta = skrot[5:]

    # 3) Pytamy serwer o wszystkie końcówki skrótów pasujące do tego prefiksu.
    odpowiedz = requests.get(
        API_URL + prefiks,
        timeout=timeout,
        headers={"User-Agent": "Przybornik-Detektyw-Hasel/1.0"},
    )
    # raise_for_status zgłosi błąd, jeśli serwer zwróci kod błędu (np. 500).
    odpowiedz.raise_for_status()

    # 4) Odpowiedź to wiele linii w formacie "KONCOWKA:ILE_RAZY".
    #    Szukamy naszej końcówki i odczytujemy liczbę wystąpień.
    for linia in odpowiedz.text.splitlines():
        koncowka, _, ile = linia.partition(":")
        if koncowka == reszta:
            return int(ile)

    # Jeśli nie znaleziono naszej końcówki -> hasła nie ma w bazie wycieków.
    return 0


def _sprawdz_i_wypisz(haslo):
    """Wspólna logika dla CLI i menu: sprawdza hasło i wypisuje czytelny wynik."""
    # Pusty wpis nie ma sensu sprawdzać.
    if not haslo:
        print("Nie podano hasła.")
        return 1

    try:
        ile = sprawdz_haslo(haslo)
    except requests.exceptions.Timeout:
        print("Przekroczono czas oczekiwania (timeout). Spróbuj ponownie.")
        return 1
    except requests.exceptions.ConnectionError:
        print("Błąd połączenia -- sprawdź internet.")
        return 1
    except requests.exceptions.RequestException as blad:
        print("Błąd zapytania: " + str(blad))
        return 1

    print("")
    if ile > 0:
        # Liczbę formatujemy ze spacjami co tysiąc dla czytelności, np. 12 345.
        print("UWAGA: to hasło pojawiło się w wyciekach " + format(ile, ",d").replace(",", " ") + " razy!")
        print("Nie używaj go nigdzie. Jeśli go używasz -- zmień je jak najszybciej.")
    else:
        print("Dobra wiadomość: tego hasła nie ma w znanych wyciekach.")
        print("(To nie gwarantuje, że jest mocne -- sprawdź je w narzędziu 'hasla'.)")
    return 0


def uruchom_cli(argv):
    """
    Tryb CLI. Dla bezpieczeństwa hasło wczytujemy ukrytym wpisem (nie z argumentów),
    żeby nie zapisało się w historii terminala.
      python3 main.py wycieki
    """
    # Parsujemy argumenty głównie po to, by działało --help; hasła nie bierzemy stąd.
    argparse.ArgumentParser(prog="main.py " + NAZWA, description=OPIS).parse_args(argv)
    print(TYTUL)
    print("Hasło nie jest pokazywane podczas pisania i nie opuszcza komputera.")
    # getpass ukrywa wpisywane znaki -- nikt nie podejrzy hasła zza pleców.
    haslo = getpass.getpass("Wpisz hasło do sprawdzenia: ")
    return _sprawdz_i_wypisz(haslo)


def uruchom_interaktywnie():
    """Tryb z menu głównego: bezpieczne wczytanie hasła i sprawdzenie."""
    print("")
    print(TYTUL)
    print("Hasło nie jest pokazywane podczas pisania i nie opuszcza komputera.")
    haslo = getpass.getpass("Wpisz hasło do sprawdzenia: ")
    return _sprawdz_i_wypisz(haslo)
