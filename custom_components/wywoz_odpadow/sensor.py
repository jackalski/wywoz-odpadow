"""Sensor platform for Wywóz Odpadów."""
from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import WywozOdpadowDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Wywóz Odpadów sensor platform."""
    coordinator: WywozOdpadowDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([WywozOdpadowSensor(coordinator, entry)])


class WywozOdpadowSensor(
    CoordinatorEntity[WywozOdpadowDataUpdateCoordinator], SensorEntity
):
    """Representation of a Wywóz Odpadów sensor."""

    _attr_has_entity_name = True
    _attr_name = "Wywóz Odpadów"
    _attr_native_unit_of_measurement = "dni"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:trash-can"

    def __init__(
        self,
        coordinator: WywozOdpadowDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_sensor"
        self._entry = entry
        # Device name will be set from coordinator data or entry title
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": None,  # Will be set from coordinator data
            "manufacturer": "Warszawa 19115",
        }

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        # Get address from coordinator data, fallback to entry title
        address = None
        if self.coordinator.data and self.coordinator.data.get("address"):
            address = self.coordinator.data["address"]
        else:
            # Fallback to entry title if data not yet loaded
            address = self._entry.title
        
        if not address:
            address = f"Wywóz Odpadów ({self.coordinator.address_point_id})"
        
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": address,
            "manufacturer": "Warszawa 19115",
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("fractions"):
            return None

        fractions = self.coordinator.data["fractions"]
        if not fractions:
            return None

        # Find the minimum days_until across all fractions
        min_days = None
        for fraction_data in fractions.values():
            days_until = fraction_data.get("days_until")
            if days_until is not None:
                if min_days is None or days_until < min_days:
                    min_days = days_until

        return min_days

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes: dict[str, Any] = {}
        
        # Add update interval information in days only
        if hasattr(self.coordinator, "_update_interval_seconds"):
            update_interval_seconds = self.coordinator._update_interval_seconds
            update_interval_days = round(update_interval_seconds / 86400, 2)
            attributes["update_interval"] = update_interval_days

        return attributes

