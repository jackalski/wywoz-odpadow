# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2025-03-02

### Fixed
- **Sensors**: Fraction sensors now show the translated fraction name (e.g. "Paper and cardboard packaging" instead of raw API name). Name is read from coordinator data and updated on refresh.
- **Translations**: Coordinator now loads fraction translations from both nested (`common.fraction_OP`) and flat (`common.fraction_OP` in some HA versions) translation structures.

---

## [1.2.0] - 2025-03-02

### Changed
- **Translations**: Fraction keys now use API `id_frakcja` (OP, MT, OS, OZ, BK, WG, ZM) instead of snake_case names derived from `nazwa`
- **Coordinator**: Translates by `fraction_id` with fallback to API name; removed `_fraction_name_to_snake_case`
- **TrashCard**: `FRACTION_TYPE_MAPPING` in `const.py` is now keyed by `id_frakcja` for stable type mapping

---

## [1.1.0] - 2025-03-02

### Fixed
- **Translations**: Flattened `common.fractions` to `common.fraction_*` string keys so translation files pass Home Assistant validation (values must be strings)
- **Coordinator**: Fraction name translations now read from flat `fraction_*` keys under `common`
- **HACS**: Removed `custom_components/brand` so the repo has a single integration and passes hassfest (domain matches dir name, IoT class present)

### Changed
- Translation JSON structure in `strings.json` and all `translations/*.json` (fraction keys under `common` are now flat)

---

## [1.0.0] - 2024-01-XX

### Added
- Initial release
- Config flow with postal code and address selection
- Calendar integration for waste collection schedule
- Sensor showing days until next collection
- Multi-language support (PL, EN, DE, FR, UK, BE, ZH, VI)
- Automatic data updates (1-7 days interval)
- TrashCard compatibility with fraction type mapping
- Translation support for waste fraction names
- Validation for empty schedules
- Error handling and logging

### Features
- Search addresses by postal code
- Automatic address dropdown population
- Update interval configuration (1-7 days, integers only)
- Fraction name translations
- Device info with address name
- Comprehensive error messages

