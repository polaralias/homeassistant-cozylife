"""CozyLife integration setup for Home Assistant."""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_AREA,
    CONF_LIGHT_POLL_INTERVAL,
    CONF_SWITCH_POLL_INTERVAL,
    DEFAULT_BROADCAST_DISCOVERY_INTERVAL,
    DEFAULT_LIGHT_POLL_INTERVAL,
    DEFAULT_SWITCH_POLL_INTERVAL,
    DOMAIN,
)
from .discovery import discover_devices_via_broadcast
from .helpers import normalize_area_value, prepare_area_value_for_storage

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH, Platform.SENSOR]


def _iter_runtime_clients(entry_data: dict[str, object]):
    """Yield runtime TCP clients created for a config entry."""

    seen: set[int] = set()

    for runtime_key, collection_key in (
        ("light_runtime", "lights"),
        ("light_runtime", "switches"),
        ("switch_runtime", "switches"),
        ("sensor_runtime", "entities"),
    ):
        runtime = entry_data.get(runtime_key)
        if not isinstance(runtime, dict):
            continue

        for entity in runtime.get(collection_key, []):
            client = getattr(entity, "_tcp_client", None)
            if client is None:
                continue

            marker = id(client)
            if marker in seen:
                continue

            seen.add(marker)
            yield client


def _update_device_payload(
    device_payload: dict[str, Any],
    discovered_by_did: dict[str, dict[str, object]],
) -> bool:
    """Update a stored device payload from a discovery result."""

    device_id = device_payload.get("did")
    if not isinstance(device_id, str):
        return False

    discovered = discovered_by_did.get(device_id)
    if not discovered:
        return False

    updated = False
    for key in ("ip", "pid", "dpid", "dmn", "type"):
        value = discovered.get(key)
        if value is None or device_payload.get(key) == value:
            continue

        device_payload[key] = value
        updated = True

    return updated


def _refresh_entry_data_from_discovery(
    entry_data: dict[str, Any],
    discovered_by_did: dict[str, dict[str, object]],
) -> bool:
    """Update entry data from broadcast discovery results."""

    updated = False

    device = entry_data.get("device")
    if isinstance(device, dict):
        updated = _update_device_payload(device, discovered_by_did) or updated

    devices_value = entry_data.get("devices")
    if isinstance(devices_value, list):
        for device_entry in devices_value:
            if not isinstance(device_entry, dict):
                continue

            device_payload = device_entry.get("device")
            if isinstance(device_payload, dict):
                updated = (
                    _update_device_payload(device_payload, discovered_by_did) or updated
                )
    elif isinstance(devices_value, dict):
        for items in devices_value.values():
            candidates = items if isinstance(items, list) else [items]
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue

                updated = (
                    _update_device_payload(candidate, discovered_by_did) or updated
                )

    return updated


