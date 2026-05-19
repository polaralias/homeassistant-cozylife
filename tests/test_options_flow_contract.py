"""Contract tests for CozyLife options flow behavior."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_NAME

from custom_components.cozylife.config_flow import CozyLifeOptionsFlow
from custom_components.cozylife.const import (
    CONF_DIY_CONTROL_MAPPINGS,
    CONF_DIY_DPID_MAPPINGS,
    CONF_ENABLE_DIY_WRITES,
    CONF_LIGHT_POLL_INTERVAL,
    CONF_SWITCH_POLL_INTERVAL,
    DOMAIN,
)


class _FakeConfig:
    """Minimal config object with a Home Assistant-like path method."""

    def path(self, *parts: str) -> str:
        return str(Path.cwd().joinpath(*parts))


class _FakeConfigEntries:
    """Capture config-entry updates triggered by the options flow."""

    def __init__(self) -> None:
        self.updated_entry = None
        self.updated_data = None
        self.reloaded_entry_id = None
        self._known_entries = {}

    def async_update_entry(self, entry, data) -> None:
        self.updated_entry = entry
        self.updated_data = data

    async def async_reload(self, entry_id: str) -> None:
        self.reloaded_entry_id = entry_id

    def async_get_known_entry(self, entry_id: str):
        return self._known_entries[entry_id]


class _FakeHass:
    """Minimal Home Assistant double for options-flow tests."""

    def __init__(self, entry_id: str, entry=None) -> None:
        self.config = _FakeConfig()
        self.config_entries = _FakeConfigEntries()
        self.data = {DOMAIN: {entry_id: {}}}
        if entry is not None:
            self.config_entries._known_entries[entry_id] = entry

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class _ProbeTcpClient:
    """TCP client double for DIY capability probing tests."""

    def __init__(self, ip: str, timeout: float = 0.3, model_path=None) -> None:
        self._ip = ip

    def query(self) -> dict[str, int]:
        return {"7": 1, "10": 0}

    def disconnect(self) -> None:
        return None


@pytest.mark.cozylife
def test_options_flow_avoids_deprecated_config_entry_assignment() -> None:
    """Options flow should bootstrap without setting the deprecated attribute."""

    entry = SimpleNamespace(entry_id="entry-options-1", data={}, options={})

    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)

    assert flow._config_entry is entry
    assert "config_entry" not in flow.__dict__


@pytest.mark.cozylife
def test_options_flow_uses_modern_config_entry_lookup_when_runtime_property_is_needed() -> None:
    """Flow methods should work through HA's config_entry property lookup path."""

    entry = SimpleNamespace(entry_id="entry-options-2", data={}, options={})

    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)

    flow.hass = _FakeHass(entry.entry_id, entry)
    flow.handler = entry.entry_id
    del flow._config_entry

    assert flow.config_entry is entry


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_legacy_options_rescan_persists_canonical_device_list() -> None:
    """Legacy rescan should stop rewriting the legacy bucketed device shape."""

    entry = SimpleNamespace(
        entry_id="entry-legacy-1",
        data={
            "start_ip": "192.168.1.10",
            "end_ip": "192.168.1.20",
            "timeout": 0.3,
            "devices": {
                "lights": [{"did": "old-light", "ip": "192.168.1.11"}],
                "switches": [],
                "sensors": [],
            },
        },
        options={},
    )
    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)
    flow.hass = _FakeHass(entry.entry_id)
    flow.async_create_entry = lambda *, title, data: {
        "type": "create_entry",
        "title": title,
        "data": data,
    }

    discovered_devices = {
        "lights": [
            {
                "did": "light-1",
                "ip": "192.168.1.50",
                "pid": "pid-light",
                "dpid": [1, 4],
                "dmn": "Desk Lamp",
                "type": "light",
            }
        ],
        "switches": [
            {
                "did": "switch-1",
                "ip": "192.168.1.51",
                "pid": "pid-switch",
                "dpid": [1],
                "dmn": "Desk Switch",
                "type": "switch",
            }
        ],
        "sensors": [],
        "unknown": [],
    }

    with patch(
        "custom_components.cozylife.config_flow.discover_devices",
        return_value=discovered_devices,
    ):
        result = await flow._async_step_legacy(
            {
                "start_ip": "192.168.1.40",
                "end_ip": "192.168.1.60",
                "timeout": 0.5,
                CONF_LIGHT_POLL_INTERVAL: 60,
                CONF_SWITCH_POLL_INTERVAL: 20,
            }
        )

    assert result == {
        "type": "create_entry",
        "title": "",
        "data": {
            CONF_LIGHT_POLL_INTERVAL: 60.0,
            CONF_SWITCH_POLL_INTERVAL: 20.0,
        },
    }
    assert flow.hass.config_entries.updated_entry is entry
    assert flow.hass.config_entries.updated_data == {
        "devices": [
            {
                "device": {
                    "did": "light-1",
                    "ip": "192.168.1.50",
                    "pid": "pid-light",
                    "dpid": [1, 4],
                    "dmn": "Desk Lamp",
                    "type": "light",
                }
            },
            {
                "device": {
                    "did": "switch-1",
                    "ip": "192.168.1.51",
                    "pid": "pid-switch",
                    "dpid": [1],
                    "dmn": "Desk Switch",
                    "type": "switch",
                }
            },
        ],
        "timeout": 0.5,
        "scan_settings": {
            "start_ip": "192.168.1.40",
            "end_ip": "192.168.1.60",
            "timeout": 0.5,
        },
    }
    assert flow.hass.config_entries.reloaded_entry_id == entry.entry_id


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_single_device_options_persist_diy_dpid_mapping() -> None:
    """Single-device options should persist validated DIY DPID mappings."""

    entry = SimpleNamespace(
        entry_id="entry-diy-1",
        data={
            "device": {
                "did": "unknown-1",
                "ip": "192.168.1.70",
                "pid": "pid-unknown",
                "dpid": [7, 10],
                "dmn": "DIY Device",
                "type": "unknown",
            },
            "timeout": 0.3,
            "name": "DIY Device",
        },
        options={},
    )
    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)
    flow.hass = _FakeHass(entry.entry_id)
    flow.async_create_entry = lambda *, title, data: {
        "type": "create_entry",
        "title": title,
        "data": data,
    }

    result = await flow.async_step_init(
        {
            "ip": "192.168.1.71",
            "timeout": 0.5,
            CONF_LIGHT_POLL_INTERVAL: 60,
            CONF_SWITCH_POLL_INTERVAL: 20,
            "name": "Garage Probe",
            CONF_DIY_DPID_MAPPINGS: "7=Contact Raw, 10=Leak Alarm",
        }
    )

    assert result == {
        "type": "create_entry",
        "title": "",
        "data": {
            CONF_LIGHT_POLL_INTERVAL: 60.0,
            CONF_SWITCH_POLL_INTERVAL: 20.0,
        },
    }
    assert flow.hass.config_entries.updated_data == {
        "device": {
            "did": "unknown-1",
            "ip": "192.168.1.71",
            "pid": "pid-unknown",
            "dpid": [7, 10],
            "dmn": "DIY Device",
            "type": "unknown",
            CONF_DIY_DPID_MAPPINGS: [
                {"dpid": 7, "name": "Contact Raw"},
                {"dpid": 10, "name": "Leak Alarm"},
            ],
        },
        "timeout": 0.5,
        CONF_NAME: "Garage Probe",
        "area": None,
    }


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_single_device_options_reject_unknown_diy_dpid_mapping() -> None:
    """DIY mappings should stay constrained to the device's known DPID list."""

    entry = SimpleNamespace(
        entry_id="entry-diy-2",
        data={
            "device": {
                "did": "unknown-2",
                "ip": "192.168.1.72",
                "pid": "pid-unknown",
                "dpid": [7],
                "dmn": "DIY Device",
                "type": "unknown",
            },
            "timeout": 0.3,
        },
        options={},
    )
    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)
    flow.hass = _FakeHass(entry.entry_id)

    result = await flow.async_step_init(
        {
            "ip": "192.168.1.72",
            "timeout": 0.3,
            CONF_LIGHT_POLL_INTERVAL: 60,
            CONF_SWITCH_POLL_INTERVAL: 20,
            CONF_DIY_DPID_MAPPINGS: "10=Leak Alarm",
        }
    )

    assert result["type"] == "form"
    assert result["errors"] == {CONF_DIY_DPID_MAPPINGS: "unsupported_diy_dpid"}
    assert flow.hass.config_entries.updated_data is None


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_single_device_options_persist_diy_control_mapping_with_write_opt_in() -> None:
    """DIY control mappings should require per-device write opt-in."""

    entry = SimpleNamespace(
        entry_id="entry-diy-write-1",
        data={
            "device": {
                "did": "unknown-3",
                "ip": "192.168.1.73",
                "pid": "pid-unknown",
                "dpid": [7, 10],
                "dmn": "DIY Device",
                "type": "unknown",
            },
            "timeout": 0.3,
        },
        options={},
    )
    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)
    flow.hass = _FakeHass(entry.entry_id)
    flow.async_create_entry = lambda *, title, data: {
        "type": "create_entry",
        "title": title,
        "data": data,
    }

    with patch("custom_components.cozylife.config_flow.tcp_client", _ProbeTcpClient):
        result = await flow.async_step_init(
            {
                "ip": "192.168.1.73",
                "timeout": 0.3,
                CONF_LIGHT_POLL_INTERVAL: 60,
                CONF_SWITCH_POLL_INTERVAL: 20,
                CONF_DIY_CONTROL_MAPPINGS: "7=switch:bool:Contact Relay",
                CONF_ENABLE_DIY_WRITES: True,
            }
        )

    assert result["type"] == "create_entry"
    assert flow.hass.config_entries.updated_data["device"][CONF_ENABLE_DIY_WRITES] is True
    assert flow.hass.config_entries.updated_data["device"][CONF_DIY_CONTROL_MAPPINGS] == [
        {
            "dpid": 7,
            "name": "Contact Relay",
            "entity_kind": "switch",
            "value_type": "bool",
        }
    ]


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_single_device_options_require_write_opt_in_for_diy_control_mapping() -> None:
    """DIY write mappings should not save without explicit per-device opt-in."""

    entry = SimpleNamespace(
        entry_id="entry-diy-write-2",
        data={
            "device": {
                "did": "unknown-4",
                "ip": "192.168.1.74",
                "pid": "pid-unknown",
                "dpid": [7],
                "dmn": "DIY Device",
                "type": "unknown",
            },
            "timeout": 0.3,
        },
        options={},
    )
    with patch("homeassistant.config_entries.report_usage", return_value=None):
        flow = CozyLifeOptionsFlow(entry)
    flow.hass = _FakeHass(entry.entry_id)

    with patch("custom_components.cozylife.config_flow.tcp_client", _ProbeTcpClient):
        result = await flow.async_step_init(
            {
                "ip": "192.168.1.74",
                "timeout": 0.3,
                CONF_LIGHT_POLL_INTERVAL: 60,
                CONF_SWITCH_POLL_INTERVAL: 20,
                CONF_DIY_CONTROL_MAPPINGS: "7=switch:bool:Contact Relay",
            }
        )

    assert result["type"] == "form"
    assert result["errors"] == {CONF_ENABLE_DIY_WRITES: "enable_diy_writes_required"}
