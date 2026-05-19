# Support

This document is the canonical support policy for the repository.

## Support Labels

The repository uses three support labels:

- `supported`
- `partially supported`
- `potentially supported`

## Definitions

### Supported

A device surface is `supported` when:
- it has been validated on real hardware,
- discovery succeeds,
- query succeeds,
- relevant control behavior succeeds,
- the repository is willing to claim it publicly as a first-class surface.

### Partially Supported

A device surface is `partially supported` when:
- it works on real hardware,
- but not all expected controls for that device or model are verified working.

### Potentially Supported

A device surface is `potentially supported` when:
- the repository can plausibly classify or operate it from code and catalog data,
- but it has not yet been validated on real hardware to the repository evidence bar.

## Evidence Bar

Promotion into `supported` requires:
- real hardware identification,
- discovery evidence,
- query evidence,
- control evidence for the relevant feature surface,
- documented limitations or quirks when applicable.

Promotion into `partially supported` requires:
- real hardware identification,
- discovery evidence,
- query evidence,
- at least some working control evidence,
- explicit documentation of which expected controls are missing or unverified.

## Truth Rules

- live device behavior determines support truth,
- `custom_components/cozylife/model.json` is the closest provider-level capability declaration,
- `model.json` is a catalog snapshot, not a support contract,
- mismatches between live behavior and `model.json` should be documented as parity gaps,
- support and parity should be tracked first per concrete model/PID, then summarized by class when useful.

## Current Repository Position

### Lights

- current label: `supported`
- basis:
  - prior successful Home Assistant control on real hardware,
  - live discovery and query verification,
  - full live validation of the repo-exposed light feature surface recorded for the current verified light PID

### Switches

- current label: `potentially supported`
- basis:
  - code paths exist,
  - catalog data exists,
  - no repository-grade real-hardware validation yet

### Sensors

- current label: `potentially supported`
- basis:
  - code paths exist,
  - catalog data exists,
  - no repository-grade real-hardware validation yet

### Unknown devices

- current label: not part of the public supported surface
- basis:
  - the config flow may still discover and store them,
  - the current repository does not provide a default first-class entity platform for `unknown` devices,
  - users may opt into read-only DIY DPID mappings that expose custom sensor entities,
  - users may also opt into narrowly constrained per-device DIY writable boolean switch mappings for observed catalog-backed DPIDs,
  - those DIY mappings remain user-defined and are not evidence of repository-supported semantics

## Contributor Path

If you want to promote a device class or model into stronger support:
- test on real hardware,
- capture discovery behavior,
- capture query behavior,
- capture control behavior,
- identify the concrete model/PID,
- document parity gaps against `model.json`,
- submit the evidence with the change.

If a physical device in a supported or potentially supported area fails in practice, open an issue with:
- device identification details,
- model name and PID if known,
- discovery behavior,
- query behavior,
- control behavior,
- the observed Home Assistant entity surface,
- logs, quirks, or constraints that narrow the failure.

## Related Docs

- `README.md`
- `CONTEXT.md`
- `docs/product-specs/entity-surface.md`
- `docs/product-specs/light-device-behavior.md`
- `docs/generated/parity-gap-register.md`
