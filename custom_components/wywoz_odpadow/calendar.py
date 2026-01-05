"""Calendar platform for Wywóz Odpadów."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    """Set up the Wywóz Odpadów calendar platform."""
    coordinator: WywozOdpadowDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([WywozOdpadowCalendar(coordinator, entry)])


class WywozOdpadowCalendar(
    CoordinatorEntity[WywozOdpadowDataUpdateCoordinator], CalendarEntity
):
    """Representation of a Wywóz Odpadów calendar."""

    _attr_has_entity_name = True
    _attr_name = "Wywóz Odpadów"

    def __init__(
        self,
        coordinator: WywozOdpadowDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the calendar."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
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
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self.coordinator.data or not self.coordinator.data.get("events"):
            return None

        events = self.coordinator.data["events"]
        if not events:
            return None

        # Get the first event (already sorted by date)
        event_data = events[0]
        start = event_data["start"]
        if isinstance(start, date):
            start = datetime.combine(start, datetime.min.time())
            start = dt_util.as_local(start)

        return CalendarEvent(
            start=start,
            end=start,
            summary=event_data["summary"],
            description=event_data.get("description", ""),
            location=None,
            uid=f"{self.unique_id}_{event_data['fraction_id']}_{start.date().isoformat()}",
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        if not self.coordinator.data or not self.coordinator.data.get("events"):
            return []

        events = []
        start_date_date = start_date.date()
        end_date_date = end_date.date()

        for event_data in self.coordinator.data["events"]:
            event_start = event_data["start"]
            if isinstance(event_start, date):
                event_start_date = event_start
            elif isinstance(event_start, datetime):
                event_start_date = event_start.date()
            else:
                continue

            # Check if event is within range
            if start_date_date <= event_start_date <= end_date_date:
                if isinstance(event_start, date):
                    event_datetime = datetime.combine(event_start, datetime.min.time())
                    event_datetime = dt_util.as_local(event_datetime)
                else:
                    event_datetime = dt_util.as_local(event_start)

                events.append(
                    CalendarEvent(
                        start=event_datetime,
                        end=event_datetime,
                        summary=event_data["summary"],
                        description=event_data.get("description", ""),
                        location=None,
                        uid=f"{self.unique_id}_{event_data['fraction_id']}_{event_start_date.isoformat()}",
                    )
                )

        return events

