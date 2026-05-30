// Śledzenie wydatków z zapisem w przeglądarce (localStorage).
// "Bezpiecznie i nieinwazyjnie": dane zostają tylko na urządzeniu użytkownika,
// nic nie jest wysyłane do żadnego serwera.

// Klucz, pod którym trzymamy wszystkie dane w pamięci przeglądarki.
const KLUCZ = "przybornik_wydatki";

// Pobieramy elementy strony.
const wyborOsoby = document.getElementById("wybor-osoby");
const przyciskDodajOsobe = document.getElementById("dodaj-osobe");
const opisWydatku = document.getElementById("opis-wydatku");
const kwotaWydatku = document.getElementById("kwota-wydatku");
const kategoriaWydatku = document.getElementById("kategoria-wydatku");
const przyciskDodajWydatek = document.getElementById("dodaj-wydatek");
const podsumowanie = document.getElementById("podsumowanie-wydatkow");
const listaWydatkow = document.getElementById("lista-wydatkow");


// --- Funkcje zapisu i odczytu danych ---

// Wczytuje wszystkie dane z pamięci przeglądarki. Zwraca obiekt {osoba: [wydatki]}.
function wczytajDane() {
  const surowe = localStorage.getItem(KLUCZ);
  // Jeśli nic nie ma -> zaczynamy od pustego obiektu.
  // JSON.parse zamienia zapisany tekst z powrotem na obiekt.
  return surowe ? JSON.parse(surowe) : {};
}

// Zapisuje dane do pamięci przeglądarki (jako tekst JSON).
function zapiszDane(dane) {
  localStorage.setItem(KLUCZ, JSON.stringify(dane));
}


// --- Obsługa osób (profili) ---

// Uzupełnia rozwijaną listę osób na podstawie zapisanych danych.
function odswiezListeOsob() {
  const dane = wczytajDane();
  const osoby = Object.keys(dane); // nazwy wszystkich zapisanych osób

  // Czyścimy listę i wstawiamy aktualne osoby.
  wyborOsoby.innerHTML = "";
  osoby.forEach(function (osoba) {
    const opcja = document.createElement("option");
    opcja.value = osoba;
    opcja.textContent = osoba;
    wyborOsoby.appendChild(opcja);
  });
}

// Dodaje nową osobę po kliknięciu przycisku.
function dodajOsobe() {
  // prompt pyta użytkownika o nazwę. .trim() usuwa spacje z brzegów.
  const nazwa = (prompt("Imię osoby:") || "").trim();
  if (!nazwa) { return; }

  const dane = wczytajDane();
  // Tworzymy pustą listę wydatków dla nowej osoby (jeśli jeszcze jej nie ma).
  if (!dane[nazwa]) {
    dane[nazwa] = [];
    zapiszDane(dane);
  }
  odswiezListeOsob();
  // Ustawiamy nowo dodaną osobę jako wybraną i pokazujemy jej wydatki.
  wyborOsoby.value = nazwa;
  pokazWydatki();
}


// --- Obsługa wydatków ---

// Dodaje wydatek dla aktualnie wybranej osoby.
function dodajWydatek() {
  const osoba = wyborOsoby.value;
  if (!osoba) {
    alert("Najpierw dodaj osobę.");
    return;
  }

  const opis = opisWydatku.value.trim();
  // parseFloat zamienia tekst z pola na liczbę.
  const kwota = parseFloat(kwotaWydatku.value);

  // Walidacja: opis nie może być pusty, a kwota musi być poprawną liczbą > 0.
  if (!opis) { alert("Wpisz, na co był wydatek."); return; }
  if (isNaN(kwota) || kwota <= 0) { alert("Wpisz poprawną kwotę."); return; }

  const dane = wczytajDane();
  dane[osoba].push({
    opis: opis,
    kwota: kwota,
    kategoria: kategoriaWydatku.value,
    // Zapisujemy datę, żeby można było pokazać, kiedy dodano wydatek.
    data: new Date().toLocaleDateString("pl-PL"),
  });
  zapiszDane(dane);

  // Czyścimy pola formularza i odświeżamy widok.
  opisWydatku.value = "";
  kwotaWydatku.value = "";
  pokazWydatki();
}

// Usuwa wydatek o danym numerze (indeksie) dla wybranej osoby.
function usunWydatek(indeks) {
  const osoba = wyborOsoby.value;
  const dane = wczytajDane();
  // splice usuwa jeden element z listy na podanej pozycji.
  dane[osoba].splice(indeks, 1);
  zapiszDane(dane);
  pokazWydatki();
}

// Wyświetla podsumowanie i listę wydatków wybranej osoby.
function pokazWydatki() {
  const osoba = wyborOsoby.value;
  const dane = wczytajDane();
  const wydatki = (osoba && dane[osoba]) ? dane[osoba] : [];

  // --- Podsumowanie: suma łączna + sumy per kategoria ---
  // reduce sumuje kwoty wszystkich wydatków.
  const suma = wydatki.reduce(function (razem, w) { return razem + w.kwota; }, 0);

  // Liczymy sumy w rozbiciu na kategorie.
  const perKategoria = {};
  wydatki.forEach(function (w) {
    perKategoria[w.kategoria] = (perKategoria[w.kategoria] || 0) + w.kwota;
  });

  // Budujemy "znaczniki" kategorii jako tekst HTML.
  let znaczniki = "";
  Object.keys(perKategoria).forEach(function (kat) {
    znaczniki += "<span class='znacznik'>" + kat + ": " +
      perKategoria[kat].toFixed(2) + " zł</span>";
  });

  podsumowanie.innerHTML =
    "<div>Razem wydano:</div>" +
    "<div class='suma'>" + suma.toFixed(2) + " zł</div>" +
    "<div class='kategorie'>" + znaczniki + "</div>";

  // --- Lista pojedynczych wydatków ---
  listaWydatkow.innerHTML = "";
  if (wydatki.length === 0) {
    listaWydatkow.innerHTML = "<li class='pusto'>Brak wydatków. Dodaj pierwszy powyżej.</li>";
    return;
  }

  wydatki.forEach(function (w, indeks) {
    const element = document.createElement("li");
    element.innerHTML =
      "<span class='opis'>" + w.opis +
      " <span class='kat'>(" + w.kategoria + ", " + w.data + ")</span></span>" +
      "<span class='kwota'>" + w.kwota.toFixed(2) + " zł</span>" +
      "<button class='usun' title='Usuń'>✕</button>";
    // Podpinamy usuwanie do przycisku przy tym konkretnym wydatku.
    element.querySelector(".usun").addEventListener("click", function () {
      usunWydatek(indeks);
    });
    listaWydatkow.appendChild(element);
  });
}


// --- Podpięcie zdarzeń i pierwsze uruchomienie ---
przyciskDodajOsobe.addEventListener("click", dodajOsobe);
przyciskDodajWydatek.addEventListener("click", dodajWydatek);
// Gdy zmienimy osobę na liście -> pokaż jej wydatki.
wyborOsoby.addEventListener("change", pokazWydatki);

// Na starcie wczytujemy listę osób i pokazujemy wydatki (jeśli są zapisane).
odswiezListeOsob();
pokazWydatki();
