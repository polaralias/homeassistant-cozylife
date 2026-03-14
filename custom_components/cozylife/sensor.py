"""Sensor platform for CozyLife devices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_AREA, DEFAULT_SWITCH_POLL_INTERVAL, DOMAIN, MANUFACTURER
from .helpers import normalize_area_value, resolve_area_id
from .tcp_client import tcp_client

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CozyLifeSensorDescription:
    """Describe a CozyLife sensor datapoint entity."""

    key: str
    name: str
    inferred: bool = False


class CozyLifeSensorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll a CozyLife sensor device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: tcp_client,
        poll_interval: float,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{client.device_id}",
            update_interval=timedelta(seconds=poll_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        data = await self.hass.async_add_executor_job(self.client.query)
        if not isinstance(data, dict) or not data:
            raise UpdateFailed("No data returned by CozyLife sensor")
        return data


def _iter_sensor_devices(data: dict[str, object]) -> list[tuple[dict[str, Any], str | None, str | None]]:
    """Return the configured CozyLife sensor devices for an entry."""

    sensors: list[tuple[dict[str, Any], str | None, str | None]] = []

    if device := data.get("device"):
        if isinstance(device, dict) and device.get("type") == "sensor":
            sensors.append(
                (
                    dict(device),
                    data.get(CONF_NAME) or data.get("name"),
                    data.get(CONF_AREA) or data.get("location"),
                )
            )
    elif isinstance(data.get("devices"), list):
        for item in data["devices"]:
            device_info = item.get("device", {})
            if not device_info or device_info.get("type") != "sensor":
                continue

            sensors.append(
                (
                    dict(device_info),
                    item.get(CONF_NAME),
                    item.get(CONF_AREA) or device_info.get("location"),
                )
            )
    else:
        devices = data.get("devices", {})
        if isinstance(devices, dict):
            for item in devices.get("sensors", []):
                if not isinstance(item, dict):
                    continue

                sensors.append((dict(item), item.get("name"), item.get("location")))

    return sensors


def _build_sensor_descriptions(
    model_name: str | None,
    dpids: list[int],
    discovered_keys: set[str],
) -> list[CozyLifeSensorDescription]:
    """Build entity descriptions for a CozyLife sensor device."""

    descriptions: dict[str, CozyLifeSensorDescription] = {}
    name = (model_name or "").lower()

    if "temperature" in name and "humidity" in name:
        if 4 in dpids:
            descriptions["4"] = CozyLifeSensorDescription("4", "Temperature Raw", True)
        if 6 in dpids:
            descriptions["6"] = CozyLifeSensorDescription("6", "Humidity Raw", True)

    if "door magnet" in name or "gate magnet" in name:
        if 7 in dpids:
            descriptions["7"] = CozyLifeSensorDescription("7", "Contact Raw", True)

    if "motion" in name:
        if 6 in dpids:
            descriptions["6"] = CozyLifeSensorDescription("6", "Motion Raw", True)

    if "radar" in name:
        if 103 in dpids:
            descriptions["103"] = CozyLifeSensorDescription("103", "Presence Raw", True)

    if "water sensor" in name and 10 in dpids:
        descriptions["10"] = CozyLifeSensorDescription("10", "Water Alarm Raw", True)

    if "smoke sensor" in name and 11 in dpids:
        descriptions["11"] = CozyLifeSensorDescription("11", "Smoke Alarm Raw", True)

    for dpid in sorted({int(key) for key in discovered_keys if str(key).isdigit()} | set(dpids)):
        key = str(dpid)
        descriptions.setdefault(
            key,
            CozyLifeSensorDescription(key, f"DPID {dpid}", False),
        )

    return list(descriptions.values())


def _coerce_native_value(value: Any) -> Any:
    """Convert raw CozyLife values into HA-friendly sensor states."""

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    try:
        return json.dumps(value, sort_keys=True)
    except TypeError:
        return str(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CozyLife sensors from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    timeout = data.get("timeout", entry.data.get("timeout", 0.3))
    poll_interval = data.get("poll_intervals", {}).get(
        "sensor", DEFAULT_SWITCH_POLL_INTERVAL
    )
    model_path = Path(hass.config.path("custom_components", DOMAIN, "model.json"))

    entities: list[CozyLifeValueSensor] = []

    for device_info, stored_name, raw_area in _iter_sensor_devices(data):
        client = tcp_client(device_info.get("ip"), timeout=timeout, model_path=model_path)
        client._device_id = device_info.get("did")
        client._pid = device_info.get("pid")
        client._dpid = device_info.get("dpid") or []
        client._device_model_name = device_info.get("dmn")

        if not client.device_id:
            continue

        friendly_name = (
            stored_name
            or device_info.get("dmn")
            or device_info.get("did")
            or "CozyLife Sensor"
        )
        client.name = friendly_name
        area_id = resolve_area_id(hass, raw_area) or normalize_area_value(raw_area)

        coordinator = CozyLifeSensorCoordinator(
            hass,
            client,
            float(poll_interval),
        )
        await coordinator.async_refresh()

        descriptions = _build_sensor_descriptions(
            client._device_model_name,
            [int(dpid) for dpid in client._dpid if isinstance(dpid, int)],
            set(coordinator.data.keys()) if isinstance(coordinator.data, dict) else set(),
        )

        if not descriptions:
            continue

        device_metadata = DeviceInfo(
            identifiers={(DOMAIN, client.device_id)},
            manufacturer=MANUFACTURER,
            model=client._device_model_name,
            name=friendly_name,
        )
        if area_id:
            device_metadata["suggested_area"] = area_id

        for description in descriptions:
            entities.append(
                CozyLifeValueSensor(
                    coordinator,
                    client,
                    device_metadata,
                    description,
                    area_id,
                )
            )

    if not entities:
        return

    data.setdefault("sensor_runtime", {})
    data["sensor_runtime"]["entities"] = entities
    async_add_entities(entities)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CozyLife sensor entities for a config entry."""

    return True


class CozyLifeValueSensor(CoordinatorEntity[CozyLifeSensorCoordinator], SensorEntity):
    """Expose a single CozyLife sensor datapoint."""

    def __init__(
        self,
        coordinator: CozyLifeSensorCoordinator,
        tcp_client: tcp_client,
        device_info: DeviceInfo,
        description: CozyLifeSensorDescription,
        area_id: str | None,
    ) -> None:
        """Initialise the CozyLife datapoint sensor."""

        super().__init__(coordinator)
        self._tcp_client = tcp_client
        self._device_info = device_info
        self._description = description
        self._area_id = area_id
        self._attr_name = description.name
        self._attr_unique_id = f"{tcp_client.device_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_suggested_area = None

    async def async_added_to_hass(self) -> None:
        """Set area metadata after entity registration."""

        await super().async_added_to_hass()
        if self._area_id:
            area_registry = ar.async_get(self.hass)
            area = area_registry.async_get_area(self._area_id)
            if area:
                self._device_info["suggested_area"] = area.name
                self._attr_suggested_area = area.name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device metadata for this entity."""

        return self._device_info

    @property
    def available(self) -> bool:
        """Return if the underlying device is available."""

        return (
            self.coordinator.last_update_success
            and isinstance(self.coordinator.data, dict)
            and self._description.key in self.coordinator.data
        )

    @property
    def native_value(self) -> Any:
        """Return the current datapoint value."""

        return _coerce_native_value(self.coordinator.data.get(self._description.key))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return metadata about the mapped datapoint."""

        return {
            "dpid": self._description.key,
            "mapping": "inferred" if self._description.inferred else "raw",
        }
