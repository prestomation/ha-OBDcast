"""Constants for the OBDcast integration.

This module defines all constants used throughout the integration:
- Domain and platform identifiers
- Configuration keys and defaults
- Entity definitions (sensors, binary sensors, device tracker)
- Device classes, state classes, and units
- MQTT topics and webhook identifiers
- Voltage thresholds for ignition detection

All sensor definitions are centralized here to ensure consistency
across config flow, coordinator, and entity platforms.
"""

from __future__ import annotations

DOMAIN = "obdcast"

# Configuration keys
CONF_DEVICE_ID = "device_id"
CONF_VEHICLE_NAME = "vehicle_name"
CONF_TRANSPORT = "transport"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"

# Transport modes
TRANSPORT_MQTT = "mqtt"
TRANSPORT_WEBHOOK = "webhook"

# Defaults
DEFAULT_MQTT_TOPIC_PREFIX = "obdcast"
IGNITION_VOLTAGE_THRESHOLD = 13.0  # Volts - above this = ignition ON

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]
