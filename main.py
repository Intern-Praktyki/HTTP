#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu główne -- jeden punkt wejścia do wszystkich narzędzi.

Sposoby uruchomienia:
  python3 main.py
      -> uruchamia interaktywne menu w terminalu.

  python3 main.py <nazwa-narzedzia> [argumenty...]
      -> uruchamia konkretne narzędzie od razu (tryb CLI / automatyzacja),
         np.:  python3 main.py skaner-naglowkow example.com --json

  python3 main.py --list
      -> wypisuje listę dostępnych narzędzi.

Każde narzędzie to osobny plik w folderze "narzedzia/". Menu wykrywa je
automatycznie, więc dodanie nowego narzędzia NIE wymaga zmian w tym pliku.
"""

# sys -> argumenty z linii poleceń i kod wyjścia programu
import sys
# importlib -> wczytywanie modułów narzędzi po nazwie (dynamicznie)
import importlib
# pkgutil -> przeglądanie, jakie moduły są w pakiecie "narzedzia"
import pkgutil

# Importujemy nasz pakiet z narzędziami, żeby poznać jego lokalizację na dysku.
import narzedzia


def znajdz_narzedzia():
    """
    Automatycznie wykrywa wszystkie narzędzia w folderze "narzedzia/".

    Za narzędzie uznajemy moduł, który ma wymagane "metadane" (NAZWA, TYTUL)
    oraz funkcje uruchom_cli i uruchom_interaktywnie. Dzięki temu zwykłe pliki
    pomocnicze (np. __init__.py) zostaną pominięte.
    """
    znalezione = []

    # pkgutil.iter_modules przegląda pliki w folderze pakietu "narzedzia".
    for info_modulu in pkgutil.iter_modules(narzedzia.__path__):
        # Wczytujemy moduł po pełnej nazwie, np. "narzedzia.skaner_naglowkow".
        modul = importlib.import_module("narzedzia." + info_modulu.name)

        # Sprawdzamy, czy moduł ma wszystko, czego potrzebuje narzędzie.
        # hasattr zwraca True, jeśli dana nazwa istnieje w module.
        ma_metadane = hasattr(modul, "NAZWA") and hasattr(modul, "TYTUL")
        ma_funkcje = (
            hasattr(modul, "uruchom_cli")
            and hasattr(modul, "uruchom_interaktywnie")
        )
        if ma_metadane and ma_funkcje:
            znalezione.append(modul)

    # Sortujemy po tytule, żeby kolejność w menu była zawsze taka sama.
    znalezione.sort(key=lambda m: m.TYTUL)
    return znalezione


def wypisz_liste(lista_narzedzi):
    """Wypisuje dostępne narzędzia wraz z nazwą do użycia w CLI."""
    print("Dostępne narzędzia:")
    for modul in lista_narzedzi:
        # Pokazujemy ładny tytuł oraz nazwę-identyfikator do wpisania w CLI.
        print("  - " + modul.TYTUL)
        print("      nazwa CLI: " + modul.NAZWA)
        print("      " + modul.OPIS)


def menu_interaktywne(lista_narzedzi):
    """
    Pętla interaktywnego menu w terminalu. Pokazuje numerowaną listę narzędzi,
    czeka na wybór użytkownika i uruchamia wybrane narzędzie.
    """
    # Jeśli nie ma żadnych narzędzi, nie ma sensu pokazywać menu.
    if not lista_narzedzi:
        print("Brak dostępnych narzędzi w folderze 'narzedzia/'.")
        return 1

    # Pętla działa, dopóki użytkownik nie wybierze opcji wyjścia.
    while True:
        print("")
        print("=" * 60)
        print("  PRZYBORNIK AI SECURITY -- menu główne")
        print("=" * 60)

        # enumerate(..., start=1) numeruje narzędzia od 1 dla wygody użytkownika.
        for numer, modul in enumerate(lista_narzedzi, start=1):
            print("  " + str(numer) + ") " + modul.TYTUL)
        print("  0) Wyjście")
        print("")

        # Pobieramy wybór. .strip() usuwa przypadkowe spacje.
        wybor = input("Wybierz narzędzie (numer): ").strip()

        # Opcje wyjścia: 0 lub litera q (od "quit").
        if wybor in ("0", "q", "Q"):
            print("Do zobaczenia!")
            return 0

        # Sprawdzamy, czy wpisano liczbę. isdigit() jest proste i czytelne.
        if not wybor.isdigit():
            print("To nie jest numer z listy. Spróbuj ponownie.")
            continue

        indeks = int(wybor)
        # Sprawdzamy, czy numer mieści się w zakresie listy.
        if indeks < 1 or indeks > len(lista_narzedzi):
            print("Nie ma narzędzia o takim numerze. Spróbuj ponownie.")
            continue

        # Lista jest liczona od 0, a menu od 1 -> odejmujemy 1.
        wybrane = lista_narzedzi[indeks - 1]
        # Uruchamiamy wybrane narzędzie w trybie interaktywnym.
        wybrane.uruchom_interaktywnie()

        # Po zakończeniu czekamy na Enter, żeby użytkownik zdążył przeczytać wynik.
        input("\nNaciśnij Enter, aby wrócić do menu...")


def main():
    """Punkt wejścia: decyduje między trybem CLI a interaktywnym menu."""
    lista_narzedzi = znajdz_narzedzia()

    # sys.argv[0] to nazwa programu; argumenty użytkownika zaczynają się od [1].
    argumenty = sys.argv[1:]

    # Brak argumentów -> uruchamiamy interaktywne menu.
    if not argumenty:
        return menu_interaktywne(lista_narzedzi)

    pierwszy = argumenty[0]

    # Obsługa flag pomocniczych.
    if pierwszy in ("-h", "--help"):
        print(__doc__)  # __doc__ to opis na górze tego pliku
        wypisz_liste(lista_narzedzi)
        return 0
    if pierwszy in ("-l", "--list"):
        wypisz_liste(lista_narzedzi)
        return 0

    # W przeciwnym razie pierwszy argument to nazwa narzędzia.
    for modul in lista_narzedzi:
        if modul.NAZWA == pierwszy:
            # Resztę argumentów przekazujemy do narzędzia (np. adresy, --json).
            return modul.uruchom_cli(argumenty[1:])

    # Nie znaleziono narzędzia o podanej nazwie -> podpowiadamy listę.
    print("Nieznane narzędzie: " + pierwszy)
    print("")
    wypisz_liste(lista_narzedzi)
    return 1


# Standardowy "strażnik" Pythona: uruchamia main() tylko gdy plik
# jest odpalany bezpośrednio, a nie importowany jako moduł.
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # Łapiemy Ctrl+C, żeby program kończył się czysto, bez brzydkiego błędu.
        print("\nPrzerwano przez użytkownika.")
        sys.exit(130)
