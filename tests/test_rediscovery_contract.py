"""Contract tests for CozyLife broadcast rediscovery."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from custom_components.cozylife import _async_setup_broadcast_rediscovery
from custom_components.cozylife.const import DOMAIN


class _FakeClient:
    """Minimal runtime client used by rediscovery tests."""

    def __init__(self, device_id: str, ip: str) -> None:
        self._device_id = device_id
        self._ip = ip
        self.disconnect_calls = 0

    @property
    def device_id(self) -> str:
        return self._device_id

    def disconnect(self) -> None:
        self.disconnect_calls += 1


class _FakeConfig:
    """Minimal config object with a Home Assistant-like path method."""

    def path(self, *parts: str) -> str:
        return "C:/fake/" + "/".join(parts)


class _FakeConfigEntries:
    """Capture config-entry mutations triggered by rediscovery."""

    def __init__(self) -> None:
        self.updated_entry = None
        self.updated_data = None
        self.reloaded_entry_id = None

    def async_update_entry(self, entry, data) -> None:
        self.updated_entry = entry
        self.updated_data = data

    async def async_reload(self, entry_id: str) -> None:
        self.reloaded_entry_id = entry_id


class _FakeHass:
    """Minimal Home Assistant double for rediscovery tests."""

    def __init__(self, entry_id: str, entry_data: dict[str, object]) -> None:
        self.config = _FakeConfig()
        self.config_entries = _FakeConfigEntries()
        self.data = {DOMAIN: {entry_id: entry_data}}

    async def async_add_executor_job(self, func, *args):
        return func(*args)


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_broadcast_rediscovery_repairs_ip_and_reload_state() -> None:
    """Rediscovery should repair stale IPs in runtime and stored entry data."""

    runtime_client = _FakeClient("did-1", "192.168.1.10")
    entry = SimpleNamespace(
        entry_id="entry-1",
        data={
            "device": {
                "did": "did-1",
                "ip": "192.168.1.10",
                "pid": "pid-1",
                "dpid": [1],
                "dmn": "Desk Lamp",
                "type": "light",
            },
            "timeout": 0.3,
        },
    )
    entry_data = {
        "device": dict(entry.data["device"]),
        "timeout": 0.3,
        "light_runtime": {"lights": [SimpleNamespace(_tcp_client=runtime_client)]},
    }
    hass = _FakeHass(entry.entry_id, entry_data)
    scheduled_callbacks = []

    def _capture_interval(hass, callback, interval):
        scheduled_callbacks.append(callback)
        return lambda: None

    with (
        patch(
            "custom_components.cozylife.async_track_time_interval",
            side_effect=_capture_interval,
        ),
        patch(
            "custom_components.cozylife.discover_devices_via_broadcast",
            return_value={
                "lights": [
                    {
                        "did": "did-1",
                        "ip": "192.168.1.99",
                        "pid": "pid-1",
                        "dpid": [1],
                        "dmn": "Desk Lamp",
                        "type": "light",
                    }
                ],
                "switches": [],
                "sensors": [],
                "unknown": [],
            },
        ),
    ):
        await _async_setup_broadcast_rediscovery(hass, entry, entry_data)
        await scheduled_callbacks[0]()

    assert runtime_client._ip == "192.168.1.99"
    assert runtime_client.disconnect_calls == 1
    assert hass.config_entries.updated_entry is entry
    assert hass.config_entries.updated_data["device"]["ip"] == "192.168.1.99"
    assert hass.config_entries.reloaded_entry_id == "entry-1"
