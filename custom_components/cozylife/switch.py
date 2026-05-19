"""Switch platform for CozyLife devices."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
from pathlib import Path
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_AREA,
    CONF_DIY_CONTROL_MAPPINGS,
    CONF_ENABLE_DIY_WRITES,
    DEFAULT_SWITCH_POLL_INTERVAL,
    DOMAIN,
    MANUFACTURER,
)
from .helpers import (
    normalize_area_value,
    normalize_diy_control_mappings,
    resolve_area_id,
)
from .tcp_client import tcp_client

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _SwitchRuntimeConfig:
    """Normalised config used to instantiate a switch entity."""

    client: tcp_client
    name: str
    area_id: str | None
    device_name: str | None = None
    control_dpid: int = 1
    custom: bool = False


def _build_client(
    device_info: dict[str, Any],
    *,
    timeout: float,
    model_path: Path,
) -> tcp_client:
    """Create a prepared CozyLife TCP client for an entity."""

    client = tcp_client(device_info.get("ip"), timeout=timeout, model_path=model_path)
    client._device_id = device_info.get("did")
    client._pid = device_info.get("pid")
    client._dpid = device_info.get("dpid") or []
    client._device_model_name = device_info.get("dmn")
    return client


def _resolve_entity_name(
    client: tcp_client,
    stored_name: str | None,
    device_info: dict[str, Any],
) -> str:
    """Resolve the friendly name for a switch-class device."""

    return (
        stored_name
        or client._device_model_name
        or client.device_id
        or "CozyLife"
    )


def _iter_switch_runtime_configs(
    data: dict[str, object],
    *,
    timeout: float,
    model_path: Path,
    hass: HomeAssistant,
) -> list[_SwitchRuntimeConfig]:
    """Flatten config-entry device shapes into switch runtime definitions."""

    configs: list[_SwitchRuntimeConfig] = []

    def append_configs(
        device_info: dict[str, Any],
        *,
        stored_name: str | None,
        raw_area: str | None,
    ) -> None:
        client = _build_client(device_info, timeout=timeout, model_path=model_path)
        if not client.device_id:
            return

        friendly_name = _resolve_entity_name(client, stored_name, device_info)
        client.name = friendly_name
        area_id = resolve_area_id(hass, raw_area) or normalize_area_value(raw_area)

        if device_info.get("type") == "switch":
            configs.append(
                _SwitchRuntimeConfig(
                    client=client,
                    name=friendly_name,
                    area_id=area_id,
                    device_name=friendly_name,
                )
            )

        if not device_info.get(CONF_ENABLE_DIY_WRITES):
            return

        for mapping in normalize_diy_control_mappings(
            device_info.get(CONF_DIY_CONTROL_MAPPINGS)
        ):
            configs.append(
                _SwitchRuntimeConfig(
                    client=client,
                    name=mapping["name"],
                    area_id=area_id,
                    device_name=friendly_name,
                    control_dpid=int(mapping["dpid"]),
                    custom=True,
                )
            )

    if device := data.get("device"):
        if isinstance(device, dict):
            append_configs(
                device,
                stored_name=data.get(CONF_NAME) or data.get("name"),
                raw_area=data.get(CONF_AREA) or data.get("location"),
            )
    elif isinstance(data.get("devices"), list):
        for item in data["devices"]:
            device_info = item.get("device", {})
            if not isinstance(device_info, dict) or not device_info:
                continue
            append_configs(
                device_info,
                stored_name=item.get(CONF_NAME),
                raw_area=item.get(CONF_AREA) or device_info.get("location"),
            )
    else:
        devices = data.get("devices", {})
        if not isinstance(devices, dict):
            return configs
        for item in devices.get("switches", []):
            if not isinstance(item, dict):
                continue
            append_configs(
                item,
                stored_name=item.get("name"),
                raw_area=item.get("location"),
            )

    return configs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CozyLife switches from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    timeout = data.get("timeout", entry.data.get("timeout", 0.3))
    model_path = Path(hass.config.path("custom_components", DOMAIN, "model.json"))

    entities: list[CozyLifeSwitch] = []
    for config in _iter_switch_runtime_configs(
        data,
        timeout=timeout,
        model_path=model_path,
        hass=hass,
    ):
        if config.custom:
            entities.append(
                CozyLifeMappedSwitch(
                    config.client,
                    hass,
                    dpid=config.control_dpid,
                    name=config.name,
                    area_id=config.area_id,
                    device_name=config.device_name,
                )
            )
        else:
            entities.append(
                CozyLifeSwitch(
                    config.client,
                    hass,
                    name=config.name,
                    area_id=config.area_id,
                )
            )

    if not entities:
        return

    interval_seconds = data.get("poll_intervals", {}).get(
        "switch",
        DEFAULT_SWITCH_POLL_INTERVAL,
    )
    interval = timedelta(seconds=interval_seconds)

    async_add_entities(entities, update_before_add=True)

    async def async_refresh(now=None) -> None:
        for entity in entities:
            await hass.async_add_executor_job(entity._refresh_state)
            entity.async_write_ha_state()
            await asyncio.sleep(0.01)

    remove_update = async_track_time_interval(hass, async_refresh, interval)
    data.setdefault("switch_runtime", {})
    data["switch_runtime"].update(
        {
            "switches": entities,
            "remove_update": remove_update,
        }
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CozyLife switch entities for a config entry."""

    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    runtime = data.get("switch_runtime", {})
    if remove := runtime.get("remove_update"):
        remove()
    return True


