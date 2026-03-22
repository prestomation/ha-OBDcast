"""Sensor platform for OBDcast integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    CONF_VEHICLE_NAME,
    DOMAIN,
    SENSOR_DEFINITIONS,
)
from .coordinator import OBDcastCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OBDcast sensors from a config entry."""
    coordinator: OBDcastCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_id: str = entry.data[CONF_DEVICE_ID]
    vehicle_name: str = entry.data[CONF_VEHICLE_NAME]

    entities = [
        OBDcastSensor(coordinator, device_id, vehicle_name, definition)
        for definition in SENSOR_DEFINITIONS
    ]
    async_add_entities(entities)


class OBDcastSensor(CoordinatorEntity[OBDcastCoordinator], SensorEntity):
    """Sensor entity for OBDcast telemetry."""

    def __init__(
        self,
        coordinator: OBDcastCoordinator,
        device_id: str,
        vehicle_name: str,
        definition: tuple,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: OBDcastCoordinator instance
            device_id: OBDcast device identifier
            vehicle_name: Friendly name for the vehicle
            definition: Tuple of (key, name, unit, device_class, state_class, icon)
        """
        super().__init__(coordinator)
        key, name, unit, device_class, state_class, icon = definition

        self._key_path = key
        self._device_id = device_id
        self._vehicle_name = vehicle_name

        # Unique ID uses underscores: obdcast001_obd_speed
        unique_key = key.replace(".", "_")
        self._attr_unique_id = f"{device_id}_{unique_key}"
        self._attr_name = f"{vehicle_name} - {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

        if device_class:
            self._attr_device_class = device_class
        if state_class:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._vehicle_name,
            manufacturer="Freematics",
            model="ONE+ Model B",
        )

    @property
    def native_value(self) -> Any:
        """Return the sensor value from coordinator data."""
        return self.coordinator.get_value(self._key_path)
