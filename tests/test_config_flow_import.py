"""Contract tests for CozyLife config-flow import behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from custom_components.cozylife.config_flow import CozyLifeConfigFlow
from custom_components.cozylife.const import CONF_AREA, DOMAIN


class _FakeConfig:
    """Minimal config object with a Home Assistant-like path method."""

    def path(self, *parts: str) -> str:
        return str(Path.cwd().joinpath(*parts))


class _FakeHass:
    """Minimal Home Assistant double for config-flow tests."""

    def __init__(self) -> None:
        self.config = _FakeConfig()

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class _FakeTcpClient:
    """Probe double for IP-only import tests."""

    def __init__(self, ip, timeout=3, model_path=None) -> None:
        self._ip = ip
        self.timeout = timeout
        self._model_path = model_path
        self._device_id = None
        self._device_type_code = None
        self._pid = None
        self._dpid = None
        self._device_model_name = None

    def _initSocket(self) -> None:
        return None

    def _device_info(self) -> None:
        self._device_id = "did-1"
        self._device_type_code = "01"
        self._pid = "pid-1"
        self._dpid = [1, 4]
        self._device_model_name = "Desk Lamp"

    def disconnect(self) -> None:
        return None


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_import_from_ip_probes_and_creates_canonical_entry() -> None:
    """IP-only import should probe the device and create a canonical entry."""

    flow = CozyLifeConfigFlow()
    flow.hass = _FakeHass()

    unique_ids: list[str] = []

    async def _async_set_unique_id(value: str) -> None:
        unique_ids.append(value)

    flow.async_set_unique_id = _async_set_unique_id
    flow._abort_if_unique_id_configured = lambda updates=None: None
    flow.async_create_entry = lambda *, title, data: {
        "type": "create_entry",
        "title": title,
        "data": data,
    }

    with (
        patch("custom_components.cozylife.config_flow.tcp_client", _FakeTcpClient),
        patch(
            "custom_components.cozylife.config_flow.prepare_area_value_for_storage",
            side_effect=lambda hass, value: value,
        ),
    ):
        result = await flow.async_step_import(
            {
                "device": {"ip": "192.168.1.50"},
                "timeout": 0.5,
                "name": "  Desk Lamp  ",
                CONF_AREA: "Office",
            }
        )

    assert unique_ids == ["did-1"]
    assert result == {
        "type": "create_entry",
        "title": "Desk Lamp",
        "data": {
            "device": {
                "ip": "192.168.1.50",
                "did": "did-1",
                "pid": "pid-1",
                "dpid": [1, 4],
                "dmn": "Desk Lamp",
                "type": "light",
            },
            "timeout": 0.5,
            "name": "Desk Lamp",
            CONF_AREA: "Office",
        },
    }
