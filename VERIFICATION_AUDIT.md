# CozyLife Verification Audit

This document is the second pass after `CODEBASE_MAP.md`.

Scope:
- trace the protocol assumptions that the code currently makes,
- clarify the actual Home Assistant entity surface implied by the code,
- separate code-observed behaviour from behaviour that still requires runtime verification.

This is still analysis only. No refactor is proposed here.

## Confidence Levels

- `Observed`: directly supported by repository code.
- `Inferred`: likely intent based on code structure, but not guaranteed correct.
- `Unverified`: depends on actual Home Assistant runtime behaviour or real CozyLife hardware.

## Protocol Surface

### Observed protocol contract

The synchronous protocol client in `custom_components/cozylife/tcp_client.py` assumes three command types:
- `CMD_INFO = 0`
- `CMD_QUERY = 2`
- `CMD_SET = 3`

Observed payload patterns:
- info request: `{"pv":0,"cmd":0,"sn":"...","msg":{}}`
- query request: `{"pv":0,"cmd":2,"sn":"...","msg":{"attr":[0]}}`
- set request: `{"pv":0,"cmd":3,"sn":"...","msg":{"attr":[...],"data":{...}}}`

Observed response expectations:
- `_device_info()` expects a single JSON message with `msg.did` and `msg.pid`.
- `query()` expects a response whose serialised bytes contain the same `sn` and whose decoded JSON contains `msg.data`.
- `control()` does not wait for a response body or acknowledgement payload.

Code anchors:
- command constants at `custom_components/cozylife/tcp_client.py:14`
- info exchange handling at `custom_components/cozylife/tcp_client.py:120`
- payload builder at `custom_components/cozylife/tcp_client.py:186`
- query receive loop at `custom_components/cozylife/tcp_client.py:227`
- fire-and-forget control path at `custom_components/cozylife/tcp_client.py:317`

### Observed metadata resolution contract

The integration does not learn device capabilities from the device alone.

Observed behaviour:
- the device reports `did` and `pid`,
- the client uses `pid` to search `model.json`,
- the first matching entry provides:
  - `device_type_code`
  - `device_model_name`
  - `dpid`

This means `model.json` is part of the protocol interpretation layer, not just UI metadata.

Code anchors:
- PID lookup at `custom_components/cozylife/tcp_client.py:164`
- discovery result payload at `custom_components/cozylife/discovery.py:72`

## Protocol Assumptions That Are Not Yet Verified

### 1. Control success is inferred from socket state, not from device acknowledgement

Observed:
- `control()` returns `self._connect is not None`.

Interpretation:
- a command is considered successful if the socket still exists after send.
- the code does not verify device acceptance, `res`, or post-command state.

Code anchor:
- `custom_components/cozylife/tcp_client.py:323`

Verification need:
- capture a real command/ack exchange from one known working device and confirm whether missing ack handling is acceptable.

### 2. Responses are assumed to fit in a single `recv(1024)` frame

Observed:
- `_device_info()` reads once with `recv(1024)`.
- `_send_receiver()` reads one socket chunk at a time and immediately attempts `json.loads(res.strip())`.

Interpretation:
- the code assumes message framing aligns with socket reads closely enough for direct JSON decoding.

Code anchors:
- `custom_components/cozylife/tcp_client.py:128`
- `custom_components/cozylife/tcp_client.py:259`

Verification need:
- confirm whether actual devices ever split messages across TCP frames or coalesce multiple JSON messages into one read.

### 3. Query response matching is string-based

Observed:
- `_send_receiver()` ignores messages until `self._sn` appears in `str(res)`.

Interpretation:
- correlation is based on substring matching in the raw received bytes converted to string.
- unsolicited status messages could be skipped or accidentally matched.

Code anchor:
- `custom_components/cozylife/tcp_client.py:266`

Verification need:
- observe traffic on a device that emits spontaneous updates while polling.

### 4. `res` status codes are ignored

Observed:
- the client validates message structure but not the response `res` field.

Interpretation:
- malformed success/failure semantics could be silently treated as valid if `msg.data` exists.

Code anchors:
- `custom_components/cozylife/tcp_client.py:141`
- `custom_components/cozylife/tcp_client.py:274`

Verification need:
- identify failure responses from real hardware and determine whether the protocol uses `res` meaningfully.

## Discovery Contract

### Observed discovery behaviour

The integration uses two discovery routes:
- UDP broadcast on port `6095` to gather candidate IPs,
- TCP probe on port `5555` to validate and classify devices.

Code anchors:
- UDP broadcast at `custom_components/cozylife/discovery.py:133`
- TCP probe at `custom_components/cozylife/discovery.py:42`
- combined broadcast discovery at `custom_components/cozylife/discovery.py:180`

### Inferred discovery intent

The intended operational model is:
- use broadcast when possible,
- fall back to scanning explicit IP ranges,
- later use periodic broadcast rediscovery to repair stale IP addresses.

This intent is consistent across:
- onboarding in `config_flow.py`,
- rediscovery in `__init__.py`.

## Entity Surface Clarification

### Observed platform setup

