# -*- coding: utf-8 -*-
"""
Narzędzie: Generator fiszek z tekstu.

Wczytuje plik tekstowy (np. artykuł w obcym języku), znajduje najczęściej
powtarzające się słowa, odrzuca te najpospolitsze (jak "the", "le", "i")
i zapisuje gotowe fiszki do pliku CSV -- do zaimportowania w Anki/Quizlet.

Działa w 100% offline. Kod celowo prosty i obficie komentowany.
"""

# re -> wyrażenia regularne, żeby wyłuskać z tekstu same słowa.
import re
# csv -> bezpieczny zapis do pliku CSV (sam dba o przecinki/cudzysłowy).
import csv
# collections.Counter -> wygodne liczenie, ile razy występuje każde słowo.
from collections import Counter
# argparse -> obsługa argumentów w trybie CLI.
import argparse
# os -> budowanie domyślnej nazwy pliku wyjściowego.
import os


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "slowka"
TYTUL = "Generator fiszek z tekstu"
OPIS = "Wyciąga najczęstsze słowa z pliku tekstowego i zapisuje fiszki do CSV."


# Listy "słów pospolitych" (stop words) -- te pomijamy, bo nie warto się ich uczyć.
# Trzymamy je w zbiorach (set), bo sprawdzanie "czy słowo jest w zbiorze" jest szybkie.
STOP_WORDS = {
    "pl": {
        "i", "w", "na", "z", "do", "to", "się", "że", "nie", "jest", "a", "o",
        "od", "po", "za", "co", "jak", "ale", "czy", "the", "lub", "oraz",
        "tym", "ten", "ta", "te", "był", "była", "było", "są", "być", "go",
    },
    "en": {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
        "is", "are", "was", "were", "be", "this", "that", "it", "as", "with",
        "at", "by", "from", "has", "have", "had", "you", "i", "we", "they",
    },
    "fr": {
        "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "à",
        "en", "dans", "que", "qui", "ne", "pas", "est", "sont", "ce", "se",
        "pour", "par", "sur", "il", "elle", "nous", "vous", "ils", "au", "aux",
    },
}


def wczytaj_tekst(sciezka):
    """Wczytuje cały tekst z pliku. Zwraca tekst albo None, jeśli pliku brak."""
    try:
        # encoding="utf-8" -> poprawne odczytanie polskich i obcych znaków.
        with open(sciezka, "r", encoding="utf-8") as plik:
            return plik.read()
    except FileNotFoundError:
        return None


def policz_slowa(tekst, jezyk="auto", min_dlugosc=3):
    """
    Zwraca listę par (słowo, liczba_wystąpień), od najczęstszych.

    jezyk -> które stop words odrzucić ("pl"/"en"/"fr"/"auto" = wszystkie).
    min_dlugosc -> pomijamy bardzo krótkie słowa (np. 1-2 litery).
    """
    # Zamieniamy na małe litery, żeby "Pies" i "pies" liczyły się razem.
    tekst = tekst.lower()

    # Wzorzec [^\W\d_]+ oznacza: ciągi samych liter (też z ogonkami/akcentami),
    # bez cyfr i podkreśleń. re.findall zwraca listę wszystkich pasujących słów.
    slowa = re.findall(r"[^\W\d_]+", tekst, flags=re.UNICODE)

    # Budujemy zbiór słów do pominięcia.
    if jezyk == "auto":
        # auto -> łączymy wszystkie listy w jeden zbiór (suma zbiorów operatorem |).
        do_pominiecia = STOP_WORDS["pl"] | STOP_WORDS["en"] | STOP_WORDS["fr"]
    else:
        # .get(..., set()) -> jeśli ktoś poda nieznany język, użyjemy pustego zbioru.
        do_pominiecia = STOP_WORDS.get(jezyk, set())

    # Zostawiamy tylko słowa wystarczająco długie i nie będące "pospolitymi".
    wybrane = [
        s for s in slowa
        if len(s) >= min_dlugosc and s not in do_pominiecia
    ]

    # Counter liczy wystąpienia; most_common() zwraca je od najczęstszych.
    return Counter(wybrane).most_common()


