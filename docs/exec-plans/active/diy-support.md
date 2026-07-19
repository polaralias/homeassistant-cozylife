# DIY Support Plan

Status: Active

## Objective

Provide a safe custom-extension path for users with unsupported or partially understood CozyLife devices, without turning undocumented protocol behaviour into default product claims.

## Current Implemented Slice

- per-device custom raw DPID mapping
- query-backed values only
- custom entity naming
- explicit labelling that the mapping is user-defined and not repository-verified
- constrained per-device writable boolean switch mappings behind explicit opt-in
- writable candidates limited to DPIDs that are both observed live and present in the stored catalogue-backed DPID list for the device

## What This Plan Still Covers

- keep DIY behaviour clearly separate from supported product behaviour
- decide whether the current writable DIY slice is sufficient or should remain tightly capped
- document future extension rules before adding broader custom entity types
- keep the contributor and support policy explicit as more DIY evidence arrives

## Why This Shape

- the repository already has raw datapoint exposure patterns in `sensor.py`
- read-first behaviour is safer than undocumented writes
- the current writable path stays narrow enough to avoid turning protocol archaeology into a default product surface
- it gives unsupported hardware owners a practical path without forcing the repo to overclaim support

## Deferred Work

- additional write-capable DIY controls beyond boolean switches
- generic writable number, select, or button synthesis
- automatic promotion from DIY mapping into supported product behaviour
- generic unknown-device entity synthesis without explicit user configuration
