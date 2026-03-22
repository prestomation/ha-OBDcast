# ha-obdcast Design Document

## Project Overview

`ha-obdcast` is a Home Assistant custom integration that receives vehicle telemetry from **OBDcast** firmware running on Freematics ONE+ Model B hardware. It enables real-time vehicle monitoring directly in Home Assistant, including OBD-II diagnostics, GPS tracking, and vehicle state monitoring.

### Goals

- Expose all vehicle telemetry as proper HA sensor entities
- Provide GPS-based device tracking (map display, home/away zones)
- Support both MQTT and Webhook data transports
- HACS-compatible for easy installation
- Zero YAML configuration (100% UI-based setup)

### Related Projects

- **OBDcast Firmware**: [prestomation/OBDcast](https://github.com/prestomation/OBDcast) — ESP32 firmware for Freematics ONE+ Model B

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Home Assistant                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ha-obdcast Integration                 │  │
│  │                                                           │  │
│  │  ┌─────────────┐    ┌─────────────────────────────────┐  │  │
│  │  │ Config Flow │───▶│        OBDcastCoordinator       │  │  │
│  │  └─────────────┘    │  (Data aggregation & caching)   │  │  │
│  │                     └─────────────┬───────────────────┘  │  │
│  │                                   │                       │  │
│  │         ┌─────────────────────────┼─────────────────────┐│  │
│  │         ▼                         ▼                     ▼│  │
│  │  ┌────────────┐          ┌──────────────┐     ┌────────┐│  │
│  │  │   Sensors  │          │Device Tracker│     │ Binary ││  │
│  │  │ (13 types) │          │    (GPS)     │     │ Sensor ││  │
│  │  └────────────┘          └──────────────┘     │(Ignit.)││  │
│  │                                               └────────┘│  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ▲                                   │
│           ┌──────────────────┴──────────────────┐               │
│           │          Transport Layer            │               │
│     ┌─────┴─────┐                       ┌───────┴─────┐         │
│     │   MQTT    │                       │   Webhook   │         │
│     │ Listener  │                       │  Handler    │         │
│     └─────┬─────┘                       └───────┬─────┘         │
└───────────┼─────────────────────────────────────┼───────────────┘
            │                                     │
            ▼                                     ▼
    ┌───────────────┐                    ┌───────────────┐
    │  MQTT Broker  │                    │   HTTP POST   │
    │  (external)   │                    │   (direct)    │
    └───────┬───────┘                    └───────┬───────┘
            │                                     │
            └──────────────────┬──────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │    OBDcast Device   │
                    │  (Freematics ONE+)  │
                    │    ESP32 + OBD-II   │
                    └─────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `__init__.py` | Integration setup, entry point, platform loading |
| `config_flow.py` | UI-based configuration wizard |
| `coordinator.py` | Data aggregation, caching, update scheduling |
| `sensor.py` | OBD-II and device sensor entities |
| `device_tracker.py` | GPS-based location tracking entity |
| `binary_sensor.py` | Ignition on/off state entity |
| `const.py` | Constants, defaults, entity definitions |

---

## Transport Modes

### MQTT Transport

**How it works:**
1. OBDcast firmware publishes telemetry to MQTT topics
2. Integration subscribes to `obdcast/{device_id}/telemetry`
3. JSON payloads are parsed and fed to coordinator
4. Coordinator updates all entity states

**Topic structure:**
```
obdcast/{device_id}/telemetry   # Main telemetry data (JSON)
obdcast/{device_id}/status      # Connection status (online/offline)
```

**Requirements:**
- MQTT broker accessible to both HA and OBDcast device
- HA's MQTT integration configured (used as dependency)

**Pros:**
- Push-based: instant updates
- Efficient for frequent telemetry
- Works across networks (via internet-accessible broker)
- Native HA MQTT autodiscovery potential

**Cons:**
- Requires MQTT broker infrastructure
- Additional configuration on firmware side
- More moving parts

### Webhook Transport

**How it works:**
1. Integration registers a webhook endpoint in HA
2. OBDcast firmware POSTs telemetry to the webhook URL
3. Webhook handler parses JSON and feeds coordinator
4. Coordinator updates all entity states

**Webhook URL format:**
```
https://{ha_external_url}/api/webhook/{webhook_id}
```

**Requirements:**
- HA must be accessible from OBDcast device (local network or port-forwarded/reverse-proxied)
- No additional infrastructure needed

**Pros:**
- Simpler setup: just a URL
- No MQTT broker needed
- Direct connection

**Cons:**
- Requires HA to be network-accessible to the device
- Slightly higher overhead per request
- No built-in message queuing/retry

### Trade-off Summary

| Factor | MQTT | Webhook |
|--------|------|---------|
| Setup complexity | Higher (need broker) | Lower (just URL) |
| Network requirements | Broker accessible to both | HA accessible to device |
| Latency | Very low | Low |
| Reliability | Good (QoS, LWT) | Depends on network |
| Infrastructure | External broker | None |

---

## Entity Model

### Device Registration

Each OBDcast unit creates a single HA device entry. The device name is the vehicle name provided during setup:

```yaml
device:
  identifiers: ["obdcast_{device_id}"]
  name: "{vehicle_name}"
  manufacturer: "Freematics"
  model: "ONE+ Model B"
  sw_version: "{firmware_version}"
```

**Multi-vehicle support works out of the box.** Each OBDcast unit is set up as a separate config entry with its own vehicle name. HA's device registry tracks them as distinct devices with no conflicts — no extra configuration needed.

### Entity Naming

All entity friendly names are prefixed with the vehicle name provided during setup:

- Friendly name pattern: `{vehicle_name} - {Sensor Name}` (e.g. `Tesla - Speed`, `Family Car - Fuel Level`)
- Entity ID pattern: `sensor.{vehicle_name_slug}_{sensor_key}` (e.g. `sensor.tesla_speed`, `sensor.family_car_fuel_level`)

The `vehicle_name` slug is derived by lowercasing and replacing spaces with underscores.

### Sensor Entities

Example entity IDs and names shown for a vehicle named `Tesla`:

| Entity ID | Friendly Name | Unit | Device Class | State Class | Notes |
|-----------|---------------|------|--------------|-------------|-------|
| `sensor.tesla_speed` | Tesla - Speed | km/h | `speed` | `measurement` | OBD-II vehicle speed |
| `sensor.tesla_rpm` | Tesla - RPM | rpm | — | `measurement` | Engine RPM |
| `sensor.tesla_fuel_level` | Tesla - Fuel Level | % | — | `measurement` | Fuel tank level |
| `sensor.tesla_coolant_temp` | Tesla - Coolant Temperature | °C | `temperature` | `measurement` | Engine coolant temp |
| `sensor.tesla_engine_load` | Tesla - Engine Load | % | `power_factor` | `measurement` | Calculated engine load |
| `sensor.tesla_throttle_position` | Tesla - Throttle Position | % | — | `measurement` | Throttle pedal position |
| `sensor.tesla_battery_voltage` | Tesla - Battery Voltage | V | `voltage` | `measurement` | 12V battery voltage |
| `sensor.tesla_altitude` | Tesla - Altitude | m | `distance` | `measurement` | GPS altitude |
| `sensor.tesla_gps_speed` | Tesla - GPS Speed | km/h | `speed` | `measurement` | Speed from GPS |
| `sensor.tesla_heading` | Tesla - Heading | ° | — | `measurement` | GPS heading/bearing |
| `sensor.tesla_gps_accuracy` | Tesla - GPS Accuracy | — | — | — | Fix quality indicator |
| `sensor.tesla_device_temp` | Tesla - Device Temperature | °C | `temperature` | `measurement` | OBDcast internal temp |
| `sensor.tesla_acceleration` | Tesla - Acceleration | m/s² | — | `measurement` | Accelerometer magnitude |

### Binary Sensor Entities

| Entity ID | Friendly Name | Device Class | Notes |
|-----------|---------------|--------------|-------|
| `binary_sensor.tesla_ignition` | Tesla - Ignition | `running` | Derived from battery voltage threshold |

### Device Tracker Entity

| Entity ID | Friendly Name | Source Type | Notes |
|-----------|---------------|-------------|-------|
| `device_tracker.tesla` | Tesla | `gps` | Lat/lon from GPS data, shows on HA map |

Device tracker attributes:
- `latitude`
- `longitude`
- `gps_accuracy`
- `altitude`
- `heading`
- `speed`

---

## Config Flow Design

### Flow Steps

#### Step 1: Transport Selection
```
┌──────────────────────────────────────┐
│     OBDcast Integration Setup        │
├──────────────────────────────────────┤
│                                      │
│  Select data transport:              │
│                                      │
│  ○ MQTT                              │
│  ○ Webhook                           │
│                                      │
│               [Next]                 │
└──────────────────────────────────────┘
```

#### Step 2a: MQTT Configuration
```
┌──────────────────────────────────────┐
│     MQTT Configuration               │
├──────────────────────────────────────┤
│                                      │
│  Vehicle Name: [________________]    │
│  (e.g. "Tesla", "Family Car")        │
│                                      │
│  Device ID: [________________]       │
│  (matches OBDcast firmware config)   │
│                                      │
│  MQTT Topic Prefix: [obdcast]        │
│  (default: obdcast)                  │
│                                      │
│               [Submit]               │
└──────────────────────────────────────┘
```

#### Step 2b: Webhook Configuration
```
┌──────────────────────────────────────┐
│     Webhook Configuration            │
├──────────────────────────────────────┤
│                                      │
│  Vehicle Name: [________________]    │
│  (e.g. "Tesla", "Family Car")        │
│                                      │
│  Device ID: [________________]       │
│  (matches OBDcast firmware config)   │
│                                      │
│  ──────────────────────────────────  │
│  Your webhook URL:                   │
│  https://ha.example.com/api/webhook/ │
│  obdcast_abc123def456                │
│  (configure this URL in OBDcast)     │
│                                      │
│               [Submit]               │
└──────────────────────────────────────┘
```

### Validation

- **Vehicle Name**: Required, string — becomes the HA device name and prefixes all entity names
- **Device ID**: Required, alphanumeric, must be unique across config entries
- **MQTT Topic Prefix**: Optional, defaults to `obdcast`

### Options Flow

After initial setup, users can modify:
- Vehicle name
- Entity enable/disable toggles
- Update interval preferences

---

## Data Model / JSON Payload Schema

### Telemetry Payload

The OBDcast firmware sends JSON payloads with the following structure:

```json
{
  "device_id": "obdcast_001",
  "timestamp": 1711080000,
  "obd": {
    "speed": 65,
    "rpm": 2500,
    "fuel_level": 72.5,
    "coolant_temp": 90,
    "engine_load": 35.2,
    "throttle_position": 22.0
  },
  "gps": {
    "latitude": 47.6062,
    "longitude": -122.3321,
    "altitude": 56.0,
    "heading": 270.5,
    "speed": 64.8,
    "fix_quality": 2,
    "satellites": 8
  },
  "battery_voltage": 14.2,
  "accelerometer": {
    "x": 0.02,
    "y": -0.15,
    "z": 9.78
  },
  "gyroscope": {
    "x": 0.5,
    "y": -0.2,
    "z": 0.1
  },
  "device_temp": 42.5,
  "firmware_version": "1.2.0"
}
```

### Field Definitions

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `device_id` | string | — | Unique device identifier |
| `timestamp` | integer | Unix epoch | Message timestamp |
| `obd.speed` | float | km/h | Vehicle speed from OBD-II |
| `obd.rpm` | integer | rpm | Engine RPM |
| `obd.fuel_level` | float | % | Fuel tank level (0-100) |
| `obd.coolant_temp` | float | °C | Engine coolant temperature |
| `obd.engine_load` | float | % | Calculated engine load |
| `obd.throttle_position` | float | % | Throttle position (0-100) |
| `gps.latitude` | float | degrees | GPS latitude |
| `gps.longitude` | float | degrees | GPS longitude |
| `gps.altitude` | float | meters | GPS altitude |
| `gps.heading` | float | degrees | Heading (0-360) |
| `gps.speed` | float | km/h | Speed from GPS |
| `gps.fix_quality` | integer | — | GPS fix quality (0=none, 1=GPS, 2=DGPS) |
| `gps.satellites` | integer | — | Number of satellites |
| `battery_voltage` | float | V | Vehicle battery voltage |
| `accelerometer.x/y/z` | float | m/s² | Accelerometer axes |
| `gyroscope.x/y/z` | float | °/s | Gyroscope axes |
| `device_temp` | float | °C | OBDcast device temperature |
| `firmware_version` | string | — | Firmware version |

### Ignition Detection

Ignition state is derived from `battery_voltage`:
- **ON**: voltage >= 13.0V (engine running, alternator charging)
- **OFF**: voltage < 13.0V (engine off, battery only)

---

## HACS Compatibility Requirements

### Directory Structure

```
ha-obdcast/
├── custom_components/
│   └── obdcast/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── device_tracker.py
│       ├── binary_sensor.py
│       ├── const.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── hacs.json
├── README.md
├── DESIGN.md
└── LICENSE
```

### hacs.json

```json
{
  "name": "OBDcast",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

### manifest.json Requirements

```json
{
  "domain": "obdcast",
  "name": "OBDcast",
  "codeowners": ["@prestomation"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/prestomation/ha-obdcast",
  "integration_type": "hub",
  "iot_class": "local_push",
  "issue_tracker": "https://github.com/prestomation/ha-obdcast/issues",
  "requirements": [],
  "version": "0.1.0"
}
```

**Note on dependencies:**
- For MQTT mode: will use `mqtt` as a dependency (HA's built-in MQTT integration)
- For Webhook mode: no external dependencies

---

## Future Considerations

### Trip History / Statistics

Potential future features:
- Trip detection (ignition on → ignition off)
- Distance traveled per trip
- Average speed, fuel consumption
- Integration with HA's statistics/history

### Additional Data

The firmware could be extended to provide:
- DTC (Diagnostic Trouble Codes) reading
- VIN decoding
- More OBD-II PIDs (intake temp, MAF, O2 sensors)

### Mobile App Integration

- HA companion app already shows device_tracker on map
- Could add custom dashboard cards for vehicle display

### Energy Dashboard Integration

- Fuel consumption tracking could integrate with HA Energy dashboard
- Would require fuel consumption calculation from fuel level delta


