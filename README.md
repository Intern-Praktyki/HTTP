# Skaner nagłówków bezpieczeństwa HTTP

Proste narzędzie CLI w Pythonie, które sprawdza, czy strona internetowa
ustawia kluczowe **nagłówki bezpieczeństwa HTTP**. Dostajesz czytelny raport
oraz wynik punktowy (np. `4/6`).

> Element mojego portfolio z obszaru **AI Security**. Nie jestem programistą —
> buduję z pomocą AI, dlatego kod jest celowo prosty i obficie komentowany,
> aby dało się go w całości zaudytować.

---

## Po co to jest? Jaki problem rozwiązuje?

Przeglądarki potrafią chronić użytkowników przed wieloma atakami (XSS,
clickjacking, podsłuch ruchu), ale **tylko wtedy, gdy serwer wyśle odpowiednie
nagłówki HTTP**. W praktyce wiele stron tych nagłówków nie ustawia lub robi to
błędnie.

Ręczne sprawdzanie tego w narzędziach deweloperskich przeglądarki jest żmudne.
To narzędzie robi to za Ciebie w kilka sekund — z linii poleceń, dla jednej lub
wielu stron naraz, a dzięki opcji `--json` także w sposób nadający się do
automatyzacji (np. w pipeline DevSecOps / CI/CD).

### Jakie nagłówki sprawdza

| Nagłówek | Po co jest |
|---|---|
| `Content-Security-Policy` | Ogranicza skąd ładują się skrypty/style i utrudnia ataki XSS. |
| `Strict-Transport-Security` | Wymusza HTTPS i chroni przed podsłuchem. |
| `X-Frame-Options` | Blokuje osadzanie strony w ramce (ochrona przed clickjackingiem). |
| `X-Content-Type-Options` | Wyłącza zgadywanie typu pliku przez przeglądarkę (MIME sniffing). |
| `Referrer-Policy` | Kontroluje ile informacji o adresie wysyłamy przy przejściu dalej. |
| `Permissions-Policy` | Ogranicza dostęp strony do funkcji jak kamera czy mikrofon. |

Dodatkowo narzędzie zaznacza proste **słabe konfiguracje**, np. HSTS bez
parametru `max-age`, `X-Content-Type-Options` bez wartości `nosniff` czy
`X-Frame-Options` z nietypową wartością.

---

## Instalacja

Wymagany Python 3.7 lub nowszy.

```bash
# 1. Pobierz repozytorium
git clone <adres-tego-repozytorium>
cd HTTP

# 2. (zalecane) utwórz wirtualne środowisko
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Zainstaluj jedyną zależność
pip install -r requirements.txt
```

---

## Użycie

```bash
# Sprawdź jedną stronę
python3 scanner.py example.com

# Sprawdź kilka stron naraz
python3 scanner.py example.com github.com mojastrona.pl

# Wynik w formacie JSON (do automatyzacji)
python3 scanner.py example.com --json

# Zmień limit czasu oczekiwania na odpowiedź (domyślnie 10 s)
python3 scanner.py example.com --timeout 5

# Pomoc
python3 scanner.py --help
```

Adres możesz podać ze schematem (`https://example.com`) lub bez — wtedy
narzędzie domyślnie dopisze `https://`.

> **Uwaga dotycząca bezpieczeństwa:** narzędzie wysyła zapytania **wyłącznie**
> do adresów, które sam podasz. Nie kontaktuje się z żadnymi innymi serwerami,
> nie zbiera ani nie wysyła żadnych danych.

---

## Przykładowy wynik

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

- `0` — wszystkie strony udało się sprawdzić.
- `1` — przynajmniej jedna strona zwróciła błąd połączenia (przydatne w CI/CD).

---

## Jak działa kod (krótko)

Cały program to jeden plik [`scanner.py`](scanner.py):

1. czyta argumenty z linii poleceń (`argparse`),
2. dla każdego adresu wykonuje jedno zapytanie `GET` z timeoutem (`requests`),
3. porównuje otrzymane nagłówki z listą oczekiwanych nagłówków bezpieczeństwa,
4. buduje wynik jako słownik i wypisuje go jako tekst lub JSON.

Każda nieoczywista linijka ma komentarz po polsku wyjaśniający „po co to jest".

---

## Czego się nauczyłem

<!-- Ta sekcja jest do uzupełnienia przeze mnie własnymi słowami. -->

- 
- 
- 

---

## Licencja

Projekt edukacyjny / portfolio. Możesz go dowolnie używać i modyfikować.
