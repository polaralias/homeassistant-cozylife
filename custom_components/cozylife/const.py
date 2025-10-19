"""Constants for the CozyLife integration."""

from __future__ import annotations

import voluptuous as vol


DOMAIN = "cozylife"
MANUFACTURER = "CozyLife"

CONF_AREA = "area"
CONF_LIGHT_POLL_INTERVAL = "light_poll_interval"
CONF_SWITCH_POLL_INTERVAL = "switch_poll_interval"

DEFAULT_LIGHT_POLL_INTERVAL = 60
DEFAULT_SWITCH_POLL_INTERVAL = 20

POLL_INTERVAL_VALIDATOR = vol.All(
    vol.Coerce(float),
    vol.Range(min=5, max=600),
)

# http://doc.doit/project-5/doc-8/
SWITCH_TYPE_CODE = '00'
LIGHT_TYPE_CODE = '01'
SUPPORT_DEVICE_CATEGORY = [SWITCH_TYPE_CODE, LIGHT_TYPE_CODE]

# http://doc.doit/project-5/doc-8/
SWITCH = '1'
WORK_MODE = '2'
TEMP = '3'
BRIGHT = '4'
HUE = '5'
SAT = '6'

LIGHT_DPID = [SWITCH, WORK_MODE, TEMP, BRIGHT, HUE, SAT]
SWITCH_DPID = [SWITCH, ]
