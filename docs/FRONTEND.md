---
type: "Design Concept"
title: "Frontend"
description: "Documents Frontend for the homeassistant-cozylife repository."
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
# Frontend

This repository does not currently contain a browser frontend in the usual application sense.

The user-facing interface is the Home Assistant integration surface:
- config flow,
- options flow,
- entity presentation,
- service exposure.

## Desired UX Outcome

The effective frontend should be:
- easy to onboard,
- predictable about what will be created,
- transparent about scan behaviour,
- clear about names, areas, and supported entity types.

## Current UX Risks

- switch-class devices are currently modelled ambiguously in code,
- legacy entry support increases configuration complexity,
- the repo has not yet documented the expected UX for sensors in a user-facing way.

See:
- `docs/product-specs/new-user-onboarding.md`
- `docs/product-specs/entity-surface.md`

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
