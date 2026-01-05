# Wywóz Odpadów - Home Assistant Integration
[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/jackalski/wywoz-odpadow/blob/master/README.md)

[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
![downloads][downloads-badge]
![Build][build-badge]

<a href="https://www.buymeacoffee.com/jackalski" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

Integracja Home Assistant dla harmonogramów wywozu odpadów w Warszawie.

## Opis

Ta integracja pozwala na automatyczne pobieranie harmonogramów wywozu odpadów dla adresów w Warszawie z portalu [Warszawa 19115](https://warszawa19115.pl/). Integracja automatycznie aktualizuje dane i udostępnia je jako sensor oraz kalendarz.

## Funkcje

- 🔍 Wyszukiwanie adresów po kodzie pocztowym
- 📅 Kalendarz z harmonogramem wywozu odpadów
- 📊 Sensor pokazujący dni do najbliższego wywozu
- 🌍 Wsparcie dla wielu języków (PL, EN, DE, FR, UK, BE, ZH, VI)
- 🔄 Automatyczna aktualizacja danych (1-7 dni)

## Instalacja

### HACS (Zalecane)

1. Upewnij się, że masz zainstalowany [HACS](https://hacs.xyz/)
2. Przejdź do HACS → Integracje
3. Kliknij menu (⋮) → Custom repositories
4. Dodaj repozytorium:
   - URL: `https://github.com/jackalski/wywoz-odpadow`
   - Kategoria: Integration
5. Kliknij "Zainstaluj"
6. Przeładuj Home Assistant

### Instalacja ręczna

1. Skopiuj folder `wywoz_odpadow` do `custom_components/` w katalogu konfiguracji Home Assistant
2. Przeładuj Home Assistant
3. Dodaj integrację przez Ustawienia → Urządzenia i usługi → Dodaj integrację

## Konfiguracja

1. Przejdź do **Ustawienia** → **Urządzenia i usługi** → **Dodaj integrację**
2. Wyszukaj **Wywóz Odpadów**
3. Wprowadź kod pocztowy w formacie `##-###` (np. `02-001`)
4. Wybierz adres z listy
5. Ustaw interwał aktualizacji (1-7 dni)
6. Kliknij **Prześlij**

## Użycie z TrashCard

**Zalecamy użycie [TrashCard](https://github.com/amaximus/trash-card) jako elementu dashboardu** dla najlepszego doświadczenia użytkownika.

TrashCard to piękna karta Lovelace, która wizualnie prezentuje harmonogram wywozu odpadów. Integracja jest w pełni kompatybilna z TrashCard i automatycznie mapuje typy frakcji.

### Instalacja TrashCard

1. Zainstaluj TrashCard przez HACS lub ręcznie
2. Dodaj kartę do dashboardu:

```yaml
type: custom:trash-card
entities:
  - entity: sensor.wywoz_odpadow_wywóz_odpadow
    name: Wywóz Odpadów
```

### Mapowanie frakcji

Integracja automatycznie mapuje typy odpadów do formatu wymaganego przez TrashCard:
- `waste` - Odpady zmieszane
- `paper` - Papier i tektura
- `recycle` - Szkło
- `organic` - Odpady biodegradowalne
- `others` - Odpady wielkogabarytowe

## Dostępne encje

### Sensor

- **Nazwa**: `sensor.wywoz_odpadow_wywóz_odpadow`
- **Stan**: Liczba dni do najbliższego wywozu odpadów
- **Atrybuty**:
  - `update_interval`: Interwał aktualizacji w dniach

### Kalendarz

- **Nazwa**: `calendar.wywoz_odpadow_wywóz_odpadow`
- **Zdarzenia**: Wszystkie zaplanowane wywozy odpadów z opisem typu frakcji

## Wsparcie języków

Integracja obsługuje następujące języki:
- 🇵🇱 Polski (domyślny)
- 🇬🇧 Angielski (EN, EN-US, EN-GB)
- 🇩🇪 Niemiecki
- 🇫🇷 Francuski
- 🇺🇦 Ukraiński
- 🇧🇾 Białoruski
- 🇨🇳 Chiński
- 🇻🇳 Wietnamski

## Wymagania

- Home Assistant 2024.1.0 lub nowszy
- Python 3.11 lub nowszy
- Połączenie z internetem

## Zgłaszanie problemów

Jeśli napotkasz problemy, zgłoś je w [Issues](https://github.com/jackalski/wywoz-odpadow/issues).

## Licencja

Ten projekt jest licencjonowany na licencji GPL-3.0 - zobacz plik [LICENSE](LICENSE) dla szczegółów.

## Autorzy

- [@jackalski](https://github.com/jackalski)

## Podziękowania

- Portal [Warszawa 19115](https://warszawa19115.pl/) za udostępnienie API
- [TrashCard](https://github.com/amaximus/trash-card) za wspaniałą kartę Lovelace

