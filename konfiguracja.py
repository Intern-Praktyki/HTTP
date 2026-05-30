# -*- coding: utf-8 -*-
"""
Konfiguracja strony WWW (wersji webowej przybornika).

To jedyne miejsce, w którym zmieniasz ustawienia uruchamiania strony.
Plik jest celowo prosty -- to zwykłe wartości, które możesz edytować ręcznie.
"""

# Port, na którym wystartuje lokalny serwer strony.
# Adres będzie wtedy: http://localhost:PORT
PORT = 8000

# Czy po starcie automatycznie otworzyć stronę w przeglądarce?
# True -> otwiera samo; False -> tylko wypisze adres do skopiowania.
AUTO_OTWORZ = True

# Folder, w którym leży strona (HTML/CSS/JS). Domyślnie "docs".
# Zmieniaj tylko, jeśli przeniesiesz pliki strony gdzie indziej.
FOLDER_STRONY = "docs"
