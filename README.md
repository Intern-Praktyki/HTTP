# Przybornik — proste, przydatne narzędzia

Zbiór małych, użytecznych narzędzi w Pythonie, połączonych **jednym menu
głównym**. Zamiast wielu osobnych repozytoriów — jeden projekt, w którym każde
narzędzie jest osobnym, czytelnym plikiem, a uruchamiasz je z wygodnego menu
(lub bezpośrednio z linii poleceń).

> Element mojego portfolio. Pomysł jest prosty: pokazać, że potrafię szybko
> składać **przydatne, działające narzędzia** — czytelnie i z dobrą
> dokumentacją. Kod jest celowo prosty, tak aby każdy mógł go przeczytać.

---

## Dostępne narzędzia

| Narzędzie | Co robi | Dla kogo |
|---|---|---|
| **Generator i audytor haseł** | Tworzy mocne hasła i ocenia, czy Twoje hasło jest dobre. Działa offline. | dla każdego |
| **Organizer plików** | Robi porządek w folderze (np. *Pobrane*) — sortuje pliki do podfolderów wg typu. Najpierw pokazuje podgląd. | dla każdego |
| **Optymalizator makro i kosztów** | Liczy koszt 1 g białka i ocenia, czy produkt to opłacalne źródło białka. Przydatne na zakupach i na siłowni. | dla każdego |
| **Generator fiszek z tekstu** | Wyciąga najczęstsze słowa z pliku tekstowego i zapisuje fiszki do CSV (import do Anki/Quizlet). | dla uczących się |
| **Skaner nagłówków bezpieczeństwa HTTP** | Sprawdza, czy strona ustawia kluczowe nagłówki bezpieczeństwa, i daje wynik punktowy (np. `4/6`). | bardziej techniczne |

> Kolejne narzędzia będą dodawane jako nowe pliki w folderze `narzedzia/` —
> pojawią się w menu automatycznie, bez zmian w pozostałym kodzie.

---

## Jak to jest zbudowane

```
.
├── main.py                       # menu główne — jedyny plik, który uruchamiasz
├── narzedzia/                    # każde narzędzie osobno (ładnie rozdzielone)
│   ├── __init__.py               # oznacza folder jako pakiet Pythona
│   ├── generator_hasel.py        # narzędzie: generator i audytor haseł
│   ├── organizer_plikow.py       # narzędzie: organizer plików
│   ├── kalkulator_makro.py       # narzędzie: optymalizator makro i kosztów
│   ├── ekstraktor_slowek.py      # narzędzie: generator fiszek z tekstu
│   └── skaner_naglowkow.py       # narzędzie: skaner nagłówków HTTP
├── README.md
└── requirements.txt
```

Pomysł jest prosty: **`main.py` to wspólne „GUI"** (interaktywne menu w
terminalu) i wspólny punkt wejścia, a logika każdego narzędzia mieszka w
osobnym pliku. `main.py` sam wykrywa narzędzia w folderze `narzedzia/`, więc
dodanie nowego = dorzucenie jednego pliku.

Każde narzędzie udostępnia ten sam prosty „interfejs":

- `NAZWA`, `TYTUL`, `OPIS` — metadane pokazywane w menu,
- `uruchom_interaktywnie()` — tryb z menu (pyta o dane przez klawiaturę),
- `uruchom_cli(argv)` — tryb z linii poleceń (do automatyzacji / CI/CD).

---

## Instalacja

Wymagany Python 3.7 lub nowszy.

```bash
# 1. Pobierz repozytorium
git clone <adres-tego-repozytorium>
cd <nazwa-folderu>

# 2. (zalecane) utwórz wirtualne środowisko
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Zainstaluj jedyną zależność
pip install -r requirements.txt
```

---

## Użycie

### 1) Menu interaktywne (najprościej)

```bash
python3 main.py
```

Zobaczysz numerowane menu — wpisujesz numer narzędzia i postępujesz zgodnie
z pytaniami na ekranie.

```
============================================================
  PRZYBORNIK -- proste, przydatne narzędzia
============================================================
  1) Generator i audytor haseł
  2) Generator fiszek z tekstu
  3) Optymalizator makro i kosztów (białko)
  4) Organizer plików
  5) Skaner nagłówków bezpieczeństwa HTTP
  0) Wyjście
============================================================

Wybierz narzędzie (numer):
```

### 2) Tryb CLI (do automatyzacji)

Uruchom konkretne narzędzie od razu, podając jego nazwę i argumenty:

