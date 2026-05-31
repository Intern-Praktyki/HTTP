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

  // Zapisujemy wybraną zakładkę w adresie (np. #makro), żeby dało się
  // linkować bezpośrednio do konkretnego narzędzia.
  if (window.location.hash !== "#" + nazwa) {
    history.replaceState(null, "", "#" + nazwa);
  }

  // Przewijamy na górę, żeby było widać początek nowej zakładki.
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Podpinamy klik do KAŻDEGO elementu z data-zakladka (menu i przyciski na kartach).
document.querySelectorAll("[data-zakladka]").forEach(function (element) {
  element.addEventListener("click", function () {
    pokazZakladke(element.dataset.zakladka);
  });
});

// Deep-link: jeśli wejdziemy z adresem #nazwa (np. #fiszki), pokazujemy
// od razu tę zakładkę. Działa też przy zmianie adresu (wstecz/dalej).
function zakladkaZAdresu() {
  const nazwa = window.location.hash.replace("#", "");
  if (nazwa && document.getElementById(nazwa)) {
    pokazZakladke(nazwa);
  }
}

if (document.readyState === "loading") {
  window.addEventListener("DOMContentLoaded", zakladkaZAdresu);
} else {
  zakladkaZAdresu();
}
window.addEventListener("hashchange", zakladkaZAdresu);
