"""Config flow for Wywóz Odpadów integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    API_AUTOCOMPLETE_PARAMS,
    API_BASE_URL,
    API_PARAMS,
    CONF_ADDRESS_POINT_ID,
    CONF_POSTAL_CODE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL_DAYS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def search_addresses(hass: HomeAssistant, postal_code: str) -> list[dict[str, Any]]:
    """Search for addresses using autocomplete API with postal code filter."""
    params = API_AUTOCOMPLETE_PARAMS.copy()
    
    # Add postal code parameter if provided
    if postal_code:
        # Remove dashes from postal code for API (format: ##-###)
        postal_code_clean = postal_code.replace("-", "")
        params[
            "_portalCKMjunkschedules_WAR_portalCKMjunkschedulesportlet_INSTANCE_o5AIb2mimbRJ_name"
        ] = postal_code_clean
    
    url = f"{API_BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    
    _LOGGER.debug("Searching addresses with postal_code: %s", postal_code)
    _LOGGER.debug("Request URL: %s", url)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    _LOGGER.warning("Autocomplete API returned status: %s", response.status)
                    return []
                
                # Parse JSON response (may have wrong Content-Type)
                try:
                    json_data = await response.json()
                except aiohttp.ContentTypeError:
                    response_text = await response.text()
                    response_text_stripped = response_text.strip()
                    if response_text_stripped.startswith(("[", "{")):
                        import json
                        json_data = json.loads(response_text)
                    else:
                        _LOGGER.warning("Autocomplete API returned non-JSON content")
                        return []
                
                if not isinstance(json_data, list):
                    _LOGGER.warning("Autocomplete API returned invalid format")
                    return []
                
                _LOGGER.debug("Found %s addresses", len(json_data))
                return json_data
                
        except Exception as err:
            _LOGGER.error("Error searching addresses: %s", err)
            return []


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    address_point_id = data[CONF_ADDRESS_POINT_ID]

    # Build API URL
    params = API_PARAMS.copy()
    params[
        f"_portalCKMjunkschedules_WAR_portalCKMjunkschedulesportlet_INSTANCE_o5AIb2mimbRJ_addressPointId"
    ] = str(address_point_id)

    url = f"{API_BASE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    
    _LOGGER.debug("Attempting to connect to API with address_point_id: %s", address_point_id)
    _LOGGER.debug("Request URL: %s", url)

    async with aiohttp.ClientSession() as session:
        try:
            _LOGGER.debug("Sending GET request to API")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                _LOGGER.debug("Response status: %s", response.status)
                _LOGGER.debug("Response headers: %s", dict(response.headers))
                
                if response.status != 200:
                    response_text = await response.text()
                    _LOGGER.error(
                        "API returned non-200 status: %s. Response body: %s",
                        response.status,
                        response_text[:500]  # Limit log size
                    )
                    raise CannotConnect(f"API returned status {response.status}")
                
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
                            raise InvalidData(
                                f"API returned invalid JSON response. This may indicate an invalid address_point_id."
                            ) from json_err
                    else:
                        # Looks like HTML or other non-JSON content
                        _LOGGER.error(
                            "API returned non-JSON content (Content-Type: %s). Response body: %s",
                            content_type,
                            response_text[:1000]  # Limit log size
                        )
                        raise InvalidData(
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
                    raise InvalidData(
                        f"API returned invalid JSON response. This may indicate an invalid address_point_id."
                    ) from parse_err
                
                _LOGGER.debug("Received JSON data: %s", str(json_data)[:200])  # Limit log size
                
                if not json_data or not isinstance(json_data, list):
                    _LOGGER.error("Invalid response format. Expected list, got: %s", type(json_data))
                    raise InvalidData("Invalid response format from API")
                
                if not json_data:
                    _LOGGER.error("Empty response from API")
                    raise InvalidData("No schedule data found for this address")
                
                # Check if harmonogramy exists and is not empty
                harmonogramy = json_data[0].get("harmonogramy", [])
                if not harmonogramy or (isinstance(harmonogramy, list) and len(harmonogramy) == 0):
                    address_name = json_data[0].get("adres", "unknown address")
                    _LOGGER.warning(
                        "Empty harmonogramy found for address: %s. Available keys: %s",
                        address_name,
                        list(json_data[0].keys()) if json_data[0] else "empty"
                    )
                    raise InvalidData("no_schedule_found")
                
                # Get address name from response
                address_name = json_data[0].get("adres", f"Address {address_point_id}")
                
                _LOGGER.info("Successfully validated connection for address_point_id: %s, address: %s", address_point_id, address_name)
                
                # Return the result here, inside the try block where json_data is available
                return {"title": address_name, "address": address_name}
                
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to API: %s", err)
            raise CannotConnect(f"Timeout connecting to API: {err}") from err
        except aiohttp.ServerTimeoutError as err:
            _LOGGER.error("Server timeout error: %s", err)
            raise CannotConnect(f"Server timeout: {err}") from err
        except aiohttp.ContentTypeError as err:
            response_text = ""
            if hasattr(err, 'request_info') and err.request_info:
                _LOGGER.error("ContentTypeError: API returned non-JSON content. URL: %s", err.request_info.url)
            _LOGGER.error("ContentTypeError details: %s", err)
            raise InvalidData(
                f"API returned HTML instead of JSON. This may indicate an invalid address_point_id or API endpoint issue."
            ) from err
        except InvalidData:
            # Re-raise InvalidData exceptions (like empty harmonogramy) without modification
            raise
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("Connection error to API: %s", err)
            raise CannotConnect(f"Connection error: {err}") from err
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("Client response error: %s (status: %s)", err, err.status)
            raise CannotConnect(f"API response error: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error connecting to API: %s (type: %s)", err, type(err).__name__)
            raise CannotConnect(f"Error connecting to API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during validation: %s", err)
            raise CannotConnect(f"Unexpected error: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wywóz Odpadów."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.postal_code: str = ""
        self.address_options: dict[str, dict[str, Any]] = {}
        self.address_options_dict: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - postal code input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            postal_code = user_input.get(CONF_POSTAL_CODE, "").strip()
            
            # Validate postal code format: ##-### (where #=0-9)
            import re
            postal_code_pattern = re.compile(r"^\d{2}-\d{3}$")
            
            if not postal_code:
                errors[CONF_POSTAL_CODE] = "required"
            elif not postal_code_pattern.match(postal_code):
                errors[CONF_POSTAL_CODE] = "invalid_format"
            else:
                # Store postal code and move to address selection step
                self.postal_code = postal_code
                return await self.async_step_address()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTAL_CODE): str,
                }
            ),
            errors=errors,
        )

    async def async_step_address(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle address selection step with postal code filter."""
        errors: dict[str, str] = {}

        # Load all addresses for postal code on first entry (if not already loaded)
        if not self.address_options_dict:
            _LOGGER.debug("Loading all addresses for postal code: %s", self.postal_code)
            addresses = await search_addresses(self.hass, self.postal_code)
            if addresses:
                self.address_options = {
                    addr["addressPointId"]: addr for addr in addresses
                }
                self.address_options_dict = {
                    addr_id: f"{addr['fullName']} ({addr_id})"
                    for addr_id, addr in self.address_options.items()
                }
                _LOGGER.debug("Loaded %s addresses", len(self.address_options))
            else:
                errors["base"] = "no_addresses"

        if user_input is not None:
            selected_address_id = user_input.get("address", "").strip()
            update_interval_days = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_DAYS)
            
            # Validate selected address
            if not selected_address_id:
                errors["address"] = "required"
            elif selected_address_id not in self.address_options:
                errors["address"] = "invalid_selection"
            else:
                # Address ID was selected, validate it
                try:
                    _LOGGER.info("Validating selected address: %s", selected_address_id)
                    # Convert days to seconds for storage (update_interval_days is already int)
                    update_interval_seconds = int(update_interval_days) * 86400
                    validation_data = {
                        CONF_ADDRESS_POINT_ID: int(selected_address_id),
                        CONF_UPDATE_INTERVAL: update_interval_seconds,
                    }
                    info = await validate_input(self.hass, validation_data)
                except CannotConnect as err:
                    _LOGGER.error("CannotConnect error during config flow: %s", err)
                    errors["base"] = "cannot_connect"
                except InvalidData as err:
                    _LOGGER.error("InvalidData error during config flow: %s", err)
                    # Check if it's a specific error message
                    # Try both str(err) and err.args[0] to handle different error representations
                    error_message = str(err)
                    if hasattr(err, 'args') and err.args:
                        error_message = err.args[0]
                    if error_message == "no_schedule_found":
                        errors["base"] = "no_schedule_found"
                    else:
                        errors["base"] = "invalid_data"
                except Exception as err:
                    _LOGGER.exception("Unexpected exception during config flow: %s", err)
                    errors["base"] = "unknown"
                else:
                    # Create entry with address name as title
                    return self.async_create_entry(
                        title=info.get("address", info["title"]),
                        data={
                            DOMAIN: {
                                CONF_ADDRESS_POINT_ID: int(selected_address_id),
                                CONF_UPDATE_INTERVAL: update_interval_seconds,
                            }
                        },
                    )

        # Build schema with address dropdown only
        schema_dict: dict[str, Any] = {
            vol.Required("address"): vol.In(self.address_options_dict) if self.address_options_dict else str,
            vol.Optional(
                CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL_DAYS
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=7)),
        }

        return self.async_show_form(
            step_id="address",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={"postal_code": self.postal_code},
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidData(HomeAssistantError):
    """Error to indicate invalid data."""

