# Architecture

This document describes the current architecture of the CozyLife Home Assistant integration and the desired direction for that architecture.

## Purpose

The repository exists to provide a reliable Home Assistant integration for CozyLife devices using local network communication rather than cloud APIs.

## Desired End State

The target architecture is:
- local-first,
- config-flow-first,
- explicit about supported device classes,
- resilient to DHCP and reconnect issues,
- clear about which behaviors are verified on real hardware,
- documented in terms of outcomes rather than implementation folklore.

## Current Runtime Shape

The integration is organized around a thin Home Assistant orchestration layer and a synchronous device protocol layer.

Main modules:
- `custom_components/cozylife/__init__.py`: config-entry setup, runtime normalization, platform forwarding, periodic rediscovery.
- `custom_components/cozylife/config_flow.py`: onboarding flow, options flow, legacy compatibility for older entry shapes.
- `custom_components/cozylife/discovery.py`: broadcast-assisted discovery and direct IP probing.
- `custom_components/cozylife/tcp_client.py`: CozyLife TCP protocol client on port `5555`.
- `custom_components/cozylife/light.py`: light entity logic and effect handling.
- `custom_components/cozylife/switch.py`: switch entity logic.
- `custom_components/cozylife/sensor.py`: raw sensor datapoint exposure through coordinators.
- `custom_components/cozylife/model.json`: local catalog snapshot used to resolve `pid` to capabilities and labels.

## Runtime Data Model

Each config entry is normalized into `hass.data[DOMAIN][entry_id]`.

Observed runtime fields may include:
- `device`
- `devices`
- `timeout`
- `scan_settings`
- `poll_intervals`
- `light_runtime`
- `switch_runtime`
- `sensor_runtime`
- `discovery_runtime`

This mixed runtime/config shape is part of the current architecture and should be treated as a compatibility surface.

## Supported Entry Shapes

The code currently supports three config-entry shapes:

1. Single-device entries.
2. Multi-device entries.
3. Legacy full-scan entries storing bucketed device dictionaries.

The long-term direction should be one clear canonical shape with deliberate migration paths, but that is not the current state.

Current migration contract:
- legacy `location` values are canonicalized into `area`,
- top-level and multi-device list entries drop legacy `location` storage during migration,
- legacy bucketed full-scan entries now migrate into canonical `devices` list rows plus `scan_settings`,
- legacy options rescans now persist canonical `devices` list rows instead of rewriting bucketed device dictionaries,
- compatibility for legacy bucketed full-scan entries still exists in setup code as a defensive fallback.

## Discovery Model

Current discovery has two mechanisms:
- UDP broadcast to collect likely CozyLife IPs.
- TCP probing on port `5555` to validate devices and fetch metadata.

Observed live validation on `2026-05-16`:
- broadcast discovery found a real light on the local network,
- the originally supplied IP for that device was stale or unreachable,
- the repo code successfully recovered the actual device IP through discovery.

This validates the architectural intent behind periodic rediscovery.

## Device Protocol Boundary

The protocol boundary is `tcp_client.py`.

Observed behavior:
- sends JSON messages terminated by `\\r\\n`,
- supports `info`, `query`, and `set` commands,
- resolves device metadata through `model.json`,
- waits for the matching top-level `sn` response and rejects explicit negative acknowledgments in automated tests.

`model.json` should be treated as an internal catalog snapshot that widens the space of potentially supported devices. It is not a maintained support contract by itself.

Observed provenance on `2026-05-17`:
- upstream catalog endpoint: [api-us.doiting.com/api/device_product/model?lang=en](https://api-us.doiting.com/api/device_product/model?lang=en)

Repository truth rule:
- live device behavior determines support status,
- `model.json` provides the closest provider-level capability declaration,
- mismatches between the two should be documented as parity gaps.

This boundary is the highest-value engineering surface for future reliability work.

## Entity Surfaces

Current Home Assistant platforms:
- `light`
- `switch`
- `sensor`

Current public support position:
- `light` is the only verified supported surface.
- `switch` and `sensor` are potentially supported surfaces present in code, but not yet verified on real hardware.

Current tested entity policy:
- switch-class devices surface through the `switch` platform,
- light surfaces are reserved for actual light-capable devices,
- light-wrapped switch entities are no longer part of the repository contract.
- active light `color_mode` now follows queried live state instead of constructor-time capability hints.

Current onboarding behavior:
- config flow can create entries for discovered `light`, `switch`, `sensor`, and `unknown` devices,
- only `light`, `switch`, and `sensor` currently have first-class Home Assistant platforms,
- `unknown` devices can therefore be stored by config flow without gaining a default entity surface,
- configured devices with explicit DIY DPID mappings can surface read-only custom sensor entities for those mapped DPIDs,
- configured devices with explicit DIY write opt-in can also surface custom writable boolean switch entities for observed catalog-backed DPIDs,
- DIY-mapped entities remain user-defined behavior rather than default supported product behavior.

## Architecture Principles

- Local protocol truth should outrank historical README claims.
- Canonical state shapes should outrank compatibility shims over time.
- Verified behavior should be documented separately from desired behavior.
- Hardware-specific quirks should be isolated, named, and justified.
- Every public-facing capability claim should map to either verified behavior or an explicit target-state design doc.

## Related Docs

- `docs/DESIGN.md`
- `docs/PLANS.md`
- `docs/RELIABILITY.md`
- `docs/SECURITY.md`
- `docs/SUPPORT.md`
- `docs/READINESS_RUBRIC.md`
- `docs/design-docs/core-beliefs.md`
- `docs/product-specs/index.md`
- `CODEBASE_MAP.md`
- `VERIFICATION_AUDIT.md`
