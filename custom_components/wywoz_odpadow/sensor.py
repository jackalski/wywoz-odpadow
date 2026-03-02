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

    entities: list[SensorEntity] = []

    fractions = {}
    if coordinator.data and coordinator.data.get("fractions"):
        fractions = coordinator.data["fractions"]

    for fraction_id, fraction_data in fractions.items():
        entities.append(
            WywozOdpadowFractionSensor(
                coordinator,
                entry,
                fraction_id,
                fraction_data.get("name", str(fraction_id)),
            )
        )

    async_add_entities(entities)


class WywozOdpadowFractionSensor(
    CoordinatorEntity[WywozOdpadowDataUpdateCoordinator], SensorEntity
):
    """Representation of a Wywóz Odpadów fraction sensor."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "dni"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:trash-can"

    def __init__(
        self,
        coordinator: WywozOdpadowDataUpdateCoordinator,
        entry: ConfigEntry,
        fraction_id: str,
        fraction_name: str,
    ) -> None:
        """Initialize the fraction sensor."""
        super().__init__(coordinator)
        self._fraction_id = fraction_id
        self._attr_unique_id = f"{entry.entry_id}_fraction_{fraction_id}"
        self._attr_name = fraction_name
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": None,
            "manufacturer": "Warszawa 19115",
        }

    @property
    def name(self) -> str | None:
        """Return the translated fraction name from coordinator data."""
        if self.coordinator.data and self.coordinator.data.get("fractions"):
            frac = self.coordinator.data["fractions"].get(self._fraction_id)
            if frac and frac.get("name"):
                return frac["name"]
        return self._attr_name or self._fraction_id

    def _handle_coordinator_update(self) -> None:
        """Update entity name from coordinator when data refreshes."""
        if self.coordinator.data and self.coordinator.data.get("fractions"):
            frac = self.coordinator.data["fractions"].get(self._fraction_id)
            if frac and frac.get("name"):
                self._attr_name = frac["name"]
        super()._handle_coordinator_update()

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

        fraction = self.coordinator.data["fractions"].get(self._fraction_id)
        if not fraction:
            return None

        return fraction.get("days_until")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes: dict[str, Any] = {}

        if not self.coordinator.data or not self.coordinator.data.get("fractions"):
            return attributes

        fraction = self.coordinator.data["fractions"].get(self._fraction_id)
        if not fraction:
            return attributes

        attributes["fraction_id"] = self._fraction_id
        attributes["fraction_type"] = fraction.get("type")
        attributes["next_date"] = fraction.get("next_date")

        return attributes
