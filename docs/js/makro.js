// Optymalizator makro -- wersja przeglądarkowa.
// Odpowiednik narzedzia/kalkulator_makro.py. Wszystko liczone lokalnie.

// Pobieramy elementy strony.
const makroCena = document.getElementById("makro-cena");
const makroWaga = document.getElementById("makro-waga");
const makroBialko = document.getElementById("makro-bialko");
const makroCel = document.getElementById("makro-cel");
const makroLicz = document.getElementById("makro-licz");
const makroWynik = document.getElementById("makro-wynik");


// Liczy wszystkie wartości i zwraca je w obiekcie (jak w wersji Pythona).
function policzMakro(cena, waga, bialkoNa100g, cel) {
  // Ile gramów białka jest w całym produkcie.
  const bialkoTotal = (waga / 100) * bialkoNa100g;
  // Koszt 1 grama białka.
  const koszt1g = cena / bialkoTotal;
  // Ile produktu trzeba zjeść, by pokryć dzienny cel białka.
  const gramyNaCel = cel * 100 / bialkoNa100g;
  // Koszt pokrycia całego celu białkowego.
  const kosztCelu = koszt1g * cel;

  // Prosta ocena opłacalności na podstawie kosztu 1 g białka (progi orientacyjne).
  let ocena;
  if (koszt1g <= 0.08) { ocena = "Świetny stosunek ceny do białka"; }
  else if (koszt1g <= 0.15) { ocena = "Dobry stosunek ceny do białka"; }
  else if (koszt1g <= 0.25) { ocena = "Przeciętny — da się taniej"; }
  else { ocena = "Słaby — drogie źródło białka"; }

  return { bialkoTotal, koszt1g, gramyNaCel, kosztCelu, cel, ocena };
}


// Obsługa kliknięcia "Policz".
makroLicz.addEventListener("click", function () {
  // parseFloat zamienia tekst z pól na liczby.
  const cena = parseFloat(makroCena.value);
  const waga = parseFloat(makroWaga.value);
  const bialko = parseFloat(makroBialko.value);
  let cel = parseFloat(makroCel.value);
  if (isNaN(cel) || cel <= 0) { cel = 150; }

  // Walidacja: wszystkie pola muszą być sensownymi liczbami.
  if (isNaN(cena) || isNaN(waga) || isNaN(bialko)) {
    makroWynik.style.display = "block";
    makroWynik.innerHTML = "<div class='kat'>Uzupełnij cenę, wagę i białko liczbami.</div>";
    return;
  }
  if (bialko <= 0) {
    makroWynik.style.display = "block";
    makroWynik.innerHTML = "<div class='kat'>Białko na 100 g musi być większe od zera.</div>";
    return;
  }

  const w = policzMakro(cena, waga, bialko, cel);

  // toFixed(n) formatuje liczbę do n miejsc po przecinku. Math.round zaokrągla.
  makroWynik.style.display = "block";
  makroWynik.innerHTML =
    "<div>Białko w całym produkcie: <strong>" + w.bialkoTotal.toFixed(1) + " g</strong></div>" +
    "<div>Koszt 1 g białka: <span class='suma'>" + w.koszt1g.toFixed(3) + " zł</span></div>" +
    "<div class='kategorie'><span class='znacznik'>" + w.ocena + "</span></div>" +
    "<div style='margin-top:10px;'>Aby pokryć cel " + w.cel + " g białka z tego produktu:</div>" +
    "<div class='kat'>• trzeba zjeść ok. " + Math.round(w.gramyNaCel) + " g produktu</div>" +
    "<div class='kat'>• koszt białka na cel: ok. " + w.kosztCelu.toFixed(2) + " zł</div>";
});
