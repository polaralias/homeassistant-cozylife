# DIY Support Plan

Status: Active

## Objective

Provide a safe custom-extension path for users with unsupported or partially understood CozyLife devices, without turning undocumented protocol behavior into default product claims.

## Recommended Sequence

1. Define the contract for DIY support in canonical docs.
2. Start with read-only or read-first raw DPID mapping.
3. Reuse current sensor-style datapoint surfacing where possible.
4. Keep DIY behavior clearly separate from supported product behavior.
5. Only consider write-capable DIY support after the read-only surface is stable.

## First Iteration Target

- per-device custom raw DPID mapping
- query-backed values only
- custom entity naming
- explicit labeling that the mapping is user-defined and not repository-verified

## Why This Order

- the repository already has raw datapoint exposure patterns in `sensor.py`
- read-first behavior is safer than undocumented writes
- it gives unsupported hardware owners a practical path without forcing the repo to overclaim support

## Deferred Work

- write-capable DIY controls
- automatic promotion from DIY mapping into supported product behavior
- generic unknown-device entity synthesis without explicit user configuration
