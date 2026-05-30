#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skaner nagłówków bezpieczeństwa HTTP.

Narzędzie CLI, które pobiera nagłówki HTTP wskazanych stron i sprawdza,
czy obecne są kluczowe nagłówki bezpieczeństwa. Wypisuje czytelny raport
oraz wynik punktowy. Obsługuje też tryb --json dla automatyzacji.

Autor portfolio AI Security. Kod celowo prosty i obficie komentowany.
"""

# argparse -> czytanie argumentów z linii poleceń (adresy stron, opcja --json)
import argparse
# json -> zamiana wyniku na format JSON, gdy użytkownik poda --json
import json
# sys -> wyjście z programu z odpowiednim kodem zakończenia (przydatne w CI/CD)
import sys

# requests -> jedyna zewnętrzna zależność; służy do wysłania zapytania HTTP
import requests


# Słownik opisujący nagłówki bezpieczeństwa, które sprawdzamy.
# Klucz to nazwa nagłówka, a wartość to krótkie wyjaśnienie "po co on jest".
# Trzymamy to w jednym miejscu, żeby łatwo było dodać kolejny nagłówek.
SECURITY_HEADERS = {
    "Content-Security-Policy":
        "Ogranicza skąd ładują się skrypty/style i utrudnia ataki XSS.",
    "Strict-Transport-Security":
        "Wymusza połączenie przez HTTPS i chroni przed podsłuchem.",
    "X-Frame-Options":
        "Blokuje osadzanie strony w ramce (ochrona przed clickjackingiem).",
    "X-Content-Type-Options":
        "Wyłącza zgadywanie typu pliku przez przeglądarkę (MIME sniffing).",
    "Referrer-Policy":
        "Kontroluje ile informacji o adresie wysyłamy przy przejściu dalej.",
    "Permissions-Policy":
        "Ogranicza dostęp strony do funkcji takich jak kamera czy mikrofon.",
}


def sprawdz_slabe_konfiguracje(nazwa, wartosc):
    """
    Zwraca krótkie ostrzeżenie (tekst) jeśli nagłówek jest obecny,
    ale skonfigurowany słabo. Jeśli wszystko jest w porządku -> zwraca None.

    Sprawdzamy tylko proste, oczywiste przypadki -- nie udajemy pełnego audytu.
    """
    # Porównujemy małymi literami, bo nazwy/wartości nagłówków bywają różne.
    nazwa = nazwa.lower()
    wartosc_lower = wartosc.lower()

    # HSTS bez "max-age" praktycznie nie działa -> to typowy błąd konfiguracji.
    if nazwa == "strict-transport-security" and "max-age" not in wartosc_lower:
        return "brak parametru max-age (HSTS bez max-age nie działa)"

    # X-Content-Type-Options powinno mieć wartość "nosniff", inaczej nie chroni.
    if nazwa == "x-content-type-options" and "nosniff" not in wartosc_lower:
        return "oczekiwano wartości 'nosniff'"

    # X-Frame-Options ma sens tylko z wartością DENY lub SAMEORIGIN.
    if nazwa == "x-frame-options" and wartosc_lower not in ("deny", "sameorigin"):
        return "zalecane DENY lub SAMEORIGIN"

    # Brak ostrzeżeń -> zwracamy None.
    return None


def przygotuj_url(adres):
    """
    Dodaje "https://" jeśli użytkownik podał adres bez schematu.
    Dzięki temu można wpisać po prostu "example.com" zamiast pełnego URL.
    """
    # startswith sprawdza początek tekstu; jeśli już jest schemat -> nie ruszamy.
    if adres.startswith("http://") or adres.startswith("https://"):
        return adres
    # Domyślnie zakładamy HTTPS, bo strona bezpieczna powinna używać HTTPS.
    return "https://" + adres


def skanuj_strone(adres, timeout):
    """
    Pobiera nagłówki jednej strony i buduje słownik z wynikami.

    Zwraca słownik (dict), żeby ten sam wynik dało się wypisać jako tekst
    albo zamienić na JSON. Wszystkie błędy łapiemy tutaj, aby program
    nie przerywał działania przy jednej niedziałającej stronie.
    """
    url = przygotuj_url(adres)

    # Szkielet wyniku -- wypełnimy go poniżej. Trzymanie stałej struktury
    # ułatwia późniejsze wypisywanie i konwersję do JSON.
    wynik = {
        "url": url,
        "error": None,         # tu trafi opis błędu, jeśli coś pójdzie nie tak
        "status_code": None,   # kod odpowiedzi HTTP (np. 200)
        "obecne": [],          # lista znalezionych nagłówków bezpieczeństwa
        "brakujace": [],       # lista brakujących nagłówków
        "ostrzezenia": {},     # słabe konfiguracje: nazwa -> opis problemu
        "wynik": 0,            # ile nagłówków obecnych
        "maks": len(SECURITY_HEADERS),  # ile sprawdzamy łącznie
    }

    try:
        # WAŻNE (bezpieczeństwo): pytamy WYŁĄCZNIE o adres podany przez użytkownika.
        # timeout zapobiega zawieszeniu programu na wolnym/niedziałającym serwerze.
        # allow_redirects=True -> idziemy za przekierowaniem (np. http -> https).
        odpowiedz = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            # User-Agent ustawiamy uczciwie, żeby było widać, że to skaner.
            headers={"User-Agent": "HTTP-Security-Header-Scanner/1.0"},
        )
    except requests.exceptions.Timeout:
        # Serwer nie odpowiedział w wyznaczonym czasie.
        wynik["error"] = "przekroczono czas oczekiwania (timeout)"
        return wynik
    except requests.exceptions.ConnectionError:
        # Nie udało się w ogóle połączyć (zła domena, brak sieci itp.).
        wynik["error"] = "błąd połączenia (sprawdź adres lub sieć)"
        return wynik
    except requests.exceptions.RequestException as blad:
        # Każdy inny błąd biblioteki requests łapiemy tutaj jako ostatnią deskę ratunku.
        wynik["error"] = "błąd zapytania: " + str(blad)
        return wynik

    # Jeśli doszliśmy tutaj -> mamy odpowiedź. Zapisujemy kod statusu.
    wynik["status_code"] = odpowiedz.status_code

    # odpowiedz.headers działa jak słownik niewrażliwy na wielkość liter,
    # więc możemy bezpiecznie pytać o "Content-Security-Policy" itd.
    for nazwa_naglowka, opis in SECURITY_HEADERS.items():
        if nazwa_naglowka in odpowiedz.headers:
            # Nagłówek istnieje -> dopisujemy do obecnych i liczymy punkt.
            wynik["obecne"].append(nazwa_naglowka)
            # Sprawdzamy, czy mimo obecności konfiguracja nie jest słaba.
            ostrzezenie = sprawdz_slabe_konfiguracje(
                nazwa_naglowka, odpowiedz.headers[nazwa_naglowka]
            )
            if ostrzezenie:
                wynik["ostrzezenia"][nazwa_naglowka] = ostrzezenie
        else:
            # Nagłówka brak -> dopisujemy do brakujących.
            wynik["brakujace"].append(nazwa_naglowka)

    # Wynik punktowy = liczba obecnych nagłówków.
    wynik["wynik"] = len(wynik["obecne"])
    return wynik


def wypisz_raport_tekstowy(wynik):
    """
    Wypisuje czytelny raport tekstowy dla pojedynczej strony.
    """
    print("=" * 60)
    print("Strona: " + wynik["url"])

    # Jeśli był błąd -> informujemy o nim i kończymy raport dla tej strony.
    if wynik["error"]:
        print("  [BŁĄD] " + wynik["error"])
        print("=" * 60)
        return

    print("Kod odpowiedzi HTTP: " + str(wynik["status_code"]))
    print("")

    # Najpierw nagłówki obecne -- z krótkim opisem, po co służą.
    print("Obecne nagłówki bezpieczeństwa:")
    if wynik["obecne"]:
        for nazwa in wynik["obecne"]:
            print("  [+] " + nazwa)
            print("      " + SECURITY_HEADERS[nazwa])
            # Jeśli dla tego nagłówka mamy ostrzeżenie -> pokazujemy je.
            if nazwa in wynik["ostrzezenia"]:
                print("      UWAGA: " + wynik["ostrzezenia"][nazwa])
    else:
        print("  (żaden)")

    print("")

    # Następnie nagłówki brakujące.
    print("Brakujące nagłówki bezpieczeństwa:")
    if wynik["brakujace"]:
        for nazwa in wynik["brakujace"]:
            print("  [-] " + nazwa)
            print("      " + SECURITY_HEADERS[nazwa])
    else:
        print("  (żaden -- wszystkie obecne!)")

    print("")
    # Wynik punktowy w formacie np. 4/6.
    print("Wynik: " + str(wynik["wynik"]) + "/" + str(wynik["maks"]))
    print("=" * 60)


def main():
    """
    Punkt wejścia programu: czyta argumenty i uruchamia skanowanie.
    """
    # Konfiguracja parsera argumentów -- opisy pojawią się przy --help.
    parser = argparse.ArgumentParser(
        description="Skaner nagłówków bezpieczeństwa HTTP."
    )
    # nargs="+" -> wymaga przynajmniej jednego adresu, ale pozwala podać więcej.
    parser.add_argument(
        "adresy",
        nargs="+",
        help="Jeden lub więcej adresów stron do sprawdzenia (np. example.com).",
    )
    # Opcjonalna flaga --json przełącza wyjście na format JSON.
    parser.add_argument(
        "--json",
        action="store_true",
        help="Wypisz wynik w formacie JSON (dla automatyzacji).",
    )
    # Opcjonalny timeout w sekundach; domyślnie 10 -- rozsądny kompromis.
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Limit czasu na odpowiedź serwera w sekundach (domyślnie 10).",
    )
    argumenty = parser.parse_args()

    # Skanujemy każdy adres po kolei i zbieramy wyniki na liście.
    wszystkie_wyniki = []
    for adres in argumenty.adresy:
        wszystkie_wyniki.append(skanuj_strone(adres, argumenty.timeout))

    if argumenty.json:
        # Tryb JSON: jeden czytelny obiekt z całą listą wyników.
        # ensure_ascii=False -> polskie znaki zostają czytelne, nie jako \uXXXX.
        # indent=2 -> ładne wcięcia, łatwiej czytać i parsować.
        print(json.dumps(wszystkie_wyniki, ensure_ascii=False, indent=2))
    else:
        # Tryb tekstowy: czytelny raport dla człowieka.
        for wynik in wszystkie_wyniki:
            wypisz_raport_tekstowy(wynik)

    # Kod wyjścia: 1, jeśli którakolwiek strona zwróciła błąd połączenia.
    # Dzięki temu narzędzie dobrze współpracuje z pipeline'ami CI/CD.
    byl_blad = any(w["error"] for w in wszystkie_wyniki)
    sys.exit(1 if byl_blad else 0)


# Standardowy "strażnik" Pythona: uruchamia main() tylko gdy plik
# jest odpalany bezpośrednio, a nie importowany jako moduł.
if __name__ == "__main__":
    main()
