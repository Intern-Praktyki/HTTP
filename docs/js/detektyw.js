// Detektyw haseł w przeglądarce.
// Działa dokładnie jak wersja w Pythonie: liczy skrót SHA-1 hasła, a do
// serwera wysyła TYLKO 5 pierwszych znaków skrótu (model k-anonimowości).
// Dzięki temu hasło nigdy nie opuszcza przeglądarki użytkownika.

// Pobieramy elementy strony, z którymi będziemy pracować.
const poleHasla = document.getElementById("pole-hasla");
const przyciskSprawdz = document.getElementById("sprawdz-haslo");
const wynikHasla = document.getElementById("wynik-hasla");


// Liczy skrót SHA-1 tekstu i zwraca go WIELKIMI literami (jak chce API).
// crypto.subtle to wbudowany, bezpieczny moduł kryptograficzny przeglądarki.
async function sha1Hex(tekst) {
  // Zamieniamy tekst na bajty (UTF-8), bo funkcja skrótu działa na bajtach.
  const bajty = new TextEncoder().encode(tekst);
  const buforSkrotu = await crypto.subtle.digest("SHA-1", bajty);
  // Zamieniamy bajty skrótu na ciąg znaków szesnastkowych (hex).
  return Array.from(new Uint8Array(buforSkrotu))
    .map(function (b) { return b.toString(16).padStart(2, "0"); })
    .join("")
    .toUpperCase();
}


// Główna funkcja: sprawdza podane hasło i wyświetla wynik.
async function sprawdzHaslo() {
  const haslo = poleHasla.value;

  // Pusty wpis -> nic nie robimy, tylko prosimy o hasło.
  if (!haslo) {
    wynikHasla.className = "wynik";
    wynikHasla.textContent = "Najpierw wpisz hasło.";
    return;
  }

  // Informujemy, że trwa sprawdzanie (zapytanie sieciowe chwilę zajmuje).
  wynikHasla.className = "wynik ladowanie";
  wynikHasla.textContent = "Sprawdzam...";

  try {
    // 1) Liczymy skrót i dzielimy go na prefiks (5 znaków) i resztę.
    const skrot = await sha1Hex(haslo);
    const prefiks = skrot.slice(0, 5);
    const reszta = skrot.slice(5);

    // 2) Pytamy API tylko o prefiks -- to jest właśnie k-anonimowość.
    const odpowiedz = await fetch("https://api.pwnedpasswords.com/range/" + prefiks);
    const tekst = await odpowiedz.text();

    // 3) Szukamy naszej końcówki w odpowiedzi (linie "KONCOWKA:ILE").
    let ile = 0;
    tekst.split("\n").forEach(function (linia) {
      const czesci = linia.trim().split(":");
      if (czesci[0] === reszta) {
        ile = parseInt(czesci[1], 10);
      }
    });

    // 4) Pokazujemy wynik w czytelnej formie.
    if (ile > 0) {
      wynikHasla.className = "wynik zly";
      // toLocaleString formatuje liczbę z odstępami, np. 3 055 216.
      wynikHasla.textContent =
        "⚠️ To hasło pojawiło się w wyciekach " + ile.toLocaleString("pl-PL") +
        " razy! Nie używaj go.";
    } else {
      wynikHasla.className = "wynik dobry";
      wynikHasla.textContent =
        "✅ Tego hasła nie ma w znanych wyciekach. (Nie znaczy to, że jest mocne.)";
    }
  } catch (blad) {
    // Najczęstsza przyczyna: brak internetu albo blokada zapytania.
    wynikHasla.className = "wynik zly";
    wynikHasla.textContent = "Nie udało się sprawdzić — sprawdź połączenie z internetem.";
  }
}

// Reagujemy na kliknięcie przycisku oraz na wciśnięcie Enter w polu.
przyciskSprawdz.addEventListener("click", sprawdzHaslo);
poleHasla.addEventListener("keydown", function (zdarzenie) {
  if (zdarzenie.key === "Enter") { sprawdzHaslo(); }
});
