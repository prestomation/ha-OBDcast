"""Data coordinator for OBDcast integration.

The OBDcastCoordinator manages data flow from the OBDcast device to
Home Assistant entities. Unlike typical coordinators that poll for data,
this coordinator receives push-based updates via MQTT or webhook.

Responsibilities:
- Receive and parse telemetry payloads
- Cache the latest state for all data points
- Notify entities when new data arrives
- Handle connection status tracking
- Derive computed values (e.g., ignition state from voltage)

Data flow:
1. Transport layer (MQTT listener or webhook handler) receives payload
2. Coordinator.async_update_data() is called with parsed JSON
3. Coordinator stores data and marks update time
4. Entities read from coordinator.data on next refresh

The coordinator does NOT poll - it's entirely push-based. Entities
subscribe to coordinator updates and refresh when new data arrives.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, IGNITION_VOLTAGE_THRESHOLD

_LOGGER = logging.getLogger(__name__)


class OBDcastCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for OBDcast device data.

    This coordinator is push-based - it receives data from MQTT or webhook
    handlers rather than polling. The update_interval is set to None.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            device_id: OBDcast device identifier
            vehicle_name: Vehicle name provided during config flow setup (e.g. "Tesla",
                "Family Car"). Used as the HA device name and passed to all entities
                for friendly name prefixing (e.g. "Tesla - Speed", "Tesla - Fuel Level").
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=None,  # Push-based, no polling
        )
        self.device_id = device_id
        self.vehicle_name = vehicle_name
        self._last_update: datetime | None = None

    async def async_receive_data(self, payload: dict[str, Any]) -> None:
        """Process incoming telemetry data.

        Called by MQTT listener or webhook handler when new data arrives.
        Parses the payload and triggers entity updates.

        Args:
            payload: JSON payload from OBDcast device
        """
        # TODO: Parse and validate payload structure
        # TODO: Store data in self.data
        # TODO: Derive ignition state from battery voltage
        # TODO: Update _last_update timestamp
        # TODO: Call async_set_updated_data() to notify entities
        pass

    @property
    def ignition_on(self) -> bool:
        """Determine if ignition is on based on battery voltage.

        Returns True if battery voltage is above threshold (typically 13V),
        indicating the alternator is charging (engine running).
        """
        if self.data is None:
            return False
        voltage = self.data.get("battery_voltage", 0)
        return voltage >= IGNITION_VOLTAGE_THRESHOLD

    @property
    def gps_coordinates(self) -> tuple[float, float] | None:
        """Get current GPS coordinates.

        Returns:
            Tuple of (latitude, longitude) or None if no GPS fix
        """
        if self.data is None:
            return None
        gps = self.data.get("gps", {})
        lat = gps.get("latitude")
        lon = gps.get("longitude")
        if lat is not None and lon is not None:
            return (lat, lon)
        return None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data - not used for push-based coordinator.

        This method exists for compatibility but should not be called
        directly. Data is received via async_receive_data().
        """
        # Push-based coordinator - return existing data
        return self.data or {}
