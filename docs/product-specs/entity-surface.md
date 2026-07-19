# Entity Surface

## Desired Product Outcome

A user should be able to predict which Home Assistant entities a CozyLife device will create.

## Current Code-Path Surface

- light-class devices should create light entities,
- switch-class devices should create switch entities,
- sensor-class devices should create sensor entities.

## Current Public Support Position

- verified supported surface: light-class devices,
- potentially supported but not yet hardware-verified: switch-class devices,
- potentially supported but not yet hardware-verified: sensor-class devices.

## Current Observed Surface

- light-class devices create light entities,
- sensor-class devices create sensor datapoint entities,
- switch-class devices create switch entities.

## Canonical Policy

- light entities are reserved for actual light-capable devices,
- switch-class devices should not be reclassified as light entities by the integration,
- Home Assistant user-side remapping choices are outside the repository's product contract.

## Product Requirement

The repository should only promote a class into supported product behaviour when it has:
- real hardware verification to the repository evidence bar,
- a canonical entity mapping,
- documented exceptions if compatibility behaviour remains.

Minimum contributor evidence for promotion:
- real hardware identification,
- discovery evidence,
- info/query evidence,
- resulting Home Assistant entity surface,
- known limitations or quirks.

Current repository evidence bar:
- discovery success on at least one real device in the class,
- query success on at least one real device in the class,
- successful control of the relevant device features on at least one real device in the class.

Partial-support policy:
- if a device class works on real hardware but only a subset of expected controls are verified, document it as partially supported rather than supported.

Capability-parity policy:
- live device behaviour determines support truth,
- `model.json` is the closest provider-level declaration of expected capability,
- differences between live behaviour and `model.json` should be recorded as parity gaps rather than silently ignored,
- parity gaps should be tracked first per concrete model/PID and only then summarised by class.

Until then:
- lights are supported,
- switches and sensors remain potentially supported available code paths open to contributor-led validation.
