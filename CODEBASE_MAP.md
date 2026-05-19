# CozyLife Codebase Map

This document maps the repository as it exists today.

Working assumptions for this map:
- Existing documentation is treated as unverified until supported by code.
- Existing code is treated as intent, not proof of correctness.
- This is an architecture and state map, not a refactor plan.

## Probable End Goal

The repository appears to aim for a polished Home Assistant custom integration that:
- discovers CozyLife devices on the local network without cloud dependency,
- creates Home Assistant config entries through a UI flow,
- controls lights and switches over TCP port `5555`,
- exposes some sensor devices as raw datapoint entities,
- keeps devices usable even when their IP changes by periodically rediscovering them.

The project is not a general CozyLife platform today. It includes a broad static device catalogue in `model.json`, but the active Home Assistant surface is limited to `light`, `switch`, and `sensor`.

## Initial State Summary

- Repository size is small and analyzable in one pass.
- There are no tests in the repo.
- There is no `.github` workflow directory.
- The code is concentrated in `custom_components/cozylife/`.
- README claims some behavior that the repo instructions now reject, especially automated HACS versioning.
- Runtime support is broader than the original docs imply because `sensor.py` is now present and loaded.

## Top-Level Layout

- `README.md`: user-facing setup and historical notes. Contains drift and should not be treated as authoritative.
- `hacs.json`: HACS metadata.
- `custom_components/cozylife/manifest.json`: Home Assistant manifest and version metadata.
- `custom_components/cozylife/__init__.py`: integration entry setup, runtime state normalization, periodic rediscovery.
- `custom_components/cozylife/config_flow.py`: onboarding and options flow. This is the largest control surface.
- `custom_components/cozylife/discovery.py`: TCP range scan and UDP broadcast-assisted discovery.
- `custom_components/cozylife/tcp_client.py`: synchronous protocol client for CozyLife hardware.
- `custom_components/cozylife/light.py`: light entities, effect handling, transition logic, and a light-wrapped switch entity.
- `custom_components/cozylife/switch.py`: switch entities.
- `custom_components/cozylife/sensor.py`: raw datapoint sensor entities using a coordinator.
- `custom_components/cozylife/utils.py`: model catalogue loader and serial number helper.
- `custom_components/cozylife/helpers.py`: area normalization and lookup helpers.
- `custom_components/cozylife/model.json`: static CozyLife product catalogue used to map `pid` to model metadata and datapoints.

## Runtime Architecture

### 1. Home Assistant entry point

`custom_components/cozylife/__init__.py` is the runtime root.

It does three things:
- normalizes stored config-entry data into a runtime shape,
- forwards setup to the `light`, `switch`, and `sensor` platforms,
- runs periodic broadcast rediscovery to repair stale IP addresses.

Key anchors:
- platforms declared at `custom_components/cozylife/__init__.py:30`
- entry normalization at `custom_components/cozylife/__init__.py:191`
- rediscovery loop at `custom_components/cozylife/__init__.py:124`

### 2. Config entry shapes

The code currently supports three entry shapes:

1. Current single-device shape
- `data["device"]`
- `data["timeout"]`
- optional `data["name"]` or `data["name"]` migrated to `CONF_NAME`
- optional area data

2. Current multi-device shape
- `data["devices"]` as a list of `{device, name, area}`
- common timeout and optional scan settings

3. Legacy full-scan shape
- `data["devices"]` as a dict with buckets like `lights`, `switches`, `sensors`
- plus `start_ip`, `end_ip`, `timeout`

The setup path in `__init__.py` explicitly preserves support for all three.

### 3. Runtime state in `hass.data`

Each config entry is normalized into `hass.data[DOMAIN][entry_id]` with a mixed runtime/config shape that may contain:
- `device` or `devices`
- `timeout`
- `scan_settings`
- `poll_intervals`
- `light_runtime`
- `switch_runtime`
- `sensor_runtime`
- `discovery_runtime`

This is the real internal state contract of the integration.

### 4. Discovery model

Discovery is two-stage:
- UDP broadcast finds candidate IPs on port `6095`
- TCP probing on port `5555` validates the device and fetches metadata

Key anchors:
- UDP broadcast at `custom_components/cozylife/discovery.py:133`
- TCP probe wrapper at `custom_components/cozylife/discovery.py:42`
- range scan at `custom_components/cozylife/discovery.py:121`

The config flow uses both broadcast discovery and explicit range scanning before presenting devices for selection.

