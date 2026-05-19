"""Contract tests for CozyLife config entry migration."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from homeassistant.const import CONF_NAME

from custom_components.cozylife import CONF_AREA
from custom_components.cozylife import async_migrate_entry


class _FakeConfigEntries:
    """Capture config entry updates."""

    def __init__(self) -> None:
        self.updated_entry = None
        self.updated_data = None

    def async_update_entry(self, entry, data) -> None:
        self.updated_entry = entry
        self.updated_data = data


class _FakeHass:
    """Minimal Home Assistant double for migration tests."""

    def __init__(self) -> None:
        self.config_entries = _FakeConfigEntries()


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_migration_replaces_legacy_location_with_area_only() -> None:
    """Migrated entries should not retain the legacy location field."""

    hass = _FakeHass()
    entry = SimpleNamespace(data={"location": "Kitchen", "name": "Desk Lamp", "timeout": 0.3})

    with patch(
        "custom_components.cozylife.prepare_area_value_for_storage",
        side_effect=lambda hass, value: value,
    ):
        assert await async_migrate_entry(hass, entry) is True

    assert hass.config_entries.updated_entry is entry
    assert hass.config_entries.updated_data == {
        CONF_AREA: "Kitchen",
        CONF_NAME: "Desk Lamp",
        "timeout": 0.3,
    }


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_migration_normalizes_nested_device_locations_in_multi_entries() -> None:
    """Migrated multi-device entries should canonicalize nested area storage."""

    hass = _FakeHass()
    entry = SimpleNamespace(
        data={
            "devices": [
                {
                    "device": {"did": "did-1", "ip": "192.168.1.10"},
                    "location": "Office",
                    "name": "Office Lamp",
                },
                {
                    "device": {"did": "did-2", "ip": "192.168.1.11"},
                    "area": "Bedroom",
                    "name": "Bedroom Lamp",
                },
            ],
            "timeout": 0.3,
        }
    )

    with patch(
        "custom_components.cozylife.prepare_area_value_for_storage",
        side_effect=lambda hass, value: value,
    ):
        assert await async_migrate_entry(hass, entry) is True

    assert hass.config_entries.updated_data == {
        "devices": [
            {
                "device": {"did": "did-1", "ip": "192.168.1.10"},
                CONF_AREA: "Office",
                CONF_NAME: "Office Lamp",
            },
            {
                "device": {"did": "did-2", "ip": "192.168.1.11"},
                CONF_AREA: "Bedroom",
                CONF_NAME: "Bedroom Lamp",
            },
        ],
        "timeout": 0.3,
    }


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_migration_normalizes_legacy_bucketed_scan_entries() -> None:
    """Legacy bucketed full-scan entries should migrate into canonical device rows."""

    hass = _FakeHass()
    entry = SimpleNamespace(
        data={
            "devices": {
                "lights": [
                    {
                        "did": "did-1",
                        "ip": "192.168.1.10",
                        "location": "Kitchen",
                    }
                ],
                "switches": {
                    "did": "did-2",
                    "ip": "192.168.1.11",
                    "location": "Hallway",
                },
                "sensors": [
                    {
                        "did": "did-3",
                        "ip": "192.168.1.12",
                        "area": "Office",
                    }
                ],
            },
            "timeout": 0.3,
        }
    )

    with patch(
        "custom_components.cozylife.prepare_area_value_for_storage",
        side_effect=lambda hass, value: value,
    ):
        assert await async_migrate_entry(hass, entry) is True

    assert hass.config_entries.updated_data == {
        "devices": [
            {
                "device": {
                    "did": "did-1",
                    "ip": "192.168.1.10",
                    "type": "light",
                },
                CONF_AREA: "Kitchen",
            },
            {
                "device": {
                    "did": "did-2",
                    "ip": "192.168.1.11",
                    "type": "switch",
                },
                CONF_AREA: "Hallway",
            },
            {
                "device": {
                    "did": "did-3",
                    "ip": "192.168.1.12",
                    "type": "sensor",
                },
                CONF_AREA: "Office",
            },
        ],
        "timeout": 0.3,
        "scan_settings": {
            "start_ip": None,
            "end_ip": None,
            "timeout": 0.3,
        },
    }
