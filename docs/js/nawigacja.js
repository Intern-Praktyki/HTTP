// Obsługa przełączania zakładek (Start / Detektyw / Wydatki).
// Każdy przycisk z atrybutem data-zakladka pokazuje sekcję o tym samym id.

// Funkcja pokazująca wybraną zakładkę i chowająca pozostałe.
function pokazZakladke(nazwa) {
  // Chowamy wszystkie sekcje, potem pokazujemy tę wybraną.
  document.querySelectorAll(".zakladka").forEach(function (sekcja) {
    sekcja.classList.remove("aktywna");
  });
  const wybrana = document.getElementById(nazwa);
  if (wybrana) {
    wybrana.classList.add("aktywna");
  }

  // Podświetlamy odpowiedni przycisk w górnym menu.
  document.querySelectorAll(".link-nawigacji").forEach(function (link) {
    // classList.toggle z drugim argumentem ustawia klasę zależnie od warunku.
    link.classList.toggle("aktywny", link.dataset.zakladka === nazwa);
  });

  // Przewijamy na górę, żeby było widać początek nowej zakładki.
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Podpinamy klik do KAŻDEGO elementu z data-zakladka (menu i przyciski na kartach).
document.querySelectorAll("[data-zakladka]").forEach(function (element) {
  element.addEventListener("click", function () {
    pokazZakladke(element.dataset.zakladka);
  });
});
