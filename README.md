<p align="center">
  <img src="custom_components/cozylife/brand/logo.png" alt="CozyLife logo" width="320" />
</p>

# CozyLife for Home Assistant

Local-first Home Assistant integration for CozyLife devices.

## What This Repository Is

This repository contains a Home Assistant custom integration that discovers and controls CozyLife devices on the local network.

Current observed scope:
- config-flow onboarding,
- local discovery through TCP scanning and UDP broadcast assistance,
- light entities,
- switch entities in code,
- sensor datapoint entities in code,
- periodic rediscovery for stale IP recovery.

Current onboarding behavior:
- the config flow can present all discovered CozyLife device classes for selection, including `light`, `switch`, `sensor`, and `unknown`,
- product support and Home Assistant surface behavior still depend on whether the repository has a maintained platform for that device type.

Current public support position:
- verified supported surface: lights,
- potentially supported but not verified on hardware: switches and sensors.

## Current Status

This repository is under active documentation and verification hardening.

What is currently verified:
- the integration can discover a live CozyLife light on a LAN through the repository's own broadcast discovery code,
- the integration can connect to a live bulb on TCP port `5555`,
- the repository can fetch device info and state using the current `tcp_client.py` implementation,
- the repository can drive the full repo-exposed verified light surface on real hardware and restore the original state after the pass,
- `model.json` is actively used to classify device type and capability metadata,
- light support is verified on real hardware and treated as first-class supported.

Repository evidence bar for verified support:
- discovery success on at least one real device in the class,
- query success on at least one real device in the class,
- successful control of the relevant features on at least one real device in the class.

Support labels used in this repository:
- supported: discovery, query, and relevant control paths verified on a real device,
- partially supported: the device works on real hardware but not all expected controls for the class are verified working,
- potentially supported: plausible from code and catalog data, but not yet verified on hardware.

Support truth rules:
- live device behavior determines whether a device is supported or partially supported,
- `model.json` is the closest provider-level declaration of expected capability,
- any mismatch between live behavior and `model.json` should be documented explicitly,
- the long-term goal is feature parity with the capabilities `model.json` declares for a model, where real hardware confirms those capabilities,
- support and parity tracking should use the concrete model/PID first, then summarize by class where useful.

Current light support note:
- lights are treated as first-class supported based on prior successful Home Assistant control plus current live discovery/query/control verification,
- the seeded parity register entry now includes a full live validation pass for the current verified light PID,
- some catalog-declared light DPIDs for that verified PID remain unverified and unmapped in the current repo surface.

What is not yet fully verified:
- switch behavior on real hardware,
- sensor behavior on real hardware,
- sensor semantics beyond raw datapoint exposure,
- long-run reliability under reconnect, timeout, and unsolicited message conditions,
- consistency of light capability inference across all supported devices.

What is potentially supported but not maintained as a first-class claim:
- device classes that can be classified or inferred from `model.json`,
- switch and sensor paths that exist in code but have not yet been hardware-validated in this repository.
- `unknown` devices can still be discovered and added as config entries, but the current repository does not expose a first-class Home Assistant platform for them.

## Catalog Provenance

`custom_components/cozylife/model.json` is a checked-in snapshot of the upstream Doiting device model catalog.

Upstream source:
- [api-us.doiting.com/api/device_product/model?lang=en](https://api-us.doiting.com/api/device_product/model?lang=en)

Repository policy:
- the local file is used as an internal catalog snapshot,
- upstream presence does not imply verified support in this repository,
- verified support still requires real hardware validation.

## Contributor Validation Path

Contributions that promote an unverified device class into a verified supported surface should include:
- real hardware identification,
- discovery evidence,
- device info and query evidence,
- the resulting Home Assistant entity surface,
- known limitations, quirks, or partial-support boundaries.

If you have a physical device that falls under a verified or potentially supported class and it does not work in practice, open an issue with:
- device identification details,
- model name and PID if known,
- discovery behavior,
- query behavior if available,
- control behavior and which features fail,
- the observed Home Assistant outcome,
- any logs or quirks that narrow the failure.

## Installation

### Preferred: HACS

1. Open **HACS -> Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add this repository URL and choose **Integration**.
4. Install **CozyLife** from HACS.
5. Restart Home Assistant.
6. Open **Settings -> Devices & Services**.
7. Add the **CozyLife** integration.
8. Let the integration scan automatically, or provide a custom IP range if required.

### Fallback: Manual

1. Copy `custom_components/cozylife` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Open **Settings -> Devices & Services**.
4. Add the **CozyLife** integration.
5. Let the integration scan automatically, or provide a custom IP range if required.

## Verified Discovery Note

The integration supports two discovery patterns:
- explicit TCP probing across one or more IP ranges,
- UDP broadcast-assisted discovery followed by TCP validation.

Observed on `2026-05-16`:
- a supplied stale IP was unreachable,
- broadcast discovery still found the real bulb IP,
- the bulb was then successfully probed and classified as a light.

## Product Direction

The goal is not just "it works on my LAN." The goal is a public-quality integration that is:
- understandable,
- verifiable,
- explicit about support boundaries,
- reliable under common LAN failure modes,
- maintainable by someone other than the original author.

## Documentation Map

- [Glossary](GLOSSARY.md)
- [Architecture](ARCHITECTURE.md)
- [Plans](docs/PLANS.md)
- [Reliability](docs/RELIABILITY.md)
- [Security](docs/SECURITY.md)
- [Support](docs/SUPPORT.md)
- [Design](docs/DESIGN.md)
- [Product Sense](docs/PRODUCT_SENSE.md)
- [Readiness Rubric](docs/READINESS_RUBRIC.md)
- [Design Docs Index](docs/design-docs/index.md)
- [Product Specs Index](docs/product-specs/index.md)
- [Execution Plans](docs/exec-plans/)
- [CI](docs/CI.md)
- [Parity Register](docs/generated/parity-gap-register.md)
- [Latest Verified Light Live Validation](docs/generated/rju4k7-live-validation-2026-05-19.md)
- [Tested But Not Confirmed](docs/generated/tested-but-not-confirmed-capabilities.md)

## Versioning

HACS metadata updates are manual in this repository.

Do not rely on automated version bump workflows. When preparing a release, update:
- `custom_components/cozylife/manifest.json`
- `hacs.json`

## Validation Artifacts

The current static and verification maps are temporary dated evidence artifacts, not long-term canonical root docs.

Current evidence artifacts:
- [CODEBASE_MAP.md](CODEBASE_MAP.md)
- [VERIFICATION_AUDIT.md](VERIFICATION_AUDIT.md)

These should eventually move under the documentation evidence/completed-work area once the canonical docs are mature enough.
