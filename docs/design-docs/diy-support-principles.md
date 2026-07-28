---
type: "Design Concept"
title: "DIY Support Principles"
description: "Documents DIY Support Principles for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - design-concept
navigation:
  role: supporting
  order: 100
---
# DIY Support Principles

## Principle

The repository should allow careful user extension without pretending that undocumented protocol behaviour is first-class supported product behaviour.

## Why This Exists

The integration already knows more about some devices than it can confidently expose:

- some devices are only partially understood,
- some catalogue-declared DPIDs are visible but unmapped,
- some live-tested behaviours are real but not yet semantically stable enough to expose by default.

DIY support is the pressure-release valve for that gap.

## Desired End State

Users should be able to opt into custom behaviour on their own devices without forcing the repository to:

- overclaim support,
- expose unstable behaviour by default,
- turn every live protocol lead into a permanent public surface.

## Repository Policy

DIY support should be:

- explicitly opt-in
- clearly labelled as custom, not verified support
- isolated from the default product surface
- reversible by configuration
- documented as user-owned behaviour rather than repository-guaranteed behaviour

## Safe Scope

The safest first scope is:

- raw DPID read exposure
- user-defined naming for raw datapoints
- user-defined type hints for datapoints that are already observed in query responses

This is safer than arbitrary writes because:

- it does not change device state,
- it builds on query behaviour the repository can already observe,
- it aligns with the current sensor platform's raw-datapoint direction.

## Higher-Risk Scope

Write-capable DIY support is materially riskier.

It should not be the first step unless the repository is willing to own:

- bad user mappings,
- device-state corruption or confusing behaviour,
- ambiguous protocol semantics,
- support issues caused by undocumented commands.

If write support is ever added, it should likely require:

- per-device explicit opt-in
- narrow allowed value shapes
- warnings in both docs and UI-facing configuration
- clear separation from default supported features

## Support Boundary

DIY support does not change support labels by itself.

A capability can be:

- available through DIY configuration,
- tested but not confirmed,
- and still not part of the public supported product surface.

## Recommended First Iteration

The repository should prefer:

1. user-defined raw sensor mappings for observed DPID values
2. optional naming and grouping for those raw entities
3. only later, carefully constrained write experiments if there is strong demand and clear semantics

## Repository knowledge

- [Documentation map](../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
