# -*- coding: utf-8 -*-
"""
Narzędzie: Organizer plików.

Robi porządek w wybranym folderze (np. "Pobrane"): grupuje pliki do podfolderów
według typu -- Obrazy, Dokumenty, Muzyka, Wideo, Archiwa, Inne.

BEZPIECZEŃSTWO / OSTROŻNOŚĆ:
  - domyślnie pokazuje tylko PODGLĄD (nic nie przenosi),
  - przenosi pliki dopiero po wyraźnej zgodzie / fladze --wykonaj,
  - działa tylko na plikach bezpośrednio w danym folderze (nie wchodzi głębiej),
  - nigdy nic nie usuwa; przy konflikcie nazw dokłada numer do nazwy pliku.

Kod celowo prosty i obficie komentowany.
"""

# os -> sprawdzanie i listowanie zawartości folderu, ścieżki.
import os
# shutil -> bezpieczne przenoszenie plików (shutil.move).
import shutil
# argparse -> obsługa argumentów w trybie CLI.
import argparse


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "porzadki"
TYTUL = "Organizer plików"
OPIS = "Robi porządek w folderze: sortuje pliki do podfolderów według typu."


# Mapa: rozszerzenie pliku -> nazwa folderu, do którego trafi.
# Rozszerzenia trzymamy małymi literami, bez kropki.
KATEGORIE = {
    # Obrazy
    "jpg": "Obrazy", "jpeg": "Obrazy", "png": "Obrazy", "gif": "Obrazy",
    "bmp": "Obrazy", "webp": "Obrazy", "svg": "Obrazy", "heic": "Obrazy",
    # Dokumenty
    "pdf": "Dokumenty", "doc": "Dokumenty", "docx": "Dokumenty",
    "odt": "Dokumenty", "txt": "Dokumenty", "rtf": "Dokumenty",
    "xls": "Dokumenty", "xlsx": "Dokumenty", "csv": "Dokumenty",
    "ppt": "Dokumenty", "pptx": "Dokumenty",
    # Muzyka
    "mp3": "Muzyka", "wav": "Muzyka", "flac": "Muzyka",
    "m4a": "Muzyka", "aac": "Muzyka", "ogg": "Muzyka",
    # Wideo
    "mp4": "Wideo", "mkv": "Wideo", "avi": "Wideo",
    "mov": "Wideo", "wmv": "Wideo",
    # Archiwa
    "zip": "Archiwa", "rar": "Archiwa", "7z": "Archiwa",
    "tar": "Archiwa", "gz": "Archiwa",
}

# Folder dla plików, których typu nie rozpoznajemy.
KATEGORIA_INNE = "Inne"


def kategoria_pliku(nazwa_pliku):
    """Zwraca nazwę kategorii (folderu) dla danego pliku na podstawie rozszerzenia."""
    # os.path.splitext dzieli "zdjecie.JPG" na ("zdjecie", ".JPG").
    rozszerzenie = os.path.splitext(nazwa_pliku)[1]
    # Usuwamy kropkę i zamieniamy na małe litery, żeby pasowało do mapy KATEGORIE.
    rozszerzenie = rozszerzenie.lower().lstrip(".")
    # .get(klucz, wartosc_domyslna) -> jeśli rozszerzenia nie ma w mapie, dajemy "Inne".
    return KATEGORIE.get(rozszerzenie, KATEGORIA_INNE)


def zaplanuj(folder):
    """
    Buduje plan: lista par (nazwa_pliku, kategoria) dla plików w folderze.
    Nie przenosi jeszcze niczego -- tylko planuje, co gdzie powinno trafić.
    """
    plan = []
    # os.listdir zwraca nazwy wszystkich elementów w folderze.
    for nazwa in os.listdir(folder):
        pelna_sciezka = os.path.join(folder, nazwa)

        # Pomijamy foldery -- ruszamy tylko pliki.
        if not os.path.isfile(pelna_sciezka):
            continue

        # Pomijamy pliki ukryte (zaczynające się od kropki), np. ".bashrc".
        if nazwa.startswith("."):
            continue

        plan.append((nazwa, kategoria_pliku(nazwa)))

    # Sortujemy po nazwie, żeby podgląd był uporządkowany i przewidywalny.
    plan.sort()
    return plan


