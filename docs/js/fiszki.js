// Generator fiszek z tekstu -- wersja przeglądarkowa.
// Odpowiednik narzedzia/ekstraktor_slowek.py. Plik czytamy LOKALNIE w
// przeglądarce (nic nie jest wysyłane), a wynik pobieramy jako plik CSV.

// Pobieramy elementy strony.
const fiszkiPlik = document.getElementById("fiszki-plik");
const fiszkiTekst = document.getElementById("fiszki-tekst");
const fiszkiJezyk = document.getElementById("fiszki-jezyk");
const fiszkiIle = document.getElementById("fiszki-ile");
const fiszkiGeneruj = document.getElementById("fiszki-generuj");
const fiszkiPobierz = document.getElementById("fiszki-pobierz");
const fiszkiWynik = document.getElementById("fiszki-wynik");

// Listy słów pospolitych (stop words), które pomijamy -- jak w wersji Pythona.
const STOP_WORDS = {
  pl: new Set(["i","w","na","z","do","to","się","że","nie","jest","a","o","od","po","za","co","jak","ale","czy","the","lub","oraz","tym","ten","ta","te","był","była","było","są","być","go"]),
  en: new Set(["the","a","an","and","or","but","of","to","in","on","for","is","are","was","were","be","this","that","it","as","with","at","by","from","has","have","had","you","i","we","they"]),
  fr: new Set(["le","la","les","un","une","des","de","du","et","ou","à","en","dans","que","qui","ne","pas","est","sont","ce","se","pour","par","sur","il","elle","nous","vous","ils","au","aux"]),
};

// Tu trzymamy ostatnio wygenerowane pary [slowo, liczba] -- do pobrania CSV.
let ostatnieFiszki = [];


// Liczy najczęstsze słowa w tekście. Zwraca posortowaną listę [slowo, liczba].
function policzSlowa(tekst, jezyk, minDlugosc) {
  tekst = tekst.toLowerCase();

  // Wzorzec dopasowuje ciągi liter (także z ogonkami/akcentami), bez cyfr.
  // \p{L} oznacza "dowolna litera Unicode"; flaga u włącza tryb Unicode.
  const slowa = tekst.match(/\p{L}+/gu) || [];

  // Budujemy zbiór słów do pominięcia.
  let doPominiecia;
  if (jezyk === "auto") {
    // Łączymy wszystkie listy w jeden zbiór.
    doPominiecia = new Set([...STOP_WORDS.pl, ...STOP_WORDS.en, ...STOP_WORDS.fr]);
  } else {
    doPominiecia = STOP_WORDS[jezyk] || new Set();
  }

  // Liczymy wystąpienia w zwykłym obiekcie (mapa słowo -> liczba).
  const licznik = {};
  slowa.forEach(function (s) {
    if (s.length >= minDlugosc && !doPominiecia.has(s)) {
      licznik[s] = (licznik[s] || 0) + 1;
    }
  });

  // Zamieniamy obiekt na listę par i sortujemy malejąco po liczbie wystąpień.
  return Object.entries(licznik).sort(function (a, b) { return b[1] - a[1]; });
}


// Buduje zawartość pliku CSV (z nagłówkiem i pustą kolumną na tłumaczenie).
function zbudujCsv(pary) {
  let tekst = "slowo,tlumaczenie,liczba_wystapien\n";
  pary.forEach(function (p) {
    // Słowo w cudzysłowie na wypadek nietypowych znaków; tłumaczenie puste.
    tekst += '"' + p[0] + '",,' + p[1] + "\n";
  });
  return tekst;
}


// Wspólna funkcja: bierze tekst, generuje fiszki i pokazuje podgląd.
function generujZTekstu(tekst) {
  if (!tekst || !tekst.trim()) {
    fiszkiWynik.style.display = "block";
    fiszkiWynik.innerHTML = "<div class='kat'>Wczytaj plik lub wklej tekst.</div>";
    fiszkiPobierz.style.display = "none";
    return;
  }

  let ile = parseInt(fiszkiIle.value, 10);
  if (isNaN(ile) || ile < 1) { ile = 30; }

  // slice(0, ile) bierze tylko tyle najczęstszych słów, ile wybrano.
  ostatnieFiszki = policzSlowa(tekst, fiszkiJezyk.value, 3).slice(0, ile);

  if (ostatnieFiszki.length === 0) {
    fiszkiWynik.style.display = "block";
    fiszkiWynik.innerHTML = "<div class='kat'>Nie znaleziono słów do zapisania.</div>";
    fiszkiPobierz.style.display = "none";
    return;
  }

  // Pokazujemy podgląd jako "znaczniki" słowo + liczba.
  let podglad = "<div>Znaleziono " + ostatnieFiszki.length + " słów:</div><div class='kategorie'>";
  ostatnieFiszki.forEach(function (p) {
    podglad += "<span class='znacznik'>" + p[0] + " (" + p[1] + ")</span>";
  });
  podglad += "</div>";
  fiszkiWynik.style.display = "block";
  fiszkiWynik.innerHTML = podglad;
  // Odsłaniamy przycisk pobierania CSV.
  fiszkiPobierz.style.display = "inline-block";
}


// --- Obsługa zdarzeń ---

// Gdy użytkownik wybierze plik -> wczytujemy jego treść lokalnie.
fiszkiPlik.addEventListener("change", function () {
  const plik = fiszkiPlik.files[0];
  if (!plik) { return; }
  // FileReader czyta plik w przeglądarce; nic nie wychodzi na zewnątrz.
  const reader = new FileReader();
  reader.onload = function () {
    // Wczytaną treść wstawiamy też do pola tekstowego (dla podglądu/edycji).
    fiszkiTekst.value = reader.result;
  };
  reader.readAsText(plik, "utf-8");
});

// Klik "Generuj" -> bierzemy tekst z pola (albo wczytany z pliku).
fiszkiGeneruj.addEventListener("click", function () {
  generujZTekstu(fiszkiTekst.value);
});

// Klik "Pobierz CSV" -> tworzymy plik do pobrania w przeglądarce.
fiszkiPobierz.addEventListener("click", function () {
  const csv = zbudujCsv(ostatnieFiszki);
  // Blob to "plik w pamięci"; tworzymy do niego tymczasowy link i klikamy go.
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fiszki.csv";
  link.click();
  URL.revokeObjectURL(url);   // sprzątamy po sobie
});
