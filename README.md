# ha-obdcast

Home Assistant custom integration for **OBDcast** vehicle telemetry. Receives real-time OBD-II diagnostics, GPS location, and vehicle state from an OBDcast device (Freematics ONE+ Model B running OBDcast firmware).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

## Features

- **OBD-II Diagnostics**: Speed, RPM, fuel level, coolant temperature, engine load, throttle position
- **GPS Tracking**: Real-time location on Home Assistant map, home/away zone detection
- **Vehicle State**: Ignition on/off detection, battery voltage monitoring
- **Device Monitoring**: Device temperature, accelerometer data
- **Flexible Transport**: Choose between MQTT or Webhook data delivery
- **Zero YAML**: 100% UI-based configuration

## Requirements

- **Home Assistant**: 2024.1.0 or newer
- **OBDcast Device**: Freematics ONE+ Model B with [OBDcast firmware](https://github.com/prestomation/OBDcast)
- **For MQTT mode**: MQTT broker configured in HA (via MQTT integration)
- **For Webhook mode**: Home Assistant accessible from the OBDcast device (local network or external URL)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/prestomation/ha-obdcast` with category **Integration**
4. Search for "OBDcast" and click **Download**
5. Restart Home Assistant

### Manual Installation

1. Download this repository
2. Copy `custom_components/obdcast/` to your HA `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **OBDcast**
4. Follow the setup wizard:
   - Select transport mode (MQTT or Webhook)
   - Enter a name for your vehicle (e.g. "Tesla", "Family Car", "Work Truck") — this becomes the HA device name and prefixes all entity names
   - Enter your OBDcast device ID (must match firmware configuration)
5. Configure your OBDcast firmware to send data to HA:
   - **MQTT**: Point to your MQTT broker, use topic prefix `obdcast`
   - **Webhook**: Use the webhook URL shown during setup

## Entities

All entities are named with your vehicle name as a prefix. For a vehicle named **"Tesla"**, you'll get entities like `Tesla - Speed` (`sensor.tesla_speed`), `Tesla - Fuel Level` (`sensor.tesla_fuel_level`), etc.

### Sensors

| Entity (example: Tesla) | Description | Unit |
|-------------------------|-------------|------|
| Tesla - Speed | Vehicle speed from OBD-II | km/h |
| Tesla - RPM | Engine RPM | rpm |
| Tesla - Fuel Level | Fuel tank level | % |
| Tesla - Coolant Temperature | Engine coolant temp | °C |
| Tesla - Engine Load | Calculated engine load | % |
| Tesla - Throttle Position | Throttle pedal position | % |
| Tesla - Battery Voltage | 12V battery voltage | V |
| Tesla - Altitude | GPS altitude | m |
| Tesla - GPS Speed | Speed from GPS | km/h |
| Tesla - Heading | GPS heading/bearing | ° |
| Tesla - GPS Accuracy | GPS fix quality | — |
| Tesla - Device Temperature | OBDcast internal temp | °C |
| Tesla - Acceleration | Accelerometer magnitude | m/s² |

### Binary Sensors

| Entity (example: Tesla) | Description |
|-------------------------|-------------|
| Tesla - Ignition | Vehicle ignition state (on when battery > 13V) |

### Device Tracker

| Entity (example: Tesla) | Description |
|-------------------------|-------------|
| Tesla | GPS location, displayed on HA map |

## Multiple Vehicles

Multiple OBDcast devices are fully supported. Each device is set up as a separate integration entry with its own vehicle name. HA's device registry handles them as distinct devices — no extra configuration or workarounds needed. Add another OBDcast device the same way you added the first.

## OBDcast Firmware

This integration works with the OBDcast firmware running on Freematics ONE+ Model B hardware:

**[prestomation/OBDcast](https://github.com/prestomation/OBDcast)**

The firmware collects:
- OBD-II data via the vehicle's diagnostic port
- GPS location via built-in GPS module
- Accelerometer/gyroscope data
- Battery voltage (used for ignition detection)

## Transport Modes

### MQTT

Best for:
- Setups with existing MQTT infrastructure
- Remote vehicles (data can go through internet broker)
- Lower latency requirements

OBDcast publishes to: `obdcast/{device_id}/telemetry`

### Webhook

Best for:
- Simple setups without MQTT
- Local network only vehicles
- Quick getting-started experience

OBDcast POSTs to: `https://{your-ha}/api/webhook/{webhook_id}`

## Troubleshooting

### No data appearing

1. Verify OBDcast device is powered and connected to vehicle
2. Check firmware is configured with correct transport settings
3. For MQTT: verify broker connectivity from both HA and device
4. For Webhook: verify HA is accessible from device network

### GPS not updating

1. Ensure vehicle is outdoors with GPS signal
2. Check `gps_accuracy` sensor for fix quality
3. Initial GPS fix can take 1-2 minutes after power-on

### Ignition always shows OFF

1. Check `battery_voltage` sensor value
2. Ignition is detected when voltage >= 13.0V (alternator charging)
3. May need adjustment for vehicles with different charging profiles

## Contributing

Contributions welcome! Please read the [DESIGN.md](DESIGN.md) for architecture details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [OBDcast Firmware](https://github.com/prestomation/OBDcast) - ESP32 firmware for Freematics ONE+
- [Freematics](https://freematics.com/) - Hardware manufacturer
