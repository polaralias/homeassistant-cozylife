"""Behavior tests for CozyLife entity surfacing."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from custom_components.cozylife.const import DOMAIN
from custom_components.cozylife import light as light_platform
from custom_components.cozylife import sensor as sensor_platform
from custom_components.cozylife import switch as switch_platform


class _FakeTcpClient:
    """Minimal TCP client test double used by entity setup tests."""

    def __init__(self, ip: str, timeout: float = 0.3, model_path=None) -> None:
        self._ip = ip
        self.timeout = timeout
        self._model_path = model_path
        self._device_id = None
        self._pid = None
        self._dpid = []
        self._device_model_name = None
        self.name = None

    @property
    def dpid(self) -> list[int]:
        return self._dpid

    @property
    def device_id(self) -> str | None:
        return self._device_id

    def query(self) -> dict[str, int]:
        return {"1": 0}

    def control(self, payload: dict[str, int]) -> bool:
        return True

    def disconnect(self) -> None:
        return None


class _FakeConfig:
    """Minimal Home Assistant config object."""

    def path(self, *parts: str) -> str:
        return str(Path.cwd().joinpath(*parts))


class _FakeServices:
    """Minimal Home Assistant services registry."""

    def has_service(self, domain: str, service: str) -> bool:
        return False

    def async_remove(self, domain: str, service: str) -> None:
        return None

    def async_register(self, domain: str, service: str, handler) -> None:
        return None


class _FakeHass:
    """Minimal Home Assistant test double."""

    def __init__(self, entry_id: str, entry_data: dict[str, object]) -> None:
        self.data = {DOMAIN: {entry_id: entry_data}}
        self.config = _FakeConfig()
        self.services = _FakeServices()

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class _FakePlatform:
    """Minimal entity platform used by the light setup path."""

    def async_register_entity_service(self, service, schema, method) -> None:
        return None


class _EntityCollector:
    """Capture entities added by a platform setup call."""

    def __init__(self) -> None:
        self.entities = []

    def __call__(self, entities, update_before_add=False) -> None:
        self.entities.extend(entities)


class _StateAwareTcpClient(_FakeTcpClient):
    """TCP client double that returns a supplied live device state."""

    def __init__(
        self,
        ip: str,
        *,
        dpid: list[int],
        device_id: str,
        model_name: str,
        state: dict[str, int],
    ) -> None:
        super().__init__(ip)
        self._dpid = dpid
        self._device_id = device_id
        self._device_model_name = model_name
        self._state = state

    def query(self) -> dict[str, int]:
        return dict(self._state)


class _MutableStateTcpClient(_StateAwareTcpClient):
    """TCP client double that applies control payloads to mutable state."""

    def control(self, payload: dict[str, int]) -> bool:
        self._state.update({str(key): value for key, value in payload.items()})
        return True


class _CustomSwitchTcpClient(_FakeTcpClient):
    """TCP client double for custom DIY switch entities."""

    def __init__(self, ip: str, timeout: float = 0.3, model_path=None) -> None:
        super().__init__(ip, timeout, model_path)
        self._device_id = "unknown-device-2"
        self._device_model_name = "Unverified Device"
        self._state = {"7": 1}

    def query(self) -> dict[str, int]:
        return dict(self._state)

    def control(self, payload: dict[str, int]) -> bool:
        self._state.update({str(key): value for key, value in payload.items()})
        return True


class _EntityHass:
    """Minimal hass object for direct entity behavior tests."""

    def __init__(self) -> None:
        self.data = {}

    async def async_add_executor_job(self, func, *args):
        return func(*args)


def _build_light_entity(state: dict[str, int]) -> tuple[light_platform.CozyLifeLight, _MutableStateTcpClient]:
    """Create a live-state light entity test double pair."""

    client = _MutableStateTcpClient(
        "192.168.1.50",
        dpid=[1, 3, 4, 5, 6],
        device_id="light-device-1",
        model_name="Desk Lamp",
        state=state,
    )
    entity = light_platform.CozyLifeLight(client, _EntityHass(), light_platform.SCENES)
    entity.async_write_ha_state = lambda *args, **kwargs: None
    entity._refresh_state()
    return entity, client


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_switch_class_device_only_creates_switch_entity() -> None:
    """Switch-class devices should not be re-surfaced as lights."""

    entry = SimpleNamespace(
        entry_id="entry-1",
        data={
            "device": {
                "ip": "192.168.1.10",
                "did": "switch-device-1",
                "pid": "pid-switch",
                "dpid": [1],
                "dmn": "Desk Switch",
                "type": "switch",
            },
            "timeout": 0.3,
            "name": "Desk Switch",
        },
    )
    hass = _FakeHass(entry.entry_id, dict(entry.data))
    light_entities = _EntityCollector()
    switch_entities = _EntityCollector()

    with (
        patch.object(light_platform, "tcp_client", _FakeTcpClient),
        patch.object(switch_platform, "tcp_client", _FakeTcpClient),
        patch(
            "custom_components.cozylife.light.async_track_time_interval",
            return_value=lambda: None,
        ),
        patch(
            "custom_components.cozylife.switch.async_track_time_interval",
            return_value=lambda: None,
        ),
        patch(
            "custom_components.cozylife.light.entity_platform.async_get_current_platform",
            return_value=_FakePlatform(),
        ),
    ):
        await light_platform.async_setup_entry(hass, entry, light_entities)
        await switch_platform.async_setup_entry(hass, entry, switch_entities)

    assert light_entities.entities == []
    assert len(switch_entities.entities) == 1
    assert switch_entities.entities[0].unique_id == "switch-device-1"


@pytest.mark.cozylife
def test_light_refresh_uses_live_white_mode_over_startup_hs_inference() -> None:
    """Light color mode should follow queried state instead of capability hints."""

    client = _StateAwareTcpClient(
        "192.168.1.50",
        dpid=[1, 4, 5, 6],
        device_id="light-device-1",
        model_name="Desk Lamp",
        state={"1": 1, "2": 0, "4": 500},
    )
    entity = light_platform.CozyLifeLight(client, SimpleNamespace(data={}), light_platform.SCENES)

    entity._refresh_state()

    assert entity.color_mode == light_platform.COLOR_MODE_WHITE
    assert entity.brightness == 127


@pytest.mark.cozylife
def test_modern_supported_color_modes_do_not_mix_brightness_with_ct_or_hs() -> None:
    """Modern HA color modes should avoid invalid ONOFF/BRIGHTNESS combinations."""

    entity, _ = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251, "5": 120, "6": 800})

    assert entity.supported_color_modes == {
        light_platform.COLOR_MODE_COLOR_TEMP,
        light_platform.COLOR_MODE_HS,
    }


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_brightness_transition_in_white_mode_does_not_require_color_temp_target() -> None:
    """Brightness transitions should work without also supplying color temperature."""

    entity, client = _build_light_entity({"1": 1, "2": 0, "3": 0, "4": 1000})

    await entity.async_turn_on(brightness=64, transition=0.1)

    assert client.query()["4"] == 251


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_color_temp_transition_keeps_existing_brightness() -> None:
    """Kelvin color-temperature transitions should not require brightness input."""

    entity, client = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    await entity.async_turn_on(color_temp_kelvin=2700, transition=0.1)

    state = client.query()
    assert state["3"] == 0
    assert state["4"] == 251


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_hs_transition_keeps_existing_brightness() -> None:
    """HS transitions should not require a brightness payload."""

    entity, client = _build_light_entity(
        {"1": 1, "2": 0, "3": 65535, "4": 251, "5": 200, "6": 800}
    )

    await entity.async_turn_on(hs_color=(240, 100), transition=0.1)

    state = client.query()
    assert state["4"] == 251
    assert state["5"] == 240
    assert state["6"] == 1000


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_kelvin_color_temp_turn_on_maps_to_device_payload() -> None:
    """Newer Kelvin-based HA light API should still drive CozyLife CT writes."""

    entity, client = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    await entity.async_turn_on(color_temp_kelvin=2700)

    state = client.query()
    assert state["3"] == 0


@pytest.mark.cozylife
def test_kelvin_properties_are_exposed_for_newer_home_assistant() -> None:
    """Entity should expose Kelvin properties for Home Assistant light state."""

    entity, _ = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    assert entity.color_temp_kelvin is not None
    assert entity.min_color_temp_kelvin == 2700
    assert entity.max_color_temp_kelvin == 6500


@pytest.mark.cozylife
def test_light_effect_list_excludes_removed_natural_mode() -> None:
    """Circadian Lighting should not leak a synthetic natural effect."""

    entity, _ = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    assert "natural" not in entity.effect_list


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_manual_controls_normalize_effect_to_effect_off() -> None:
    """Direct light controls should surface the standard HA no-effect marker."""

    entity, _ = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    await entity.async_turn_on(brightness=128)

    assert entity.effect == light_platform.EFFECT_OFF


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_manual_effect_alias_maps_to_effect_off() -> None:
    """Legacy manual effect requests should normalize to HA's EFFECT_OFF."""

    entity, _ = _build_light_entity({"1": 1, "2": 0, "3": 500, "4": 251})

    await entity.async_set_effect("manual")

    assert entity.effect == light_platform.EFFECT_OFF


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_unknown_device_with_diy_mapping_surfaces_custom_sensor_entities() -> None:
    """Unknown devices should surface only explicit DIY-mapped sensor entities."""

    entry = SimpleNamespace(
        entry_id="entry-diy-sensor-1",
        data={
            "device": {
                "ip": "192.168.1.80",
                "did": "unknown-device-1",
                "pid": "pid-unknown",
                "dpid": [7, 10],
                "dmn": "Unverified Device",
                "type": "unknown",
                "diy_dpid_mappings": [
                    {"dpid": 7, "name": "Contact Raw"},
                    {"dpid": 10, "name": "Leak Alarm"},
                ],
            },
            "timeout": 0.3,
            "name": "Garage Probe",
        },
    )
    hass = _FakeHass(entry.entry_id, dict(entry.data))
    sensor_entities = _EntityCollector()

    with patch.object(sensor_platform, "tcp_client", _FakeTcpClient):
        await sensor_platform.async_setup_entry(hass, entry, sensor_entities)

    assert len(sensor_entities.entities) == 2
    assert [entity.name for entity in sensor_entities.entities] == [
        "Contact Raw",
        "Leak Alarm",
    ]
    assert [entity.unique_id for entity in sensor_entities.entities] == [
        "unknown-device-1_7",
        "unknown-device-1_10",
    ]
    assert [entity.extra_state_attributes["mapping"] for entity in sensor_entities.entities] == [
        "custom",
        "custom",
    ]


