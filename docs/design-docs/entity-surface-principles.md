# Entity Surface Principles

## Principle

Each physical device should map to a coherent Home Assistant surface.

## Desired End State

- a supported device should create predictable entities,
- entity domain choice should be intentional,
- duplicated representations should only exist if they are explicitly justified.
- light entities should be reserved for actual light-capable devices rather than compatibility wrappers around switches.

## Current State

The repository now enforces one entity-domain choice for switch-class devices:
- `switch` entities remain the canonical switch surface,
- light-wrapped switch entities are no longer part of the tested contract.

## Standard

Before code cleanup, the repository should first define:
- what a switch should be,
- how sensors should be represented beyond raw datapoints.
