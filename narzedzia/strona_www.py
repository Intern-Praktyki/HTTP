# -*- coding: utf-8 -*-
"""
Narzędzie: Uruchom stronę WWW.

To cienka "nakładka" na launcher start_strony.py, dzięki której stronę
można odpalić również z menu głównego przybornika. Cała logika serwera
mieszka w start_strony.py, a ustawienia w konfiguracja.py.
"""

# Importujemy gotowy launcher -- nie powielamy logiki serwera.
import start_strony


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "strona"
TYTUL = "Uruchom stronę WWW (Detektyw haseł + Wydatki)"
OPIS = "Startuje lokalny serwer i otwiera stronę w przeglądarce."


def uruchom_cli(argv):
    """Tryb CLI: po prostu uruchamia launcher strony."""
    # argv ignorujemy -- ustawienia bierzemy z pliku konfiguracja.py.
    return start_strony.main()


def uruchom_interaktywnie():
    """Tryb z menu głównego: identyczny efekt jak w CLI."""
    return start_strony.main()