```bash
# Hasła: wygeneruj mocne hasło / oceń istniejące
python3 main.py hasla generuj
python3 main.py hasla generuj --dlugosc 24 --bez-znakow
python3 main.py hasla sprawdz "MojeHaslo123!"

# Porządki: najpierw podgląd, potem (z --wykonaj) faktyczne przeniesienie
python3 main.py porzadki /sciezka/do/folderu
python3 main.py porzadki /sciezka/do/folderu --wykonaj

# Makro: koszt 1 g białka i ocena opłacalności
python3 main.py makro --cena 15 --waga 300 --bialko 18

# Fiszki: wyciągnij najczęstsze słowa z pliku i zapisz CSV
python3 main.py slowka artykul.txt --ile 30 --jezyk fr

# Skaner nagłówków: jedna lub wiele stron, opcjonalnie JSON
python3 main.py skaner-naglowkow example.com
python3 main.py skaner-naglowkow example.com github.com --json
python3 main.py skaner-naglowkow example.com --timeout 5
```

### Polecenia pomocnicze

```bash
python3 main.py --list      # lista dostępnych narzędzi
python3 main.py --help      # pomoc ogólna
```

Adres możesz podać ze schematem (`https://example.com`) lub bez — wtedy
narzędzie domyślnie dopisze `https://`.

> **Uwaga dotycząca bezpieczeństwa:** narzędzia wysyłają zapytania **wyłącznie**
> do adresów, które sam podasz. Nie kontaktują się z żadnymi innymi serwerami,
> nie zbierają ani nie wysyłają żadnych danych.

---

## Przykładowy wynik (skaner nagłówków)

### Tryb tekstowy

```
============================================================
Strona: https://example.com
Kod odpowiedzi HTTP: 200

Obecne nagłówki bezpieczeństwa:
  [+] Content-Security-Policy
      Ogranicza skąd ładują się skrypty/style i utrudnia ataki XSS.
  [+] X-Content-Type-Options
      Wyłącza zgadywanie typu pliku przez przeglądarkę (MIME sniffing).

Brakujące nagłówki bezpieczeństwa:
  [-] Strict-Transport-Security
      Wymusza połączenie przez HTTPS i chroni przed podsłuchem.
  [-] X-Frame-Options
      Blokuje osadzanie strony w ramce (ochrona przed clickjackingiem).
  [-] Referrer-Policy
      Kontroluje ile informacji o adresie wysyłamy przy przejściu dalej.
  [-] Permissions-Policy
      Ogranicza dostęp strony do funkcji takich jak kamera czy mikrofon.

Wynik: 2/6
============================================================
```

### Tryb JSON (`--json`)

```json
[
  {
    "url": "https://example.com",
    "error": null,
    "status_code": 200,
    "obecne": [
      "Content-Security-Policy",
      "X-Content-Type-Options"
    ],
    "brakujace": [
      "Strict-Transport-Security",
      "X-Frame-Options",
      "Referrer-Policy",
      "Permissions-Policy"
    ],
    "ostrzezenia": {},
    "wynik": 2,
    "maks": 6
  }
]
```

### Kody wyjścia

- `0` — wszystko sprawdzone bez błędów.
- `1` — przynajmniej jedna strona zwróciła błąd połączenia (przydatne w CI/CD).

---

## Jakie nagłówki sprawdza skaner

| Nagłówek | Po co jest |
|---|---|
| `Content-Security-Policy` | Ogranicza skąd ładują się skrypty/style i utrudnia ataki XSS. |
| `Strict-Transport-Security` | Wymusza HTTPS i chroni przed podsłuchem. |
| `X-Frame-Options` | Blokuje osadzanie strony w ramce (ochrona przed clickjackingiem). |
| `X-Content-Type-Options` | Wyłącza zgadywanie typu pliku przez przeglądarkę (MIME sniffing). |
| `Referrer-Policy` | Kontroluje ile informacji o adresie wysyłamy przy przejściu dalej. |
| `Permissions-Policy` | Ogranicza dostęp strony do funkcji jak kamera czy mikrofon. |

Dodatkowo skaner zaznacza proste **słabe konfiguracje**, np. HSTS bez parametru
`max-age`, `X-Content-Type-Options` bez wartości `nosniff` czy `X-Frame-Options`
z nietypową wartością.

---

## Jak dodać własne narzędzie

1. Utwórz nowy plik w `narzedzia/`, np. `narzedzia/moje_narzedzie.py`.
2. Dodaj w nim metadane `NAZWA`, `TYTUL`, `OPIS` oraz funkcje
   `uruchom_interaktywnie()` i `uruchom_cli(argv)`.
3. Gotowe — narzędzie samo pojawi się w menu i w trybie CLI.

(Najłatwiej podejrzeć `narzedzia/skaner_naglowkow.py` jako wzór.)

---

## Czego się nauczyłem

<!-- Ta sekcja jest do uzupełnienia przeze mnie własnymi słowami. -->

- 
- 
- 

---

## Licencja

Projekt edukacyjny / portfolio. Możesz go dowolnie używać i modyfikować.
