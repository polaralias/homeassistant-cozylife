"""Helper utilities for CozyLife integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar


def normalize_area_value(area_value: Any) -> str | None:
    """Return a normalised area identifier or ``None``."""

    if isinstance(area_value, dict):
        area_value = area_value.get("area_id") or area_value.get("id")

    if isinstance(area_value, str):
        area_value = area_value.strip()

    if not area_value:
        return None

    return str(area_value)


def _lookup_area_id(area_registry: ar.AreaRegistry, area_value: str) -> str | None:
    """Resolve the provided value to an existing area identifier."""

    if area := area_registry.async_get_area(area_value):
        return area.id

    if area := area_registry.async_get_area_by_name(area_value):
        return area.id

    return None


def resolve_area_id(hass: HomeAssistant, area_value: Any) -> str | None:
    """Return a Home Assistant area ID for the provided value, if possible."""

    normalized = normalize_area_value(area_value)
    if not normalized:
        return None

    area_registry = ar.async_get(hass)
    return _lookup_area_id(area_registry, normalized)


def prepare_area_value_for_storage(
    hass: HomeAssistant, area_value: Any
) -> str | None:
    """Coerce user-provided area data into a stored representation."""

    normalized = normalize_area_value(area_value)
    if not normalized:
        return None

    area_registry = ar.async_get(hass)
    resolved = _lookup_area_id(area_registry, normalized)
    return resolved or normalized


def flatten_discovery_result(
    discovered: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return a canonical device-entry list from bucketed discovery results."""

    flattened: list[dict[str, Any]] = []

    for section in ("lights", "switches", "sensors", "unknown"):
        rows = discovered.get(section, [])
        if not isinstance(rows, list):
            continue

        for row in rows:
            if not isinstance(row, dict):
                continue
            flattened.append({"device": dict(row)})

    return flattened


def flatten_legacy_devices_payload(
    devices: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return canonical device rows from a legacy bucketed entry payload."""

    section_types = {
        "lights": "light",
        "switches": "switch",
        "sensors": "sensor",
        "unknown": "unknown",
    }
    flattened: list[dict[str, Any]] = []

    for section, device_type in section_types.items():
        rows = devices.get(section, [])
        candidates = rows if isinstance(rows, list) else [rows]

        for row in candidates:
            if not isinstance(row, dict):
                continue

            device_payload = dict(row)
            area_value = device_payload.pop("area", None)
            location_value = device_payload.pop("location", None)
            name_value = device_payload.pop("name", None)
            device_payload.setdefault("type", device_type)

            flattened_row: dict[str, Any] = {"device": device_payload}
            if name_value:
                flattened_row["name"] = name_value
            if area_value is not None:
                flattened_row["area"] = area_value
            elif location_value is not None:
                flattened_row["location"] = location_value

            flattened.append(flattened_row)

    return flattened


def normalize_diy_dpid_mappings(value: Any) -> list[dict[str, Any]]:
    """Return a canonical list of DIY DPID mapping rows."""

    if not isinstance(value, list):
        return []

    normalized: list[dict[str, Any]] = []
    seen: set[int] = set()

    for item in value:
        if not isinstance(item, dict):
            continue

        dpid_value = item.get("dpid")
        name_value = item.get("name")

        try:
            dpid = int(dpid_value)
        except (TypeError, ValueError):
            continue

        if dpid < 1 or dpid in seen:
            continue

        if not isinstance(name_value, str):
            continue

        name = name_value.strip()
        if not name:
            continue

        normalized.append({"dpid": dpid, "name": name})
        seen.add(dpid)

    return normalized


def normalize_diy_control_mappings(value: Any) -> list[dict[str, Any]]:
    """Return canonical DIY control mappings for supported custom controls."""

    if not isinstance(value, list):
        return []

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[int, str, str]] = set()

    for item in value:
        if not isinstance(item, dict):
            continue

        dpid_value = item.get("dpid")
        name_value = item.get("name")
        entity_kind = item.get("entity_kind")
        value_type = item.get("value_type")

        try:
            dpid = int(dpid_value)
        except (TypeError, ValueError):
            continue

        if dpid < 1:
            continue

        if not isinstance(name_value, str) or not isinstance(entity_kind, str) or not isinstance(value_type, str):
            continue

        name = name_value.strip()
        kind = entity_kind.strip().lower()
        value_shape = value_type.strip().lower()

        if not name or kind != "switch" or value_shape != "bool":
            continue

        marker = (dpid, kind, value_shape)
        if marker in seen:
            continue

        normalized.append(
            {
                "dpid": dpid,
                "name": name,
                "entity_kind": kind,
                "value_type": value_shape,
            }
        )
        seen.add(marker)

    return normalized