def zapisz_csv(pary, sciezka_wyjsciowa):
    """
    Zapisuje fiszki do pliku CSV z kolumnami: slowo, tlumaczenie, liczba.
    Kolumnę "tlumaczenie" zostawiamy pustą -- uzupełnisz ją w Anki/Quizlet.
    """
    # newline="" to zalecany sposób otwierania plików dla modułu csv.
    with open(sciezka_wyjsciowa, "w", encoding="utf-8", newline="") as plik:
        writer = csv.writer(plik)
        # Nagłówek -- ułatwia import i orientację w pliku.
        writer.writerow(["slowo", "tlumaczenie", "liczba_wystapien"])
        for slowo, liczba in pary:
            # Puste pole na tłumaczenie -> do uzupełnienia przez użytkownika.
            writer.writerow([slowo, "", liczba])


def uruchom_cli(argv):
    """
    Tryb CLI. Przykład:
      python3 main.py slowka artykul.txt --ile 30 --jezyk fr
    """
    parser = argparse.ArgumentParser(prog="main.py " + NAZWA, description=OPIS)
    parser.add_argument("plik", help="Ścieżka do pliku tekstowego (.txt).")
    parser.add_argument("--ile", type=int, default=30,
                        help="Ile najczęstszych słów zapisać (domyślnie 30).")
    parser.add_argument("--jezyk", default="auto", choices=["auto", "pl", "en", "fr"],
                        help="Język tekstu (decyduje, które słowa pospolite pominąć).")
    parser.add_argument("--wyjscie", default=None,
                        help="Nazwa pliku CSV (domyślnie: <nazwa-pliku>_fiszki.csv).")
    argumenty = parser.parse_args(argv)

    tekst = wczytaj_tekst(argumenty.plik)
    if tekst is None:
        print("Nie znaleziono pliku: " + argumenty.plik)
        return 1

    pary = policz_slowa(tekst, argumenty.jezyk)[: argumenty.ile]
    if not pary:
        print("Nie znaleziono żadnych słów do zapisania.")
        return 1

    # Jeśli nie podano nazwy wyjścia -> budujemy ją na bazie nazwy pliku wejściowego.
    wyjscie = argumenty.wyjscie or _domyslne_wyjscie(argumenty.plik)
    zapisz_csv(pary, wyjscie)
    print("Zapisano " + str(len(pary)) + " fiszek do pliku: " + wyjscie)
    return 0


def _domyslne_wyjscie(sciezka_wejsciowa):
    """Tworzy domyślną nazwę pliku wyjściowego, np. 'artykul.txt' -> 'artykul_fiszki.csv'."""
    # splitext dzieli na ("artykul", ".txt"); bierzemy pierwszy element [0].
    rdzen = os.path.splitext(sciezka_wejsciowa)[0]
    return rdzen + "_fiszki.csv"


def uruchom_interaktywnie():
    """Tryb z menu głównego: pyta o plik i ustawienia, zapisuje CSV."""
    print("")
    print(TYTUL)
    sciezka = input("Ścieżka do pliku tekstowego: ").strip()

    tekst = wczytaj_tekst(sciezka)
    if tekst is None:
        print("Nie znaleziono takiego pliku.")
        return 1

    # Pytamy o język; pusta odpowiedź -> "auto".
    jezyk = input("Język (auto/pl/en/fr, Enter = auto): ").strip().lower() or "auto"
    if jezyk not in ("auto", "pl", "en", "fr"):
        jezyk = "auto"

    # Pytamy ile słów; pusta lub błędna odpowiedź -> 30.
    tekst_ile = input("Ile słów zapisać? (Enter = 30): ").strip()
    ile = int(tekst_ile) if tekst_ile.isdigit() else 30

    pary = policz_slowa(tekst, jezyk)[:ile]
    if not pary:
        print("Nie znaleziono żadnych słów do zapisania.")
        return 1

    wyjscie = _domyslne_wyjscie(sciezka)
    zapisz_csv(pary, wyjscie)
    print("\nZapisano " + str(len(pary)) + " fiszek do pliku: " + wyjscie)
    print("Możesz go teraz zaimportować do Anki lub Quizleta.")
    return 0
