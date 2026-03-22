"""Data coordinator for OBDcast integration.

Push-based coordinator that receives telemetry from MQTT or webhook transport.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OBDcastCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for OBDcast device data (push-based, no polling)."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_id}",
            update_interval=None,  # Push-based, no polling
        )
        self.device_id = device_id
        self.vehicle_name = vehicle_name
        self._last_update: datetime | None = None
        self.data: dict[str, Any] = {}

    async def async_receive_data(self, payload: dict[str, Any]) -> None:
        """Process incoming telemetry data from MQTT or webhook.

        Args:
            payload: Parsed JSON payload from OBDcast device
        """
        _LOGGER.debug("OBDcast %s received telemetry: %s", self.device_id, payload)
        self._last_update = datetime.utcnow()
        self.async_set_updated_data(payload)

    async def async_receive_raw(self, raw: str | bytes) -> None:
        """Parse raw JSON string and process as telemetry data."""
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as err:
            _LOGGER.error("OBDcast %s failed to parse payload: %s", self.device_id, err)
            return
        await self.async_receive_data(payload)

    def get_value(self, key_path: str) -> Any:
        """Get a value from coordinator data using dot-notation key path.

        Args:
            key_path: Dot-separated path, e.g. "obd.speed" or "signal_dbm"

        Returns:
            The value at that path, or None if not found.
        """
        if not self.data:
            return None
        parts = key_path.split(".")
        current: Any = self.data
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None
        return current

    @property
    def last_update(self) -> datetime | None:
        """Return the last update timestamp."""
        return self._last_update

    async def _async_update_data(self) -> dict[str, Any]:
        """Required by base class — not used for push-based coordinator."""
        return self.data or {}