async def _async_setup_broadcast_rediscovery(
    hass: HomeAssistant,
    entry: ConfigEntry,
    entry_data: dict[str, object],
) -> None:
    """Schedule periodic UDP broadcast rediscovery for configured devices."""

    model_path = Path(hass.config.path("custom_components", DOMAIN, "model.json"))

    async def _async_rediscover(now=None) -> None:
        current_entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
        if not isinstance(current_entry_data, dict):
            return

        timeout = float(current_entry_data.get("timeout", entry.data.get("timeout", 0.3)))

        try:
            result = await hass.async_add_executor_job(
                discover_devices_via_broadcast,
                model_path,
                timeout,
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Broadcast discovery failed for %s: %s", entry.entry_id, err)
            return

        discovered_devices = [
            device
            for section in ("lights", "switches", "sensors", "unknown")
            for device in result.get(section, [])
            if isinstance(device, dict) and isinstance(device.get("did"), str)
        ]
        if not discovered_devices:
            return

        discovered_by_did = {
            device["did"]: device
            for device in discovered_devices
        }

        for client in _iter_runtime_clients(current_entry_data):
            discovered = discovered_by_did.get(getattr(client, "device_id", None))
            if not discovered:
                continue

            new_ip = discovered.get("ip")
            if isinstance(new_ip, str):
                client._ip = new_ip

            # Drop stale sockets so the next poll reconnects cleanly.
            client.disconnect()

        updated_data = deepcopy(dict(entry.data))
        if _refresh_entry_data_from_discovery(updated_data, discovered_by_did):
            hass.config_entries.async_update_entry(entry, data=updated_data)
            await hass.config_entries.async_reload(entry.entry_id)

    remove = async_track_time_interval(
        hass,
        _async_rediscover,
        timedelta(seconds=DEFAULT_BROADCAST_DISCOVERY_INTERVAL),
    )

    entry_data.setdefault("discovery_runtime", {})
    entry_data["discovery_runtime"]["remove_broadcast"] = remove


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CozyLife from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    entry_data: dict[str, object]

    devices_value = entry.data.get("devices")

    if isinstance(devices_value, dict):
        # Legacy configuration where a single entry represented a full scan.
        entry_data = {
            "devices": devices_value,
            "timeout": entry.data.get("timeout", 0.3),
            "scan_settings": {
                "start_ip": entry.data.get("start_ip"),
                "end_ip": entry.data.get("end_ip"),
                "timeout": entry.data.get("timeout", 0.3),
            },
        }
    elif isinstance(devices_value, list):
        normalized_devices: list[dict[str, object]] = []

        for device_entry in devices_value:
            device_info = dict(device_entry.get("device", {}))
            name_value = device_entry.get(CONF_NAME) or device_entry.get("name")
            area_value = device_entry.get(CONF_AREA) or device_entry.get("location")

            normalized_devices.append(
                {
                    "device": device_info,
                    CONF_NAME: name_value,
                    CONF_AREA: prepare_area_value_for_storage(hass, area_value),
                }
            )

        entry_data = {
            "devices": normalized_devices,
            "timeout": entry.data.get("timeout", 0.3),
            "scan_settings": entry.data.get("scan_settings"),
        }
    else:
        device_info = dict(entry.data.get("device", {}))
        timeout = entry.data.get("timeout", 0.3)
        name_value = entry.data.get(CONF_NAME)
        if name_value is None:
            name_value = entry.data.get("name")

        area = entry.data.get(CONF_AREA)
        if area is None:
            area = entry.data.get("location")

        area = prepare_area_value_for_storage(hass, area)

        entry_data = {
            "device": device_info,
            "timeout": timeout,
            CONF_NAME: name_value,
            CONF_AREA: area,
        }

    options = dict(entry.options)

    def _coerce_interval(value: object, default: float) -> float:
        try:
            interval = float(value)
        except (TypeError, ValueError):
            interval = float(default)
        else:
            if interval < 5:
                interval = 5.0
            elif interval > 600:
                interval = 600.0
        return interval

    light_interval = _coerce_interval(
        options.get(CONF_LIGHT_POLL_INTERVAL, DEFAULT_LIGHT_POLL_INTERVAL),
        DEFAULT_LIGHT_POLL_INTERVAL,
    )
    switch_interval = _coerce_interval(
        options.get(CONF_SWITCH_POLL_INTERVAL, DEFAULT_SWITCH_POLL_INTERVAL),
        DEFAULT_SWITCH_POLL_INTERVAL,
    )

    entry_data["poll_intervals"] = {
        "light": light_interval,
        "switch": switch_interval,
        "sensor": switch_interval,
    }

    hass.data[DOMAIN][entry.entry_id] = entry_data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_setup_broadcast_rediscovery(hass, entry, entry_data)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a CozyLife config entry."""

    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    discovery_runtime = entry_data.get("discovery_runtime", {})
    if isinstance(discovery_runtime, dict):
        remove_broadcast = discovery_runtime.get("remove_broadcast")
        if callable(remove_broadcast):
            remove_broadcast()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle migration of config entries."""

    data = dict(entry.data)
    updated = False

    stored_area = normalize_area_value(data.get(CONF_AREA))
    location_value = normalize_area_value(data.get("location"))

    candidate_area = stored_area or location_value
    normalized_area = prepare_area_value_for_storage(hass, candidate_area)

    if normalized_area is not None:
        if data.get(CONF_AREA) != normalized_area:
            data[CONF_AREA] = normalized_area
            updated = True
    elif CONF_AREA in data:
        data.pop(CONF_AREA)
        updated = True

    if updated:
        hass.config_entries.async_update_entry(entry, data=data)

    return True
