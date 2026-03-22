"""Fixtures for OBDcast integration tests."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_payload():
    """Return a sample OBDcast telemetry payload."""
    return {
        "device_id": "obdcast-001",
        "ts": 1742600000,
        "obd": {
            "speed": 65,
            "rpm": 2100,
            "fuel_pct": 72,
            "coolant_c": 88,
            "engine_load_pct": 34,
            "throttle_pct": 18,
            "voltage": 13.8,
        },
        "gps": {
            "lat": 47.6062,
            "lon": -122.3321,
            "alt_m": 52,
            "heading": 180,
            "speed_kph": 65,
            "hdop": 1.2,
            "fix": True,
        },
        "motion": {
            "ax": 0.01,
            "ay": -0.02,
            "az": 9.81,
        },
        "ignition": True,
        "signal_dbm": -87,
    }
