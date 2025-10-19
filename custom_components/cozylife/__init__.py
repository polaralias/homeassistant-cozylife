"""CozyLife integration setup for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_AREA,
    CONF_LIGHT_POLL_INTERVAL,
    CONF_SWITCH_POLL_INTERVAL,
    DEFAULT_LIGHT_POLL_INTERVAL,
    DEFAULT_SWITCH_POLL_INTERVAL,
    DOMAIN,
)
from .helpers import normalize_area_value, prepare_area_value_for_storage


PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH]


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
    }

    hass.data[DOMAIN][entry.entry_id] = entry_data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a CozyLife config entry."""

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