class CozyLifeSwitch(SwitchEntity):
    """Home Assistant switch backed by a CozyLife datapoint."""

    def __init__(
        self,
        tcp_client: tcp_client,
        hass,
        *,
        name: str | None = None,
        area_id: str | None = None,
    ) -> None:
        self.hass = hass
        self._tcp_client = tcp_client
        self._unique_id = tcp_client.device_id
        self._name = name or tcp_client.name or tcp_client.device_id[-4:]
        self._area_id = area_id or None
        self._attr_name = self._name
        self._attr_available = False
        self._attr_is_on = True
        self._attr_suggested_area = None
        self._control_dpid = "1"
        self._state: dict[str, Any] = {}
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, tcp_client.device_id)},
            manufacturer=MANUFACTURER,
            model=tcp_client._device_model_name,
            name=self._name,
        )
        if self._area_id:
            self._device_info["suggested_area"] = self._area_id

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if self._area_id:
            area_registry = ar.async_get(self.hass)
            area = area_registry.async_get_area(self._area_id)
            suggested_area = area.name if area else self._area_id
            self._device_info["suggested_area"] = suggested_area
            self._attr_suggested_area = suggested_area
        await self.async_update()

    async def async_update(self) -> None:
        await self.hass.async_add_executor_job(self._refresh_state)

    def _refresh_state(self) -> None:
        state = self._tcp_client.query()
        _LOGGER.info("Refreshed CozyLife switch %s state: %s", self._name, state)
        if isinstance(state, dict):
            self._state = state
            self._attr_is_on = int(state.get(self._control_dpid, 0)) > 0
            self._attr_available = True
        else:
            self._attr_available = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        return self._device_info

    @property
    def available(self) -> bool:
        return bool(self._attr_available)

    @property
    def is_on(self) -> bool:
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()
        await self.hass.async_add_executor_job(
            self._tcp_client.control,
            {self._control_dpid: 1},
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
        await self.hass.async_add_executor_job(
            self._tcp_client.control,
            {self._control_dpid: 0},
        )


class CozyLifeMappedSwitch(CozyLifeSwitch):
    """Custom user-defined writable switch for a specific DPID."""

    def __init__(
        self,
        tcp_client: tcp_client,
        hass,
        *,
        dpid: int,
        name: str,
        area_id: str | None = None,
        device_name: str | None = None,
    ) -> None:
        super().__init__(tcp_client, hass, name=name, area_id=area_id)
        self._control_dpid = str(dpid)
        self._unique_id = f"{tcp_client.device_id}_{self._control_dpid}_switch"
        self._attr_name = name
        self._name = name
        if device_name:
            self._device_info["name"] = device_name
        self._attr_has_entity_name = True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "dpid": self._control_dpid,
            "mapping": "custom",
            "entity_kind": "switch",
            "value_type": "bool",
        }
