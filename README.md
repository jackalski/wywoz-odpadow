# Waste Collection - Home Assistant Integration
[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/jackalski/wywoz-odpadow/blob/master/README.md)
[![pl](https://img.shields.io/badge/lang-pl-red.svg)](https://github.com/jackalski/wywoz-odpadow/blob/master/README.pl.md)

[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
![downloads][downloads-badge]
![Build][build-badge]

<a href="https://www.buymeacoffee.com/jackalski" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

Home Assistant integration for waste collection schedules in Warsaw.

## Description

This integration allows automatic retrieval of waste collection schedules for addresses in Warsaw from the [Warszawa 19115](https://warszawa19115.pl/) portal. The integration automatically updates data and provides it as a sensor and calendar.

## Features

- 🔍 Address search by postal code
- 📅 Calendar with waste collection schedule
- 📊 Sensor showing days until next collection
- 🌍 Multi-language support (PL, EN, DE, FR, UK, BE, ZH, VI)
- 🔄 Automatic data updates (1-7 days)

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations
3. Click menu (⋮) → Custom repositories
4. Add repository:
   - URL: `https://github.com/jackalski/wywoz-odpadow`
   - Category: Integration
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `wywoz_odpadow` folder to `custom_components/` in your Home Assistant configuration directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services → Add Integration

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Waste Collection** (Wywóz Odpadów)
3. Enter postal code in format `##-###` (e.g., `02-001`)
4. Select address from the list
5. Set update interval (1-7 days)
6. Click **Submit**

## Usage with TrashCard

**We recommend using [TrashCard](https://github.com/amaximus/trash-card) as a dashboard element** for the best user experience.

TrashCard is a beautiful Lovelace card that visually presents the waste collection schedule. The integration is fully compatible with TrashCard and automatically maps fraction types.

### TrashCard Installation

1. Install TrashCard via HACS or manually
2. Add card to dashboard:

```yaml
type: custom:trash-card
entities:
  - entity: sensor.wywoz_odpadow_wywóz_odpadow
    name: Waste Collection
```

### Fraction Mapping

The integration automatically maps waste types to the format required by TrashCard:
- `waste` - Mixed waste
- `paper` - Paper and cardboard
- `recycle` - Glass
- `organic` - Biodegradable waste
- `others` - Bulky waste

## Available Entities

### Sensor

- **Name**: `sensor.wywoz_odpadow_wywóz_odpadow`
- **State**: Number of days until next waste collection
- **Attributes**:
  - `update_interval`: Update interval in days

### Calendar

- **Name**: `calendar.wywoz_odpadow_wywóz_odpadow`
- **Events**: All scheduled waste collections with fraction type description

## Language Support

The integration supports the following languages:
- 🇵🇱 Polish (default)
- 🇬🇧 English (EN, EN-US, EN-GB)
- 🇩🇪 German
- 🇫🇷 French
- 🇺🇦 Ukrainian
- 🇧🇾 Belarusian
- 🇨🇳 Chinese
- 🇻🇳 Vietnamese

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.11 or newer
- Internet connection

## Reporting Issues

If you encounter any problems, please report them in [Issues](https://github.com/jackalski/wywoz-odpadow/issues).

## License

This project is licensed under the GPL-3.0 license - see the [LICENSE](LICENSE) file for details.

## Authors

- [@jackalski](https://github.com/jackalski)

## Acknowledgments

- [Warszawa 19115](https://warszawa19115.pl/) portal for providing the API
- [TrashCard](https://github.com/amaximus/trash-card) for the excellent Lovelace card

