# DIY Support

## Desired Product Outcome

A user with unsupported or partially understood CozyLife hardware should have a documented path to expose custom datapoints without the repository falsely claiming that the device is fully supported.

## Current State

Current repository behavior:

- users can add discovered `light`, `switch`, `sensor`, and `unknown` devices through config flow,
- only `light`, `switch`, and `sensor` have first-class runtime platforms,
- the sensor platform already exposes raw datapoints when a device is classified as a sensor,
- tested-but-not-confirmed DPID behavior is recorded in generated evidence docs but not exposed as product behavior.

## Proposed Scope

The first useful DIY support target should be:

- custom raw DPID mappings on a per-device basis
- read-oriented first
- focused on observed query datapoints

Current implemented slice:

- custom read mappings for observed/catalog-backed DPIDs
- custom writable mappings only for explicitly opted-in per-device boolean switch DPIDs
- writable candidates constrained to DPIDs that are both observed in live query data and present in the stored catalog-backed DPID list for the device

Example outcome:

- a user adds a device,
- the repository knows its `did`, `pid`, and current query keys,
- the user defines a custom mapping for selected DPIDs,
- Home Assistant exposes those values under a clearly custom surface.

## Non-Goals For The First Iteration

- arbitrary write support for undocumented DPIDs
- claiming custom mappings are repository-supported semantics
- automatic inference that a custom mapping should become default product behavior
- generic writable number, select, or button synthesis without further evidence and design work

## Product Labels

DIY-mapped behavior should be labeled as:

- custom
- user-defined
- not repository-verified unless separately promoted

## Verification Rule

A successful DIY mapping does not automatically promote a capability into:

- `supported`
- `partially supported`

Promotion still requires the repository evidence bar and an explicit product decision.

## Open Questions

Resolved current contract:

- DIY support applies to any configured device with explicit mappings, including `unknown` devices.
- DIY mappings currently live in config-entry options.
- The read path exposes custom sensor-style values.
- The current write path exists only for explicitly opted-in per-device boolean switch mappings.

Still open:

- whether DIY configuration should stay in the options flow long term or move to a more guided UI,
- whether the writable DIY surface should remain capped at boolean switches,
- whether any future custom entity types can be added without weakening the repository support contract.
