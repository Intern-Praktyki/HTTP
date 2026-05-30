// Generator i audytor haseł -- wersja przeglądarkowa.
// Odpowiednik narzedzia/generator_hasel.py. Wszystko liczone lokalnie,
// nic nie jest wysyłane do żadnego serwera.

// Pobieramy elementy strony.
const dlugoscHasla = document.getElementById("dlugosc-hasla");
const znakiSpecjalne = document.getElementById("znaki-specjalne");
const przyciskGeneruj = document.getElementById("generuj-haslo");
const wynikGeneratora = document.getElementById("wynik-generatora");
const hasloDoOceny = document.getElementById("haslo-do-oceny");
const przyciskOcen = document.getElementById("ocen-haslo");
const wynikOceny = document.getElementById("wynik-oceny");

// Lista najpopularniejszych, łatwych do złamania haseł (małymi literami).
const NAJCZESTSZE_HASLA = new Set([
  "123456", "123456789", "12345678", "111111", "000000", "qwerty",
  "password", "haslo", "admin", "iloveyou", "qwerty123", "zaq12wsx",
  "1q2w3e4r", "polska", "abc123", "qwerty1", "monkey", "dragon",
]);


// Tworzy losowe hasło o zadanej długości.
// crypto.getRandomValues to bezpieczny generator losowy wbudowany w przeglądarkę.
function generujHaslo(dlugosc, zeZnakami) {
  let pula = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  if (zeZnakami) {
    pula += "!@#$%^&*()-_=+?";
  }
  // Losujemy tyle bezpiecznych liczb, ile znaków ma mieć hasło.
  const losowe = new Uint32Array(dlugosc);
  crypto.getRandomValues(losowe);

  let haslo = "";
  for (let i = 0; i < dlugosc; i++) {
    // Resztą z dzielenia mapujemy losową liczbę na znak z puli.
    haslo += pula[losowe[i] % pula.length];
  }
  return haslo;
}


// Ocenia siłę hasła. Zwraca obiekt: { ocena, punkty, maks, uwagi }.
function ocenHaslo(haslo) {
  const uwagi = [];
  let punkty = 0;

  // 1) Długość -- najważniejszy czynnik.
  if (haslo.length >= 12) {
    punkty += 2;
  } else if (haslo.length >= 8) {
    punkty += 1;
    uwagi.push("Wydłuż hasło do co najmniej 12 znaków.");
  } else {
    uwagi.push("Hasło jest za krótkie — użyj co najmniej 12 znaków.");
  }

  // 2) Różnorodność znaków (wyrażenia regularne sprawdzają obecność danego typu).
  if (/[a-z]/.test(haslo)) { punkty += 1; } else { uwagi.push("Dodaj małe litery."); }
  if (/[A-Z]/.test(haslo)) { punkty += 1; } else { uwagi.push("Dodaj wielkie litery."); }
  if (/[0-9]/.test(haslo)) { punkty += 1; } else { uwagi.push("Dodaj cyfry."); }
  // Znak specjalny = cokolwiek, co nie jest literą ani cyfrą.
  if (/[^a-zA-Z0-9]/.test(haslo)) { punkty += 1; } else { uwagi.push("Dodaj znak specjalny (np. ! ? # @)."); }

  // 3) Czy to jedno z najpopularniejszych haseł?
  if (NAJCZESTSZE_HASLA.has(haslo.toLowerCase())) {
    return {
      ocena: "Słabe", punkty: 0, maks: 6,
      uwagi: ["To jedno z najczęściej używanych haseł — zmień je natychmiast."],
    };
  }

  // Zamiana punktów na ocenę słowną.
  let ocena;
  if (punkty >= 5) { ocena = "Mocne"; }
  else if (punkty >= 3) { ocena = "Średnie"; }
  else { ocena = "Słabe"; }

  return { ocena: ocena, punkty: punkty, maks: 6, uwagi: uwagi };
}


// --- Obsługa kliknięć ---

// Generowanie hasła + przycisk kopiowania do schowka.
przyciskGeneruj.addEventListener("click", function () {
  // parseInt zamienia tekst z pola na liczbę; jeśli błędna -> używamy 16.
  let dlugosc = parseInt(dlugoscHasla.value, 10);
  if (isNaN(dlugosc) || dlugosc < 4) { dlugosc = 16; }
  if (dlugosc > 100) { dlugosc = 100; }

  const haslo = generujHaslo(dlugosc, znakiSpecjalne.checked);
  wynikGeneratora.className = "wynik dobry";
  // Pokazujemy hasło i mały przycisk do skopiowania.
  wynikGeneratora.innerHTML =
    "<code>" + haslo + "</code> " +
    "<button class='przycisk wtorny' id='kopiuj-haslo'>Kopiuj</button>";

  document.getElementById("kopiuj-haslo").addEventListener("click", function () {
    // navigator.clipboard kopiuje tekst do schowka systemowego.
    navigator.clipboard.writeText(haslo);
    this.textContent = "Skopiowano!";
  });
});

// Ocena siły wpisanego hasła.
przyciskOcen.addEventListener("click", function () {
  const haslo = hasloDoOceny.value;
  if (!haslo) {
    wynikOceny.className = "wynik";
    wynikOceny.textContent = "Najpierw wpisz hasło.";
    return;
  }

  const wynik = ocenHaslo(haslo);
  // Kolor zależny od oceny: mocne -> zielony, inaczej -> czerwony.
  wynikOceny.className = "wynik " + (wynik.ocena === "Mocne" ? "dobry" : "zly");

  let tekst = "Ocena: " + wynik.ocena + " (" + wynik.punkty + "/" + wynik.maks + ")";
  if (wynik.uwagi.length > 0) {
    // Doklejamy listę podpowiedzi jako wypunktowanie.
    tekst += "<ul>";
    wynik.uwagi.forEach(function (u) { tekst += "<li>" + u + "</li>"; });
    tekst += "</ul>";
  } else {
    tekst += " — świetnie, to hasło wygląda solidnie!";
  }
  wynikOceny.innerHTML = tekst;
});
