#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher strony WWW przybornika.

Uruchom ten plik, a on:
  1) wystartuje lokalny serwer ze stroną z folderu "docs",
  2) (opcjonalnie) otworzy stronę w przeglądarce,
  3) będzie działał, dopóki go nie zatrzymasz klawiszami Ctrl+C.

Ustawienia (port, auto-otwieranie, folder) zmienisz w pliku konfiguracja.py.
Wszystko działa na wbudowanej bibliotece Pythona -- bez dodatkowych zależności.
"""

# http.server -> gotowy, prosty serwer plików wbudowany w Pythona.
import http.server
# socketserver -> "opakowanie", które utrzymuje serwer w działaniu.
import socketserver
# webbrowser -> otwarcie strony w domyślnej przeglądarce użytkownika.
import webbrowser
# os -> sprawdzanie ścieżek (czy folder strony istnieje).
import os
# sys -> kod wyjścia, gdyby coś poszło nie tak.
import sys
# functools.partial -> wygodne ustawienie, z którego folderu serwer ma serwować.
from functools import partial

# Wczytujemy ustawienia z osobnego pliku, żeby konfiguracja była w jednym miejscu.
import konfiguracja


def main():
    # Budujemy pełną ścieżkę do folderu strony (obok tego pliku).
    katalog_projektu = os.path.dirname(os.path.abspath(__file__))
    folder_strony = os.path.join(katalog_projektu, konfiguracja.FOLDER_STRONY)

    # Zabezpieczenie: jeśli folder strony nie istnieje -> grzecznie informujemy.
    if not os.path.isdir(folder_strony):
        print("Nie znaleziono folderu strony: " + folder_strony)
        print("Sprawdź ustawienie FOLDER_STRONY w pliku konfiguracja.py.")
        return 1

    adres = "http://localhost:" + str(konfiguracja.PORT)

    # partial tworzy handler, który serwuje pliki WYŁĄCZNIE z folderu strony.
    # directory=... sprawia, że serwer nie wychodzi poza ten folder.
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=folder_strony)

    try:
        # Tworzymy serwer nasłuchujący na ustawionym porcie.
        # "" oznacza nasłuch na lokalnym komputerze.
        with socketserver.TCPServer(("", konfiguracja.PORT), handler) as serwer:
            print("=" * 56)
            print("  Strona przybornika działa pod adresem:")
            print("  " + adres)
            print("=" * 56)
            print("Zatrzymaj serwer klawiszami Ctrl+C.")

            # Jeśli włączone w konfiguracji -> otwieramy stronę w przeglądarce.
            if konfiguracja.AUTO_OTWORZ:
                webbrowser.open(adres)

            # serve_forever utrzymuje serwer aż do przerwania (Ctrl+C).
            serwer.serve_forever()
    except OSError:
        # Najczęstsza przyczyna: port jest już zajęty przez inny program.
        print("Nie udało się uruchomić serwera na porcie "
              + str(konfiguracja.PORT) + ".")
        print("Port może być zajęty -- zmień PORT w konfiguracja.py i spróbuj ponownie.")
        return 1
    except KeyboardInterrupt:
        # Ctrl+C -> kończymy czysto, bez brzydkiego błędu.
        print("\nZatrzymano serwer. Do zobaczenia!")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
