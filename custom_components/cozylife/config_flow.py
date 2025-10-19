"""Config flow for the CozyLife integration."""

from __future__ import annotations

import ipaddress
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import network, selector

from .const import (
    CONF_AREA,
    CONF_LIGHT_POLL_INTERVAL,
    CONF_SWITCH_POLL_INTERVAL,
    DEFAULT_LIGHT_POLL_INTERVAL,
    DEFAULT_SWITCH_POLL_INTERVAL,
    DOMAIN,
    LIGHT_TYPE_CODE,
    POLL_INTERVAL_VALIDATOR,
    SWITCH_TYPE_CODE,
)
from .helpers import (
    prepare_area_value_for_storage,
    resolve_area_id,
)
from .discovery import discover_devices
from .tcp_client import tcp_client

DEFAULT_START_IP = "192.168.0.0"
DEFAULT_END_IP = "192.168.0.255"

_LOGGER = logging.getLogger(__name__)


def _coerce_ip(value: str) -> str:
    """Validate and normalise an IPv4 address string."""

    try:
        return str(ipaddress.ip_address(value))
    except ValueError as err:
        raise vol.Invalid("invalid_ip") from err


TIMEOUT_VALIDATOR = vol.All(vol.Coerce(float), vol.Range(min=0.05, max=10.0))

class CozyLifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the CozyLife config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_devices: list[dict[str, Any]] = []
        self._available_devices: list[dict[str, Any]] = []
        self._scan_settings: dict[str, Any] = {}
        self._auto_scan_ranges: list[tuple[str, str]] = []
        self._selected_devices: list[dict[str, Any]] = []
        self._customise_index: int = 0
        self._customise_results: list[dict[str, Any]] = []

    def _build_ip_selector(self) -> selector.TextSelector:
        """Return a text selector configured for IP input."""

        return selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        )

    def _build_timeout_selector(self) -> selector.NumberSelector:
        """Return a number selector for timeouts."""

        return selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.05,
                max=10.0,
                step=0.05,
                mode=selector.NumberSelectorMode.BOX,
            )
        )

    async def _async_get_auto_scan_ranges(self) -> list[tuple[str, str]]:
        """Return the automatically detected scan ranges for the host network."""

        if self._auto_scan_ranges:
            return self._auto_scan_ranges

        ranges: list[tuple[str, str]] = []

        try:
            adapters = await network.async_get_adapters(self.hass)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Unable to determine network adapters: %s", err)
            adapters = []

        seen: set[tuple[str, str]] = set()

        for adapter in adapters:
            if not adapter.get("enabled", True):
                continue

            for ipv4_data in adapter.get("ipv4", []):
                if ipv4_data.get("scope") not in (None, "global"):
                    continue

                address = ipv4_data.get("address")
                netmask = ipv4_data.get("netmask")

                if not address or not netmask:
                    continue

                try:
                    interface = ipaddress.IPv4Interface(f"{address}/{netmask}")
                except ValueError:
                    continue

                network_details = interface.network

                start = str(network_details.network_address)
                end = str(network_details.broadcast_address)

                if (start, end) in seen:
                    continue

                seen.add((start, end))
                ranges.append((start, end))

        self._auto_scan_ranges = ranges
        return self._auto_scan_ranges

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step initiated by the user."""

        errors: dict[str, str] = {}

        if user_input is None:
            self._discovered_devices = []
            self._available_devices = []
            self._scan_settings = {}

        detected_auto_ranges = await self._async_get_auto_scan_ranges()
        effective_auto_ranges = (
            detected_auto_ranges
            if detected_auto_ranges
            else [(DEFAULT_START_IP, DEFAULT_END_IP)]
        )

        suggested_start = (
            user_input.get("start_ip")
            if user_input and "start_ip" in user_input
            else effective_auto_ranges[0][0]
        )
        suggested_end = (
            user_input.get("end_ip")
            if user_input and "end_ip" in user_input
            else effective_auto_ranges[0][1]
        )
        suggested_timeout = (
            user_input.get("timeout")
            if user_input and "timeout" in user_input
            else 0.3
        )

        use_custom_range = bool(user_input and user_input.get("use_custom_range"))
        if (
            not use_custom_range
            and user_input is not None
            and (user_input.get("start_ip") or user_input.get("end_ip"))
        ):
            # Treat manual IP input as opting into custom mode even if the
            # toggle was not explicitly enabled.
            use_custom_range = True

        show_manual_fields = use_custom_range

        if user_input is not None:
            try:
                timeout = TIMEOUT_VALIDATOR(user_input.get("timeout", 0.3))
            except vol.Invalid:
                errors["timeout"] = "invalid_timeout"
                timeout = 0.3
            else:
                suggested_timeout = timeout

            ranges_to_scan: list[tuple[str, str]] = []

            if use_custom_range:
                start_ip = user_input.get("start_ip", "")
                end_ip = user_input.get("end_ip", "")

                if not start_ip or not end_ip:
                    errors["base"] = "manual_range_required"
                else:
                    try:
                        start_ip = _coerce_ip(start_ip)
                    except vol.Invalid:
                        errors["start_ip"] = "invalid_ip"

                    try:
                        end_ip = _coerce_ip(end_ip)
                    except vol.Invalid:
                        errors["end_ip"] = "invalid_ip"

                    if not errors and int(ipaddress.ip_address(start_ip)) > int(
                        ipaddress.ip_address(end_ip)
                    ):
                        errors["end_ip"] = "range_order"

                    if not errors:
                        ranges_to_scan = [(start_ip, end_ip)]
            else:
                ranges_to_scan = effective_auto_ranges

            if not errors and ranges_to_scan:
                self._scan_settings = {
                    "mode": "custom" if use_custom_range else "auto",
                    "ranges": ranges_to_scan,
                    "timeout": timeout,
                }

                return await self.async_step_select_many()

        description_default_start = (
            suggested_start if suggested_start else effective_auto_ranges[0][0]
        )
        description_default_end = (
            suggested_end if suggested_end else effective_auto_ranges[0][1]
        )

        placeholders = {
            "auto": ", ".join(
                f"{start} – {end}" for start, end in detected_auto_ranges
            )
            if detected_auto_ranges
            else f"{DEFAULT_START_IP} – {DEFAULT_END_IP}",
            "protocol": "a TCP probe on port 5555",
            "default_range": f"{description_default_start} – {description_default_end}",
        }

        schema = self._build_user_schema(
            show_manual_fields,
            suggested_start,
            suggested_end,
            suggested_timeout,
            use_custom_range,
        )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                schema,
                user_input or {},
            ),
            errors=errors,
            description_placeholders=placeholders,
        )

    def _build_user_schema(
        self,
        show_manual_fields: bool,
        suggested_start: str,
        suggested_end: str,
        suggested_timeout: float,
        use_custom_range: bool,
    ) -> vol.Schema:
        """Construct the dynamic schema for the user step."""

        schema_fields: dict[Any, Any] = {
            vol.Required("use_custom_range", default=use_custom_range): selector.BooleanSelector(),
        }

        if show_manual_fields:
            schema_fields.update(
                {
                    vol.Required("start_ip", default=suggested_start): self._build_ip_selector(),
                    vol.Required("end_ip", default=suggested_end): self._build_ip_selector(),
                }
            )

        schema_fields[vol.Required("timeout", default=suggested_timeout)] = (
            self._build_timeout_selector()
        )

        return vol.Schema(schema_fields)

    async def _async_get_ranges_to_scan(self) -> list[tuple[str, str]]:
        """Return the IP ranges to scan based on stored settings."""

        ranges = self._scan_settings.get("ranges")
        if ranges:
            return ranges

        auto_ranges = await self._async_get_auto_scan_ranges()
        if auto_ranges:
            return auto_ranges

        return [(DEFAULT_START_IP, DEFAULT_END_IP)]

    async def _async_discover_and_filter(self) -> list[dict[str, Any]]:
        """Discover devices and filter out those already configured."""

        ranges = await self._async_get_ranges_to_scan()
        timeout = float(self._scan_settings.get("timeout", 0.3))
        discovered: list[dict[str, Any]] = []
        model_path = Path(
            self.hass.config.path("custom_components", DOMAIN, "model.json")
        )
        seen_devices: set[str] = set()

        for start_ip, end_ip in ranges:
            try:
                result = await self.hass.async_add_executor_job(
                    discover_devices, start_ip, end_ip, model_path, timeout
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Discovery failed for %s–%s", start_ip, end_ip
                )
                result = {"lights": [], "switches": [], "unknown": []}

            if not isinstance(result, Mapping):
                continue

            for section in ("lights", "switches", "unknown"):
                rows = result.get(section) or []
                if not isinstance(rows, list):
                    continue

                filtered_rows = [
                    dict(row)
                    for row in rows
                    if isinstance(row, Mapping)
                ]

                for raw_device in filtered_rows:
                    did = raw_device.get("did")
                    ip_address = raw_device.get("ip")

                    if not did or not ip_address:
                        continue

                    if did in seen_devices:
                        continue

                    device = dict(raw_device)
                    seen_devices.add(did)

                    if not device.get("type"):
                        if section == "lights":
                            device["type"] = "light"
                        elif section == "switches":
                            device["type"] = "switch"
                        else:
                            device["type"] = "unknown"

                    discovered.append(device)

        self._discovered_devices = sorted(
            discovered,
            key=lambda item: (
                item.get("dmn") or "",
                item.get("ip") or "",
            ),
        )

        current_entries = list(self._async_current_entries())

        existing_ids: set[str] = {
            entry.unique_id
            for entry in current_entries
            if entry.unique_id
        }

        for entry in current_entries:
            device_info = entry.data.get("device")
            if isinstance(device_info, Mapping):
                candidate_id = device_info.get("did")
                if isinstance(candidate_id, str):
                    existing_ids.add(candidate_id)

            devices_value = entry.data.get("devices")
            if isinstance(devices_value, list):
                for device_entry in devices_value:
                    if not isinstance(device_entry, Mapping):
                        continue

                    payload = device_entry.get("device")
                    if isinstance(payload, Mapping):
                        candidate_id = payload.get("did")
                    else:
                        candidate_id = device_entry.get("did")

                    if isinstance(candidate_id, str):
                        existing_ids.add(candidate_id)
            elif isinstance(devices_value, Mapping):
                for device_entry in devices_value.values():
                    if isinstance(device_entry, list):
                        candidates = device_entry
                    else:
                        candidates = [device_entry]

                    for item in candidates:
                        if not isinstance(item, Mapping):
                            continue

                        candidate_id = item.get("did")
                        if isinstance(candidate_id, str):
                            existing_ids.add(candidate_id)

        available: list[dict[str, Any]] = []
        for device in self._discovered_devices:
            did = device.get("did")
            if not did or did in existing_ids:
                continue
            available.append(device)

        self._available_devices = available

        return self._available_devices

    @callback
    def _async_current_entries(self) -> list[config_entries.ConfigEntry]:
        """Return currently configured entries for the integration."""

        return self.hass.config_entries.async_entries(DOMAIN)

    async def async_step_select_many(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Allow the user to select multiple devices to import."""

        errors: dict[str, str] = {}

        if user_input is None or not self._available_devices:
            await self._async_discover_and_filter()
            self._selected_devices = []
            self._customise_index = 0
            self._customise_results = []

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        if not self._available_devices:
            return self.async_abort(reason="all_devices_configured")

        options: list[dict[str, str]] = []

        for item in self._available_devices:
            did = item.get("did")
            if not did:
                continue
            model = item.get("dmn") or did
            ip_address = item.get("ip") or "unknown IP"
            label = f"{model} ({ip_address})"
            options.append({"value": did, "label": label})

        schema = vol.Schema(
            {
                vol.Required("targets"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        if user_input is not None:
            targets = user_input.get("targets") or []
            available_by_id = {
                device.get("did"): device
                for device in self._available_devices
                if device.get("did")
            }

            self._selected_devices = [
                available_by_id[key]
                for key in targets
                if key in available_by_id
            ]
            self._customise_index = 0
            self._customise_results = []

            if not self._selected_devices:
                errors["base"] = "select_at_least_one"

            if not errors:
                return await self.async_step_customise()

        return self.async_show_form(
            step_id="select_many",
            data_schema=self.add_suggested_values_to_schema(
                schema,
                user_input or {},
            ),
            errors=errors,
        )

    async def async_step_customise(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Collect name and area information for each selected device."""

        if not self._selected_devices:
            return await self.async_step_select_many()

        if self._customise_index >= len(self._selected_devices):
            return self.async_abort(reason="created_multiple_entries")

        device = self._selected_devices[self._customise_index]
        name_suggest = device.get("dmn") or device.get("did") or "CozyLife"
        device_id = device.get("did") or "unknown ID"
        ip_label = device.get("ip") or "unknown IP"

        schema = vol.Schema(
            {
                vol.Optional(
                    "name", default=name_suggest
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT
                    )
                ),
                vol.Optional("area"): selector.AreaSelector(),
            }
        )

        placeholders = {
            "device": f"{name_suggest} • {device_id} • {ip_label}",
        }

        if user_input is None:
            return self.async_show_form(
                step_id="customise",
                data_schema=schema,
                description_placeholders=placeholders,
            )

        raw_name = user_input.get("name")
        name_value = raw_name.strip() if isinstance(raw_name, str) else None
        if not name_value:
            name_value = None

        area_value = prepare_area_value_for_storage(
            self.hass, user_input.get("area")
        )

        self._customise_results.append(
            {
                "device": device,
                "name": name_value,
                "area": area_value,
            }
        )
        self._customise_index += 1

        if self._customise_index < len(self._selected_devices):
            return await self.async_step_customise()

        timeout = float(self._scan_settings.get("timeout", 0.3))

        for row in self._customise_results:
            selected_device = row["device"]
            payload = {
                "device": {
                    "ip": selected_device.get("ip"),
                    "did": selected_device.get("did"),
                    "pid": selected_device.get("pid"),
                    "dpid": selected_device.get("dpid"),
                    "dmn": selected_device.get("dmn"),
                    "type": selected_device.get("type"),
                },
                "timeout": timeout,
                CONF_NAME: row.get("name"),
                CONF_AREA: row.get("area"),
            }
            self.hass.async_create_task(
                self.hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": config_entries.SOURCE_IMPORT},
                    data=payload,
                )
            )

        return self.async_abort(reason="created_multiple_entries")

    async def async_step_import(self, import_data: Mapping[str, Any]) -> FlowResult:
        """Handle the import step for a single CozyLife device."""

        device = dict(import_data.get("device", {}))
        try:
            timeout = float(import_data.get("timeout", 0.3))
        except (TypeError, ValueError):
            timeout = 0.3

        raw_name = import_data.get(CONF_NAME)
        name = raw_name.strip() if isinstance(raw_name, str) else None
        if not name:
            name = None

        area = prepare_area_value_for_storage(self.hass, import_data.get(CONF_AREA))

        model_path = Path(
            self.hass.config.path("custom_components", DOMAIN, "model.json")
        )

        did = device.get("did")

        if not did:
            ip_address = device.get("ip")

            if not ip_address:
                return self.async_abort(reason="no_devices_found")

            def _probe_device() -> dict[str, Any] | None:
                client = tcp_client(
                    ip_address,
                    timeout=timeout,
                    model_path=model_path,
                )

                try:
                    client._initSocket()
                    client._device_info()

                    device_id = getattr(client, "_device_id", None)
                    if not device_id:
                        return None

                    type_code = getattr(client, "_device_type_code", None)
                    if type_code == LIGHT_TYPE_CODE:
                        device_type = "light"
                    elif type_code == SWITCH_TYPE_CODE:
                        device_type = "switch"
                    else:
                        device_type = "unknown"

                    dpid_value = getattr(client, "_dpid", None)
                    if isinstance(dpid_value, list):
                        dpid_value = list(dpid_value)

                    return {
                        "ip": ip_address or getattr(client, "_ip", None),
                        "did": device_id,
                        "pid": getattr(client, "_pid", None),
                        "dpid": dpid_value,
                        "dmn": getattr(client, "_device_model_name", None),
                        "type": device_type,
                    }
                finally:
                    client.disconnect()

            try:
                refreshed = await self.hass.async_add_executor_job(_probe_device)
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Import probe failed for CozyLife device at %s", ip_address)
                return self.async_abort(reason="cannot_connect")

            if refreshed:
                device.update(
                    {key: value for key, value in refreshed.items() if value is not None}
                )
                did = device.get("did")

            if not did:
                return self.async_abort(reason="no_devices_found")

        await self.async_set_unique_id(did)
        self._abort_if_unique_id_configured(
            updates={
                "device": device,
                "timeout": timeout,
                CONF_NAME: name,
                CONF_AREA: area,
            }
        )

        device.setdefault("type", "unknown")

        title = name or device.get("dmn") or did or "CozyLife"

        return self.async_create_entry(
            title=title,
            data={
                "device": device,
                "timeout": timeout,
                CONF_NAME: name,
                CONF_AREA: area,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow handler."""

        return CozyLifeOptionsFlow(config_entry)


class CozyLifeOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the CozyLife integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry
        self._multi_devices: list[dict[str, Any]] = []
        self._multi_results: list[dict[str, Any]] = []
        self._multi_index: int = 0
        self._multi_timeout: float = 0.3
        self._multi_initialized = False
        try:
            self._light_poll_interval = float(
                POLL_INTERVAL_VALIDATOR(
                    config_entry.options.get(
                        CONF_LIGHT_POLL_INTERVAL, DEFAULT_LIGHT_POLL_INTERVAL
                    )
                )
            )
        except vol.Invalid:
            self._light_poll_interval = float(DEFAULT_LIGHT_POLL_INTERVAL)

        try:
            self._switch_poll_interval = float(
                POLL_INTERVAL_VALIDATOR(
                    config_entry.options.get(
                        CONF_SWITCH_POLL_INTERVAL, DEFAULT_SWITCH_POLL_INTERVAL
                    )
                )
            )
        except vol.Invalid:
            self._switch_poll_interval = float(DEFAULT_SWITCH_POLL_INTERVAL)
        self._multi_light_poll_interval: float = self._light_poll_interval
        self._multi_switch_poll_interval: float = self._switch_poll_interval

    def _build_ip_selector(self) -> selector.TextSelector:
        """Return a text selector configured for IP input."""

        return selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        )

    def _build_timeout_selector(self) -> selector.NumberSelector:
        """Return a number selector for timeouts."""

        return selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.05,
                max=10.0,
                step=0.05,
                mode=selector.NumberSelectorMode.BOX,
            )
        )

    def _build_poll_interval_selector(self) -> selector.NumberSelector:
        """Return a number selector for polling intervals."""

        return selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=5,
                max=600,
                step=1,
                mode=selector.NumberSelectorMode.BOX,
            )
        )

    def _update_runtime_poll_intervals(
        self, light_interval: float, switch_interval: float
    ) -> None:
        """Update cached poll intervals and cancel existing timers."""

        domain_data = self.hass.data.get(DOMAIN, {})
        entry_data = domain_data.get(self.config_entry.entry_id)

        if not isinstance(entry_data, dict):
            return

        poll_intervals = entry_data.setdefault("poll_intervals", {})
        poll_intervals["light"] = float(light_interval)
        poll_intervals["switch"] = float(switch_interval)

        light_runtime = entry_data.get("light_runtime")
        if isinstance(light_runtime, dict):
            remove_lights = light_runtime.pop("remove_lights", None)
            if callable(remove_lights):
                remove_lights()

            remove_switches = light_runtime.pop("remove_switches", None)
            if callable(remove_switches):
                remove_switches()

        switch_runtime = entry_data.get("switch_runtime")
        if isinstance(switch_runtime, dict):
            remove_update = switch_runtime.pop("remove_update", None)
            if callable(remove_update):
                remove_update()

    async def async_step_init(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options for the integration."""

        errors: dict[str, str] = {}

        data = self.config_entry.data

        if isinstance(data.get("devices"), list):
            return await self._async_step_multi(user_input)

        if "device" not in data:
            return await self._async_step_legacy(user_input)

        device = data.get("device", {})

        if user_input is not None:
            ip_value = user_input.get("ip", "")
            timeout_value = user_input.get("timeout")
            name_value = (user_input.get(CONF_NAME) or "").strip()
            area_value = prepare_area_value_for_storage(
                self.hass, user_input.get(CONF_AREA)
            )
            light_poll_input = user_input.get(
                CONF_LIGHT_POLL_INTERVAL, self._light_poll_interval
            )
            switch_poll_input = user_input.get(
                CONF_SWITCH_POLL_INTERVAL, self._switch_poll_interval
            )

            try:
                ip_value = _coerce_ip(ip_value)
            except vol.Invalid:
                errors["ip"] = "invalid_ip"

            try:
                timeout_value = float(timeout_value)
            except (TypeError, ValueError):
                errors["timeout"] = "invalid_timeout"
            else:
                if not 0.05 <= timeout_value <= 10.0:
                    errors["timeout"] = "invalid_timeout"

            try:
                light_poll_value = POLL_INTERVAL_VALIDATOR(light_poll_input)
            except vol.Invalid:
                errors[CONF_LIGHT_POLL_INTERVAL] = "invalid_poll_interval"
                light_poll_value = None
            else:
                light_poll_value = float(light_poll_value)

            try:
                switch_poll_value = POLL_INTERVAL_VALIDATOR(switch_poll_input)
            except vol.Invalid:
                errors[CONF_SWITCH_POLL_INTERVAL] = "invalid_poll_interval"
                switch_poll_value = None
            else:
                switch_poll_value = float(switch_poll_value)

            if not errors:
                updated_device = {**device, "ip": ip_value}
                updated_data = {
                    **data,
                    "device": updated_device,
                    "timeout": timeout_value,
                    CONF_NAME: name_value or None,
                    CONF_AREA: area_value or None,
                }

                if "location" in updated_data:
                    updated_data.pop("location", None)
                if "name" in updated_data and CONF_NAME in updated_data:
                    updated_data.pop("name", None)

                options_data = {
                    **self.config_entry.options,
                    CONF_LIGHT_POLL_INTERVAL: float(light_poll_value),
                    CONF_SWITCH_POLL_INTERVAL: float(switch_poll_value),
                }

                self._update_runtime_poll_intervals(
                    float(light_poll_value), float(switch_poll_value)
                )

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=updated_data
                )
                await self.hass.config_entries.async_reload(
                    self.config_entry.entry_id
                )
                return self.async_create_entry(title="", data=options_data)

        suggested_name = (
            data.get(CONF_NAME)
            or data.get("name")
            or device.get("dmn")
            or device.get("did")
        )
        raw_area = data.get(CONF_AREA) or data.get("location") or None
        suggested_area = resolve_area_id(self.hass, raw_area)
        suggested_ip = device.get("ip", "")
        suggested_timeout = data.get("timeout", 0.3)

        area_field: Any
        if suggested_area is None:
            area_field = vol.Optional(CONF_AREA)
        else:
            area_field = vol.Optional(CONF_AREA, default=suggested_area)

        options_schema = vol.Schema(
            {
                vol.Required("ip", default=suggested_ip): self._build_ip_selector(),
                vol.Required("timeout", default=suggested_timeout): self._build_timeout_selector(),
                vol.Required(
                    CONF_LIGHT_POLL_INTERVAL, default=self._light_poll_interval
                ): self._build_poll_interval_selector(),
                vol.Required(
                    CONF_SWITCH_POLL_INTERVAL, default=self._switch_poll_interval
                ): self._build_poll_interval_selector(),
                vol.Optional(CONF_NAME, default=suggested_name or ""): selector.TextSelector(),
                area_field: selector.AreaSelector(),
            }
        )

        sanitized_input: dict[str, Any]
        if user_input is None:
            sanitized_input = {}
        else:
            sanitized_input = dict(user_input)
            if sanitized_input.get(CONF_NAME) is None:
                sanitized_input.pop(CONF_NAME, None)
            if not sanitized_input.get(CONF_AREA):
                sanitized_input.pop(CONF_AREA, None)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                options_schema, sanitized_input
            ),
            errors=errors,
        )

    async def _async_step_multi(
        self, user_input: Mapping[str, Any] | None
    ) -> FlowResult:
        """Handle options updates for multi-device entries."""

        errors: dict[str, str] = {}

        if not self._multi_initialized:
            data = self.config_entry.data
            self._multi_devices = [dict(device) for device in data.get("devices", [])]
            self._multi_results = []
            self._multi_index = 0
            self._multi_timeout = data.get("timeout", 0.3)
            self._multi_light_poll_interval = self._light_poll_interval
            self._multi_switch_poll_interval = self._switch_poll_interval
            self._multi_initialized = True

        if not self._multi_devices:
            return self.async_abort(reason="no_devices_found")

        if self._multi_index < len(self._multi_devices):
            device_entry = self._multi_devices[self._multi_index]
            device_info = dict(device_entry.get("device", {}))
            current_ip = device_info.get("ip", "")
            suggested_name = (
                device_entry.get(CONF_NAME)
                or device_info.get("dmn")
                or device_info.get("did")
                or ""
            )
            raw_area = device_entry.get(CONF_AREA) or device_info.get("location")
            suggested_area = resolve_area_id(self.hass, raw_area)

            if user_input is not None:
                ip_value = user_input.get("ip", current_ip)
                name_value = (user_input.get(CONF_NAME) or "").strip()
                area_input = prepare_area_value_for_storage(
                    self.hass, user_input.get(CONF_AREA)
                )

                try:
                    ip_value = _coerce_ip(ip_value)
                except vol.Invalid:
                    errors["ip"] = "invalid_ip"

                if not errors:
                    updated_device = {**device_info, "ip": ip_value}
                    result_entry: dict[str, Any] = {"device": updated_device}
                    if name_value:
                        result_entry[CONF_NAME] = name_value
                    if area_input:
                        result_entry[CONF_AREA] = area_input
                    self._multi_results.append(result_entry)
                    self._multi_index += 1
                    return await self._async_step_multi(None)

            schema_fields: dict[Any, Any] = {
                vol.Required("ip", default=current_ip): self._build_ip_selector(),
                vol.Optional(CONF_NAME, default=suggested_name): selector.TextSelector(),
            }

            if suggested_area is None:
                area_field = vol.Optional(CONF_AREA)
            else:
                area_field = vol.Optional(CONF_AREA, default=suggested_area)

            schema_fields[area_field] = selector.AreaSelector()
            schema = vol.Schema(schema_fields)

            sanitized_input: dict[str, Any]
            if user_input is None:
                sanitized_input = {}
            else:
                sanitized_input = dict(user_input)
                if sanitized_input.get(CONF_NAME) is None:
                    sanitized_input.pop(CONF_NAME, None)
                if not sanitized_input.get(CONF_AREA):
                    sanitized_input.pop(CONF_AREA, None)

            device_label = (
                device_info.get("dmn")
                or device_info.get("did")
                or device_info.get("ip")
                or "device"
            )
            progress = f"{self._multi_index + 1} / {len(self._multi_devices)}"

            return self.async_show_form(
                step_id="init",
                data_schema=self.add_suggested_values_to_schema(
                    schema, sanitized_input
                ),
                errors=errors,
                description_placeholders={
                    "progress": progress,
                    "current_device": device_label,
                },
            )

        if user_input is not None:
            try:
                timeout_value = float(user_input.get("timeout"))
            except (TypeError, ValueError):
                errors["timeout"] = "invalid_timeout"
            else:
                if not 0.05 <= timeout_value <= 10.0:
                    errors["timeout"] = "invalid_timeout"

            try:
                light_poll_value = POLL_INTERVAL_VALIDATOR(
                    user_input.get(
                        CONF_LIGHT_POLL_INTERVAL, self._multi_light_poll_interval
                    )
                )
            except vol.Invalid:
                errors[CONF_LIGHT_POLL_INTERVAL] = "invalid_poll_interval"
                light_poll_value = None

            try:
                switch_poll_value = POLL_INTERVAL_VALIDATOR(
                    user_input.get(
                        CONF_SWITCH_POLL_INTERVAL, self._multi_switch_poll_interval
                    )
                )
            except vol.Invalid:
                errors[CONF_SWITCH_POLL_INTERVAL] = "invalid_poll_interval"
                switch_poll_value = None

            if not errors:
                updated_devices: list[dict[str, Any]] = []

                for result in self._multi_results:
                    device_payload = dict(result.get("device", {}))
                    entry_payload: dict[str, Any] = {"device": device_payload}
                    if result.get(CONF_NAME):
                        entry_payload[CONF_NAME] = result[CONF_NAME]
                    if result.get(CONF_AREA):
                        entry_payload[CONF_AREA] = result[CONF_AREA]
                    updated_devices.append(entry_payload)

                new_data = {
                    **self.config_entry.data,
                    "devices": updated_devices,
                    "timeout": timeout_value,
                }

                options_data = {
                    **self.config_entry.options,
                    CONF_LIGHT_POLL_INTERVAL: float(light_poll_value),
                    CONF_SWITCH_POLL_INTERVAL: float(switch_poll_value),
                }

                self._update_runtime_poll_intervals(
                    float(light_poll_value), float(switch_poll_value)
                )

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                await self.hass.config_entries.async_reload(
                    self.config_entry.entry_id
                )
                return self.async_create_entry(title="", data=options_data)

        timeout_selector = self._build_timeout_selector()
        poll_selector = self._build_poll_interval_selector()
        schema = vol.Schema(
            {
                vol.Required("timeout", default=self._multi_timeout): timeout_selector,
                vol.Required(
                    CONF_LIGHT_POLL_INTERVAL, default=self._multi_light_poll_interval
                ): poll_selector,
                vol.Required(
                    CONF_SWITCH_POLL_INTERVAL,
                    default=self._multi_switch_poll_interval,
                ): poll_selector,
            }
        )

        sanitized_input = {} if user_input is None else dict(user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, sanitized_input),
            errors=errors,
        )

    async def _async_step_legacy(
        self, user_input: Mapping[str, Any] | None
    ) -> FlowResult:
        """Handle options for legacy search-based entries."""

        errors: dict[str, str] = {}
        model_path = Path(
            self.hass.config.path("custom_components", DOMAIN, "model.json")
        )
        timeout_selector = self._build_timeout_selector()
        ip_selector = self._build_ip_selector()
        poll_selector = self._build_poll_interval_selector()

        if user_input is not None:
            start_ip = user_input.get("start_ip", "")
            end_ip = user_input.get("end_ip", "")

            try:
                start_ip = _coerce_ip(start_ip)
            except vol.Invalid:
                errors["start_ip"] = "invalid_ip"

            try:
                end_ip = _coerce_ip(end_ip)
            except vol.Invalid:
                errors["end_ip"] = "invalid_ip"

            if not errors and int(ipaddress.ip_address(start_ip)) > int(
                ipaddress.ip_address(end_ip)
            ):
                errors["end_ip"] = "range_order"

            timeout_value = user_input.get("timeout")
            if timeout_value is None:
                timeout_value = self.config_entry.data.get("timeout", 0.3)

            if not errors:
                timeout = float(timeout_value)

                try:
                    light_poll_value = POLL_INTERVAL_VALIDATOR(
                        user_input.get(
                            CONF_LIGHT_POLL_INTERVAL, self._light_poll_interval
                        )
                    )
                except vol.Invalid:
                    errors[CONF_LIGHT_POLL_INTERVAL] = "invalid_poll_interval"
                    light_poll_value = None

                try:
                    switch_poll_value = POLL_INTERVAL_VALIDATOR(
                        user_input.get(
                            CONF_SWITCH_POLL_INTERVAL, self._switch_poll_interval
                        )
                    )
                except vol.Invalid:
                    errors[CONF_SWITCH_POLL_INTERVAL] = "invalid_poll_interval"
                    switch_poll_value = None

            if not errors:
                devices = await self.hass.async_add_executor_job(
                    discover_devices, start_ip, end_ip, model_path, timeout
                )

                if not any(devices.values()):
                    errors["base"] = "no_devices_found"
                else:
                    data = {
                        "start_ip": start_ip,
                        "end_ip": end_ip,
                        "timeout": timeout,
                        "devices": devices,
                    }
                    options_data = {
                        **self.config_entry.options,
                        CONF_LIGHT_POLL_INTERVAL: float(light_poll_value),
                        CONF_SWITCH_POLL_INTERVAL: float(switch_poll_value),
                    }

                    self._update_runtime_poll_intervals(
                        float(light_poll_value), float(switch_poll_value)
                    )

                    self.hass.config_entries.async_update_entry(
                        self.config_entry, data=data
                    )
                    await self.hass.config_entries.async_reload(
                        self.config_entry.entry_id
                    )
                    return self.async_create_entry(title="", data=options_data)

        current = self.config_entry.data
        suggested = {
            "start_ip": current.get("start_ip"),
            "end_ip": current.get("end_ip"),
            "timeout": current.get("timeout", 0.3),
        }

        legacy_schema = vol.Schema(
            {
                vol.Required("start_ip", default=suggested["start_ip"]): ip_selector,
                vol.Required("end_ip", default=suggested["end_ip"]): ip_selector,
                vol.Required("timeout", default=suggested["timeout"]): timeout_selector,
                vol.Required(
                    CONF_LIGHT_POLL_INTERVAL, default=self._light_poll_interval
                ): poll_selector,
                vol.Required(
                    CONF_SWITCH_POLL_INTERVAL, default=self._switch_poll_interval
                ): poll_selector,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=legacy_schema,
            errors=errors,
        )
