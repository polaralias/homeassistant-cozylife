"""Light platform for CozyLife devices."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
from pathlib import Path
import time
from typing import Any

import voluptuous as vol

from homeassistant.components import light as light_platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EFFECT, CONF_NAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import color as colorutil

from .const import CONF_AREA, DEFAULT_LIGHT_POLL_INTERVAL, DOMAIN, MANUFACTURER
from .helpers import normalize_area_value, resolve_area_id
from .tcp_client import tcp_client

ATTR_BRIGHTNESS = light_platform.ATTR_BRIGHTNESS
ATTR_EFFECT = light_platform.ATTR_EFFECT
ATTR_HS_COLOR = light_platform.ATTR_HS_COLOR
ATTR_TRANSITION = light_platform.ATTR_TRANSITION
ATTR_COLOR_TEMP_KELVIN = getattr(light_platform, "ATTR_COLOR_TEMP_KELVIN", None)
ATTR_COLOR_TEMP = getattr(light_platform, "ATTR_COLOR_TEMP", None)
EFFECT_OFF = getattr(light_platform, "EFFECT_OFF", "off")

COLOR_MODE_BRIGHTNESS = light_platform.COLOR_MODE_BRIGHTNESS
COLOR_MODE_COLOR_TEMP = light_platform.COLOR_MODE_COLOR_TEMP
COLOR_MODE_HS = light_platform.COLOR_MODE_HS
COLOR_MODE_ONOFF = light_platform.COLOR_MODE_ONOFF
COLOR_MODE_WHITE = getattr(light_platform, "COLOR_MODE_WHITE", None)
LightEntity = light_platform.LightEntity

ColorMode = getattr(light_platform, "ColorMode", None)
if ColorMode is not None:
    COLOR_MODE_BRIGHTNESS = ColorMode.BRIGHTNESS
    COLOR_MODE_COLOR_TEMP = ColorMode.COLOR_TEMP
    COLOR_MODE_HS = ColorMode.HS
    COLOR_MODE_ONOFF = ColorMode.ONOFF
    COLOR_MODE_WHITE = getattr(ColorMode, "WHITE", COLOR_MODE_WHITE)

LightEntityFeature = getattr(light_platform, "LightEntityFeature", None)
if LightEntityFeature is None:
    FEATURE_EFFECT = light_platform.SUPPORT_EFFECT
    FEATURE_TRANSITION = light_platform.SUPPORT_TRANSITION
    FEATURE_BRIGHTNESS = light_platform.SUPPORT_BRIGHTNESS
else:
    FEATURE_EFFECT = LightEntityFeature.EFFECT
    FEATURE_TRANSITION = LightEntityFeature.TRANSITION
    FEATURE_BRIGHTNESS = getattr(LightEntityFeature, "BRIGHTNESS", 0)

MIN_INTERVAL = 0.2
SERVICE_SET_EFFECT = "set_effect"
SERVICE_SET_ALL_EFFECT = "set_all_effect"
SCENES = ["manual", "sleep", "warm", "study", "chrismas"]
EFFECTS = [EFFECT_OFF, "sleep", "warm", "study", "chrismas"]
SERVICE_SCHEMA_SET_ALL_EFFECT = {
    vol.Required(CONF_EFFECT): vol.In([mode.lower() for mode in EFFECTS + ["manual"]])
}
SERVICE_SCHEMA_SET_EFFECT = {
    vol.Required(CONF_EFFECT): vol.In([mode.lower() for mode in EFFECTS + ["manual"]])
}

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _LightRuntimeConfig:
    """Normalised config used to instantiate a light entity."""

    client: tcp_client
    name: str
    area_id: str | None


def _build_client(
    device_info: dict[str, Any],
    *,
    timeout: float,
    model_path: Path,
) -> tcp_client:
    client = tcp_client(device_info.get("ip"), timeout=timeout, model_path=model_path)
    client._device_id = device_info.get("did")
    client._pid = device_info.get("pid")
    client._dpid = device_info.get("dpid") or []
    client._device_model_name = device_info.get("dmn")
    return client


def _iter_light_runtime_configs(
    data: dict[str, object],
    *,
    timeout: float,
    model_path: Path,
    hass: HomeAssistant,
) -> list[_LightRuntimeConfig]:
    configs: list[_LightRuntimeConfig] = []

    def append_if_light(
        device_info: dict[str, Any],
        *,
        stored_name: str | None,
        raw_area: str | None,
    ) -> None:
        client = _build_client(device_info, timeout=timeout, model_path=model_path)
        if not client.device_id:
            return
        if device_info.get("type") != "light":
            return

        model_name = (client._device_model_name or "").lower()
        if "switch" in model_name:
            return

        friendly_name = (
            stored_name
            or client._device_model_name
            or client.device_id
            or "CozyLife"
        )
        client.name = friendly_name
        area_id = resolve_area_id(hass, raw_area) or normalize_area_value(raw_area)
        configs.append(_LightRuntimeConfig(client=client, name=friendly_name, area_id=area_id))

    if device := data.get("device"):
        if isinstance(device, dict):
            append_if_light(
                device,
                stored_name=data.get(CONF_NAME) or data.get("name"),
                raw_area=data.get(CONF_AREA) or data.get("location"),
            )
    elif isinstance(data.get("devices"), list):
        for item in data["devices"]:
            device_info = item.get("device", {})
            if not isinstance(device_info, dict) or not device_info:
                continue
            append_if_light(
                device_info,
                stored_name=item.get(CONF_NAME)
                or device_info.get("dmn")
                or device_info.get("did"),
                raw_area=item.get(CONF_AREA) or device_info.get("location"),
            )
    else:
        devices = data.get("devices", {})
        if not isinstance(devices, dict):
            return configs
        for item in devices.get("lights", []):
            if not isinstance(item, dict):
                continue
            append_if_light(
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
    """Set up CozyLife lights from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    timeout = data.get("timeout", entry.data.get("timeout", 0.3))
    model_path = Path(hass.config.path("custom_components", DOMAIN, "model.json"))

    lights = [
        CozyLifeLight(config.client, hass, SCENES, name=config.name, area_id=config.area_id)
        for config in _iter_light_runtime_configs(
            data,
            timeout=timeout,
            model_path=model_path,
            hass=hass,
        )
    ]

    if not lights:
        return

    interval_seconds = data.get("poll_intervals", {}).get(
        "light",
        DEFAULT_LIGHT_POLL_INTERVAL,
    )
    scan_interval = timedelta(seconds=interval_seconds)
    async_add_entities(lights, update_before_add=True)

    async def async_update_lights(now=None) -> None:
        for light in lights:
            await hass.async_add_executor_job(light._refresh_state)
            light.async_write_ha_state()
            await asyncio.sleep(0.1)

    remove_lights = async_track_time_interval(hass, async_update_lights, scan_interval)

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_EFFECT,
        SERVICE_SCHEMA_SET_EFFECT,
        "async_set_effect",
    )

    remove_service = None
    if lights:

        async def async_set_all_effect(call: ServiceCall) -> None:
            for light in lights:
                await light.async_set_effect(call.data.get(ATTR_EFFECT))
                await asyncio.sleep(0.01)

        if hass.services.has_service(DOMAIN, SERVICE_SET_ALL_EFFECT):
            hass.services.async_remove(DOMAIN, SERVICE_SET_ALL_EFFECT)
        hass.services.async_register(DOMAIN, SERVICE_SET_ALL_EFFECT, async_set_all_effect)
        remove_service = lambda: hass.services.async_remove(DOMAIN, SERVICE_SET_ALL_EFFECT)

    data.setdefault("light_runtime", {})
    data["light_runtime"].update(
        {
            "lights": lights,
            "remove_lights": remove_lights,
            "remove_service": remove_service,
        }
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CozyLife light entities for a config entry."""

    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    runtime = data.get("light_runtime", {})
    if remove := runtime.get("remove_lights"):
        remove()
    if remove_service := runtime.get("remove_service"):
        remove_service()
    return True


class CozyLifeLightBase(LightEntity):
    """Common CozyLife entity state and metadata handling."""

    _unrecorded_attributes = frozenset({"brightness", "color_temp_kelvin"})

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
        self._name = name or tcp_client.device_id[-4:]
        self._area_id = area_id or None
        self._attr_name = self._name
        self._attr_available = False
        self._attr_is_on = True
        self._attr_suggested_area = None
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

    def _apply_common_state(self, state: dict[str, Any]) -> None:
        self._state = state
        self._attr_is_on = int(state.get("1", 0)) > 0
        self._attr_available = True

    def _refresh_state(self) -> None:
        state = self._tcp_client.query()
        _LOGGER.info("Refreshed CozyLife light %s state: %s", self._name, state)
        if isinstance(state, dict):
            self._apply_common_state(state)
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
        await self.hass.async_add_executor_job(self._tcp_client.control, {"1": 1})

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()
        await self.hass.async_add_executor_job(self._tcp_client.control, {"1": 0})


class CozyLifeLight(CozyLifeLightBase, RestoreEntity):
    """Home Assistant light backed by CozyLife light datapoints."""

    _unrecorded_attributes = frozenset({"brightness", "color_temp_kelvin"})

    def __init__(
        self,
        tcp_client: tcp_client,
        hass,
        scenes,
        *,
        name: str | None = None,
        area_id: str | None = None,
    ) -> None:
        del scenes
        super().__init__(tcp_client, hass, name=name, area_id=area_id)
        self._scenes = EFFECTS
        self._effect = EFFECT_OFF
        self._transitioning = 0.0
        self._max_brightness = 255
        self._min_brightness = 1
        self._supports_brightness = False
        self._attr_is_on = False
        self._attr_brightness = 0
        self._color_temp_mired = 153
        self._attr_hs_color: tuple[float, float] | None = (0, 0)
        self._min_color_temp_kelvin = 2700
        self._max_color_temp_kelvin = 6500
        self._min_mireds = colorutil.color_temperature_kelvin_to_mired(
            self._max_color_temp_kelvin
        )
        self._max_mireds = colorutil.color_temperature_kelvin_to_mired(
            self._min_color_temp_kelvin
        )
        self._miredsratio = (self._max_mireds - self._min_mireds) / 1000
        self._attr_supported_color_modes: set[str] = {COLOR_MODE_ONOFF}
        self._attr_color_mode = COLOR_MODE_ONOFF

        model_name = (self._tcp_client._device_model_name or "").lower()
        dpids = {int(value) for value in tcp_client.dpid if isinstance(value, int)}
        if "switch" not in model_name:
            supports_color_temp = 3 in dpids
            self._supports_brightness = 4 in dpids
            supports_hs = 5 in dpids or 6 in dpids

            supported_color_modes: set[str] = set()
            if supports_color_temp:
                supported_color_modes.add(COLOR_MODE_COLOR_TEMP)
            elif supports_hs and self._supports_brightness and COLOR_MODE_WHITE is not None:
                supported_color_modes.add(COLOR_MODE_WHITE)
            elif self._supports_brightness:
                supported_color_modes.add(COLOR_MODE_BRIGHTNESS)

            if supports_hs:
                supported_color_modes.add(COLOR_MODE_HS)

            if supported_color_modes:
                self._attr_supported_color_modes = supported_color_modes
                self._attr_color_mode = next(iter(sorted(supported_color_modes)))

        self.SUPPORT_COZYLIGHT = self.get_supported_features()

    async def async_set_effect(self, effect: str) -> None:
        self._effect = self._normalize_effect(effect)
        if self._attr_is_on:
            await self.async_turn_on(effect=self._effect)

    @property
    def effect(self):
        return self._effect

    @property
    def effect_list(self):
        return self._scenes

    def _normalize_effect(self, effect: str | None) -> str:
        if effect in (None, "", "manual", EFFECT_OFF):
            return EFFECT_OFF
        return effect

    def _resolve_active_color_mode(self, state: dict[str, Any]) -> str:
        if (
            state.get("2") == 0
            and "3" in state
            and state["3"] < 60000
            and COLOR_MODE_COLOR_TEMP in self._attr_supported_color_modes
        ):
            return COLOR_MODE_COLOR_TEMP

        if (
            "5" in state
            and "6" in state
            and state["5"] < 60000
            and COLOR_MODE_HS in self._attr_supported_color_modes
        ):
            return COLOR_MODE_HS

        if "4" in state and COLOR_MODE_BRIGHTNESS in self._attr_supported_color_modes:
            return COLOR_MODE_BRIGHTNESS

        if COLOR_MODE_WHITE is not None and COLOR_MODE_WHITE in self._attr_supported_color_modes:
            return COLOR_MODE_WHITE

        if COLOR_MODE_COLOR_TEMP in self._attr_supported_color_modes:
            return COLOR_MODE_COLOR_TEMP

        if COLOR_MODE_HS in self._attr_supported_color_modes:
            return COLOR_MODE_HS

        return COLOR_MODE_ONOFF

    def _apply_common_state(self, state: dict[str, Any]) -> None:
        super()._apply_common_state(state)
        self._attr_color_mode = self._resolve_active_color_mode(state)

        if state.get("2") == 0 and "3" in state and state["3"] < 60000:
            self._color_temp_mired = round(
                self._max_mireds - state["3"] * self._miredsratio
            )

        if "4" in state:
            self._attr_brightness = int(state["4"] / 1000 * 255)

        if "5" in state and "6" in state and state["5"] < 60000:
            rgb = colorutil.color_hs_to_RGB(round(state["5"]), round(state["6"] / 10))
            self._attr_hs_color = colorutil.color_RGB_to_hs(*rgb)

        if self._attr_color_mode == COLOR_MODE_WHITE:
            self._color_temp_mired = None

    def _mired_to_device_color_temp(self, mireds: int) -> int:
        return 1000 - round((mireds - self._min_mireds) / self._miredsratio)

    def _build_effect_payload(self, effect: str, transition: float | None) -> tuple[dict[str, Any], float | None]:
        payload: dict[str, Any] = {"1": 255, "2": 0}
        if effect == "sleep":
            payload["3"] = 0
            payload["4"] = 12
            self._attr_color_mode = COLOR_MODE_COLOR_TEMP
        elif effect == "study":
            payload["3"] = 1000
            payload["4"] = 1000
        elif effect == "warm":
            payload["3"] = 0
            payload["4"] = 1000
        elif effect == "chrismas":
            payload["2"] = 1
            payload["4"] = 1000
            payload["8"] = 500
            payload["7"] = "03000003E8FFFF007803E8FFFF00F003E8FFFF003C03E8FFFF00B403E8FFFF010E03E8FFFF002603E8FFFF"

        return payload, transition

    async def _apply_transition(
        self,
        *,
        final_payload: dict[str, Any],
        original_brightness: int,
        original_color_temp: int,
        original_hs: tuple[float, float] | None,
        transition: float,
    ) -> None:
        self._transitioning = time.time()
        token = self._transitioning

        if self._effect == "chrismas":
            await self.hass.async_add_executor_job(self._tcp_client.control, final_payload)
            self._transitioning = 0
            return

        start_payload = {"1": 255, "2": 0}
        start_brightness = round(original_brightness / 255 * 1000)
        target_brightness = final_payload.get("4", start_brightness)

        if self._attr_color_mode == COLOR_MODE_HS:
            initial_hs = original_hs or (0.0, 0.0)
            start_hue = initial_hs[0]
            start_sat = initial_hs[1] * 10
            target_hue = final_payload.get("5", start_hue)
            target_sat = final_payload.get("6", start_sat)
            steps = max(
                1,
                abs(round((start_brightness - target_brightness) / 4)),
                abs(round((start_hue - target_hue) / 3)),
                abs(round((start_sat - target_sat) / 10)),
            )
        else:
            start_color_temp = self._mired_to_device_color_temp(original_color_temp)
            target_color_temp = final_payload.get("3", start_color_temp)
            steps = max(
                1,
                abs(round((start_brightness - target_brightness) / 4)),
                abs(round((start_color_temp - target_color_temp) / 4)),
            )

        step_seconds = max(MIN_INTERVAL, transition / steps)
        steps = max(1, round(transition / step_seconds))
        step_seconds = transition / steps

        for index in range(1, steps + 1):
            if token != self._transitioning:
                self._transitioning = 0
                return

            payload = dict(start_payload)
            payload["4"] = round(
                start_brightness + (target_brightness - start_brightness) * index / steps
            )

            if self._attr_color_mode == COLOR_MODE_HS:
                payload["5"] = round(
                    start_hue + (target_hue - start_hue) * index / steps
                )
                payload["6"] = round(
                    start_sat + (target_sat - start_sat) * index / steps
                )
            elif "3" in final_payload:
                payload["3"] = round(
                    start_color_temp
                    + (target_color_temp - start_color_temp) * index / steps
                )

            await self.hass.async_add_executor_job(self._tcp_client.control, payload)
            if index < steps:
                await asyncio.sleep(step_seconds)

        self._transitioning = 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = None
        if ATTR_COLOR_TEMP_KELVIN is not None:
            color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
            if color_temp_kelvin is not None:
                color_temp = colorutil.color_temperature_kelvin_to_mired(
                    color_temp_kelvin
                )
        if color_temp is None and ATTR_COLOR_TEMP is not None:
            color_temp = kwargs.get(ATTR_COLOR_TEMP)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        transition = kwargs.get(ATTR_TRANSITION)
        effect = self._normalize_effect(kwargs.get(ATTR_EFFECT))

        original_color_temp = self._color_temp_mired or self._max_mireds
        original_hs = self._attr_hs_color
        original_brightness = self._attr_brightness if self._attr_is_on else 0

        self._attr_is_on = True
        self.async_write_ha_state()

        payload: dict[str, Any] = {"1": 255, "2": 0}
        attribute_updates = 0

        if brightness is not None:
            self._effect = EFFECT_OFF
            self._attr_brightness = brightness
            payload["4"] = round(brightness / 255 * 1000)
            attribute_updates += 1

        if color_temp is not None:
            self._effect = EFFECT_OFF
            self._attr_color_mode = COLOR_MODE_COLOR_TEMP
            self._color_temp_mired = color_temp
            payload["3"] = self._mired_to_device_color_temp(color_temp)
            attribute_updates += 1

        if hs_color is not None:
            self._effect = EFFECT_OFF
            self._attr_color_mode = COLOR_MODE_HS
            self._attr_hs_color = hs_color
            rgb = colorutil.color_hs_to_RGB(*hs_color)
            normalised_hs = colorutil.color_RGB_to_hs(*rgb)
            payload["5"] = round(normalised_hs[0])
            payload["6"] = round(normalised_hs[1] * 10)
            attribute_updates += 1

        if attribute_updates == 0:
            self._effect = effect
            payload, transition = self._build_effect_payload(self._effect, transition)

        self._transitioning = 0
        if transition:
            await self._apply_transition(
                final_payload=payload,
                original_brightness=original_brightness,
                original_color_temp=original_color_temp,
                original_hs=original_hs,
                transition=transition,
            )
        else:
            await self.hass.async_add_executor_job(self._tcp_client.control, payload)

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._transitioning = 0
        self._attr_is_on = False
        self.async_write_ha_state()

        transition = kwargs.get(ATTR_TRANSITION)
        original_brightness = self._attr_brightness
        if transition:
            self._transitioning = time.time()
            token = self._transitioning
            start_brightness = round(original_brightness / 255 * 1000)
            steps = max(1, abs(round(start_brightness / 4)))
            step_seconds = max(MIN_INTERVAL, transition / steps)
            steps = max(1, round(transition / step_seconds))
            step_seconds = transition / steps

            for index in range(0, steps + 1):
                if token != self._transitioning:
                    self._transitioning = 0
                    return
                payload = {
                    "1": 255,
                    "2": 0,
                    "4": round(start_brightness - (start_brightness * index / steps)),
                }
                await self.hass.async_add_executor_job(self._tcp_client.control, payload)
                if index < steps:
                    await asyncio.sleep(step_seconds)

        await super().async_turn_off()
        self._transitioning = 0

    @property
    def hs_color(self) -> tuple[float, float] | None:
        return self._attr_hs_color

    @property
    def brightness(self) -> int | None:
        return self._attr_brightness

    @property
    def color_mode(self) -> str | None:
        return self._attr_color_mode

    @property
    def color_temp_kelvin(self) -> int | None:
        if self._color_temp_mired is None:
            return None
        return colorutil.color_temperature_mired_to_kelvin(self._color_temp_mired)

    @property
    def min_color_temp_kelvin(self) -> int:
        return self._min_color_temp_kelvin

    @property
    def max_color_temp_kelvin(self) -> int:
        return self._max_color_temp_kelvin

    @property
    def assumed_state(self):
        return True

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and "last_effect" in last_state.attributes:
            self._effect = self._normalize_effect(last_state.attributes["last_effect"])

    @property
    def extra_state_attributes(self):
        return {
            "last_effect": self._effect,
            "transitioning": self._transitioning,
        }

    @property
    def supported_features(self) -> int:
        return self.SUPPORT_COZYLIGHT

    def get_supported_features(self) -> int:
        features = FEATURE_EFFECT | FEATURE_TRANSITION
        if self._supports_brightness:
            features |= FEATURE_BRIGHTNESS
        return features
