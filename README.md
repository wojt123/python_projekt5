
# Kototurniej - Quiz o Kotach 🐾
**Kototurniej** to aplikacja internetowa napisana w Pythonie z wykorzystaniem frameworka Flask. Główne założenie projektu to interaktywny quiz o kotach, w którym użytkownicy mogą sprawdzić swoją wiedzę i rywalizować z innymi w tabeli wyników.

## Funkcjonalności ✨
- **Rejestracja i logowanie użytkowników**: Bezpieczny system autoryzacji z wykorzystaniem Flask-Security.
- **Quiz jednokrotnego wyboru**: Interaktywne pytania z możliwością wyboru jednej poprawnej odpowiedzi.
- **Tabela wyników**: Lista najlepszych wyników w quizie.
- **Responsywny interfejs**: Stylowanie za pomocą Bootstrap.

## Jak uruchomić projekt? 🚀
1. **Sklonuj repozytorium**:
   ```bash
   git clone <link_do_repozytorium>
   cd <nazwa_katalogu>
   ```

2. **Zainstaluj wymagania**:
   Upewnij się, że masz zainstalowanego Pythona 3. Następnie wykonaj:
   ```bash
   pip install -r requirements.txt
   ```

3. **Uruchom serwer aplikacji**:
   ```bash
   python projekt_fakultet.py
   ```

4. **Otwórz w przeglądarce**:
   Przejdź do adresu wyświetlonego w konsoli.

## Wymagania systemowe 📋
Lista użytych bibliotek znajduje się w pliku `requirements.txt`. Kluczowe technologie to:
- Flask i jego rozszerzenia: Flask-Security, Flask-SQLAlchemy, Flask-WTF.
- Bootstrap 5: Responsywny frontend.
- SQLite: Lekka baza danych.

## Struktura projektu 📂
- **`projekt_fakultet.py`**: Główny plik aplikacji.
- **Szablony HTML**:
  - `base.html`: Szablon bazowy.
  - `index.html`: Strona główna.
  - `quiz.html`: Widok quizu.
  - `leaderboard.html`: Tabela wyników.
  - `login_user.html`: Widok logowania.
  - `register_user.html`: Widok rejestracji.
- **Baza danych**: Plik `quiz.db`.

## Autorzy 👨‍💻
- **Wojciech Franczak**
- **Adam Włodarski**
- **Dawid Hraniuk**

## Licencja 📄
Projekt jest udostępniony na licencji MIT.

---

Ciesz się Kototurniejem i sprawdź, jak dużo wiesz o kotach! 🐱
