# -*- coding: utf-8 -*-
"""
Narzędzie: Optymalizator makro i kosztów (białko).

Pomaga odpowiedzieć na pytanie ze sklepu/siłowni:
"Czy ten produkt to opłacalne źródło białka?".

Podajesz cenę produktu, jego wagę i ile białka ma na 100 g (z etykiety),
a narzędzie liczy ile kosztuje Cię 1 gram białka i ocenia opłacalność.

Działa w 100% offline. Kod celowo prosty i obficie komentowany.
"""

# argparse -> obsługa argumentów w trybie CLI.
import argparse


# --- METADANE NARZĘDZIA (odczytuje je menu główne) ---
NAZWA = "makro"
TYTUL = "Optymalizator makro i kosztów (białko)"
OPIS = "Liczy koszt 1 g białka i ocenia, czy produkt to opłacalne źródło białka."

# Domyślny dzienny cel białka w gramach (typowy dla osób aktywnych).
DOMYSLNY_CEL = 150


def parse_liczba(tekst):
    """
    Zamienia tekst na liczbę, akceptując polski przecinek dziesiętny.
    Dzięki temu "15,50" oraz "15.50" działają tak samo.
    """
    # .replace zamienia przecinek na kropkę, bo float() rozumie tylko kropkę.
    return float(str(tekst).replace(",", ".").strip())


def policz(cena, waga, bialko_na_100g, cel=DOMYSLNY_CEL):
    """
    Liczy wszystkie wartości i zwraca je w słowniku.
    Trzymanie wyniku w słowniku ułatwia osobne wypisywanie go na ekran.
    """
    # Ile gramów białka jest w CAŁYM produkcie.
    # (waga / 100) mówi "ile setek gramów", mnożymy przez białko na 100 g.
    bialko_total = (waga / 100.0) * bialko_na_100g

    # Koszt 1 grama białka = cena podzielona przez ilość białka w produkcie.
    koszt_1g = cena / bialko_total

    # Ile produktu (w gramach) trzeba zjeść, żeby dobić do dziennego celu białka.
    gramy_na_cel = cel * 100.0 / bialko_na_100g
    # Ile to kosztuje (sam koszt białka na pokrycie celu).
    koszt_celu = koszt_1g * cel

    # Prosta ocena opłacalności na podstawie kosztu 1 g białka.
    # Progi są orientacyjne dla polskiego rynku spożywczego.
    if koszt_1g <= 0.08:
        ocena = "Świetny stosunek ceny do białka"
    elif koszt_1g <= 0.15:
        ocena = "Dobry stosunek ceny do białka"
    elif koszt_1g <= 0.25:
        ocena = "Przeciętny -- da się taniej"
    else:
        ocena = "Słaby -- drogie źródło białka"

    return {
        "bialko_total": bialko_total,
        "koszt_1g": koszt_1g,
        "gramy_na_cel": gramy_na_cel,
        "koszt_celu": koszt_celu,
        "cel": cel,
        "ocena": ocena,
    }


def _wypisz(wynik):
    """Wypisuje czytelny raport. Wspólne dla trybu CLI i interaktywnego."""
    # round(..., 2) zaokrągla do 2 miejsc po przecinku, żeby było czytelnie.
    print("Białko w całym produkcie: " + str(round(wynik["bialko_total"], 1)) + " g")
    print("Koszt 1 g białka:         " + str(round(wynik["koszt_1g"], 3)) + " zł")
    print("Ocena: " + wynik["ocena"])
    print("")
    print("Aby pokryć cel " + str(wynik["cel"]) + " g białka z tego produktu:")
    print("  - trzeba zjeść ok. " + str(round(wynik["gramy_na_cel"])) + " g produktu")
    print("  - koszt białka na cel: ok. " + str(round(wynik["koszt_celu"], 2)) + " zł")


def uruchom_cli(argv):
    """
    Tryb CLI. Przykład:
      python3 main.py makro --cena 15 --waga 300 --bialko 18
    """
    parser = argparse.ArgumentParser(prog="main.py " + NAZWA, description=OPIS)
    # type=parse_liczba -> argument od razu zamieniany na liczbę (z obsługą przecinka).
    parser.add_argument("--cena", type=parse_liczba, required=True,
                        help="Cena produktu w zł.")
    parser.add_argument("--waga", type=parse_liczba, required=True,
                        help="Waga produktu w gramach.")
    parser.add_argument("--bialko", type=parse_liczba, required=True,
                        help="Ile gramów białka na 100 g (z etykiety).")
    parser.add_argument("--cel", type=parse_liczba, default=DOMYSLNY_CEL,
                        help="Dzienny cel białka w gramach (domyślnie 150).")
    argumenty = parser.parse_args(argv)

    # Zabezpieczenie: produkt bez białka -> nie da się policzyć kosztu 1 g białka.
    if argumenty.bialko <= 0:
        print("Białko na 100 g musi być większe od zera.")
        return 1

    _wypisz(policz(argumenty.cena, argumenty.waga, argumenty.bialko, argumenty.cel))
    return 0


def uruchom_interaktywnie():
    """Tryb z menu głównego: pyta o trzy liczby i wypisuje wynik."""
    print("")
    print(TYTUL)
    try:
        # Pobieramy dane od użytkownika i od razu zamieniamy na liczby.
        cena = parse_liczba(input("Cena produktu (zł): "))
        waga = parse_liczba(input("Waga produktu (g): "))
        bialko = parse_liczba(input("Białko na 100 g (g): "))
    except ValueError:
        # Jeśli ktoś wpisze litery zamiast liczby -> grzecznie informujemy.
        print("To nie wygląda na liczbę. Spróbuj ponownie.")
        return 1

    if bialko <= 0:
        print("Białko na 100 g musi być większe od zera.")
        return 1

    print("")
    _wypisz(policz(cena, waga, bialko))
    return 0