def _wolna_sciezka_docelowa(folder_docelowy, nazwa_pliku):
    """
    Zwraca ścieżkę docelową, która NIE nadpisze istniejącego pliku.
    Jeśli "raport.pdf" już istnieje, spróbuje "raport (1).pdf", "raport (2).pdf"...
    """
    cel = os.path.join(folder_docelowy, nazwa_pliku)
    if not os.path.exists(cel):
        return cel

    # Rozdzielamy nazwę i rozszerzenie, żeby numer wstawić przed kropką.
    rdzen, rozsz = os.path.splitext(nazwa_pliku)
    numer = 1
    # Zwiększamy numer, dopóki nie znajdziemy wolnej nazwy.
    while True:
        kandydat = os.path.join(folder_docelowy, rdzen + " (" + str(numer) + ")" + rozsz)
        if not os.path.exists(kandydat):
            return kandydat
        numer += 1


def wykonaj(folder, plan):
    """
    Faktycznie przenosi pliki zgodnie z planem. Zwraca liczbę przeniesionych plików.
    Wywoływać dopiero PO potwierdzeniu przez użytkownika.
    """
    przeniesione = 0
    for nazwa, kategoria in plan:
        folder_docelowy = os.path.join(folder, kategoria)
        # exist_ok=True -> nie wyrzuca błędu, gdy folder już istnieje.
        os.makedirs(folder_docelowy, exist_ok=True)

        zrodlo = os.path.join(folder, nazwa)
        cel = _wolna_sciezka_docelowa(folder_docelowy, nazwa)
        # shutil.move przenosi plik (a nie kopiuje), zachowując jego zawartość.
        shutil.move(zrodlo, cel)
        przeniesione += 1
    return przeniesione


def _pokaz_podglad(plan):
    """Wypisuje czytelny podgląd: co i gdzie trafi."""
    if not plan:
        print("W tym folderze nie ma plików do uporządkowania.")
        return

    print("Podgląd zmian (jeszcze nic nie przeniesiono):")
    for nazwa, kategoria in plan:
        print("  " + nazwa + "  ->  " + kategoria + "/")
    print("Razem plików: " + str(len(plan)))


def uruchom_cli(argv):
    """
    Tryb CLI. Przykłady:
      python3 main.py porzadki /sciezka/do/folderu            (sam podgląd)
      python3 main.py porzadki /sciezka/do/folderu --wykonaj  (przenosi pliki)
    """
    parser = argparse.ArgumentParser(prog="main.py " + NAZWA, description=OPIS)
    parser.add_argument("folder", help="Folder do uporządkowania.")
    parser.add_argument("--wykonaj", action="store_true",
                        help="Faktycznie przenieś pliki (bez tej flagi -> tylko podgląd).")
    argumenty = parser.parse_args(argv)

    # Sprawdzamy, czy podany folder w ogóle istnieje -- inaczej grzecznie kończymy.
    if not os.path.isdir(argumenty.folder):
        print("To nie jest istniejący folder: " + argumenty.folder)
        return 1

    plan = zaplanuj(argumenty.folder)
    _pokaz_podglad(plan)

    # Bez flagi --wykonaj zostajemy przy samym podglądzie (bezpiecznie).
    if not argumenty.wykonaj:
        print("\n(To był tylko podgląd. Dodaj --wykonaj, aby przenieść pliki.)")
        return 0

    if plan:
        liczba = wykonaj(argumenty.folder, plan)
        print("\nGotowe. Przeniesiono plików: " + str(liczba))
    return 0


def uruchom_interaktywnie():
    """Tryb z menu głównego: pyta o folder, pokazuje podgląd i prosi o zgodę."""
    print("")
    print(TYTUL)
    folder = input("Podaj folder do uporządkowania: ").strip()

    if not os.path.isdir(folder):
        print("To nie jest istniejący folder.")
        return 1

    plan = zaplanuj(folder)
    print("")
    _pokaz_podglad(plan)

    # Jeśli nie ma nic do zrobienia, kończymy bez pytania.
    if not plan:
        return 0

    # Pytamy o zgodę -- domyślnie NIE, żeby nie ruszać plików przez przypadek.
    odp = input("\nPrzenieść te pliki? (t/N): ").strip().lower()
    if odp in ("t", "tak", "y", "yes"):
        liczba = wykonaj(folder, plan)
        print("Gotowe. Przeniesiono plików: " + str(liczba))
    else:
        print("Anulowano -- nic nie zostało przeniesione.")
    return 0
