"""Constants for the OBDcast integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "obdcast"

# Configuration keys
CONF_DEVICE_ID = "device_id"
CONF_VEHICLE_NAME = "vehicle_name"
CONF_TRANSPORT = "transport"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"
CONF_WEBHOOK_ID = "webhook_id"

# Transport modes
TRANSPORT_MQTT = "mqtt"
TRANSPORT_WEBHOOK = "webhook"

# Defaults
DEFAULT_MQTT_TOPIC_PREFIX = "obdcast"
IGNITION_VOLTAGE_THRESHOLD = 13.0  # Volts - above this = ignition ON

# Platforms
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]

# Sensor definitions: (key, name, unit, device_class, state_class, icon)
SENSOR_DEFINITIONS = [
    ("obd.speed", "Speed", "km/h", "speed", "measurement", "mdi:speedometer"),
    ("obd.rpm", "Engine RPM", "rpm", None, "measurement", "mdi:engine"),
    ("obd.fuel_pct", "Fuel Level", "%", None, "measurement", "mdi:gas-station"),
    ("obd.coolant_c", "Coolant Temperature", "°C", "temperature", "measurement", None),
    ("obd.engine_load_pct", "Engine Load", "%", None, "measurement", "mdi:engine"),
    ("obd.throttle_pct", "Throttle Position", "%", None, "measurement", None),
    ("obd.voltage", "Battery Voltage", "V", "voltage", "measurement", "mdi:battery-charging"),
    ("gps.alt_m", "Altitude", "m", None, "measurement", "mdi:altimeter"),
    ("gps.heading", "Heading", "°", None, "measurement", "mdi:compass"),
    ("gps.hdop", "GPS Accuracy (HDOP)", None, None, "measurement", "mdi:crosshairs-gps"),
    ("signal_dbm", "Signal Strength", "dBm", "signal_strength", "measurement", None),
]

# Binary sensor definitions: (key, name, device_class, icon)
BINARY_SENSOR_DEFINITIONS = [
    ("ignition", "Ignition", "running", "mdi:key"),
    ("gps.fix", "GPS Fix", None, "mdi:crosshairs-gps"),
]