### 5. Device protocol layer

`tcp_client.py` is a synchronous transport and protocol adapter. It:
- opens a TCP socket to port `5555`,
- sends JSON payloads terminated by `\r\n`,
- supports info, query, and set commands,
- looks up device metadata in `model.json` using the device `pid`.

This file is the real hardware boundary. Everything above it is orchestration.

Key anchors:
- class start at `custom_components/cozylife/tcp_client.py:21`
- device info fetch at `custom_components/cozylife/tcp_client.py:105`
- command packaging at `custom_components/cozylife/tcp_client.py:165`
- state query path at `custom_components/cozylife/tcp_client.py:325`

## App Surfaces

### Config Flow

`config_flow.py` is effectively the product surface.

Observed workflow:
1. User opens integration setup.
2. Flow derives auto-scan ranges from Home Assistant network adapters.
3. User can override with manual start and end IPs.
4. Flow runs broadcast discovery and TCP scans.
5. Already-configured devices are filtered out.
6. User selects one or more devices.
7. User customizes name and area for each selected device.
8. The flow creates single-device entries by re-entering through `async_step_import`.

Key anchors:
- initial user step at `custom_components/cozylife/config_flow.py:137`
- discovery and filtering at `custom_components/cozylife/config_flow.py:307`
- multi-select step at `custom_components/cozylife/config_flow.py:464`
- per-device customization at `custom_components/cozylife/config_flow.py:537`
- import-based entry creation at `custom_components/cozylife/config_flow.py:625`
- options flow start at `custom_components/cozylife/config_flow.py:836`

Important interpretation:
- The intended modern UX is config-flow-first and multi-device-aware.
- The code still carries substantial legacy compatibility logic.

### Lights

`light.py` handles both real lights and a second entity type: a switch represented as a light.

Real light behavior includes:
- on/off,
- brightness,
- color temperature,
- HS color,
- several named effects,
- custom transition logic.

Key anchors:
- platform setup at `custom_components/cozylife/light.py:81`
- switch-as-light entity at `custom_components/cozylife/light.py:296`
- main light entity at `custom_components/cozylife/light.py:403`
- effect setter at `custom_components/cozylife/light.py:478`
- turn-on control path at `custom_components/cozylife/light.py:559`
- turn-off transition path at `custom_components/cozylife/light.py:750`

Important interpretation:
- This file contains the most bespoke device behavior.
- It also contains the most product-specific assumptions.
- It is the main place where “works for my bulbs” logic seems to live.

### Switches

`switch.py` is a simpler on/off entity implementation.

It:
- builds switch entities from the stored device payload,
- polls state on a timer,
- exposes straightforward on/off control through the TCP client.

Key anchors:
- setup at `custom_components/cozylife/switch.py:32`
- entity class at `custom_components/cozylife/switch.py:161`

### Sensors

`sensor.py` is newer-looking than the light/switch modules.

It:
- creates a `DataUpdateCoordinator` per physical sensor device,
- queries raw device state,
- infers some friendly datapoint names from the model name and known DPID values,
- falls back to generic `DPID <n>` entities for anything else.

Key anchors:
- coordinator at `custom_components/cozylife/sensor.py:41`
- sensor-device extraction at `custom_components/cozylife/sensor.py:65`
- datapoint naming heuristics at `custom_components/cozylife/sensor.py:104`
- setup at `custom_components/cozylife/sensor.py:160`
- entity class at `custom_components/cozylife/sensor.py:245`

Important interpretation:
- Sensor support exists, but it is mostly raw datapoint exposure, not polished domain modeling.

## Static Device Catalogue

`model.json` is central.

Observed facts:
- It contains `11` top-level device type groups.
- The sample catalogue includes many categories beyond lights, switches, and sensors.
- The active Home Assistant integration only recognizes CozyLife type codes:
  - `00` switch
  - `01` light
  - `03` sensor

Interpretation:
- The repository contains a much broader upstream device catalogue than the integration currently surfaces.
- `model.json` should be treated as capability hints, not proof that those devices work in Home Assistant here.

## State and Data Flow

### Stored data path

Discovery returns device payloads like:
- `ip`
- `did`
- `pid`
- `dpid`
- `dmn`
- `type`

Those values are persisted into config entries and then copied into runtime `tcp_client` objects during platform setup.

### Polling path

