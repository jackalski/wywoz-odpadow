"""Data update coordinator for Wywóz Odpadów."""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers import translation
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_BASE_URL,
    API_PARAMS,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    FRACTION_TYPE_MAPPING,
)

_LOGGER = logging.getLogger(__name__)


class WywozOdpadowDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        address_point_id: int,
        update_interval: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        self.address_point_id = address_point_id
        # Store update interval in seconds for reference, but don't set it as attribute
        # because DataUpdateCoordinator expects update_interval to be a timedelta
        self._update_interval_seconds = update_interval
        self._fraction_translations: dict[str, str] = {}

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        # Load translations if not already loaded
        if not self._fraction_translations:
            await self._load_fraction_translations()
        
        # Build API URL
        params = API_PARAMS.copy()
        params[
            f"_portalCKMjunkschedules_WAR_portalCKMjunkschedulesportlet_INSTANCE_o5AIb2mimbRJ_addressPointId"
        ] = str(self.address_point_id)

        url = f"{API_BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        
        _LOGGER.debug("Fetching data for address_point_id: %s", self.address_point_id)
        _LOGGER.debug("Request URL: %s", url)

        async with aiohttp.ClientSession() as session:
            try:
                _LOGGER.debug("Sending GET request to API")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    _LOGGER.debug("Response status: %s", response.status)
                    
                    if response.status != 200:
                        response_text = await response.text()
                        _LOGGER.error(
                            "API returned non-200 status: %s. Response body: %s",
                            response.status,
                            response_text[:500]  # Limit log size
                        )
                        raise UpdateFailed(f"API returned status {response.status}")

                    # Try to parse JSON - API may return JSON with wrong Content-Type header
                    content_type = response.headers.get("Content-Type", "").lower()
                    _LOGGER.debug("Response Content-Type: %s", content_type)
                    
                    _LOGGER.debug("Parsing JSON response")
                    try:
                        # Try to parse as JSON first (even if Content-Type is wrong)
                        json_data = await response.json()
                    except aiohttp.ContentTypeError as err:
                        # API returned wrong Content-Type, but might still be JSON
                        # Read the response text to check
                        response_text = await response.text()
                        _LOGGER.debug(
                            "ContentTypeError, but checking if response is actually JSON. Content-Type: %s. Response preview: %s",
                            content_type,
                            response_text[:200]
                        )
                        
                        # Check if response looks like JSON (starts with [ or {)
                        response_text_stripped = response_text.strip()
                        if response_text_stripped.startswith(("[", "{")):
                            # Looks like JSON, try to parse it manually
                            import json
                            try:
                                json_data = json.loads(response_text)
                                _LOGGER.info("Successfully parsed JSON despite wrong Content-Type header")
                            except json.JSONDecodeError as json_err:
                                _LOGGER.error(
                                    "Response looks like JSON but failed to parse: %s. Response body: %s",
                                    json_err,
                                    response_text[:1000]
                                )
                                raise UpdateFailed(
                                    f"API returned invalid JSON response. This may indicate an invalid address_point_id."
                                ) from json_err
                        else:
                            # Looks like HTML or other non-JSON content
                            _LOGGER.error(
                                "API returned non-JSON content (Content-Type: %s). Response body: %s",
                                content_type,
                                response_text[:1000]  # Limit log size
                            )
                            raise UpdateFailed(
                                f"API returned HTML instead of JSON. This may indicate an invalid address_point_id or API endpoint issue."
                            ) from err
                    except Exception as parse_err:
                        # Other parsing errors
                        response_text = await response.text()
                        _LOGGER.error(
                            "Failed to parse JSON response. Error: %s. Content-Type: %s. Response body: %s",
                            parse_err,
                            content_type,
                            response_text[:1000]
                        )
                        raise UpdateFailed(
                            f"API returned invalid JSON response. This may indicate an invalid address_point_id."
                        ) from parse_err
                    
                    _LOGGER.debug("Received JSON data length: %s items", len(json_data) if isinstance(json_data, list) else "N/A")

                    if not json_data or not isinstance(json_data, list):
                        _LOGGER.error("Invalid response format. Expected list, got: %s", type(json_data))
                        raise UpdateFailed("Invalid response format from API")

                    # Process the data
                    _LOGGER.debug("Processing data")
                    processed_data = self._process_data(json_data)
                    _LOGGER.debug("Processed %s events", len(processed_data.get("events", [])))
                    return processed_data

            except asyncio.TimeoutError as err:
                _LOGGER.error("Timeout communicating with API: %s", err)
                raise UpdateFailed(f"Timeout communicating with API: {err}") from err
            except aiohttp.ServerTimeoutError as err:
                _LOGGER.error("Server timeout error: %s", err)
                raise UpdateFailed(f"Server timeout: {err}") from err
            except aiohttp.ContentTypeError as err:
                _LOGGER.error("ContentTypeError: API returned non-JSON content. URL: %s", url)
                _LOGGER.error("ContentTypeError details: %s", err)
                raise UpdateFailed(
                    f"API returned HTML instead of JSON. This may indicate an invalid address_point_id or API endpoint issue."
                ) from err
            except aiohttp.ClientConnectorError as err:
                _LOGGER.error("Connection error to API: %s", err)
                raise UpdateFailed(f"Connection error: {err}") from err
            except aiohttp.ClientResponseError as err:
                _LOGGER.error("Client response error: %s (status: %s)", err, err.status)
                raise UpdateFailed(f"API response error: {err}") from err
            except aiohttp.ClientError as err:
                _LOGGER.error("Client error communicating with API: %s (type: %s)", err, type(err).__name__)
                raise UpdateFailed(f"Error communicating with API: {err}") from err
            except Exception as err:
                _LOGGER.exception("Unexpected error during data update: %s", err)
                raise UpdateFailed(f"Unexpected error: {err}") from err

    def _process_data(self, json_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Process raw JSON data into structured format."""
        if not json_data:
            return {
                "address": None,
                "district": None,
                "events": [],
                "fractions": {},
            }

        # Get first entry (should be only one for a specific address)
        data = json_data[0]

        address = data.get("adres", "")
        district = data.get("dzielnicy", "")
        harmonogramy = data.get("harmonogramy", [])

        # Process events for calendar
        events = []
        fractions = {}  # fraction_id -> fraction data

        now = dt_util.now().date()

        for item in harmonogramy:
            event_date_str = item.get("data", "")
            frakcja = item.get("frakcja", {})
            fraction_id = frakcja.get("id_frakcja", "")
            fraction_name = frakcja.get("nazwa", "")

            if not event_date_str or not fraction_id:
                continue

            try:
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                _LOGGER.warning(f"Invalid date format: {event_date_str}")
                continue

            # Translate fraction name
            translated_name = self._translate_fraction_name(fraction_name)
            
            # Only include future events or today
            if event_date >= now:
                events.append(
                    {
                        "start": event_date,
                        "end": event_date,
                        "summary": translated_name,
                        "description": f"Wywóz: {translated_name}",
                        "fraction_id": fraction_id,
                        "fraction_name": translated_name,
                    }
                )

            # Track fractions for sensor attributes
            if fraction_id not in fractions:
                fractions[fraction_id] = {
                    "id": fraction_id,
                    "name": translated_name,
                    "type": FRACTION_TYPE_MAPPING.get(fraction_name, "custom"),
                    "next_date": None,
                    "days_until": None,
                }

        # Sort events by date
        events.sort(key=lambda x: x["start"])

        # Calculate next date and days until for each fraction
        for fraction_id, fraction_data in fractions.items():
            fraction_events = [
                e for e in events if e["fraction_id"] == fraction_id and e["start"] >= now
            ]
            if fraction_events:
                next_event = fraction_events[0]
                next_date = next_event["start"]
                days_until = (next_date - now).days

                fraction_data["next_date"] = next_date.isoformat()
                fraction_data["days_until"] = days_until

        return {
            "address": address,
            "district": district,
            "events": events,
            "fractions": fractions,
        }

    async def _load_fraction_translations(self) -> None:
        """Load fraction translations from Home Assistant translations."""
        try:
            # Get translations for the current language
            translations = await translation.async_get_translations(
                self.hass, self.hass.config.language, "config", [DOMAIN]
            )
            if translations and DOMAIN in translations:
                domain_translations = translations[DOMAIN]
                # Get translations from config.fractions section (fractions is now inside config)
                if "config" in domain_translations and isinstance(domain_translations["config"], dict):
                    config_translations = domain_translations["config"]
                    if "fractions" in config_translations:
                        self._fraction_translations = config_translations["fractions"]
        except Exception:
            # If translation loading fails, use empty dict (will return original names)
            self._fraction_translations = {}

    def _fraction_name_to_snake_case(self, fraction_name: str) -> str:
        """Convert fraction name from API to snake_case key for translations."""
        # Convert to lowercase, replace spaces and special chars with underscores
        # Remove parentheses and their content, then clean up multiple underscores
        key = fraction_name.lower()
        # Remove parentheses and their content
        key = re.sub(r'\s*\([^)]*\)\s*', '_', key)
        # Replace spaces and special characters with underscores
        key = re.sub(r'[^a-z0-9]+', '_', key)
        # Remove multiple consecutive underscores
        key = re.sub(r'_+', '_', key)
        # Remove leading/trailing underscores
        key = key.strip('_')
        return key

    def _translate_fraction_name(self, fraction_name: str) -> str:
        """Translate fraction name using loaded translations."""
        # Convert fraction name to snake_case key
        snake_case_key = self._fraction_name_to_snake_case(fraction_name)
        # Look up translation using snake_case key
        translated = self._fraction_translations.get(snake_case_key, fraction_name)
        return translated