@pytest.mark.asyncio
@pytest.mark.cozylife
async def test_unknown_device_with_diy_write_mapping_surfaces_custom_switch_entity() -> None:
    """Unknown devices with write opt-in should surface custom bool switch entities."""

    entry = SimpleNamespace(
        entry_id="entry-diy-switch-1",
        data={
            "device": {
                "ip": "192.168.1.81",
                "did": "unknown-device-2",
                "pid": "pid-unknown",
                "dpid": [7],
                "dmn": "Unverified Device",
                "type": "unknown",
                "enable_diy_writes": True,
                "diy_control_mappings": [
                    {
                        "dpid": 7,
                        "name": "Contact Relay",
                        "entity_kind": "switch",
                        "value_type": "bool",
                    }
                ],
            },
            "timeout": 0.3,
            "name": "Garage Probe",
        },
    )
    hass = _FakeHass(entry.entry_id, dict(entry.data))
    switch_entities = _EntityCollector()

    with (
        patch.object(switch_platform, "tcp_client", _CustomSwitchTcpClient),
        patch(
            "custom_components.cozylife.switch.async_track_time_interval",
            return_value=lambda: None,
        ),
    ):
        await switch_platform.async_setup_entry(hass, entry, switch_entities)

    assert len(switch_entities.entities) == 1
    entity = switch_entities.entities[0]
    assert entity.unique_id == "unknown-device-2_7_switch"
    assert entity.name == "Contact Relay"
    assert entity.is_on is True
    assert entity.extra_state_attributes == {
        "dpid": "7",
        "mapping": "custom",
        "entity_kind": "switch",
        "value_type": "bool",
    }