There are two polling styles in the codebase:
- `light.py` and `switch.py` use manual `async_track_time_interval`
- `sensor.py` uses `DataUpdateCoordinator`

This means the codebase has two different synchronization models for device state.

### Rediscovery path

Every config entry sets up periodic broadcast rediscovery.

If a known device ID is rediscovered at a new IP:
- the in-memory client IP is updated,
- the socket is dropped,
- config-entry data is updated,
- the entry is reloaded.

This is the clearest evidence that the intended end state is “local discovery plus resilience to DHCP movement.”

## Things That Look Intentional

- Config flow instead of YAML configuration.
- Multi-device onboarding from one scan session.
- Preservation of legacy entries while evolving the data model.
- Local-only operation over TCP.
- Device metadata lookup through `model.json`.
- Poll interval customization in the options flow.
- Device area support tied to Home Assistant area registry.
- Automatic recovery from device IP changes.

## Things That Look Fragile Or Ambiguous

- `README.md` still describes automated HACS metadata updates, which conflicts with repo instructions.
- `light.py` creates `CozyLifeSwitchAsLight` entities for switch devices, while `switch.py` also creates switch entities for switch devices. That means a switch can plausibly be surfaced in two different HA domains depending on entry shape and setup path.
- `light.py` contains older-style custom transition and effect logic with many hard-coded payload assumptions.
- Sensor entities are mostly raw datapoints, not semantically typed Home Assistant entities.
- The device catalogue is broad, but the supported Home Assistant entity model is narrow.
- The repo has no test harness to verify behavior against Home Assistant or device protocol changes.

## Highest-Value Investigation Containers

These are the follow-up areas that should be expanded next.

### 1. Protocol Truth

Question:
- Which commands, payloads, and response shapes are actually required by current CozyLife hardware?

Files:
- `custom_components/cozylife/tcp_client.py`
- `custom_components/cozylife/discovery.py`
- `custom_components/cozylife/light.py`

Why it matters:
- This is the single source of truth for whether the integration really works.

### 2. Config Entry Contract

Question:
- What entry shapes exist in the wild, and which ones should survive long term?

Files:
- `custom_components/cozylife/__init__.py`
- `custom_components/cozylife/config_flow.py`

Why it matters:
- The integration currently supports old and new shapes simultaneously.

### 3. Entity Surface Design

Question:
- What should each physical device become in Home Assistant: light, switch, sensor, or multiple entities?

Files:
- `custom_components/cozylife/light.py`
- `custom_components/cozylife/switch.py`
- `custom_components/cozylife/sensor.py`

Why it matters:
- Public-facing polish depends on coherent entity modeling.

### 4. Device Coverage

Question:
- Which products in `model.json` are genuinely supported, partially supported, or unsupported?

Files:
- `custom_components/cozylife/model.json`
- `custom_components/cozylife/const.py`
- platform modules

Why it matters:
- The static catalogue currently overstates the apparent scope of the project.

### 5. Operational Quality

Question:
- How does the integration behave under timeout, reconnect, offline devices, and IP churn?

Files:
- `custom_components/cozylife/__init__.py`
- `custom_components/cozylife/discovery.py`
- `custom_components/cozylife/tcp_client.py`

Why it matters:
- This is where “mostly works” turns into reliable software.

### 6. Documentation Truthfulness

Question:
- Which README claims are still true, and which belong to historical context only?

Files:
- `README.md`
- `AGENTS.md`
- manifest and HACS metadata

Why it matters:
- A public job-application repo needs trustworthy docs more than ambitious docs.

## Recommended Next Pass

The next investigation should not start with refactoring. It should produce verified truth in this order:

1. Confirm actual supported device classes and remove ambiguity about switch-as-light behavior.
2. Trace the device protocol with one known working light and one known working switch.
3. Define the target config-entry shape and list legacy shapes that still need migration support.
4. Audit README claims against code and against observed behavior.
5. Add a minimal validation harness so future cleanup is evidence-based.

## Fast Reference

- Runtime root: `custom_components/cozylife/__init__.py`
- Onboarding and options: `custom_components/cozylife/config_flow.py`
- Local discovery: `custom_components/cozylife/discovery.py`
- Hardware protocol: `custom_components/cozylife/tcp_client.py`
- Light behavior: `custom_components/cozylife/light.py`
- Switch behavior: `custom_components/cozylife/switch.py`
- Sensor behavior: `custom_components/cozylife/sensor.py`
- Device catalogue: `custom_components/cozylife/model.json`
