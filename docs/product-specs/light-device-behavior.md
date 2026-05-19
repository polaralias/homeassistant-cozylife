# Light Device Behavior

## Desired Product Outcome

A supported CozyLife light should expose a stable and understandable Home Assistant light entity.

## Current Verified Behavior

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
  - color temperature
  - HS color
  - `sleep`, `warm`, `study`, and `chrismas`
  - brightness, color-temperature, and HS transition paths
  - explicit state restore after the full pass

Repository support bar for this class:
- discovery, query, and successful control of the relevant light features on at least one real light are required for first-class light support in this repository.

Partial-support rule for lights:
- if a light can be discovered and controlled only for a subset of expected features, it should be documented as partially supported rather than fully supported.

Validation note:
- the seeded PID now has a full live validation record in the parity register and a generated evidence artifact.

Observed query result:
- power `1`
- mode `0`
- color temp `0`
- brightness `1000`
- hue `65535`
- saturation `65535`

## Current Capability Inference

From `model.json`, the repo infers support for:
- on/off,
- brightness,
- color temperature,
- HS color,
- effect-related datapoints.

This is capability inference for the verified light surface, not broad support proof for every cataloged device class.

## Capability Truth Rule

- live light behavior determines whether a specific light is supported or partially supported,
- `model.json` is the closest provider-level declaration of what that model should be capable of,
- if live behavior differs from `model.json`, the mismatch should be documented explicitly,
- the long-term target is feature parity with catalog-declared capability where real hardware confirms the model,
- the concrete model/PID is the primary support and parity tracking unit.

## Current Tested Behavior

Automated contract coverage now protects this rule:
- startup DPID capability hints determine supported color modes,
- refreshed live state determines the active Home Assistant `color_mode`.

This closes the earlier mismatch where HS-capable lights could initialize in `hs` mode before the first query even when the queried live state was white-mode brightness.

## Current Risk

What is still not hardware-verified:
- some catalog-declared light DPIDs for the verified PID,
- longer-session behavior beyond the current focused live pass,
- `natural` as a distinct effect path without the Circadian Lighting dependency loaded.
