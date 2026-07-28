---
type: "Product Contract"
title: "Light Device Behaviour"
description: "Documents Light Device Behaviour for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - product-contract
navigation:
  role: foundational
  order: 20
---
# Light Device Behaviour

## Desired Product Outcome

A supported CozyLife light should expose a stable and understandable Home Assistant light entity.

## Current Verified Behaviour

Live validation across `2026-05-16`, `2026-05-17`, and `2026-05-19` confirmed a real verified light PID with:
- model name `Smart Bulb Light`
- one verified light PID
- type code `01`

Verified discovery and state query data:
- the bulb was discovered through broadcast-assisted discovery,
- the repository connected over TCP `5555`,
- the bulb returned a valid info response and a valid state query response.
- the bulb class is also considered control-verified from prior successful Home Assistant usage on an earlier repository revision.
- explicit current-state validation on `2026-05-17` confirmed reversible brightness control from `1000` to `900` and successful restore to `1000`.
- full live validation on `2026-05-19` confirmed the repo-exposed light feature surface on real hardware:
  - on/off
  - brightness
  - colour temperature
  - HS colour
  - `sleep`, `warm`, `study`, and `chrismas`
  - brightness, colour-temperature, and HS transition paths
  - explicit state restore after the full pass

Repository support bar for this class:
- discovery, query, and successful control of the relevant light features on at least one real light are required for first-class light support in this repository.

Partial-support rule for lights:
- if a light can be discovered and controlled only for a subset of expected features, it should be documented as partially supported rather than fully supported.

Validation note:
- the seeded PID now has a full live validation record in the parity register and a generated evidence artefact.

Observed query result:
- power `1`
- mode `0`
- colour temp `0`
- brightness `1000`
- hue `65535`
- saturation `65535`

## Current Capability Inference

From `model.json`, the repo infers support for:
- on/off,
- brightness,
- colour temperature,
- HS colour,
- effect-related datapoints.

This is capability inference for the verified light surface, not broad support proof for every catalogued device class.

## Capability Truth Rule

- live light behaviour determines whether a specific light is supported or partially supported,
- `model.json` is the closest provider-level declaration of what that model should be capable of,
- if live behaviour differs from `model.json`, the mismatch should be documented explicitly,
- the long-term target is feature parity with catalogue-declared capability where real hardware confirms the model,
- the concrete model/PID is the primary support and parity tracking unit.

## Current Tested Behaviour

Automated contract coverage now protects this rule:
- startup DPID capability hints determine supported colour modes,
- refreshed live state determines the active Home Assistant `color_mode`.

This closes the earlier mismatch where HS-capable lights could initialise in `hs` mode before the first query even when the queried live state was white-mode brightness.

## Current Risk

What is still not hardware-verified:
- some catalogue-declared light DPIDs for the verified PID,
- longer-session behaviour beyond the current focussed live pass.

## Repository knowledge

- [Documentation map](../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
