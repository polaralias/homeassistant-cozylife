"""Light platform for CozyLife devices."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_FLASH,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ATTR_TRANSITION,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    FLASH_LONG,
    FLASH_SHORT,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EFFECT, CONF_NAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import color as colorutil

from .const import (
    CONF_AREA,
    DEFAULT_LIGHT_POLL_INTERVAL,
    DEFAULT_SWITCH_POLL_INTERVAL,
    DOMAIN,
    MANUFACTURER,
)
from .helpers import normalize_area_value, resolve_area_id
from .tcp_client import tcp_client


MIN_INTERVAL = 0.2

CIRCADIAN_BRIGHTNESS = True
try:
    import custom_components.circadian_lighting as cir

    DATA_CIRCADIAN_LIGHTING = cir.DOMAIN  # 'circadian_lighting'
except Exception:  # noqa: BLE001
    CIRCADIAN_BRIGHTNESS = False

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_EFFECT = "set_effect"
SERVICE_SET_ALL_EFFECT = "set_all_effect"
SCENES = ["manual", "natural", "sleep", "warm", "study", "chrismas"]
SERVICE_SCHEMA_SET_ALL_EFFECT = {
    vol.Required(CONF_EFFECT): vol.In([mode.lower() for mode in SCENES])
}
SERVICE_SCHEMA_SET_EFFECT = {
    vol.Required(CONF_EFFECT): vol.In([mode.lower() for mode in SCENES])
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CozyLife lights from a config entry."""

    data = hass.data[DOMAIN][entry.entry_id]
    lights: list[CozyLifeLight] = []
    switches: list[CozyLifeSwitchAsLight] = []

    timeout = data.get("timeout", entry.data.get("timeout", 0.3))
    model_path = Path(hass.config.path("custom_components", DOMAIN, "model.json"))

    if device := data.get("device"):
        client = tcp_client(
            device.get("ip"), timeout=timeout, model_path=model_path
        )
        client._device_id = device.get("did")
        client._pid = device.get("pid")
        client._dpid = device.get("dpid")
        client._device_model_name = device.get("dmn")
        fallback_name = client._device_model_name or (
            client.device_id[-4:] if client.device_id else "CozyLife"
        )
        friendly_name = (
            data.get(CONF_NAME)
            or data.get("name")
            or fallback_name
        )
        raw_area = data.get(CONF_AREA) or data.get("location")
        area_id = resolve_area_id(hass, raw_area) or normalize_area_value(raw_area)
        client.name = friendly_name

        if device.get("type") == "light" and (
            not client._device_model_name
            or "switch" not in client._device_model_name.lower()
        ):
            lights.append(
                CozyLifeLight(
                    client,
                    hass,
                    SCENES,
                    name=friendly_name,
                    area_id=area_id,
                )
            )
        elif device.get("type") == "switch" or (
            client._device_model_name and "switch" in client._device_model_name.lower()
        ):
            switches.append(
                CozyLifeSwitchAsLight(
                    client,
                    hass,
                    name=friendly_name,
                    area_id=area_id,
                )
            )
    elif isinstance(data.get("devices"), list):
        for item in data["devices"]:
            device_info = item.get("device", {})
            if not device_info:
                continue

            client = tcp_client(
                device_info.get("ip"), timeout=timeout, model_path=model_path
            )
            client._device_id = device_info.get("did")
            client._pid = device_info.get("pid")
            client._dpid = device_info.get("dpid")
            client._device_model_name = device_info.get("dmn")

            fallback_name = client._device_model_name or (
                client.device_id[-4:] if client.device_id else "CozyLife"
            )
            friendly_name = (
                item.get(CONF_NAME)
                or device_info.get("dmn")
                or device_info.get("did")
                or fallback_name
            )
            raw_area = item.get(CONF_AREA) or device_info.get("location")
            area_id = resolve_area_id(hass, raw_area) or normalize_area_value(raw_area)
            client.name = friendly_name

            if device_info.get("type") == "light" and (
                not client._device_model_name
                or "switch" not in client._device_model_name.lower()
            ):
                lights.append(
                    CozyLifeLight(
                        client,
                        hass,
                        SCENES,
                        name=friendly_name,
                        area_id=area_id,
                    )
                )
            elif device_info.get("type") == "switch" or (
                client._device_model_name
                and "switch" in client._device_model_name.lower()
            ):
                switches.append(
                    CozyLifeSwitchAsLight(
                        client,
                        hass,
                        name=friendly_name,
                        area_id=area_id,
                    )
                )
    else:
        devices = data.get("devices", {})
        for item in devices.get("lights", []):
            client = tcp_client(
                item.get("ip"), timeout=timeout, model_path=model_path
            )
            client._device_id = item.get("did")
            client._pid = item.get("pid")
            client._dpid = item.get("dpid")
            client._device_model_name = item.get("dmn")
            if "switch" not in client._device_model_name.lower():
                lights.append(CozyLifeLight(client, hass, SCENES))
            else:
                switches.append(CozyLifeSwitchAsLight(client, hass))

    if not lights and not switches:
        return

    poll_intervals = data.get("poll_intervals", {})
    light_interval_seconds = poll_intervals.get(
        "light", DEFAULT_LIGHT_POLL_INTERVAL
    )
    switch_interval_seconds = poll_intervals.get(
        "switch", DEFAULT_SWITCH_POLL_INTERVAL
    )

    light_scan_interval = timedelta(seconds=light_interval_seconds)
    switch_scan_interval = timedelta(seconds=switch_interval_seconds)

    async_add_entities(lights + switches, update_before_add=True)

    async def async_update_lights(now=None):
        for light in lights:
            if light._attr_is_on and light._effect == "natural":
                await light.async_turn_on(effect="natural")
                await hass.async_add_executor_job(light._refresh_state)
            else:
                await hass.async_add_executor_job(light._refresh_state)
            light.async_write_ha_state()
            await asyncio.sleep(0.1)

    async def async_update_switches(now=None):
        for light in switches:
            await hass.async_add_executor_job(light._refresh_state)
            light.async_write_ha_state()
            await asyncio.sleep(0.1)

    remove_light_update = async_track_time_interval(
        hass, async_update_lights, light_scan_interval
    )
    remove_switch_update = async_track_time_interval(
        hass, async_update_switches, switch_scan_interval
    )

    data.setdefault("light_runtime", {})
    data["light_runtime"].update(
        {
            "lights": lights,
            "switches": switches,
            "remove_lights": remove_light_update,
            "remove_switches": remove_switch_update,
        }
    )

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_EFFECT, SERVICE_SCHEMA_SET_EFFECT, "async_set_effect"
    )

    if lights:
        async def async_set_all_effect(call: ServiceCall) -> None:
            for light in lights:
                await light.async_set_effect(call.data.get(ATTR_EFFECT))
                await asyncio.sleep(0.01)

        if hass.services.has_service(DOMAIN, SERVICE_SET_ALL_EFFECT):
            hass.services.async_remove(DOMAIN, SERVICE_SET_ALL_EFFECT)

        hass.services.async_register(
            DOMAIN, SERVICE_SET_ALL_EFFECT, async_set_all_effect
        )
        data["light_runtime"]["remove_service"] = lambda: hass.services.async_remove(
            DOMAIN, SERVICE_SET_ALL_EFFECT
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CozyLife light entities for a config entry."""

    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    runtime = data.get("light_runtime", {})

    if remove := runtime.get("remove_lights"):
        remove()
    if remove := runtime.get("remove_switches"):
        remove()
    if remove_service := runtime.get("remove_service"):
        remove_service()

    return True


# ---------------------------------------------------------------------------
# Helper: Mired <-> Kelvin
# ---------------------------------------------------------------------------
def _mired_to_kelvin(mired: int) -> int:
    return int(1_000_000 / mired)

def _kelvin_to_mired(kelvin: int) -> int:
    return int(1_000_000 / kelvin)


class CozyLifeSwitchAsLight(LightEntity):

    _tcp_client = None
    _attr_is_on = True
    _unrecorded_attributes = frozenset({"brightness", "color_temp_kelvin"})

    def __init__(
        self,
        tcp_client: tcp_client,
        hass,
        *,
        name: str | None = None,
        area_id: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        _LOGGER.info('__init__')
        self.hass = hass
        self._tcp_client = tcp_client
        self._unique_id = tcp_client.device_id
        self._name = name or tcp_client.device_id[-4:]
        self._area_id = area_id or None
        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, tcp_client.device_id)},
            manufacturer=MANUFACTURER,
            model=tcp_client._device_model_name,
            name=self._name,
        )
        self._device_info["name"] = self._name
        if self._area_id:
            self._device_info["suggested_area"] = self._area_id
        self._attr_name = self._name
        self._attr_suggested_area = None
        self._attr_available = False

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
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

    async def async_update(self):
        await self.hass.async_add_executor_job(self._refresh_state)

    def _refresh_state(self):
        self._state = self._tcp_client.query()
        _LOGGER.info(f'_name={self._name},_state={self._state}')
        if self._state:
            self._attr_is_on = 0 < int(self._state.get('1', 0))
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
        """Return if the device is available."""
        return bool(self._attr_available)

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True
        self.async_write_ha_state()
        _LOGGER.info(f'turn_on:{kwargs}')
        await self.hass.async_add_executor_job(self._tcp_client.control, {'1': 1})
        return None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._attr_is_on = False
        self.async_write_ha_state()
        _LOGGER.info('turn_off')
        await self.hass.async_add_executor_job(self._tcp_client.control, {'1': 0})
        return None


class CozyLifeLight(CozyLifeSwitchAsLight, RestoreEntity):
    _attr_brightness: int | None = None
    _attr_color_mode: str | None = None
    # Store color temp internally in Kelvin
    _attr_color_temp_kelvin: int | None = None
    _attr_hs_color = None
    _unrecorded_attributes = frozenset({"brightness", "color_temp_kelvin"})

    _tcp_client = None

    _attr_supported_color_modes = frozenset({ColorMode.ONOFF})
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(
        self,
        tcp_client: tcp_client,
        hass,
        scenes,
        *,
        name: str | None = None,
        area_id: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        _LOGGER.info('__init__')
        super().__init__(tcp_client, hass, name=name, area_id=area_id)
        self.hass = hass
        self._tcp_client = tcp_client
        self._unique_id = tcp_client.device_id
        self._scenes = scenes
        self._effect = 'manual'

        self._cl = None
        self._max_brightness = 255
        self._min_brightness = 1
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.BRIGHTNESS

        _LOGGER.info(f'before:{self._unique_id}._attr_color_mode={self._attr_color_mode}._attr_supported_color_modes='
                     f'{self._attr_supported_color_modes}.dpid={tcp_client.dpid}')

        if not name:
            self._name = tcp_client.device_id[-4:]
            self._device_info["name"] = self._name

        # Color temp range in Kelvin (2700 K warm – 6500 K cool)
        self._min_kelvin = 2700
        self._max_kelvin = 6500
        self._min_mireds = colorutil.color_temperature_kelvin_to_mired(self._max_kelvin)
        self._max_mireds = colorutil.color_temperature_kelvin_to_mired(self._min_kelvin)
        self._miredsratio = (self._max_mireds - self._min_mireds) / 1000

        # Default color temp: 4000 K (neutral white)
        self._attr_color_temp_kelvin = 4000
        self._attr_hs_color = (0, 0)
        self._transitioning = 0
        self._attr_is_on = False
        self._attr_brightness = 0

        model_name = (self._tcp_client._device_model_name or "").lower()
        if "switch" not in model_name:
            if 3 in tcp_client.dpid:
                self._attr_color_mode = ColorMode.COLOR_TEMP
                self._attr_supported_color_modes.add(ColorMode.COLOR_TEMP)

            if 4 in tcp_client.dpid:
                self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

            if 5 in tcp_client.dpid or 6 in tcp_client.dpid:
                self._attr_color_mode = ColorMode.HS
                self._attr_supported_color_modes.add(ColorMode.HS)

        # HA-Regel: ONOFF und BRIGHTNESS dürfen nicht zusammen mit
        # "echten" Farbmodi (COLOR_TEMP, HS, RGB, …) stehen.
        real_modes = {ColorMode.COLOR_TEMP, ColorMode.HS, ColorMode.RGB}
        if self._attr_supported_color_modes & real_modes:
            self._attr_supported_color_modes.discard(ColorMode.ONOFF)
            self._attr_supported_color_modes.discard(ColorMode.BRIGHTNESS)

        # Falls nach dem Bereinigen gar nichts übrig ist → Fallback
        if not self._attr_supported_color_modes:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF

        _LOGGER.info(f'after:{self._unique_id}._attr_color_mode={self._attr_color_mode}._attr_supported_color_modes='
                     f'{self._attr_supported_color_modes}.dpid={tcp_client.dpid}')

        self.SUPPORT_COZYLIGHT = self.get_supported_features()

    async def async_set_effect(self, effect: str):
        """Set the effect regardless it is On or Off."""
        _LOGGER.info(f'onoff:{self._attr_is_on} effect:{effect}')
        self._effect = effect
        if self._attr_is_on:
            await self.async_turn_on(effect=effect)

    @property
    def effect(self):
        """Return the current effect."""
        return self._effect

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return self._scenes

    def _refresh_state(self):
        """Query device & set attr."""
        self._state = self._tcp_client.query()
        _LOGGER.info(f'_name={self._name},_state={self._state}')
        if self._state:
            self._attr_is_on = 0 < int(self._state.get('1', 0))
            self._attr_available = True

            if '2' in self._state:
                if self._state['2'] == 0:
                    if '3' in self._state:
                        color_temp_raw = self._state['3']
                        if color_temp_raw < 60000:
                            self._attr_color_mode = ColorMode.COLOR_TEMP
                            # Convert device value (0-1000) → Mired → Kelvin
                            mired = round(
                                self._max_mireds - color_temp_raw * self._miredsratio
                            )
                            self._attr_color_temp_kelvin = _mired_to_kelvin(mired)

                    if '4' in self._state:
                        self._attr_brightness = int(self._state['4'] / 1000 * 255)

                    if '5' in self._state:
                        color = self._state['5']
                        if color < 60000:
                            self._attr_color_mode = ColorMode.HS
                            r, g, b = colorutil.color_hs_to_RGB(
                                round(self._state['5']), round(self._state['6'] / 10))
                            hs_color = colorutil.color_RGB_to_hs(r, g, b)
                            self._attr_hs_color = hs_color
        else:
            self._attr_available = False

    def calc_color_temp(self):
        """Return color temp in Mired from circadian lighting."""
        if self._cl is None:
            self._cl = self.hass.data.get(DATA_CIRCADIAN_LIGHTING)
            if self._cl is None:
                return None
        colortemp_in_kelvin = self._cl._colortemp
        return colorutil.color_temperature_kelvin_to_mired(colortemp_in_kelvin)

    def calc_brightness(self):
        if self._cl is None:
            self._cl = self.hass.data.get(DATA_CIRCADIAN_LIGHTING)
            if self._cl is None:
                return None
        if self._cl._percent > 0:
            return self._max_brightness
        else:
            return round(
                ((self._max_brightness - self._min_brightness) * ((100 + self._cl._percent) / 100))
                + self._min_brightness
            )

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the CT color value in Kelvin."""
        return self._attr_color_temp_kelvin

    @property
    def min_color_temp_kelvin(self) -> int:
        return self._min_kelvin

    @property
    def max_color_temp_kelvin(self) -> int:
        return self._max_kelvin

    # Keep legacy mired properties for any code that still reads them
    @property
    def color_temp(self) -> int | None:
        """Return color temp in mireds (legacy)."""
        if self._attr_color_temp_kelvin:
            return _kelvin_to_mired(self._attr_color_temp_kelvin)
        return None

    @property
    def min_mireds(self):
        return self._min_mireds

    @property
    def max_mireds(self):
        return self._max_mireds

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""

        brightness = kwargs.get(ATTR_BRIGHTNESS)
        # HA now sends ATTR_COLOR_TEMP_KELVIN; keep mired fallback just in case
        color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        transition = kwargs.get(ATTR_TRANSITION)
        effect = kwargs.get(ATTR_EFFECT)

        # Convert Kelvin → Mired for internal calculations
        colortemp = _kelvin_to_mired(color_temp_kelvin) if color_temp_kelvin else None

        originalcolortemp_mired = self.color_temp  # mired
        originalhs = self._attr_hs_color
        originalbrightness = self._attr_brightness if self._attr_is_on else 0

        _LOGGER.info(
            f'turn_on.kwargs={kwargs},color_temp_kelvin={color_temp_kelvin},hs_color={hs_color},'
            f'originalbrightness={originalbrightness},self._attr_is_on={self._attr_is_on}'
        )
        self._attr_is_on = True
        self.async_write_ha_state()
        payload = {'1': 255, '2': 0}
        count = 0

        if brightness is not None:
            self._effect = 'manual'
            payload['4'] = round(brightness / 255 * 1000)
            self._attr_brightness = brightness
            count += 1

        if colortemp is not None:
            self._effect = 'manual'
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_color_temp_kelvin = color_temp_kelvin
            payload['3'] = 1000 - round(
                (colortemp - self._min_mireds) / self._miredsratio
            )
            count += 1

        if hs_color is not None:
            self._effect = 'manual'
            self._attr_color_mode = ColorMode.HS
            self._attr_hs_color = hs_color
            r, g, b = colorutil.color_hs_to_RGB(*hs_color)
            hs_color = colorutil.color_RGB_to_hs(r, g, b)
            payload['5'] = round(hs_color[0])
            payload['6'] = round(hs_color[1] * 10)
            count += 1

        if count == 0:
            if effect is not None:
                self._effect = effect
            if self._effect == 'natural':
                if CIRCADIAN_BRIGHTNESS:
                    brightness = self.calc_brightness()
                    payload['4'] = round(brightness / 255 * 1000)
                    self._attr_brightness = brightness
                    self._attr_color_mode = ColorMode.COLOR_TEMP
                    colortemp = self.calc_color_temp()  # mired
                    payload['3'] = 1000 - round(
                        (colortemp - self._min_mireds) / self._miredsratio
                    )
                    self._attr_color_temp_kelvin = _mired_to_kelvin(int(colortemp))
                    _LOGGER.info(f'color={colortemp},payload3={payload["3"]}')
                    if self._transitioning != 0:
                        return None
                    if transition is None:
                        transition = 5
            elif self._effect == 'sleep':
                payload['4'] = 12
                payload['3'] = 0
                self._attr_color_mode = ColorMode.COLOR_TEMP
            elif self._effect == 'study':
                payload['4'] = 1000
                payload['3'] = 1000
            elif self._effect == 'warm':
                payload['4'] = 1000
                payload['3'] = 0
            elif self._effect == 'chrismas':
                payload['2'] = 1
                payload['4'] = 1000
                payload['8'] = 500
                payload['7'] = '03000003E8FFFF007803E8FFFF00F003E8FFFF003C03E8FFFF00B403E8FFFF010E03E8FFFF002603E8FFFF'

        self._transitioning = 0

        if transition:
            self._transitioning = time.time()
            now = self._transitioning
            if self._effect == 'chrismas':
                await self.hass.async_add_executor_job(self._tcp_client.control, payload)
                self._transitioning = 0
                return None
            if brightness:
                payloadtemp = {'1': 255, '2': 0}
                p4i = round(originalbrightness / 255 * 1000)
                p4f = payload['4']
                p4steps = abs(round((p4i - p4f) / 4))
                _LOGGER.info(f'p4i={p4i},p4f={p4f},p4steps={p4steps}')
            else:
                p4steps = 0
            if self._attr_color_mode == ColorMode.COLOR_TEMP:
                p3i = 1000 - round(
                    (originalcolortemp_mired - self._min_mireds) / self._miredsratio
                )
                p3steps = 0
                if '3' in payload:
                    p3f = payload['3']
                    p3steps = abs(round((p3i - p3f) / 4))
                _LOGGER.info(f'p3i={p3i},p3f={p3f},p3steps={p3steps}')
                steps = p3steps if p3steps > p4steps else p4steps
                if steps <= 0:
                    self._transitioning = 0
                    return None
                stepseconds = transition / steps
                if stepseconds < MIN_INTERVAL:
                    stepseconds = MIN_INTERVAL
                    steps = round(transition / stepseconds)
                    stepseconds = transition / steps
                _LOGGER.info(f'steps={steps},transition={transition},stepseconds={stepseconds}')
                for s in range(1, steps + 1):
                    payloadtemp['4'] = round(p4i + (p4f - p4i) * s / steps)
                    if p3steps != 0:
                        payloadtemp['3'] = round(p3i + (p3f - p3i) * s / steps)
                    if now == self._transitioning:
                        await self.hass.async_add_executor_job(
                            self._tcp_client.control, payloadtemp
                        )
                        _LOGGER.info(f'payloadtemp={payloadtemp},stepseconds={stepseconds}')
                        if s < steps:
                            await asyncio.sleep(stepseconds)
                    else:
                        self._transitioning = 0
                        return None

            elif self._attr_color_mode == ColorMode.HS:
                p5i = originalhs[0]
                p6i = originalhs[1] * 10
                p5steps = 0
                p6steps = 0
                if '5' in payload:
                    p5f = payload['5']
                    p6f = payload['6']
                    p5steps = abs(round((p5i - p5f) / 3))
                    p6steps = abs(round((p6i - p6f) / 10))
                steps = max([p4steps, p5steps, p6steps])
                if steps <= 0:
                    self._transitioning = 0
                    return None
                stepseconds = transition / steps
                if stepseconds < 4:
                    steps = round(transition / stepseconds)
                    stepseconds = transition / steps
                _LOGGER.info(f'steps={steps}')
                for s in range(steps):
                    payloadtemp['4'] = round(p4i + (p4f - p4i) * s / steps)
                    if p5steps != 0:
                        payloadtemp['5'] = round(p5i + (p5f - p5i) * s / steps)
                        payloadtemp['6'] = round(p6i + (p6f - p6i) * s / steps)
                    if now == self._transitioning:
                        await self.hass.async_add_executor_job(
                            self._tcp_client.control, payloadtemp
                        )
                        await asyncio.sleep(stepseconds)
                    else:
                        self._transitioning = 0
                        return None
        else:
            await self.hass.async_add_executor_job(self._tcp_client.control, payload)

        self._transitioning = 0
        return None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._transitioning = 0
        self._attr_is_on = False
        self.async_write_ha_state()
        transition = kwargs.get(ATTR_TRANSITION)
        originalbrightness = self._attr_brightness
        if self._effect == 'natural' and transition is None:
            transition = 5
        if transition:
            self._transitioning = time.time()
            now = self._transitioning
            payloadtemp = {'1': 255, '2': 0}
            p4i = round(originalbrightness / 255 * 1000)
            p4f = 0
            steps = abs(round((p4i - p4f) / 4))
            stepseconds = transition / steps
            if stepseconds < MIN_INTERVAL:
                stepseconds = MIN_INTERVAL
                steps = round(transition / stepseconds)
                stepseconds = transition / steps
            for s in range(1 + steps + 1):
                payloadtemp['4'] = round(p4i + (p4f - p4i) * s / steps)
                if now == self._transitioning:
                    await self.hass.async_add_executor_job(
                        self._tcp_client.control, payloadtemp
                    )
                    if s < steps:
                        await asyncio.sleep(stepseconds)
                    else:
                        await super().async_turn_off()
                else:
                    return None
        else:
            await super().async_turn_off()
        self._transitioning = 0
        return None

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hue and saturation color value [float, float]."""
        return self._attr_hs_color

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._attr_brightness

    @property
    def color_mode(self) -> str | None:
        """Return the color mode of the light."""
        return self._attr_color_mode

    @property
    def assumed_state(self):
        return True

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        if 'last_effect' in last_state.attributes:
            self._effect = last_state.attributes['last_effect']

    @property
    def extra_state_attributes(self):
        attributes = {}
        attributes['last_effect'] = self._effect
        attributes['transitioning'] = self._transitioning
        return attributes

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self.SUPPORT_COZYLIGHT

    def get_supported_features(self) -> int:
        """Flag supported features."""
        features = LightEntityFeature.EFFECT | LightEntityFeature.TRANSITION
        if ColorMode.BRIGHTNESS in self._attr_supported_color_modes:
            features = features | LightEntityFeature.FLASH
        return features