The integration always forwards config entries to all three platforms:
- `light`
- `switch`
- `sensor`

Code anchor:
- `custom_components/cozylife/__init__.py:30`

### Observed light surface

`light.py` creates two entity classes:
- `CozyLifeLight` for actual lights,
- `CozyLifeSwitchAsLight` for switch devices represented as lights.

Observed switch-as-light creation paths:
- single-device entry path at `custom_components/cozylife/light.py:128`
- multi-device entry path at `custom_components/cozylife/light.py:179`
- legacy path at `custom_components/cozylife/light.py:204`

### Observed switch surface

`switch.py` independently creates `CozyLifeSwitch` entities for switch devices.

Observed creation paths:
- single-device entry path at `custom_components/cozylife/switch.py:46`
- multi-device entry path at `custom_components/cozylife/switch.py:76`
- legacy path at `custom_components/cozylife/switch.py:119`

### Conclusion: switch devices are currently dual-modelled

Observed:
- a switch-class device can produce a `light` domain entity and a `switch` domain entity from the same physical device.

This is not a theoretical edge case. It is directly encoded in both platform setup functions.

Implications:
- Home Assistant may expose two entities for one physical switch.
- service targeting and user expectations become ambiguous.
- any future public-facing documentation must decide whether this is a feature, a compatibility bridge, or an error.

Confidence:
- `Observed`

## Light Behaviour Audit

### Observed control datapoints

The main light control path actively uses these DPID-like payload keys:
- `1`: power
- `2`: work mode / effect mode
- `3`: colour temperature
- `4`: brightness
- `5`: hue
- `6`: saturation
- `7`: effect payload
- `8`: effect speed

Code anchors:
- state interpretation at `custom_components/cozylife/light.py:497`
- control payload build at `custom_components/cozylife/light.py:593`
- canned effect payload at `custom_components/cozylife/light.py:661`

### Observed effect surface

The integration exposes these effect names:
- `manual`
- `sleep`
- `warm`
- `study`
- `chrismas`

Code anchors:
- effect list at `custom_components/cozylife/light.py:73`
- service metadata at `custom_components/cozylife/services.yaml:1`

Notes:
- `chrismas` is spelled that way in both code and service metadata.
- the effect implementation is uneven:
  - `chrismas` uses a hard-coded raw payload,
  - the other effects write simple brightness and colour-temperature values.

### Observed light capability inference

The light entity decides supported colour modes from the stored `dpid` list:
- `3` implies colour temperature mode
- `4` implies brightness
- `5` or `6` implies HS colour

Code anchor:
- `custom_components/cozylife/light.py:456`

Interpretation:
- capability modelling is catalogue-driven, not probed dynamically from live device state.

## Sensor Surface Audit

### Observed sensor modelling

The sensor implementation is intentionally generic.

Observed behaviour:
- one coordinator per physical sensor device,
- one HA entity per discovered or catalogued DPID,
- inferred friendly names only for a small subset of device-name patterns,
- otherwise a raw `DPID <n>` entity name is used.

Code anchors:
- coordinator at `custom_components/cozylife/sensor.py:41`
- description inference at `custom_components/cozylife/sensor.py:104`
- generic fallback at `custom_components/cozylife/sensor.py:138`

Interpretation:
- sensor support exists, but the current public surface is a diagnostic/raw-data surface rather than a strongly modelled Home Assistant integration.

## Documentation Drift Confirmed

Observed README claims that are now questionable or incorrect:
- it claims automated HACS metadata updates as a feature,
- it describes “Async I/O everywhere,”
- it emphasises lights and switches while the runtime now also loads sensors.

Code and repo evidence:
- no `.github` workflow directory exists,
- `tcp_client.py` is synchronous socket code,
- `sensor.py` is part of `PLATFORMS`.

Code/document anchors:
- README line for HACS automation section: `README.md:47`
- sensor platform registration: `custom_components/cozylife/__init__.py:30`
- synchronous socket client: `custom_components/cozylife/tcp_client.py:21`

## What Can Be Trusted Today

High confidence from code:
- the integration is designed around local network control, not cloud control,
- config flow is the intended onboarding path,
- discovery combines range scanning and broadcast discovery,
- `model.json` is operationally important,
- switch devices are currently modelled in more than one HA domain,
- protocol correctness is only partially enforced by the client.

Low confidence until runtime verification:
- whether all supported light operations map correctly to current CozyLife firmware,
- whether effect payloads are correct beyond the author’s original hardware,
- whether sensor DPID naming is accurate,
- whether the TCP parser is robust under real network conditions,
- whether dual-modelled switches behave acceptably in Home Assistant UI and automation flows.

## Suggested Next Verification Session

The next session should use real runtime evidence, not more static reading.

Order:
1. Test one known switch and one known light in Home Assistant.
2. Confirm whether a switch appears once or twice as entities.
3. Capture one `info`, one `query`, and one `set` exchange from live hardware.
4. Validate whether command success can be trusted without response parsing.
5. Compare live device state to `model.json` capability assumptions.

Expected output of that session:
- a truth table of device type -> HA entities,
- a minimal protocol transcript,
- a list of README claims that can be retained versus removed.
