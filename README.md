# Przybornik AI Security

Zbiór prostych, użytecznych narzędzi bezpieczeństwa w Pythonie, połączonych
**jednym menu głównym**. Zamiast wielu osobnych repozytoriów — jeden projekt,
w którym każde narzędzie jest osobnym, czytelnym plikiem, a uruchamiasz je
z wygodnego menu (lub bezpośrednio z linii poleceń).

> Element mojego portfolio z obszaru **AI Security**. Kod jest celowo prosty,
> przejrzysty i obficie komentowany — tak, aby każdy mógł go w całości
> przeczytać i zaudytować.

---

## Dostępne narzędzia

| Narzędzie | Co robi |
|---|---|
| **Skaner nagłówków bezpieczeństwa HTTP** | Sprawdza, czy strona ustawia kluczowe nagłówki bezpieczeństwa, i daje wynik punktowy (np. `4/6`). |

> Kolejne narzędzia będą dodawane jako nowe pliki w folderze `narzedzia/` —
> pojawią się w menu automatycznie, bez zmian w pozostałym kodzie.

---

## Jak to jest zbudowane

```
.
├── main.py                       # menu główne — jedyny plik, który uruchamiasz
├── narzedzia/                    # każde narzędzie osobno (ładnie rozdzielone)
│   ├── __init__.py               # oznacza folder jako pakiet Pythona
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
  PRZYBORNIK AI SECURITY -- menu główne
============================================================
  1) Skaner nagłówków bezpieczeństwa HTTP
  0) Wyjście
============================================================

Wybierz narzędzie (numer):
```

### 2) Tryb CLI (do automatyzacji)

Uruchom konkretne narzędzie od razu, podając jego nazwę i argumenty:

```bash
# Sprawdź jedną stronę
python3 main.py skaner-naglowkow example.com

# Kilka stron naraz
python3 main.py skaner-naglowkow example.com github.com mojastrona.pl

# Wynik w formacie JSON (do automatyzacji / DevSecOps)
python3 main.py skaner-naglowkow example.com --json

# Zmień limit czasu na odpowiedź (domyślnie 10 s)
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
