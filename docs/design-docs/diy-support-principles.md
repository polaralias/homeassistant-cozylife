# DIY Support Principles

## Principle

The repository should allow careful user extension without pretending that undocumented protocol behavior is first-class supported product behavior.

## Why This Exists

The integration already knows more about some devices than it can confidently expose:

- some devices are only partially understood,
- some catalog-declared DPIDs are visible but unmapped,
- some live-tested behaviors are real but not yet semantically stable enough to expose by default.

DIY support is the pressure-release valve for that gap.

## Desired End State

Users should be able to opt into custom behavior on their own devices without forcing the repository to:

- overclaim support,
- expose unstable behavior by default,
- turn every live protocol lead into a permanent public surface.

## Repository Policy

DIY support should be:

- explicitly opt-in
- clearly labeled as custom, not verified support
- isolated from the default product surface
- reversible by configuration
- documented as user-owned behavior rather than repository-guaranteed behavior

## Safe Scope

The safest first scope is:

- raw DPID read exposure
- user-defined naming for raw datapoints
- user-defined type hints for datapoints that are already observed in query responses

This is safer than arbitrary writes because:

- it does not change device state,
- it builds on query behavior the repository can already observe,
- it aligns with the current sensor platform's raw-datapoint direction.

## Higher-Risk Scope

Write-capable DIY support is materially riskier.

It should not be the first step unless the repository is willing to own:

- bad user mappings,
- device-state corruption or confusing behavior,
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
